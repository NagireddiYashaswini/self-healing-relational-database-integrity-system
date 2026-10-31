from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.app.database.connection import get_connection, validate_identifier
from backend.app.models.schemas import ApiResponse, IssueStatusUpdateRequest
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/issues", tags=["Integrity Issues Management"])

@router.get("", response_model=ApiResponse[Dict[str, Any]])
def list_issues(
    status: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    table_name: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Retrieves paginated integrity issues with comprehensive filtering."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            where_clauses = ["1=1"]
            params = []

            if status:
                where_clauses.append("i.status = %s")
                params.append(status)
            if category:
                where_clauses.append("i.category = %s")
                params.append(category)
            if severity:
                where_clauses.append("i.severity = %s")
                params.append(severity)
            if table_name:
                where_clauses.append("i.table_name = %s")
                params.append(table_name)
            if search:
                where_clauses.append("(i.description LIKE %s OR i.table_name LIKE %s OR i.record_id LIKE %s OR i.rule_code LIKE %s)")
                term = f"%{search}%"
                params.extend([term, term, term, term])

            where_sql = " AND ".join(where_clauses)

            # Count total matching
            cur.execute(f"SELECT COUNT(*) as total FROM integrity_issues i WHERE {where_sql}", tuple(params))
            total = cur.fetchone()["total"]

            # Query items with joined recommendation info
            query = f"""
                SELECT 
                    i.*,
                    r.recommendation_id,
                    r.strategy,
                    r.proposed_action,
                    r.risk_level,
                    r.approval_status
                FROM integrity_issues i
                LEFT JOIN repair_recommendations r ON i.issue_id = r.issue_id
                WHERE {where_sql}
                ORDER BY 
                    CASE i.severity 
                        WHEN 'CRITICAL' THEN 1 
                        WHEN 'HIGH' THEN 2 
                        WHEN 'MEDIUM' THEN 3 
                        WHEN 'LOW' THEN 4 
                    END,
                    i.detected_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cur.execute(query, tuple(params))
            items = cur.fetchall()

            return ApiResponse(
                success=True,
                message=f"Found {total} integrity issues.",
                data={
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "items": items
                }
            )
    finally:
        conn.close()

@router.get("/{issue_id}", response_model=ApiResponse[Dict[str, Any]])
def get_issue(issue_id: str):
    """Retrieves full details of a single integrity issue including raw row data."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM integrity_issues WHERE issue_id = %s", (issue_id,))
            issue = cur.fetchone()
            if not issue:
                raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found.")

            # Recommendation
            cur.execute("SELECT * FROM repair_recommendations WHERE issue_id = %s", (issue_id,))
            rec = cur.fetchone()

            # Executions
            cur.execute("SELECT * FROM repair_executions WHERE issue_id = %s ORDER BY executed_at DESC", (issue_id,))
            executions = cur.fetchall()

            # Try to fetch current live row data
            table_name = validate_identifier(issue["table_name"])
            cur.execute("""
                SELECT COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND CONSTRAINT_NAME = 'PRIMARY'
                LIMIT 1
            """, (table_name,))
            pk_res = cur.fetchone()
            pk_col = pk_res["COLUMN_NAME"] if pk_res else "id"

            cur.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s", (issue["record_id"],))
            live_row = cur.fetchone()

            return ApiResponse(
                success=True,
                message=f"Retrieved issue {issue_id}.",
                data={
                    "issue": issue,
                    "recommendation": rec,
                    "executions": executions,
                    "live_record_data": live_row,
                    "primary_key_column": pk_col
                }
            )
    finally:
        conn.close()

@router.patch("/{issue_id}/status", response_model=ApiResponse[Dict[str, Any]])
def update_issue_status(issue_id: str, payload: IssueStatusUpdateRequest):
    """
    Updates status of an integrity issue (e.g. REVIEWED, IGNORED).
    Enforces validation rule: REPAIRED can ONLY be set via verified repair execution.
    """
    if payload.status == "REPAIRED":
        raise HTTPException(
            status_code=400,
            detail="Cannot manually mark issue as REPAIRED. Issues are marked REPAIRED only after a successful verified repair execution."
        )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM integrity_issues WHERE issue_id = %s", (issue_id,))
            issue = cur.fetchone()
            if not issue:
                raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found.")

            cur.execute(
                "UPDATE integrity_issues SET status = %s, ignored_reason = %s WHERE issue_id = %s",
                (payload.status.value, payload.reason, issue_id)
            )
        conn.commit()

        AuditService.log_event(
            event_type="ISSUE_STATUS_UPDATED",
            action_description=f"Issue {issue_id} status changed from {issue['status']} to {payload.status.value}. Reason: {payload.reason or 'None provided'}",
            actor="ADMIN_USER",
            related_issue_id=issue_id,
            target_table=issue["table_name"],
            record_identifier=issue["record_id"],
            result="SUCCESS"
        )

        return ApiResponse(
            success=True,
            message=f"Issue status updated to {payload.status.value}.",
            data={"issue_id": issue_id, "new_status": payload.status.value}
        )
    finally:
        conn.close()
