import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.app.database.connection import get_connection, validate_identifier
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class RecoveryManager:
    @staticmethod
    def create_checkpoint(
        target_table: str,
        checkpoint_name: str,
        checkpoint_type: str = "PRE_REPAIR",
        row_id_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates an application-level recovery checkpoint by snapshotting metadata and row data.
        Does not replace native physical MySQL binary logs/mysqldump, but provides atomic table recovery.
        """
        table_name = validate_identifier(target_table)
        checkpoint_id = f"CKPT-{uuid.uuid4().hex[:10].upper()}"
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                # Capture table structure
                cur.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_table_row = cur.fetchone()
                schema_ddl = list(create_table_row.values())[1]

                # Capture rows
                if row_id_filter:
                    # Find primary key
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
                    cur.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s", (row_id_filter,))
                else:
                    cur.execute(f"SELECT * FROM `{table_name}` LIMIT 500")

                rows = cur.fetchall()

                snapshot_metadata = {
                    "table_name": table_name,
                    "row_count": len(rows),
                    "created_at": datetime.now().isoformat(),
                    "ddl": schema_ddl
                }

                cur.execute("""
                    INSERT INTO recovery_checkpoints (
                        checkpoint_id, checkpoint_name, checkpoint_type, target_table,
                        snapshot_metadata_json, snapshot_rows_json, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
                """, (
                    checkpoint_id,
                    checkpoint_name,
                    checkpoint_type,
                    table_name,
                    json.dumps(snapshot_metadata, default=str),
                    json.dumps(rows, default=str)
                ))

            conn.commit()

            AuditService.log_event(
                event_type="CHECKPOINT_CREATED",
                action_description=f"Created recovery checkpoint '{checkpoint_name}' for table '{table_name}' ({len(rows)} rows captured).",
                target_table=table_name,
                result="SUCCESS"
            )

            return {
                "checkpoint_id": checkpoint_id,
                "checkpoint_name": checkpoint_name,
                "target_table": table_name,
                "rows_captured": len(rows),
                "status": "ACTIVE",
                "created_at": datetime.now()
            }

        except Exception as e:
            logger.error(f"Failed to create recovery checkpoint: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def list_checkpoints(limit: int = 50) -> List[Dict[str, Any]]:
        """Lists active and historical checkpoints."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        checkpoint_id, checkpoint_name, created_at, checkpoint_type,
                        target_table, status,
                        JSON_LENGTH(snapshot_rows_json) AS rows_captured
                    FROM recovery_checkpoints
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                checkpoints = cur.fetchall()
                for c in checkpoints:
                    if c.get("rows_captured") is None:
                        c["rows_captured"] = 0
                return checkpoints
        finally:
            conn.close()

    @staticmethod
    def restore_from_checkpoint(checkpoint_id: str, operator: str = "ADMIN_USER") -> Dict[str, Any]:
        """
        Restores table data from an existing recovery checkpoint inside an ACID transaction.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM recovery_checkpoints WHERE checkpoint_id = %s", (checkpoint_id,))
                ckpt = cur.fetchone()
                if not ckpt:
                    raise ValueError(f"Checkpoint '{checkpoint_id}' not found.")

                table_name = validate_identifier(ckpt["target_table"])
                rows = json.loads(ckpt["snapshot_rows_json"])

                if not rows:
                    return {
                        "checkpoint_id": checkpoint_id,
                        "status": "RESTORED",
                        "restored_rows": 0,
                        "message": "Checkpoint contained 0 rows to restore."
                    }

                # Safe restore: Upsert rows back into target table
                cols = list(rows[0].keys())
                cols_sql = ", ".join([f"`{validate_identifier(c)}`" for c in cols])
                placeholders = ", ".join(["%s"] * len(cols))
                update_sql = ", ".join([f"`{validate_identifier(c)}` = VALUES(`{validate_identifier(c)}`)" for c in cols])

                upsert_query = f"INSERT INTO `{table_name}` ({cols_sql}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_sql}"

                for r in rows:
                    vals = [r[c] for c in cols]
                    cur.execute(upsert_query, tuple(vals))

                cur.execute("UPDATE recovery_checkpoints SET status = 'RESTORED' WHERE checkpoint_id = %s", (checkpoint_id,))

            conn.commit()

            AuditService.log_event(
                event_type="CHECKPOINT_RESTORED",
                action_description=f"Restored table '{table_name}' from recovery checkpoint '{checkpoint_id}' ({len(rows)} rows re-applied).",
                actor=operator,
                target_table=table_name,
                result="SUCCESS"
            )

            return {
                "checkpoint_id": checkpoint_id,
                "status": "RESTORED",
                "target_table": table_name,
                "restored_rows": len(rows),
                "message": f"Successfully restored {len(rows)} records into '{table_name}'."
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to restore from checkpoint: {e}")
            raise e
        finally:
            conn.close()
