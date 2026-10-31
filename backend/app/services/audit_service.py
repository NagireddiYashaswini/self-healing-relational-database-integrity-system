import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.app.database.connection import get_connection

logger = logging.getLogger(__name__)

# Sensitive field names that must be redacted in audit payloads
SENSITIVE_KEYS = {"password", "secret", "token", "pwd", "hash", "credit_card"}

def sanitize_json(data: Optional[Dict[str, Any]]) -> Optional[str]:
    """Sanitizes and serializes dictionary data, redacting sensitive keys."""
    if data is None:
        return None
    if isinstance(data, str):
        return data
    
    sanitized = {}
    for k, v in data.items():
        if any(sens in k.lower() for sens in SENSITIVE_KEYS):
            sanitized[k] = "[REDACTED]"
        else:
            sanitized[k] = v
    try:
        return json.dumps(sanitized, default=str)
    except Exception:
        return str(sanitized)

class AuditService:
    @staticmethod
    def log_event(
        event_type: str,
        action_description: str,
        actor: str = "SYSTEM",
        related_scan_id: Optional[str] = None,
        related_issue_id: Optional[str] = None,
        related_transaction_id: Optional[str] = None,
        target_table: Optional[str] = None,
        record_identifier: Optional[str] = None,
        result: str = "SUCCESS",
        before_values: Optional[Dict[str, Any]] = None,
        after_values: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> int:
        """
        Persists an event to the audit_logs table. Never throws to avoid interrupting calling logic.
        """
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                sql = """
                    INSERT INTO audit_logs (
                        event_type, actor, related_scan_id, related_issue_id, 
                        related_transaction_id, action_description, target_table, 
                        record_identifier, result, before_values_json, after_values_json, 
                        error_message
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql, (
                    event_type,
                    actor,
                    related_scan_id,
                    related_issue_id,
                    related_transaction_id,
                    action_description,
                    target_table,
                    record_identifier,
                    result,
                    sanitize_json(before_values),
                    sanitize_json(after_values),
                    error_message
                ))
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return -1
        finally:
            if conn:
                conn.close()

    @staticmethod
    def log_transaction(
        transaction_id: str,
        execution_id: Optional[str],
        start_time: datetime,
        end_time: datetime,
        status: str,
        operations_count: int = 1,
        savepoints_used: int = 0,
        rollback_reason: Optional[str] = None
    ):
        """Records an entry in the transaction_logs table."""
        conn = None
        try:
            conn = get_connection()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            with conn.cursor() as cur:
                sql = """
                    INSERT INTO transaction_logs (
                        transaction_id, execution_id, start_time, end_time, 
                        status, operations_count, savepoints_used, rollback_reason, duration_ms
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql, (
                    transaction_id,
                    execution_id,
                    start_time,
                    end_time,
                    status,
                    operations_count,
                    savepoints_used,
                    rollback_reason,
                    duration_ms
                ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to record transaction log: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_logs(
        event_type: Optional[str] = None,
        target_table: Optional[str] = None,
        result: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieves paginated audit logs matching search filters."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = ["1=1"]
                params = []

                if event_type:
                    where_clauses.append("event_type = %s")
                    params.append(event_type)
                if target_table:
                    where_clauses.append("target_table = %s")
                    params.append(target_table)
                if result:
                    where_clauses.append("result = %s")
                    params.append(result)
                if search:
                    where_clauses.append("(action_description LIKE %s OR record_identifier LIKE %s OR actor LIKE %s)")
                    term = f"%{search}%"
                    params.extend([term, term, term])

                where_sql = " AND ".join(where_clauses)

                # Total count
                cur.execute(f"SELECT COUNT(*) AS total FROM audit_logs WHERE {where_sql}", tuple(params))
                total = cur.fetchone()["total"]

                # Paginated items
                params.extend([limit, offset])
                cur.execute(
                    f"SELECT * FROM audit_logs WHERE {where_sql} ORDER BY event_id DESC LIMIT %s OFFSET %s",
                    tuple(params)
                )
                items = cur.fetchall()

                return {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "items": items
                }
        finally:
            conn.close()
