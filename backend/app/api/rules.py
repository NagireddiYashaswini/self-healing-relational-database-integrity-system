from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import json
from backend.app.database.connection import get_connection, validate_identifier
from backend.app.models.schemas import ApiResponse, RuleModel, RuleCreate, RuleUpdate
from backend.app.services.integrity_scanner import IntegrityScanner
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/rules", tags=["Integrity Rules Configuration"])

@router.get("", response_model=ApiResponse[List[Dict[str, Any]]])
def list_rules(target_table: Optional[str] = None, rule_type: Optional[str] = None):
    """Retrieves all defined integrity rules."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM integrity_rules WHERE 1=1"
            params = []
            if target_table:
                sql += " AND target_table = %s"
                params.append(target_table)
            if rule_type:
                sql += " AND rule_type = %s"
                params.append(rule_type)
            sql += " ORDER BY rule_id ASC"

            cur.execute(sql, tuple(params))
            rules = cur.fetchall()

            for r in rules:
                if r.get("parameters_json") and isinstance(r["parameters_json"], str):
                    try:
                        r["parameters_json"] = json.loads(r["parameters_json"])
                    except Exception:
                        pass
                r["is_enabled"] = bool(r["is_enabled"])

            return ApiResponse(
                success=True,
                message=f"Retrieved {len(rules)} integrity rules.",
                data=rules
            )
    finally:
        conn.close()

@router.post("", response_model=ApiResponse[Dict[str, Any]])
def create_rule(payload: RuleCreate):
    """Creates a new integrity rule after validating table and column identifiers."""
    # Identifier validations
    validate_identifier(payload.target_table)
    validate_identifier(payload.rule_code)
    for col in payload.target_column.split(","):
        validate_identifier(col.strip())
    if payload.parent_table:
        validate_identifier(payload.parent_table)
    if payload.parent_column:
        validate_identifier(payload.parent_column)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check unique rule_code
            cur.execute("SELECT COUNT(*) AS c FROM integrity_rules WHERE rule_code = %s", (payload.rule_code,))
            if cur.fetchone()["c"] > 0:
                raise HTTPException(status_code=400, detail=f"Rule code '{payload.rule_code}' already exists.")

            params_str = json.dumps(payload.parameters_json) if payload.parameters_json else None
            sql = """
                INSERT INTO integrity_rules (
                    rule_code, name, description, rule_type, target_table,
                    target_column, parent_table, parent_column, parameters_json,
                    severity, is_enabled
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                payload.rule_code,
                payload.name,
                payload.description,
                payload.rule_type.value,
                payload.target_table,
                payload.target_column,
                payload.parent_table,
                payload.parent_column,
                params_str,
                payload.severity.value,
                payload.is_enabled
            ))
            rule_id = cur.lastrowid
        conn.commit()

        AuditService.log_event(
            event_type="RULE_CREATED",
            action_description=f"Created new integrity rule {payload.rule_code} ({payload.name}) for table {payload.target_table}.",
            actor="ADMIN_USER",
            target_table=payload.target_table,
            result="SUCCESS"
        )

        return ApiResponse(
            success=True,
            message=f"Rule '{payload.rule_code}' successfully created.",
            data={"rule_id": rule_id, "rule_code": payload.rule_code}
        )
    finally:
        conn.close()

@router.patch("/{rule_id}", response_model=ApiResponse[Dict[str, Any]])
def update_rule(rule_id: int, payload: RuleUpdate):
    """Updates an existing integrity rule (toggle enabled, change severity, parameters)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM integrity_rules WHERE rule_id = %s", (rule_id,))
            rule = cur.fetchone()
            if not rule:
                raise HTTPException(status_code=404, detail="Rule not found.")

            updates = []
            params = []
            if payload.name is not None:
                updates.append("name = %s")
                params.append(payload.name)
            if payload.description is not None:
                updates.append("description = %s")
                params.append(payload.description)
            if payload.severity is not None:
                updates.append("severity = %s")
                params.append(payload.severity.value)
            if payload.is_enabled is not None:
                updates.append("is_enabled = %s")
                params.append(payload.is_enabled)
            if payload.parameters_json is not None:
                updates.append("parameters_json = %s")
                params.append(json.dumps(payload.parameters_json))

            if updates:
                sql = f"UPDATE integrity_rules SET {', '.join(updates)} WHERE rule_id = %s"
                params.append(rule_id)
                cur.execute(sql, tuple(params))
                conn.commit()

        AuditService.log_event(
            event_type="RULE_UPDATED",
            action_description=f"Updated integrity rule #{rule_id} ({rule['rule_code']}).",
            actor="ADMIN_USER",
            result="SUCCESS"
        )

        return ApiResponse(
            success=True,
            message=f"Rule #{rule_id} updated successfully.",
            data={"rule_id": rule_id}
        )
    finally:
        conn.close()

@router.post("/{rule_id}/test", response_model=ApiResponse[Dict[str, Any]])
def test_rule(rule_id: int):
    """Tests a single rule against active database records without persisting a scan."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM integrity_rules WHERE rule_id = %s", (rule_id,))
            rule = cur.fetchone()
            if not rule:
                raise HTTPException(status_code=404, detail="Rule not found.")

            if rule.get("parameters_json") and isinstance(rule["parameters_json"], str):
                try:
                    rule["parameters_json"] = json.loads(rule["parameters_json"])
                except Exception:
                    rule["parameters_json"] = {}

            scanner = IntegrityScanner()
            test_scan_id = "TEST-DRY-RUN"
            issues = scanner._execute_rule(conn, test_scan_id, rule)

            return ApiResponse(
                success=True,
                message=f"Test executed for rule '{rule['rule_code']}'. Found {len(issues)} matching violation(s).",
                data={
                    "rule_id": rule_id,
                    "rule_code": rule["rule_code"],
                    "violations_detected_count": len(issues),
                    "violations": issues
                }
            )
    finally:
        conn.close()

@router.delete("/{rule_id}", response_model=ApiResponse[Dict[str, Any]])
def delete_rule(rule_id: int):
    """Deletes an integrity rule."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM integrity_rules WHERE rule_id = %s", (rule_id,))
            rule = cur.fetchone()
            if not rule:
                raise HTTPException(status_code=404, detail="Rule not found.")

            cur.execute("DELETE FROM integrity_rules WHERE rule_id = %s", (rule_id,))
            conn.commit()

        AuditService.log_event(
            event_type="RULE_DELETED",
            action_description=f"Deleted integrity rule #{rule_id} ({rule['rule_code']}).",
            actor="ADMIN_USER",
            result="SUCCESS"
        )

        return ApiResponse(
            success=True,
            message=f"Rule #{rule_id} deleted successfully.",
            data={"rule_id": rule_id}
        )
    finally:
        conn.close()
