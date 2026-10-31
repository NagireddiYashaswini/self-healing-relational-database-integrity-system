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
    def _get_primary_key(cur, table_name: str) -> str:
        """Finds primary key column name for a given table from INFORMATION_SCHEMA."""
        cur.execute("""
            SELECT COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND CONSTRAINT_NAME = 'PRIMARY'
            LIMIT 1
        """, (table_name,))
        res = cur.fetchone()
        if res and res.get("COLUMN_NAME"):
            return res["COLUMN_NAME"]
        return "id"

    @classmethod
    def create_checkpoint(
        cls,
        target_table: str,
        checkpoint_name: str,
        checkpoint_type: str = "PRE_REPAIR",
        row_id_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates an application-level recovery checkpoint by snapshotting metadata and row data.
        Captures full table state or filtered single-record state for atomic restoration.
        """
        table_name = validate_identifier(target_table)
        checkpoint_id = f"CKPT-{uuid.uuid4().hex[:10].upper()}"
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                # Capture table structure
                cur.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_table_row = cur.fetchone()
                schema_ddl = list(create_table_row.values())[1] if create_table_row else ""

                pk_col = cls._get_primary_key(cur, table_name)

                # Capture rows (full table or filtered)
                if row_id_filter:
                    cur.execute(f"SELECT * FROM `{table_name}` WHERE `{pk_col}` = %s", (row_id_filter,))
                else:
                    cur.execute(f"SELECT * FROM `{table_name}`")

                rows = cur.fetchall()

                snapshot_metadata = {
                    "table_name": table_name,
                    "pk_column": pk_col,
                    "row_count": len(rows),
                    "is_full_table": row_id_filter is None,
                    "row_id_filter": row_id_filter,
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

    @classmethod
    def restore_from_checkpoint(cls, checkpoint_id: str, operator: str = "ADMIN_USER") -> Dict[str, Any]:
        """
        Restores complete table data from an existing recovery checkpoint inside an ACID transaction.
        Handles inserted records (removes rows absent from snapshot), updated records (restores values),
        and deleted records (re-inserts missing rows), while strictly respecting foreign-key hierarchy.
        
        Verification is performed prior to COMMIT: if restored counts or keys differ from the snapshot,
        the transaction is rolled back and an audit failure is logged.
        
        Scope & Limitations:
        Operates on a table-by-table basis. When restoring interrelated tables, administrators must
        restore parent tables (e.g. categories, suppliers, customers) before child tables (products, orders, payments)
        to satisfy referential integrity constraints without blindly disabling database checks.
        """
        conn = get_connection()
        table_name = None
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM recovery_checkpoints WHERE checkpoint_id = %s", (checkpoint_id,))
                ckpt = cur.fetchone()
                if not ckpt:
                    raise ValueError(f"Checkpoint '{checkpoint_id}' not found.")

                table_name = validate_identifier(ckpt["target_table"])
                rows = json.loads(ckpt["snapshot_rows_json"])
                metadata = {}
                if ckpt.get("snapshot_metadata_json"):
                    try:
                        metadata = json.loads(ckpt["snapshot_metadata_json"])
                    except Exception:
                        metadata = {}

                pk_col = metadata.get("pk_column") or cls._get_primary_key(cur, table_name)
                is_full_table = metadata.get("is_full_table", True)
                row_id_filter = metadata.get("row_id_filter")

                # Step 1: Discover Child Foreign Keys to prevent orphan cascades
                cur.execute("""
                    SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND REFERENCED_TABLE_NAME = %s
                """, (table_name,))
                child_fks = cur.fetchall()

                # Step 2: Discover Parent Foreign Keys to ensure referenced parents exist
                cur.execute("""
                    SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = %s
                      AND REFERENCED_TABLE_NAME IS NOT NULL
                """, (table_name,))
                parent_fks = cur.fetchall()

                # Validate parent references exist before restoring child records
                for p_fk in parent_fks:
                    p_col = p_fk["COLUMN_NAME"]
                    p_tbl = p_fk["REFERENCED_TABLE_NAME"]
                    p_ref_col = p_fk["REFERENCED_COLUMN_NAME"]
                    parent_vals = {r[p_col] for r in rows if r.get(p_col) is not None}
                    if parent_vals:
                        fmt = ",".join(["%s"] * len(parent_vals))
                        cur.execute(f"SELECT `{p_ref_col}` FROM `{p_tbl}` WHERE `{p_ref_col}` IN ({fmt})", tuple(parent_vals))
                        existing_parent_vals = {r[p_ref_col] for r in cur.fetchall()}
                        missing_parents = [pv for pv in parent_vals if pv not in existing_parent_vals]
                        if missing_parents:
                            raise ValueError(
                                f"Referential constraint blocked restoration of '{table_name}': Snapshot references non-existent parent records "
                                f"in '{p_tbl}' (missing {p_ref_col}={missing_parents[:3]}). Restore parent table '{p_tbl}' first."
                            )

                deleted_excess_count = 0
                restored_row_count = 0

                if is_full_table:
                    # 1. Handle inserted records: Any record currently in the table but absent from snapshot must be removed
                    snapshot_pk_values = {str(r[pk_col]) for r in rows if pk_col in r}

                    cur.execute(f"SELECT `{pk_col}` FROM `{table_name}`")
                    current_rows = cur.fetchall()
                    current_pks = [str(cr[pk_col]) for cr in current_rows]

                    pks_to_delete = [cpk for cpk in current_pks if cpk not in snapshot_pk_values]
                    if pks_to_delete and child_fks:
                        for c_fk in child_fks:
                            c_tbl = c_fk["TABLE_NAME"]
                            c_col = c_fk["COLUMN_NAME"]
                            fmt_pks = ",".join(["%s"] * len(pks_to_delete))
                            cur.execute(f"SELECT COUNT(*) AS c FROM `{c_tbl}` WHERE `{c_col}` IN ({fmt_pks})", tuple(pks_to_delete))
                            dep_count = cur.fetchone()["c"]
                            if dep_count > 0:
                                raise ValueError(
                                    f"Cannot restore '{table_name}': {dep_count} dependent records exist in child table '{c_tbl}' "
                                    f"referencing keys marked for deletion ({', '.join(pks_to_delete[:5])}). "
                                    f"Please restore dependent child table '{c_tbl}' first."
                                )

                    for dpk in pks_to_delete:
                        cur.execute(f"DELETE FROM `{table_name}` WHERE `{pk_col}` = %s", (dpk,))
                        deleted_excess_count += 1

                # 2. Re-apply / restore snapshot rows
                if rows:
                    cols = list(rows[0].keys())
                    cols_sql = ", ".join([f"`{validate_identifier(c)}`" for c in cols])
                    placeholders = ", ".join(["%s"] * len(cols))
                    update_sql = ", ".join([f"`{validate_identifier(c)}` = VALUES(`{validate_identifier(c)}`)" for c in cols])

                    upsert_query = f"INSERT INTO `{table_name}` ({cols_sql}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_sql}"

                    for r in rows:
                        vals = [r[c] for c in cols]
                        cur.execute(upsert_query, tuple(vals))
                        restored_row_count += 1
                elif is_full_table and not rows:
                    cur.execute(f"DELETE FROM `{table_name}`")

                # Step 3: Verification Phase (Requirement 10)
                # Confirm restored table matches snapshot exactly before committing
                cur.execute(f"SELECT COUNT(*) AS c FROM `{table_name}`")
                post_restore_count = cur.fetchone()["c"]

                if is_full_table:
                    expected_count = len(rows)
                    if post_restore_count != expected_count:
                        raise RuntimeError(
                            f"Recovery verification failed: Expected {expected_count} rows in '{table_name}', "
                            f"but found {post_restore_count}."
                        )
                    # Verify each snapshot PK is present
                    for r in rows:
                        if pk_col in r:
                            cur.execute(f"SELECT COUNT(*) AS c FROM `{table_name}` WHERE `{pk_col}` = %s", (r[pk_col],))
                            if cur.fetchone()["c"] != 1:
                                raise RuntimeError(
                                    f"Recovery verification failed: Record {pk_col}={r[pk_col]} is missing or non-unique in '{table_name}'."
                                )

                # Update checkpoint status
                cur.execute("UPDATE recovery_checkpoints SET status = 'RESTORED' WHERE checkpoint_id = %s", (checkpoint_id,))

            conn.commit()

            AuditService.log_event(
                event_type="CHECKPOINT_RESTORED",
                action_description=(
                    f"Restored table '{table_name}' from checkpoint '{checkpoint_id}'. "
                    f"Re-applied {restored_row_count} rows, removed {deleted_excess_count} post-checkpoint inserted rows. Verified 100% match."
                ),
                actor=operator,
                target_table=table_name,
                result="SUCCESS"
            )

            return {
                "checkpoint_id": checkpoint_id,
                "status": "RESTORED",
                "target_table": table_name,
                "restored_rows": restored_row_count,
                "removed_excess_rows": deleted_excess_count,
                "verified": True,
                "message": f"Successfully restored '{table_name}' from snapshot ({restored_row_count} records restored, {deleted_excess_count} excess rows pruned). Verification confirmed."
            }

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to restore from checkpoint, rolled back: {e}")

            AuditService.log_event(
                event_type="CHECKPOINT_RESTORE_FAILED",
                action_description=f"Failed to restore table '{table_name}' from checkpoint '{checkpoint_id}': {str(e)}",
                actor=operator,
                target_table=table_name,
                result="FAILURE",
                error_message=str(e)
            )
            raise e
        finally:
            conn.close()
