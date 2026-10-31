import uuid
import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.database.connection import get_connection, validate_identifier
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

# Business and staging tables that are scanned by default
DEFAULT_SCAN_TABLES = [
    "departments", "instructors", "courses", "students", "enrollments", "staging_enrollments"
]

class IntegrityScanner:
    def __init__(self):
        pass

    def run_scan(
        self,
        scan_type: str = "FULL",
        target_tables: Optional[List[str]] = None,
        rule_codes: Optional[List[str]] = None,
        operator: str = "SYSTEM"
    ) -> Dict[str, Any]:
        """
        Executes a real integrity scan against the database.
        Queries INFORMATION_SCHEMA and executes safe inspection queries for active rules.
        """
        scan_id = f"SCAN-{uuid.uuid4().hex[:10].upper()}"
        start_time = datetime.now()

        # Determine target tables
        if not target_tables or len(target_tables) == 0:
            tables_to_scan = DEFAULT_SCAN_TABLES
        else:
            tables_to_scan = [validate_identifier(t) for t in target_tables]

        conn = get_connection()
        total_rows_inspected = 0
        detected_issues: List[Dict[str, Any]] = []

        try:
            # Step 1: Create scan_runs entry in RUNNING state
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO scan_runs (
                        scan_id, scan_type, target_tables, start_time, status
                    ) VALUES (%s, %s, %s, %s, 'RUNNING')
                    """,
                    (scan_id, scan_type, ",".join(tables_to_scan), start_time)
                )
            conn.commit()

            AuditService.log_event(
                event_type="SCAN_STARTED",
                action_description=f"Initiated {scan_type} integrity scan covering tables: {', '.join(tables_to_scan)}",
                actor=operator,
                related_scan_id=scan_id
            )

            # Step 2: Calculate total rows inspected across target tables
            with conn.cursor() as cur:
                for tbl in tables_to_scan:
                    cur.execute(f"SELECT COUNT(*) AS c FROM `{tbl}`")
                    res = cur.fetchone()
                    total_rows_inspected += res["c"] if res else 0

            # Step 3: Fetch active integrity rules for target tables
            active_rules = self._get_active_rules(conn, tables_to_scan, rule_codes)

            # Step 4: Execute each rule's detection algorithm
            for rule in active_rules:
                issues = self._execute_rule(conn, scan_id, rule)
                detected_issues.extend(issues)

            # Step 5: Also inspect declared Foreign Keys in INFORMATION_SCHEMA for unconstrained child tables
            fk_issues = self._scan_declared_foreign_keys(conn, scan_id, tables_to_scan)
            detected_issues.extend(fk_issues)

            # Step 6: Deduplicate issues by (table_name, record_id, rule_code)
            unique_issues_map = {}
            for issue in detected_issues:
                key = (issue["table_name"], str(issue["record_id"]), issue["rule_code"])
                if key not in unique_issues_map:
                    unique_issues_map[key] = issue
            final_issues = list(unique_issues_map.values())

            # Step 7: Persist detected issues and recommendations
            critical_count = sum(1 for i in final_issues if i["severity"] == "CRITICAL")
            high_count = sum(1 for i in final_issues if i["severity"] == "HIGH")
            medium_count = sum(1 for i in final_issues if i["severity"] == "MEDIUM")
            low_count = sum(1 for i in final_issues if i["severity"] == "LOW")

            with conn.cursor() as cur:
                for issue in final_issues:
                    t_name = issue["table_name"]
                    r_id = str(issue["record_id"])
                    r_code = issue["rule_code"]

                    # Check for an existing open/active issue for this exact record and rule
                    cur.execute(
                        """
                        SELECT issue_id, status FROM integrity_issues
                        WHERE table_name = %s AND record_id = %s AND rule_code = %s
                        ORDER BY detected_at DESC
                        LIMIT 1
                        """,
                        (t_name, r_id, r_code)
                    )
                    existing_issue = cur.fetchone()

                    if existing_issue and existing_issue["status"] in ("OPEN", "REVIEWED", "APPROVED"):
                        # Reuse existing issue_id to prevent duplicate issue creation across scans
                        issue["issue_id"] = existing_issue["issue_id"]
                        cur.execute(
                            """
                            UPDATE integrity_issues SET
                                scan_id = %s,
                                invalid_value = %s,
                                description = %s,
                                detected_at = NOW()
                            WHERE issue_id = %s
                            """,
                            (
                                issue["scan_id"],
                                str(issue.get("invalid_value")),
                                issue["description"],
                                issue["issue_id"]
                            )
                        )
                        # Ensure repair recommendation exists without inserting duplicates
                        cur.execute(
                            "SELECT recommendation_id FROM repair_recommendations WHERE issue_id = %s",
                            (issue["issue_id"],)
                        )
                        if not cur.fetchone():
                            rec = self._generate_recommendation(issue)
                            cur.execute(
                                """
                                INSERT INTO repair_recommendations (
                                    issue_id, strategy, problem_description, proposed_action,
                                    reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
                                """,
                                (
                                    rec["issue_id"],
                                    rec["strategy"],
                                    rec["problem_description"],
                                    rec["proposed_action"],
                                    rec["reason"],
                                    rec["expected_impact"],
                                    rec["risk_level"],
                                    rec["is_reversible"],
                                    rec["requires_approval"]
                                )
                            )
                    else:
                        # Insert new issue
                        cur.execute(
                            """
                            INSERT INTO integrity_issues (
                                issue_id, scan_id, rule_id, rule_code, category, severity,
                                table_name, record_id, column_name, invalid_value, description, status
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN')
                            """,
                            (
                                issue["issue_id"],
                                issue["scan_id"],
                                issue.get("rule_id"),
                                issue["rule_code"],
                                issue["category"],
                                issue["severity"],
                                issue["table_name"],
                                str(issue["record_id"]),
                                issue.get("column_name"),
                                str(issue.get("invalid_value")),
                                issue["description"]
                            )
                        )

                        # Generate repair recommendation
                        rec = self._generate_recommendation(issue)
                        cur.execute(
                            """
                            INSERT INTO repair_recommendations (
                                issue_id, strategy, problem_description, proposed_action,
                                reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
                            """,
                            (
                                rec["issue_id"],
                                rec["strategy"],
                                rec["problem_description"],
                                rec["proposed_action"],
                                rec["reason"],
                                rec["expected_impact"],
                                rec["risk_level"],
                                rec["is_reversible"],
                                rec["requires_approval"]
                            )
                        )

                # Auto-resolve open issues for records that no longer exist in the scanned tables (e.g. quarantined or deleted)
                for tbl in tables_to_scan:
                    pk_col = self._get_primary_key(conn, tbl)
                    cur.execute(f"SELECT `{pk_col}` FROM `{tbl}`")
                    existing_pks = {str(r[pk_col]) for r in cur.fetchall()}

                    cur.execute(
                        "SELECT issue_id, record_id FROM integrity_issues WHERE table_name = %s AND status IN ('OPEN', 'REVIEWED', 'APPROVED')",
                        (tbl,)
                    )
                    open_issues = cur.fetchall()
                    for oi in open_issues:
                        if str(oi["record_id"]) not in existing_pks:
                            cur.execute(
                                "UPDATE integrity_issues SET status = 'REPAIRED', repaired_at = NOW() WHERE issue_id = %s",
                                (oi["issue_id"],)
                            )
                            cur.execute(
                                "UPDATE repair_recommendations SET approval_status = 'APPROVED' WHERE issue_id = %s",
                                (oi["issue_id"],)
                            )

            conn.commit()

            # Step 8: Update scan_runs to COMPLETED
            end_time = datetime.now()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE scan_runs SET 
                        end_time = %s,
                        status = 'COMPLETED',
                        total_rows_inspected = %s,
                        issues_found = %s,
                        critical_count = %s,
                        high_count = %s,
                        medium_count = %s,
                        low_count = %s
                    WHERE scan_id = %s
                    """,
                    (
                        end_time,
                        total_rows_inspected,
                        len(final_issues),
                        critical_count,
                        high_count,
                        medium_count,
                        low_count,
                        scan_id
                    )
                )
            conn.commit()

            AuditService.log_event(
                event_type="SCAN_COMPLETED",
                action_description=f"Integrity scan completed. Inspected {total_rows_inspected} rows across {len(tables_to_scan)} tables. Detected {len(final_issues)} integrity issues.",
                actor=operator,
                related_scan_id=scan_id,
                result="SUCCESS"
            )

            duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)
            return {
                "scan_id": scan_id,
                "scan_type": scan_type,
                "target_tables": tables_to_scan,
                "start_time": start_time,
                "end_time": end_time,
                "status": "COMPLETED",
                "total_rows_inspected": total_rows_inspected,
                "issues_found": len(final_issues),
                "critical_count": critical_count,
                "high_count": high_count,
                "medium_count": medium_count,
                "low_count": low_count,
                "duration_ms": duration_ms,
                "issues": final_issues
            }

        except Exception as e:
            logger.error(f"Integrity scan failed: {e}", exc_info=True)
            conn.rollback()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE scan_runs SET status = 'FAILED', error_message = %s, end_time = NOW() WHERE scan_id = %s",
                        (str(e), scan_id)
                    )
                conn.commit()
            except Exception:
                pass

            AuditService.log_event(
                event_type="SCAN_FAILED",
                action_description=f"Integrity scan {scan_id} failed: {str(e)}",
                actor=operator,
                related_scan_id=scan_id,
                result="FAILURE",
                error_message=str(e)
            )
            raise e
        finally:
            conn.close()

    def _get_active_rules(self, conn, tables: List[str], rule_codes: Optional[List[str]]) -> List[Dict[str, Any]]:
        with conn.cursor() as cur:
            format_strings = ','.join(['%s'] * len(tables))
            sql = f"SELECT * FROM integrity_rules WHERE is_enabled = TRUE AND target_table IN ({format_strings})"
            params = list(tables)
            if rule_codes and len(rule_codes) > 0:
                rc_placeholders = ','.join(['%s'] * len(rule_codes))
                sql += f" AND rule_code IN ({rc_placeholders})"
                params.extend(rule_codes)
            cur.execute(sql, tuple(params))
            rules = cur.fetchall()
            for r in rules:
                if r.get("parameters_json") and isinstance(r["parameters_json"], str):
                    try:
                        r["parameters_json"] = json.loads(r["parameters_json"])
                    except Exception:
                        r["parameters_json"] = {}
            return rules

    def _get_primary_key(self, conn, table_name: str) -> str:
        """Finds primary key column name for a given table."""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s
                  AND CONSTRAINT_NAME = 'PRIMARY'
                LIMIT 1
            """, (table_name,))
            res = cur.fetchone()
            if res:
                return res["COLUMN_NAME"]
            # Fallback heuristics
            return f"{table_name.rstrip('s')}_id"

    def _execute_rule(self, conn, scan_id: str, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        rule_type = rule["rule_type"]
        target_table = validate_identifier(rule["target_table"])
        pk_col = self._get_primary_key(conn, target_table)
        params = rule.get("parameters_json") or {}

        with conn.cursor() as cur:
            # 1. ORPHAN CHECK
            if rule_type == "ORPHAN":
                target_col = validate_identifier(rule["target_column"])
                parent_table = validate_identifier(rule["parent_table"])
                parent_col = validate_identifier(rule["parent_column"])
                allow_null = params.get("allow_null", False)

                null_filter = f"AND t.`{target_col}` IS NOT NULL" if not allow_null else f"AND t.`{target_col}` IS NOT NULL"
                query = f"""
                    SELECT t.`{pk_col}` AS pk_val, t.`{target_col}` AS fk_val
                    FROM `{target_table}` t
                    LEFT JOIN `{parent_table}` p ON t.`{target_col}` = p.`{parent_col}`
                    WHERE p.`{parent_col}` IS NULL {null_filter}
                """
                cur.execute(query)
                rows = cur.fetchall()
                for r in rows:
                    issue_id = f"ISSUE-ORPH-{uuid.uuid4().hex[:8].upper()}"
                    issues.append({
                        "issue_id": issue_id,
                        "scan_id": scan_id,
                        "rule_id": rule["rule_id"],
                        "rule_code": rule["rule_code"],
                        "category": "ORPHAN",
                        "severity": rule["severity"],
                        "table_name": target_table,
                        "record_id": str(r["pk_val"]),
                        "column_name": target_col,
                        "invalid_value": str(r["fk_val"]),
                        "description": f"Record in '{target_table}' ({pk_col}={r['pk_val']}) references missing parent in '{parent_table}' ({parent_col}={r['fk_val']}).",
                        "parent_table": parent_table,
                        "parent_column": parent_col
                    })

            # 2. DUPLICATE CHECK
            elif rule_type == "DUPLICATE":
                cols = [validate_identifier(c.strip()) for c in rule["target_column"].split(",")]
                cols_sql = ", ".join([f"`{c}`" for c in cols])
                
                query = f"""
                    SELECT {cols_sql}, COUNT(*) as dup_count, GROUP_CONCAT(`{pk_col}`) as conflicting_pks
                    FROM `{target_table}`
                    GROUP BY {cols_sql}
                    HAVING COUNT(*) > 1
                """
                cur.execute(query)
                rows = cur.fetchall()
                for r in rows:
                    conflicting_ids = str(r["conflicting_pks"]).split(",")
                    # Flag the later occurrences as duplicate issues
                    for dup_pk in conflicting_ids[1:]:
                        issue_id = f"ISSUE-DUP-{uuid.uuid4().hex[:8].upper()}"
                        val_repr = ", ".join([f"{c}={r[c]}" for c in cols])
                        issues.append({
                            "issue_id": issue_id,
                            "scan_id": scan_id,
                            "rule_id": rule["rule_id"],
                            "rule_code": rule["rule_code"],
                            "category": "DUPLICATE",
                            "severity": rule["severity"],
                            "table_name": target_table,
                            "record_id": dup_pk,
                            "column_name": rule["target_column"],
                            "invalid_value": val_repr,
                            "description": f"Duplicate record in '{target_table}' on ({val_repr}) colliding with canonical record ID {conflicting_ids[0]}."
                        })

            # 3. NULL / REQUIRED CHECK
            elif rule_type == "NULL_CHECK":
                target_col = validate_identifier(rule["target_column"])
                disallow_empty = params.get("disallow_empty_string", True)
                
                empty_cond = f"OR TRIM(`{target_col}`) = ''" if disallow_empty else ""
                query = f"""
                    SELECT `{pk_col}` AS pk_val, `{target_col}` AS col_val
                    FROM `{target_table}`
                    WHERE `{target_col}` IS NULL {empty_cond}
                """
                cur.execute(query)
                rows = cur.fetchall()
                for r in rows:
                    issue_id = f"ISSUE-NULL-{uuid.uuid4().hex[:8].upper()}"
                    issues.append({
                        "issue_id": issue_id,
                        "scan_id": scan_id,
                        "rule_id": rule["rule_id"],
                        "rule_code": rule["rule_code"],
                        "category": "NULL_VIOLATION",
                        "severity": rule["severity"],
                        "table_name": target_table,
                        "record_id": str(r["pk_val"]),
                        "column_name": target_col,
                        "invalid_value": "NULL" if r["col_val"] is None else "EMPTY_STRING",
                        "description": f"Mandatory column '{target_col}' in '{target_table}' ({pk_col}={r['pk_val']}) is empty or NULL."
                    })

            # 4. DOMAIN CHECK
            elif rule_type == "DOMAIN_CHECK":
                target_col = validate_identifier(rule["target_column"])
                min_val = params.get("min_value")
                max_val = params.get("max_value")
                allowed_values = params.get("allowed_values")
                regex_pattern = params.get("regex_pattern")

                # Range check
                if min_val is not None or max_val is not None:
                    conditions = []
                    if min_val is not None:
                        conditions.append(f"`{target_col}` < {min_val}")
                    if max_val is not None:
                        conditions.append(f"`{target_col}` > {max_val}")
                    cond_sql = " OR ".join(conditions)
                    query = f"SELECT `{pk_col}` AS pk_val, `{target_col}` AS col_val FROM `{target_table}` WHERE `{target_col}` IS NOT NULL AND ({cond_sql})"
                    cur.execute(query)
                    for r in cur.fetchall():
                        issue_id = f"ISSUE-DOM-{uuid.uuid4().hex[:8].upper()}"
                        issues.append({
                            "issue_id": issue_id,
                            "scan_id": scan_id,
                            "rule_id": rule["rule_id"],
                            "rule_code": rule["rule_code"],
                            "category": "DOMAIN_VIOLATION",
                            "severity": rule["severity"],
                            "table_name": target_table,
                            "record_id": str(r["pk_val"]),
                            "column_name": target_col,
                            "invalid_value": str(r["col_val"]),
                            "description": f"Domain constraint violation: Column '{target_col}' value {r['col_val']} is outside permissible range [{min_val}, {max_val}]."
                        })

                # Allowed values check
                elif allowed_values and isinstance(allowed_values, list):
                    vals_quoted = ", ".join([f"'{v}'" for v in allowed_values])
                    query = f"SELECT `{pk_col}` AS pk_val, `{target_col}` AS col_val FROM `{target_table}` WHERE `{target_col}` IS NOT NULL AND `{target_col}` NOT IN ({vals_quoted})"
                    cur.execute(query)
                    for r in cur.fetchall():
                        issue_id = f"ISSUE-DOM-{uuid.uuid4().hex[:8].upper()}"
                        issues.append({
                            "issue_id": issue_id,
                            "scan_id": scan_id,
                            "rule_id": rule["rule_id"],
                            "rule_code": rule["rule_code"],
                            "category": "DOMAIN_VIOLATION",
                            "severity": rule["severity"],
                            "table_name": target_table,
                            "record_id": str(r["pk_val"]),
                            "column_name": target_col,
                            "invalid_value": str(r["col_val"]),
                            "description": f"Invalid enumeration: Column '{target_col}' has value '{r['col_val']}' which is not in allowed set ({', '.join(allowed_values)})."
                        })

                # Regex pattern check
                elif regex_pattern:
                    query = f"SELECT `{pk_col}` AS pk_val, `{target_col}` AS col_val FROM `{target_table}` WHERE `{target_col}` IS NOT NULL"
                    cur.execute(query)
                    compiled_re = re.compile(regex_pattern)
                    for r in cur.fetchall():
                        val_str = str(r["col_val"])
                        if not compiled_re.match(val_str):
                            issue_id = f"ISSUE-DOM-{uuid.uuid4().hex[:8].upper()}"
                            issues.append({
                                "issue_id": issue_id,
                                "scan_id": scan_id,
                                "rule_id": rule["rule_id"],
                                "rule_code": rule["rule_code"],
                                "category": "DOMAIN_VIOLATION",
                                "severity": rule["severity"],
                                "table_name": target_table,
                                "record_id": str(r["pk_val"]),
                                "column_name": target_col,
                                "invalid_value": val_str,
                                "description": f"Syntax format violation: Column '{target_col}' value '{val_str}' failed format validation."
                            })

        return issues

    def _scan_declared_foreign_keys(self, conn, scan_id: str, tables: List[str]) -> List[Dict[str, Any]]:
        """Scans declared foreign keys in INFORMATION_SCHEMA for orphan child records."""
        issues = []
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME, CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            fk_list = cur.fetchall()

            for fk in fk_list:
                child_tbl = fk["TABLE_NAME"]
                child_col = fk["COLUMN_NAME"]
                parent_tbl = fk["REFERENCED_TABLE_NAME"]
                parent_col = fk["REFERENCED_COLUMN_NAME"]

                if child_tbl not in tables:
                    continue

                pk_col = self._get_primary_key(conn, child_tbl)
                query = f"""
                    SELECT c.`{pk_col}` AS pk_val, c.`{child_col}` AS fk_val
                    FROM `{child_tbl}` c
                    LEFT JOIN `{parent_tbl}` p ON c.`{child_col}` = p.`{parent_col}`
                    WHERE c.`{child_col}` IS NOT NULL AND p.`{parent_col}` IS NULL
                """
                cur.execute(query)
                for r in cur.fetchall():
                    issue_id = f"ISSUE-FK-{uuid.uuid4().hex[:8].upper()}"
                    issues.append({
                        "issue_id": issue_id,
                        "scan_id": scan_id,
                        "rule_id": None,
                        "rule_code": f"FK_{fk['CONSTRAINT_NAME']}",
                        "category": "ORPHAN",
                        "severity": "CRITICAL",
                        "table_name": child_tbl,
                        "record_id": str(r["pk_val"]),
                        "column_name": child_col,
                        "invalid_value": str(r["fk_val"]),
                        "description": f"Referential integrity failure: Child record in '{child_tbl}' ({pk_col}={r['pk_val']}) references missing parent in '{parent_tbl}' ({parent_col}={r['fk_val']})."
                    })
        return issues

    def _generate_recommendation(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a safe self-healing recommendation based on issue category and risk profile."""
        cat = issue["category"]
        table = issue["table_name"]
        pk = issue["record_id"]
        col = issue.get("column_name", "")
        val = issue.get("invalid_value", "")

        if cat == "ORPHAN":
            if table.startswith("staging_") or table.startswith("legacy_"):
                strategy = "QUARANTINE"
                action = f"Move orphan staging record ({table}.id={pk}) into quarantine_records table with audit snapshot."
                reason = "Staging records with missing foreign keys cannot be migrated to production without data loss or corruption."
                impact = f"Removes 1 invalid row from {table}; archives full row state into quarantine."
                risk = "LOW"
                reversible = True
            else:
                strategy = "MAP_PARENT"
                action = f"Prompt administrator to map record {table} (ID={pk}) to a valid parent, or quarantine for manual resolution."
                reason = "Never fabricate missing parent records with arbitrary dummy keys; require verified mapping."
                impact = f"Updates foreign key reference in {table}."
                risk = "MEDIUM"
                reversible = True

        elif cat == "DUPLICATE":
            strategy = "DELETE_RECORD"
            action = f"Remove redundant duplicate record {table} (ID={pk}) while retaining canonical record."
            reason = "Redundant duplicate records violate relational uniqueness rules and skew aggregations."
            impact = f"Deletes duplicate row {pk} from {table} after validating no child dependencies exist."
            risk = "MEDIUM"
            reversible = True

        elif cat == "NULL_VIOLATION":
            strategy = "SET_DEFAULT"
            action = f"Apply default sanitized value or prompt administrator for verified input for {table}.{col} (ID={pk})."
            reason = "Column is marked as mandatory; NULL violates domain requirements."
            impact = f"Updates column {col} in {table} row {pk} with valid data."
            risk = "LOW"
            reversible = True

        elif cat == "DOMAIN_VIOLATION":
            if "marks" in col.lower() or "grade" in col.lower():
                strategy = "SET_DEFAULT"
                action = f"Clamp score to standard range or flag for instructor verification (current value: {val})."
                reason = "Grade score falls outside valid 0.00-100.00 scale."
                impact = f"Corrects score in {table} row {pk}."
                risk = "MEDIUM"
                reversible = True
            else:
                strategy = "MANUAL_INTERVENTION"
                action = f"Mark for manual administrator review with recorded reason."
                reason = "Domain violation cannot be safely repaired automatically without business context."
                impact = f"Logs warning and leaves data unchanged until explicit human review."
                risk = "LOW"
                reversible = False
        else:
            strategy = "MANUAL_INTERVENTION"
            action = "Request database administrator review."
            reason = "Unclassified relational discrepancy."
            impact = "No database modification performed."
            risk = "LOW"
            reversible = False

        return {
            "issue_id": issue["issue_id"],
            "strategy": strategy,
            "problem_description": issue["description"],
            "proposed_action": action,
            "reason": reason,
            "expected_impact": impact,
            "risk_level": issue.get("severity", "MEDIUM"),
            "is_reversible": reversible,
            "requires_approval": True
        }
