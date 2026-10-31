import pytest
from backend.app.services.transaction_manager import TransactionManager

def test_transaction_demo_commit(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    try:
        res = TransactionManager.run_demonstration("COMMIT_SUCCESS")
        assert res["overall_status"] == "COMMITTED"
        assert res["state_preserved"] is True
        assert len(res["steps"]) >= 3
    finally:
        from backend.app.database.connection import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM customers WHERE customer_id >= 9 OR email LIKE 'tx_%'")
            conn.commit()
        finally:
            conn.close()

def test_transaction_demo_rollback(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    res = TransactionManager.run_demonstration("SIMULATED_FAILURE_ROLLBACK")
    assert res["overall_status"] == "ROLLED_BACK"
    assert res["initial_state_count"] == res["final_state_count"]
    assert res["state_preserved"] is True
    assert any(s["status"] == "ROLLED_BACK" for s in res["steps"])

def test_transaction_demo_savepoint(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    try:
        res = TransactionManager.run_demonstration("SAVEPOINT_PARTIAL_ROLLBACK")
        assert res["overall_status"] == "COMMITTED"
        assert res["state_preserved"] is True
        assert any(s["operation_name"] == "SET_SAVEPOINT" for s in res["steps"])
    finally:
        from backend.app.database.connection import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM customers WHERE customer_id >= 9 OR email LIKE 'tx_%'")
            conn.commit()
        finally:
            conn.close()
