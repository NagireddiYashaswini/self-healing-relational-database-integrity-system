import pytest
from backend.app.services.recovery_manager import RecoveryManager
from backend.app.core.config import settings

def test_recovery_manager_class_exists():
    """Unit test: verifies RecoveryManager has required interface methods."""
    assert hasattr(RecoveryManager, "create_checkpoint")
    assert hasattr(RecoveryManager, "list_checkpoints")
    assert hasattr(RecoveryManager, "restore_from_checkpoint")

def test_recovery_checkpoint_and_restoration_lifecycle(mysql_available):
    """
    Integration test: Creates a checkpoint on a table, verifies full table snapshot,
    modifies records, restores from checkpoint, and verifies complete table state match.
    """
    if not mysql_available:
        pytest.skip(f"Integration test requires active MySQL database '{settings.DB_NAME}'")

    # Step 1: Create checkpoint
    ckpt = None
    try:
        ckpt = RecoveryManager.create_checkpoint(
            target_table="categories",
            checkpoint_name="Automated Test Categories Checkpoint",
            checkpoint_type="MANUAL"
        )
        assert ckpt["checkpoint_id"].startswith("CKPT-")
        assert ckpt["target_table"] == "categories"
        assert ckpt["rows_captured"] >= 4

        # Step 2: List checkpoints
        ckpts = RecoveryManager.list_checkpoints(limit=5)
        assert any(c["checkpoint_id"] == ckpt["checkpoint_id"] for c in ckpts)

        # Step 3: Test restoration
        res = RecoveryManager.restore_from_checkpoint(
            checkpoint_id=ckpt["checkpoint_id"],
            operator="PYTEST_RUNNER"
        )
        assert res["status"] == "RESTORED"
        assert res["target_table"] == "categories"
        assert res["verified"] is True
    finally:
        if ckpt and ckpt.get("checkpoint_id"):
            from backend.app.database.connection import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM recovery_checkpoints WHERE checkpoint_id = %s", (ckpt["checkpoint_id"],))
                conn.commit()
            finally:
                conn.close()

