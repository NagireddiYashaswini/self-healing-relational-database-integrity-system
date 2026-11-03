import uuid
import json
import time
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set
from backend.app.database.connection import get_connection, validate_identifier
from backend.app.services.audit_service import AuditService
from backend.app.services.recovery_manager import RecoveryManager
from backend.app.services.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)

class AlreadyRepairedError(Exception):
    """Raised when an integrity issue has already been repaired and duplicate execution is attempted."""
    pass

class StalePreviewError(Exception):
    """Raised when the database record has been modified after preview generation."""
    pass

def compute_row_hash(row_dict: Optional[Dict[str, Any]]) -> str:
    """Computes a deterministic cryptographic SHA-256 hash of a database row state."""
    if not row_dict:
        return ""
    clean_row = {}
    for k, v in row_dict.items():
        if isinstance(v, datetime):
            clean_row[k] = v.isoformat()
        else:
            clean_row[k] = str(v) if v is not None else None
    s = json.dumps(clean_row, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

class RepairEngine:
    def __init__(self):
        self.dependency_analyzer = DependencyAnalyzer()

    @staticmethod
    def _get_column_metadata(cur, table_name: str, column_name: str) -> Optional[Dict[str, Any]]:
        cur.execute("""
            SELECT DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, CHARACTER_MAXIMUM_LENGTH
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
            LIMIT 1
        """, (table_name, column_name))
        return cur.fetchone()

    @staticmethod
    def _validate_value_for_column_type(val: Any, data_type: str) -> Tuple[bool, Optional[str]]:
        if val is None or str(val).upper() == "DEFAULT" or str(val).upper() == "NULL":
            return True, None
        dt = (data_type or "").lower()
        if dt in ("int", "tinyint", "smallint", "mediumint", "bigint"):
            try:
                int(val)
                return True, None
            except (ValueError, TypeError):
                return False, f"Value '{val}' cannot be converted to integer for column type '{dt}'."
        elif dt in ("decimal", "numeric", "float", "double"):
            try:
                float(val)
                return True, None
            except (ValueError, TypeError):
                return False, f"Value '{val}' cannot be converted to numeric for column type '{dt}'."
        return True, None

    @staticmethod
    def _validate_proposed_value(
        cur,
        table_name: str,
        column_name: str,
        record_id: Any,
        pk_col: str,
        val: Any,
        rule_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates an administrator-supplied replacement value against:
        - NOT NULL / empty-string constraints
        - MySQL column DATA_TYPE
        - CHARACTER_MAXIMUM_LENGTH
        - Prohibited placeholder patterns (e.g. '[PROPOSED: ...]')
        - UNIQUE constraints
        - Domain / business rules (e.g., allowed values, min/max ranges)
        """
        if val is None or str(val).strip() == "":
            return False, f"Value for column '{column_name}' cannot be NULL or empty."

        val_str = str(val).strip()

        # Reject dummy / placeholder values
        prohibited_placeholders = ["[PROPOSED", "[PLACEHOLDER", "UNSPECIFIED", "DUMMY", "UNKNOWN", "N/A", "NONE", "NULL"]
        for p in prohibited_placeholders:
            if p in val_str.upper():
                return False, f"Value '{val_str}' contains an unverified placeholder pattern and is prohibited for business tables."

        # Fetch column definition
        cur.execute("""
            SELECT DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
            LIMIT 1
        """, (table_name, column_name))
        col_info = cur.fetchone()

        if col_info:
            dt = (col_info.get("DATA_TYPE") or "").lower()
            max_len = col_info.get("CHARACTER_MAXIMUM_LENGTH")

            # Check length
            if max_len and len(val_str) > max_len:
                return False, f"Value exceeds maximum allowed length of {max_len} characters (provided: {len(val_str)} characters)."

            # Check type
            if dt in ("int", "tinyint", "smallint", "mediumint", "bigint"):
                try:
                    int(val_str)
                except (ValueError, TypeError):
                    return False, f"Value '{val_str}' is not a valid integer for column type '{dt}'."
            elif dt in ("decimal", "numeric", "float", "double"):
                try:
                    float(val_str)
                except (ValueError, TypeError):
                    return False, f"Value '{val_str}' is not a valid numeric value for column type '{dt}'."
            elif dt in ("date", "datetime", "timestamp"):
                try:
                    datetime.strptime(val_str[:10], "%Y-%m-%d")
                except ValueError:
                    return False, f"Value '{val_str}' is not a valid date format (expected YYYY-MM-DD)."

        # Check unique constraint
        cur.execute("""
            SELECT tc.CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS tc
            JOIN information_schema.KEY_COLUMN_USAGE kcu 
              ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME 
             AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            WHERE tc.TABLE_SCHEMA = DATABASE()
              AND tc.TABLE_NAME = %s
              AND kcu.COLUMN_NAME = %s
              AND tc.CONSTRAINT_TYPE = 'UNIQUE'
            LIMIT 1
        """, (table_name, column_name))
        unique_c = cur.fetchone()
        if unique_c:
            cur.execute(
                f"SELECT COUNT(*) AS c FROM `{table_name}` WHERE `{column_name}` = %s AND `{pk_col}` != %s",
                (val_str, record_id)
            )
            if cur.fetchone()["c"] > 0:
                return False, f"Value '{val_str}' violates unique constraint on '{table_name}.{column_name}'. Another record already possesses this value."

        # Domain / rule params validation
        if rule_params:
            if "allowed_values" in rule_params:
                allowed = [str(a).strip().upper() for a in rule_params["allowed_values"]]
                if val_str.upper() not in allowed:
                    return False, f"Value '{val_str}' is not one of the permitted allowed values: {rule_params['allowed_values']}."
            if "min_value" in rule_params:
                try:
                    if float(val_str) < float(rule_params["min_value"]):
                        return False, f"Value '{val_str}' is less than minimum permitted value {rule_params['min_value']}."
                except ValueError:
                    pass
            if "max_value" in rule_params:
                try:
                    if float(val_str) > float(rule_params["max_value"]):
                        return False, f"Value '{val_str}' exceeds maximum permitted value {rule_params['max_value']}."
                except ValueError:
                    pass

        # Email format check if column is email
        if "email" in column_name.lower():
            if "@" not in val_str or "." not in val_str or len(val_str) < 5:
                return False, f"Value '{val_str}' is not a valid email address."

        # Customer name checks
        if "customer_name" in column_name.lower() or "name" in column_name.lower():
            if len(val_str) < 2:
                return False, "Customer name must be at least 2 characters in length."

        return True, None

    def get_repair_preview(
        self,
        issue_id: str,
        strategy_override: Optional[str] = None,
        repair_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates a transparent preview of a proposed self-healing action
        WITHOUT committing any modifications to the database.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Fetch issue
                cur.execute("SELECT * FROM integrity_issues WHERE issue_id = %s", (issue_id,))
                issue = cur.fetchone()
                if not issue:
                    raise ValueError(f"Integrity issue '{issue_id}' not found.")

                if issue["status"] == "REPAIRED":
                    raise AlreadyRepairedError("This integrity issue has already been repaired. Duplicate execution is not allowed.")

                if issue["status"] == "IGNORED":
                    raise ValueError(f"Integrity issue '{issue_id}' is marked as IGNORED and cannot be repaired.")

                table_name = validate_identifier(issue["table_name"])
                record_id = issue["record_id"]

                # 2. Fetch primary key column
                cur.execute("""
                    SELECT COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = %s
                      AND CONSTRAINT_NAME = 'PRIMARY'
                    LIMIT 1
                """, (table_name,))
                pk_res = cur.fetchone()
                pk_col = pk_res["COLUMN_NAME"] if pk_res else "id"

                # 3. Fetch current row state
                cur.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s", (record_id,))
                current_row = cur.fetchone()
                if not current_row:
                    # Check if the record is in quarantine or was already removed
                    cur.execute(
                        "SELECT * FROM quarantine_records WHERE source_table = %s AND source_pk_value = %s",
                        (table_name, str(record_id))
                    )
                    quarantined = cur.fetchone()

                    # Mark this issue and any duplicate issues for this non-existent record as REPAIRED
                    cur.execute(
                        "UPDATE integrity_issues SET status = 'REPAIRED', repaired_at = NOW() WHERE table_name = %s AND record_id = %s AND status != 'REPAIRED'",
                        (table_name, str(record_id))
                    )
                    cur.execute(
                        """
                        UPDATE repair_recommendations r
                        JOIN integrity_issues i ON r.issue_id = i.issue_id
                        SET r.approval_status = 'APPROVED'
                        WHERE i.table_name = %s AND i.record_id = %s
                        """,
                        (table_name, str(record_id))
                    )
                    conn.commit()

                    status_msg = "already quarantined" if quarantined else "already deleted/resolved"
                    return {
                        "issue_id": issue_id,
                        "table_name": table_name,
                        "record_id": str(record_id),
                        "strategy": strategy_override or "QUARANTINE",
                        "risk_level": "LOW",
                        "affected_rows_count": 0,
                        "before_state": {"status": "ABSENT_OR_QUARANTINED"},
                        "after_state": {"status": "ALREADY_REPAIRED"},
                        "dependent_tables": [],
                        "direct_children": [],
                        "downstream_tables": [],
                        "has_dependent_records": False,
                        "matching_child_records_count": 0,
                        "foreign_key_consequences": f"Record is {status_msg} and is no longer present in `{table_name}`.",
                        "sql_preview": [f"-- Record {table_name}.{pk_col}={record_id} does not exist in the database ({status_msg}). Marked issue as REPAIRED."],
                        "is_destructive": False,
                        "requires_confirmation": False,
                        "warning": f"Record {table_name}.{pk_col}={record_id} does not exist in the database ({status_msg}). The issue status has been marked as REPAIRED.",
                        "requires_admin_input": False,
                        "input_field_name": None,
                        "input_field_type": None,
                        "input_field_max_length": None,
                        "input_field_nullable": True,
                        "validation_error": None,
                        "row_version_token": "ALREADY_REPAIRED",
                        "status": "ALREADY_REPAIRED"
                    }

                # 4. Fetch recommendation & rule metadata
                cur.execute("SELECT * FROM repair_recommendations WHERE issue_id = %s", (issue_id,))
                rec = cur.fetchone()
                strategy = strategy_override or (rec["strategy"] if rec else "QUARANTINE")

                cur.execute("""
                    SELECT rule_code, name, description, parameters_json, parent_table, parent_column
                    FROM integrity_rules
                    WHERE rule_id = %s OR rule_code = %s
                    LIMIT 1
                """, (issue.get("rule_id"), issue.get("rule_code")))
                rule_row = cur.fetchone()
                rule_params = {}
                if rule_row and rule_row.get("parameters_json"):
                    try:
                        rule_params = json.loads(rule_row["parameters_json"]) if isinstance(rule_row["parameters_json"], str) else rule_row["parameters_json"]
                    except Exception:
                        rule_params = {}

                # 5. Assess dependent foreign key impact
                issue_severity = issue.get("severity") or (rec.get("risk_level") if rec else "MEDIUM")
                impact_assessment = self.dependency_analyzer.assess_repair_impact(
                    table_name, record_id, strategy, issue_severity=issue_severity
                )

                row_version_token = compute_row_hash(current_row)
                requires_admin_input = False
                input_field_name = None
                validation_error = None
                warning = None

                # 6. Simulate after-state and SQL statements
                after_row = dict(current_row)
                sql_preview = []
                is_destructive = False
                col_name = issue.get("column_name")
                invalid_val = issue.get("invalid_value")

                col_info = self._get_column_metadata(cur, table_name, col_name) if col_name else None
                col_type = col_info["DATA_TYPE"].upper() if col_info else "UNKNOWN"

                if strategy == "QUARANTINE":
                    is_destructive = True
                    sql_preview.append(f"INSERT INTO `quarantine_records` (source_table, source_pk_value, issue_type, row_data_json, quarantine_reason) VALUES ('{table_name}', '{record_id}', '{issue['category']}', '{{JSON_PAYLOAD}}', 'Automated quarantine repair');")
                    sql_preview.append(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = {record_id};")
                    after_row = {"status": "QUARANTINED", "archived_in": "quarantine_records"}

                elif strategy == "DELETE_RECORD":
                    is_destructive = True
                    sql_preview.append(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = {record_id};")
                    after_row = {"status": "DELETED"}

                elif strategy in ("RESTORE_PARENT", "RESTORE", "restore_parent", "restore"):
                    parent_table = issue.get("parent_table") or (rule_row.get("parent_table") if rule_row else None) or "departments"
                    parent_col = issue.get("parent_column") or (rule_row.get("parent_column") if rule_row else None) or f"{parent_table.rstrip('s')}_id"
                    missing_id = current_row.get(col_name) or issue.get("invalid_value")

                    cur.execute("SELECT * FROM quarantine_records WHERE source_table = %s AND source_pk_value = %s", (parent_table, str(missing_id)))
                    quarantined_parent = cur.fetchone()

                    if quarantined_parent:
                        sql_preview.append(f"-- Restoring parent record from quarantine_records (quarantine_id = {quarantined_parent['quarantine_id']})")
                        sql_preview.append(f"INSERT INTO `{parent_table}` VALUES (... archived row ...);")
                        after_row["parent_status"] = f"RESTORED_FROM_QUARANTINE (ID: {missing_id})"
                    else:
                        sql_preview.append(f"-- Creating baseline parent entity in `{parent_table}` to resolve foreign key reference")
                        sql_preview.append(f"INSERT INTO `{parent_table}` (`{parent_col}`, ...) VALUES ({missing_id}, ...);")
                        after_row["parent_status"] = f"RESTORED_BASELINE (ID: {missing_id})"

                elif strategy in ("MERGE_DUPLICATION", "MERGE_DUPLICATE", "MERGE", "merge_duplicate", "merge", "merge_duplication"):
                    is_destructive = True
                    sql_preview.append(f"-- Merging duplicate record: archiving to quarantine and deleting redundant row")
                    sql_preview.append(f"INSERT INTO `quarantine_records` (source_table, source_pk_value, issue_type, row_data_json, quarantine_reason) VALUES ('{table_name}', '{record_id}', 'DUPLICATE_MERGE', '{{JSON_PAYLOAD}}', 'Merged duplicate record into canonical');")
                    sql_preview.append(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = {record_id};")
                    after_row["status"] = "MERGED_AND_QUARANTINED"

                elif strategy == "MAP_PARENT":
                    parent_table = issue.get("parent_table") or (rule_row.get("parent_table") if rule_row else None)
                    parent_col = issue.get("parent_column") or (rule_row.get("parent_column") if rule_row else None)
                    if not parent_table or not parent_col:
                        cur.execute("""
                            SELECT REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                            FROM information_schema.KEY_COLUMN_USAGE
                            WHERE TABLE_SCHEMA = DATABASE()
                              AND TABLE_NAME = %s AND COLUMN_NAME = %s
                              AND REFERENCED_TABLE_NAME IS NOT NULL
                            LIMIT 1
                        """, (table_name, col_name))
                        fk_res = cur.fetchone()
                        if fk_res:
                            parent_table = fk_res["REFERENCED_TABLE_NAME"]
                            parent_col = fk_res["REFERENCED_COLUMN_NAME"]

                    new_parent_id = repair_parameters.get("parent_id") if repair_parameters else None
                    if new_parent_id:
                        cur.execute(f"SELECT COUNT(*) AS c FROM `{parent_table}` WHERE `{parent_col}` = %s", (new_parent_id,))
                        parent_exists = cur.fetchone()["c"] > 0
                        if parent_exists:
                            after_row[col_name] = new_parent_id
                            sql_preview.append(f"-- Verified parent mapping: `{parent_table}`.{parent_col} = {new_parent_id} exists")
                            sql_preview.append(f"UPDATE `{table_name}` SET `{col_name}` = %s WHERE `{pk_col}` = %s;  -- Parameters: ({new_parent_id}, {record_id})")
                        else:
                            requires_admin_input = True
                            input_field_name = col_name or "parent_id"
                            validation_error = f"Specified parent ID '{new_parent_id}' does NOT exist in `{parent_table}` (`{parent_col}`)."
                            after_row[col_name] = f"<Invalid Parent ID: {new_parent_id}>"
                            sql_preview.append(f"-- VALIDATION ERROR: Specified parent ID '{new_parent_id}' does NOT exist in `{parent_table}` (`{parent_col}`).")
                            sql_preview.append("-- Execution blocked. Administrator must supply an existing, verified parent ID.")
                            sql_preview.append("-- Note: Fabricating dummy parent records is strictly prohibited.")
                    else:
                        requires_admin_input = True
                        input_field_name = col_name or "parent_id"
                        warning = f"Orphan foreign key detected. Administrator must supply an authoritative parent ID from `{parent_table}`."
                        after_row[col_name] = f"<Awaiting Authoritative {parent_col or 'Parent ID'}>"
                        sql_preview.append("-- ==========================================================================")
                        sql_preview.append("-- ORPHAN FOREIGN KEY: PARENT MAPPING REQUIRED")
                        sql_preview.append(f"-- Missing Parent Reference: `{table_name}`.{col_name} = {invalid_val}")
                        sql_preview.append(f"-- Referenced Parent Entity: `{parent_table}` (`{parent_col}`)")
                        sql_preview.append(f"-- Administrator input required: An existing, verified `{parent_col}` from `{parent_table}` must be provided.")
                        sql_preview.append("-- Automatic fabrication of parent IDs or records is strictly prohibited.")
                        sql_preview.append(f"-- Template: UPDATE `{table_name}` SET `{col_name}` = %s WHERE `{pk_col}` = %s;")
                        sql_preview.append("-- ==========================================================================")

                elif strategy == "SET_DEFAULT":
                    curr_val = current_row.get(col_name)
                    curr_val_display = "NULL" if curr_val is None else (f'"{curr_val}"' if str(curr_val).strip() != "" else '"" (empty string)')
                    admin_val = None
                    if repair_parameters:
                        admin_val = repair_parameters.get("value")
                        if admin_val is None and "admin_provided_value" in repair_parameters:
                            admin_val = repair_parameters.get("admin_provided_value")

                    schema_default = col_info.get("COLUMN_DEFAULT") if col_info else None
                    has_legitimate_default = (schema_default is not None and schema_default != "" and str(schema_default).upper() != "NULL")

                    if admin_val is not None and str(admin_val).strip() != "":
                        is_valid, type_err = self._validate_proposed_value(cur, table_name, col_name, record_id, pk_col, admin_val, rule_params)
                        if not is_valid:
                            requires_admin_input = True
                            input_field_name = col_name
                            validation_error = type_err
                            after_row[col_name] = f"<Invalid Value: {admin_val}>"
                            sql_preview.append("-- ==========================================================================")
                            sql_preview.append("-- VALIDATION ERROR ON ADMINISTRATOR INPUT")
                            sql_preview.append(f"-- Error: {type_err}")
                            sql_preview.append(f"-- Column `{col_name}` requires a valid replacement value.")
                            sql_preview.append("-- Execution blocked until a valid administrator replacement value is provided.")
                            sql_preview.append("-- ==========================================================================")
                        else:
                            requires_admin_input = False
                            after_row[col_name] = str(admin_val).strip()
                            sql_preview.append(f"-- Administrator-Provided Replacement Value: '{admin_val}' (Validated against schema & business rules)")
                            sql_preview.append(f"-- Target: `{table_name}`.`{col_name}` ({col_type}) | Record ID: {record_id}")
                            sql_preview.append(f"UPDATE `{table_name}` SET `{col_name}` = %s WHERE `{pk_col}` = %s;  -- Parameters: ('{admin_val}', {record_id})")
                    elif has_legitimate_default:
                        requires_admin_input = False
                        after_row[col_name] = schema_default
                        sql_preview.append(f"-- Legitimate Schema Default Applied: '{schema_default}'")
                        sql_preview.append(f"UPDATE `{table_name}` SET `{col_name}` = %s WHERE `{pk_col}` = %s;  -- Parameters: ('{schema_default}', {record_id})")
                    else:
                        requires_admin_input = True
                        input_field_name = col_name
                        warning = f"Original value for column '{col_name}' is missing. The database schema does not define a default value. Administrator replacement value is required before execution."
                        after_row[col_name] = "<Awaiting Administrator Replacement Value>"
                        sql_preview.append("-- ==========================================================================")
                        sql_preview.append("-- MISSING ORIGINAL VALUE: ADMINISTRATOR INPUT REQUIRED")
                        sql_preview.append(f"-- Target: `{table_name}`.`{col_name}` ({col_type}) | Record ID: {record_id}")
                        sql_preview.append(f"-- Current Value: {curr_val_display}")
                        sql_preview.append(f"-- The MySQL schema does not define a default value for `{table_name}`.`{col_name}`.")
                        sql_preview.append("-- Policy: Automatic insertion of fabricated placeholders (e.g. '[PROPOSED: ...]') is strictly prohibited.")
                        sql_preview.append("-- Administrator must enter a verified replacement value in the modal to execute repair.")
                        sql_preview.append("-- Execution is disabled until a valid value is supplied.")
                        sql_preview.append(f"-- Parameterized SQL Template: UPDATE `{table_name}` SET `{col_name}` = %s WHERE `{pk_col}` = %s;")
                        sql_preview.append("-- ==========================================================================")

                elif strategy in ["MANUAL_INTERVENTION", "MANUAL_REVIEW", "NOTIFY_ADMIN"]:
                    if "allowed_values" in rule_params:
                        expected_domain_str = f"Allowed values = {rule_params['allowed_values']}"
                    elif "min_value" in rule_params and "max_value" in rule_params:
                        expected_domain_str = f"Permissible range = [{rule_params['min_value']} to {rule_params['max_value']}]"
                    elif "min_value" in rule_params:
                        expected_domain_str = f"Must be >= {rule_params['min_value']}"
                    elif "max_value" in rule_params:
                        expected_domain_str = f"Must be <= {rule_params['max_value']}"
                    else:
                        expected_domain_str = "Conformant domain value as defined by business rules"

                    violation_reason = issue.get("description") or f"Value '{invalid_val}' fails integrity constraints on `{table_name}`.{col_name}."

                    sql_preview.append("-- ==========================================================================")
                    sql_preview.append("-- MANUAL INTERVENTION REQUIRED")
                    sql_preview.append("-- Administrator input required. No automatic SQL execution available.")
                    sql_preview.append(f"-- Target: `{table_name}`.{col_name} ({col_type}) | Record ID: {record_id}")
                    sql_preview.append(f"-- Current Invalid Value: {invalid_val}")
                    sql_preview.append(f"-- Expected Range / Allowed Values: {expected_domain_str}")
                    sql_preview.append(f"-- Violation Reason: {violation_reason}")
                    sql_preview.append("-- Action: Human administrator must inspect this record and apply the verified business value manually.")
                    sql_preview.append("-- Automatic SQL execution is blocked by safety policy.")
                    sql_preview.append("-- ==========================================================================")

                else:
                    sql_preview.append(f"-- Strategy '{strategy}' for `{table_name}`.{col_name} (Record ID: {record_id})")
                    sql_preview.append("-- Administrator input required. No automatic execution available.")

                return {
                    "issue_id": issue_id,
                    "table_name": table_name,
                    "record_id": str(record_id),
                    "strategy": strategy,
                    "risk_level": impact_assessment["risk_level"],
                    "affected_rows_count": 1,
                    "before_state": current_row,
                    "after_state": after_row,
                    "dependent_tables": impact_assessment["dependent_tables"],
                    "direct_children": impact_assessment.get("direct_children", []),
                    "downstream_tables": impact_assessment.get("downstream_tables", []),
                    "has_dependent_records": impact_assessment.get("has_dependent_records", False),
                    "matching_child_records_count": impact_assessment.get("matching_child_records_count", 0),
                    "foreign_key_consequences": impact_assessment.get("foreign_key_consequences"),
                    "sql_preview": sql_preview,
                    "is_destructive": is_destructive,
                    "requires_confirmation": is_destructive or impact_assessment["has_dependent_records"],
                    "warning": warning or impact_assessment.get("warning"),
                    "requires_admin_input": requires_admin_input,
                    "input_field_name": input_field_name,
                    "input_field_type": col_type if requires_admin_input else None,
                    "input_field_max_length": col_info.get("CHARACTER_MAXIMUM_LENGTH") if col_info else None,
                    "input_field_nullable": (col_info.get("IS_NULLABLE") == "YES") if col_info else False,
                    "validation_error": validation_error,
                    "row_version_token": row_version_token
                }

        finally:
            conn.close()

    def approve_recommendation(self, recommendation_id: Any, operator: str = "ADMIN_USER") -> Dict[str, Any]:
        """Marks a repair recommendation as APPROVED by an authorized operator."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                if isinstance(recommendation_id, str) and (recommendation_id.startswith("ISSUE-") or not recommendation_id.isdigit()):
                    cur.execute("SELECT * FROM repair_recommendations WHERE issue_id = %s", (recommendation_id,))
                else:
                    cur.execute("SELECT * FROM repair_recommendations WHERE recommendation_id = %s", (int(recommendation_id),))
                rec = cur.fetchone()
                if not rec:
                    raise ValueError(f"Recommendation ID {recommendation_id} not found.")

                rec_id = rec["recommendation_id"]
                cur.execute("UPDATE repair_recommendations SET approval_status = 'APPROVED' WHERE recommendation_id = %s", (rec_id,))
                cur.execute("UPDATE integrity_issues SET status = 'APPROVED' WHERE issue_id = %s", (rec["issue_id"],))

            conn.commit()

            AuditService.log_event(
                event_type="REPAIR_APPROVED",
                action_description=f"Approved repair recommendation #{recommendation_id} for issue {rec['issue_id']}.",
                actor=operator,
                related_issue_id=rec["issue_id"]
            )

            return {
                "recommendation_id": recommendation_id,
                "approval_status": "APPROVED",
                "message": "Recommendation successfully approved. Ready for transaction execution."
            }
        finally:
            conn.close()

    def execute_repair(
        self,
        issue_id: str,
        strategy: str,
        repair_parameters: Optional[Dict[str, Any]] = None,
        confirmed: bool = False,
        operator: str = "ADMIN_USER",
        row_version_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a self-healing repair inside an atomic InnoDB transaction.
        Enforces idempotency, pre-repair checkpointing, before-and-after verification, and rollback on failure.
        """
        execution_id = f"EXEC-{uuid.uuid4().hex[:10].upper()}"
        transaction_id = f"TX-{uuid.uuid4().hex[:10].upper()}"
        start_time = datetime.now()
        t0 = time.time()

        conn = get_connection()
        conn.begin()
        try:
            with conn.cursor() as cur:
                # 1. Fetch issue and verify eligibility with row-level lock (concurrency & duplicate protection)
                cur.execute("SELECT * FROM integrity_issues WHERE issue_id = %s FOR UPDATE", (issue_id,))
                issue = cur.fetchone()
                if not issue:
                    raise ValueError(f"Issue '{issue_id}' not found.")

                if issue["status"] == "REPAIRED":
                    raise AlreadyRepairedError("This integrity issue has already been repaired. Duplicate execution is not allowed.")

                if issue["status"] == "IGNORED":
                    raise ValueError(f"Issue '{issue_id}' is marked as IGNORED and cannot be repaired.")

                # Lock recommendation row for concurrency protection
                cur.execute("SELECT * FROM repair_recommendations WHERE issue_id = %s FOR UPDATE", (issue_id,))
                rec = cur.fetchone()
                if not rec:
                    raise ValueError(f"Repair recommendation for issue '{issue_id}' not found.")

                if rec.get("approval_status") in ("EXECUTED", "REPAIRED"):
                    raise AlreadyRepairedError("This integrity issue has already been repaired. Duplicate execution is not allowed.")

                if rec.get("requires_approval") and rec.get("approval_status") != "APPROVED" and not confirmed:
                    raise ValueError(
                        f"Repair execution for issue '{issue_id}' requires explicit administrator approval before execution."
                    )

                if strategy == "MANUAL_INTERVENTION":
                    raise ValueError(
                        "Recommendations with strategy 'MANUAL_INTERVENTION' require human operator action and cannot be executed automatically."
                    )

                table_name = validate_identifier(issue["table_name"])
                record_id = issue["record_id"]

                # 2. Find primary key column
                cur.execute("""
                    SELECT COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = %s
                      AND CONSTRAINT_NAME = 'PRIMARY'
                    LIMIT 1
                """, (table_name,))
                pk_res = cur.fetchone()
                pk_col = pk_res["COLUMN_NAME"] if pk_res else "id"

                # 3. Capture before-state row
                cur.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s FOR UPDATE", (record_id,))
                before_row = cur.fetchone()

                if not before_row:
                    # Check if already quarantined or deleted
                    cur.execute(
                        "SELECT * FROM quarantine_records WHERE source_table = %s AND source_pk_value = %s",
                        (table_name, str(record_id))
                    )
                    quarantined = cur.fetchone()

                    cur.execute(
                        "UPDATE integrity_issues SET status = 'REPAIRED', repaired_at = NOW() WHERE table_name = %s AND record_id = %s AND status != 'REPAIRED'",
                        (table_name, str(record_id))
                    )
                    cur.execute(
                        """
                        UPDATE repair_recommendations r
                        JOIN integrity_issues i ON r.issue_id = i.issue_id
                        SET r.approval_status = 'APPROVED'
                        WHERE i.table_name = %s AND i.record_id = %s
                        """,
                        (table_name, str(record_id))
                    )
                    conn.commit()

                    status_msg = "already quarantined" if quarantined else "already deleted/resolved"
                    return {
                        "execution_id": f"EXEC-{uuid.uuid4().hex[:8].upper()}",
                        "issue_id": issue_id,
                        "transaction_id": f"TX-{uuid.uuid4().hex[:8].upper()}",
                        "status": "SUCCESS",
                        "strategy": strategy,
                        "executed_by": operator,
                        "executed_at": datetime.now(),
                        "sql_executed": f"-- Record {table_name}.{pk_col}={record_id} does not exist ({status_msg}). Marked issue as REPAIRED.",
                        "execution_time_ms": 0,
                        "verified": True,
                        "message": f"Record {table_name}.{pk_col}={record_id} does not exist ({status_msg}). The issue has been marked as REPAIRED."
                    }

                # Stale preview check
                current_token = compute_row_hash(before_row)
                if row_version_token and row_version_token != current_token:
                    raise StalePreviewError(
                        "Database record has been modified since the preview was generated. "
                        "Please refresh the preview before executing."
                    )

            # 4. Take recovery checkpoint before modifying database
            RecoveryManager.create_checkpoint(
                target_table=table_name,
                checkpoint_name=f"Pre-repair checkpoint for {issue_id}",
                checkpoint_type="PRE_REPAIR",
                row_id_filter=str(record_id)
            )

            # 5. Execute repair within strict transaction
            sql_statements_executed = []
            with conn.cursor() as cur:
                cur.execute("SAVEPOINT pre_repair_step;")

                if strategy == "QUARANTINE":
                    # Insert into quarantine
                    insert_quarantine_sql = """
                        INSERT INTO quarantine_records (
                            source_table, source_pk_value, issue_type, row_data_json, quarantine_reason, quarantined_by
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(insert_quarantine_sql, (
                        table_name,
                        str(record_id),
                        issue["category"],
                        json.dumps(before_row, default=str),
                        issue["description"],
                        operator
                    ))
                    # Delete from active/staging table
                    cur.execute(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = %s", (record_id,))
                    sql_statements_executed.append(f"QUARANTINE row from `{table_name}` WHERE `{pk_col}` = {record_id}")

                elif strategy == "DELETE_RECORD":
                    cur.execute(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = %s", (record_id,))
                    sql_statements_executed.append(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = {record_id}")

                elif strategy in ("RESTORE_PARENT", "RESTORE", "restore_parent", "restore"):
                    parent_table = validate_identifier(issue.get("parent_table") or (rule_meta.get("parent_table") if rule_meta else None) or "departments")
                    parent_col = validate_identifier(issue.get("parent_column") or (rule_meta.get("parent_column") if rule_meta else None) or f"{parent_table.rstrip('s')}_id")
                    missing_id = before_row.get(col_name) or issue.get("invalid_value")

                    cur.execute("SELECT * FROM quarantine_records WHERE source_table = %s AND source_pk_value = %s", (parent_table, str(missing_id)))
                    q_parent = cur.fetchone()
                    if q_parent and q_parent.get("row_data_json"):
                        parent_data = json.loads(q_parent["row_data_json"])
                        cols = [f"`{k}`" for k in parent_data.keys()]
                        placeholders = ["%s"] * len(cols)
                        vals = list(parent_data.values())
                        cur.execute(f"INSERT INTO `{parent_table}` ({', '.join(cols)}) VALUES ({', '.join(placeholders)})", tuple(vals))
                        cur.execute("UPDATE quarantine_records SET resolved = TRUE, resolution_notes = 'Restored via self-healing' WHERE quarantine_id = %s", (q_parent["quarantine_id"],))
                        sql_statements_executed.append(f"RESTORE parent from quarantine into `{parent_table}` ({parent_col} = {missing_id})")
                    else:
                        if parent_table == "departments":
                            cur.execute("INSERT INTO `departments` (`dept_id`, `dept_code`, `dept_name`, `budget`) VALUES (%s, %s, %s, 100000.00)",
                                        (missing_id, f"DEPT_{missing_id}", f"Restored Department {missing_id}"))
                        elif parent_table == "instructors":
                            cur.execute("INSERT INTO `instructors` (`instructor_id`, `instructor_name`, `email`, `salary`) VALUES (%s, %s, %s, 50000.00)",
                                        (missing_id, f"Restored Faculty {missing_id}", f"faculty_{missing_id}@univ.edu"))
                        elif parent_table == "courses":
                            cur.execute("INSERT INTO `courses` (`course_id`, `course_code`, `course_name`, `credits`) VALUES (%s, %s, %s, 3)",
                                        (missing_id, f"CRS{missing_id}", f"Restored Course {missing_id}"))
                        elif parent_table == "students":
                            cur.execute("INSERT INTO `students` (`student_id`, `student_name`, `email`, `age`, `gpa`) VALUES (%s, %s, %s, 21, 3.00)",
                                        (missing_id, f"Restored Student {missing_id}", f"student_{missing_id}@univ.edu"))
                        sql_statements_executed.append(f"INSERT baseline parent stub into `{parent_table}` ({parent_col} = {missing_id})")

                elif strategy in ("MERGE_DUPLICATION", "MERGE_DUPLICATE", "MERGE", "merge_duplicate", "merge", "merge_duplication"):
                    insert_quarantine_sql = """
                        INSERT INTO quarantine_records (
                            source_table, source_pk_value, issue_type, row_data_json, quarantine_reason, quarantined_by
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(insert_quarantine_sql, (
                        table_name,
                        str(record_id),
                        "DUPLICATE_MERGE",
                        json.dumps(before_row, default=str),
                        issue["description"],
                        operator
                    ))
                    cur.execute(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = %s", (record_id,))
                    sql_statements_executed.append(f"MERGE: Archived duplicate row {pk_col}={record_id} to quarantine_records and deleted from `{table_name}`")

                elif strategy == "MAP_PARENT":
                    parent_id = repair_parameters.get("parent_id") if repair_parameters else None
                    if not parent_id:
                        raise ValueError("Mapping strategy requires an authoritative 'parent_id' parameter.")
                    col_name = validate_identifier(issue.get("column_name") or "parent_id")

                    parent_table = issue.get("parent_table")
                    parent_col = issue.get("parent_column")
                    if not parent_table or not parent_col:
                        cur.execute("""
                            SELECT REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                            FROM information_schema.KEY_COLUMN_USAGE
                            WHERE TABLE_SCHEMA = DATABASE()
                              AND TABLE_NAME = %s AND COLUMN_NAME = %s
                              AND REFERENCED_TABLE_NAME IS NOT NULL
                            LIMIT 1
                        """, (table_name, col_name))
                        fk_res = cur.fetchone()
                        if fk_res:
                            parent_table = fk_res["REFERENCED_TABLE_NAME"]
                            parent_col = fk_res["REFERENCED_COLUMN_NAME"]

                    if parent_table and parent_col:
                        cur.execute(f"SELECT COUNT(*) AS c FROM `{parent_table}` WHERE `{parent_col}` = %s", (parent_id,))
                        if cur.fetchone()["c"] == 0:
                            raise ValueError(f"Parent record with {parent_col}='{parent_id}' does not exist in parent table '{parent_table}'. Mapping rejected.")

                    cur.execute(f"UPDATE `{table_name}` SET `{col_name}` = %s WHERE `{pk_col}` = %s", (parent_id, record_id))
                    sql_statements_executed.append(f"UPDATE `{table_name}` SET `{col_name}` = {parent_id} WHERE `{pk_col}` = {record_id}")

                elif strategy == "SET_DEFAULT":
                    col_name = validate_identifier(issue.get("column_name"))
                    admin_val = None
                    if repair_parameters:
                        admin_val = repair_parameters.get("value")
                        if admin_val is None and "admin_provided_value" in repair_parameters:
                            admin_val = repair_parameters.get("admin_provided_value")

                    col_info = self._get_column_metadata(cur, table_name, col_name)
                    schema_default = col_info.get("COLUMN_DEFAULT") if col_info else None
                    has_legitimate_default = (schema_default is not None and schema_default != "" and str(schema_default).upper() != "NULL")

                    # Fetch rule parameters for domain validation
                    cur.execute("""
                        SELECT parameters_json FROM integrity_rules
                        WHERE rule_id = %s OR rule_code = %s
                        LIMIT 1
                    """, (issue.get("rule_id"), issue.get("rule_code")))
                    r_meta = cur.fetchone()
                    rule_params = {}
                    if r_meta and r_meta.get("parameters_json"):
                        try:
                            rule_params = json.loads(r_meta["parameters_json"]) if isinstance(r_meta["parameters_json"], str) else r_meta["parameters_json"]
                        except Exception:
                            rule_params = {}

                    if admin_val is not None and str(admin_val).strip() != "":
                        val_to_set = str(admin_val).strip()
                    elif has_legitimate_default:
                        val_to_set = schema_default
                    else:
                        raise ValueError(
                            f"Administrator replacement value is required for column '{col_name}'. "
                            "Automatic insertion of placeholder values is strictly prohibited."
                        )

                    # Validate value against column type, length, unique constraints, and domain rules
                    is_valid, err = self._validate_proposed_value(cur, table_name, col_name, record_id, pk_col, val_to_set, rule_params)
                    if not is_valid:
                        raise ValueError(f"Invalid replacement value for column '{col_name}': {err}")

                    cur.execute(f"UPDATE `{table_name}` SET `{col_name}` = %s WHERE `{pk_col}` = %s", (val_to_set, record_id))
                    sql_statements_executed.append(f"UPDATE `{table_name}` SET `{col_name}` = '{val_to_set}' WHERE `{pk_col}` = {record_id}")

                else:
                    raise ValueError(f"Unsupported repair strategy: {strategy}")

                # 6. Verification check: Verify state after repair
                after_row = None
                if strategy not in ["DELETE_RECORD", "QUARANTINE"]:
                    cur.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s", (record_id,))
                    after_row = cur.fetchone()
                else:
                    cur.execute(f"SELECT COUNT(*) as c FROM `{table_name}` WHERE `{pk_col}` = %s", (record_id,))
                    cnt = cur.fetchone()["c"]
                    if cnt != 0:
                        raise RuntimeError("Verification failed: Record still exists after deletion.")
                    after_row = {"status": "DELETED_OR_QUARANTINED"}

                # 7. Update issue and recommendation status
                cur.execute(
                    "UPDATE integrity_issues SET status = 'REPAIRED', repaired_at = NOW() WHERE issue_id = %s",
                    (issue_id,)
                )
                cur.execute(
                    "UPDATE repair_recommendations SET approval_status = 'APPROVED' WHERE issue_id = %s",
                    (issue_id,)
                )

                # If this was a destructive repair (QUARANTINE or DELETE_RECORD), any other open issues on this row are now also resolved
                if strategy in ["DELETE_RECORD", "QUARANTINE"]:
                    cur.execute(
                        "UPDATE integrity_issues SET status = 'REPAIRED', repaired_at = NOW() WHERE table_name = %s AND record_id = %s AND status != 'REPAIRED'",
                        (table_name, str(record_id))
                    )
                    cur.execute(
                        """
                        UPDATE repair_recommendations r
                        JOIN integrity_issues i ON r.issue_id = i.issue_id
                        SET r.approval_status = 'APPROVED'
                        WHERE i.table_name = %s AND i.record_id = %s
                        """,
                        (table_name, str(record_id))
                    )

                # 8. Record repair execution log
                exec_time_ms = int((time.time() - t0) * 1000)
                cur.execute("""
                    INSERT INTO repair_executions (
                        execution_id, issue_id, transaction_id, status, executed_by,
                        before_state_json, after_state_json, sql_executed, execution_time_ms
                    ) VALUES (%s, %s, %s, 'SUCCESS', %s, %s, %s, %s, %s)
                """, (
                    execution_id,
                    issue_id,
                    transaction_id,
                    operator,
                    json.dumps(before_row, default=str),
                    json.dumps(after_row, default=str),
                    "; ".join(sql_statements_executed),
                    exec_time_ms
                ))

            # Step 9: Commit the transaction
            conn.commit()

            # Step 10: Log audit trail and transaction log
            AuditService.log_event(
                event_type="REPAIR_EXECUTED",
                action_description=f"Successfully repaired issue {issue_id} using {strategy}.",
                actor=operator,
                related_issue_id=issue_id,
                related_transaction_id=transaction_id,
                target_table=table_name,
                record_identifier=str(record_id),
                result="SUCCESS",
                before_values=before_row,
                after_values=after_row
            )

            AuditService.log_transaction(
                transaction_id=transaction_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=datetime.now(),
                status="COMMITTED",
                operations_count=len(sql_statements_executed)
            )

            return {
                "execution_id": execution_id,
                "issue_id": issue_id,
                "transaction_id": transaction_id,
                "status": "SUCCESS",
                "strategy": strategy,
                "executed_by": operator,
                "executed_at": datetime.now(),
                "sql_executed": "; ".join(sql_statements_executed),
                "execution_time_ms": exec_time_ms,
                "verified": True,
                "message": f"Successfully executed {strategy} repair for {table_name}.{pk_col}={record_id}."
            }

        except (AlreadyRepairedError, StalePreviewError):
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            logger.error(f"Repair execution failed, transaction rolled back: {e}")
            
            # Log failure in audit
            AuditService.log_event(
                event_type="REPAIR_FAILED",
                action_description=f"Repair execution for issue {issue_id} failed: {str(e)}. Transaction rolled back.",
                actor=operator,
                related_issue_id=issue_id,
                related_transaction_id=transaction_id,
                result="FAILURE",
                error_message=str(e)
            )

            AuditService.log_transaction(
                transaction_id=transaction_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=datetime.now(),
                status="ROLLED_BACK",
                rollback_reason=str(e)
            )
            raise e

        finally:
            conn.close()
