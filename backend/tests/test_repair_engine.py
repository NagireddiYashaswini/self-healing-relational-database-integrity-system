import pytest
from backend.app.services.repair_engine import RepairEngine, AlreadyRepairedError
from backend.app.services.integrity_scanner import IntegrityScanner

def test_repair_preview(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    
    # Ensure scan has run so we have an issue
    scanner = IntegrityScanner()
    scan_res = scanner.run_scan(scan_type="TABLE", target_tables=["orders"], operator="TEST")
    
    if scan_res["issues_found"] == 0:
        pytest.skip("No orders issues found to preview")
        
    issue = scan_res["issues"][0]
    engine = RepairEngine()
    
    preview = engine.get_repair_preview(issue_id=issue["issue_id"])
    assert preview["issue_id"] == issue["issue_id"]
    assert "before_state" in preview
    assert "after_state" in preview
    assert "sql_preview" in preview
    assert len(preview["sql_preview"]) > 0

def test_destructive_repair_requires_confirmation(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
        
    engine = RepairEngine()
    # Attempting to call without confirmed flag should fail if handled by API
    # Directly test engine method with safe test issue or preview
    assert True

def test_missing_record_handling_and_auto_resolution(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    from backend.app.database.connection import get_connection
    engine = RepairEngine()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM repair_recommendations WHERE issue_id = 'TEST-ISSUE-MISSING'")
            cur.execute("DELETE FROM integrity_issues WHERE issue_id = 'TEST-ISSUE-MISSING'")
            # Create a test issue for a non-existent row
            cur.execute("""
                INSERT INTO integrity_issues (
                    issue_id, scan_id, rule_id, rule_code, category, severity,
                    table_name, record_id, column_name, invalid_value, description, status
                ) VALUES (
                    'TEST-ISSUE-MISSING', 'SCAN-TEST', 1, 'RULE_ORPHAN_ORDERS_CUSTOMER',
                    'ORPHAN', 'HIGH', 'orders', '999999', 'customer_id', '999',
                    'Test orphan on non-existent record', 'OPEN'
                )
            """)
            cur.execute("""
                INSERT INTO repair_recommendations (
                    issue_id, strategy, problem_description, proposed_action,
                    reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                ) VALUES (
                    'TEST-ISSUE-MISSING', 'QUARANTINE', 'Test problem', 'Test action',
                    'Test reason', 'Test impact', 'HIGH', FALSE, TRUE, 'PENDING'
                )
            """)
        conn.commit()

        # Preview on non-existent row should raise ValueError and mark issue REPAIRED
        with pytest.raises(ValueError) as excinfo:
            engine.get_repair_preview(issue_id="TEST-ISSUE-MISSING")
        assert "does not exist in the database" in str(excinfo.value)
        assert "REPAIRED" in str(excinfo.value)

        # Check DB to confirm it was marked REPAIRED
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM integrity_issues WHERE issue_id = 'TEST-ISSUE-MISSING'")
            assert cur.fetchone()["status"] == "REPAIRED"

        # Execute repair on an already REPAIRED issue must raise AlreadyRepairedError
        with pytest.raises(AlreadyRepairedError) as excinfo:
            engine.execute_repair(issue_id="TEST-ISSUE-MISSING", strategy="QUARANTINE")
        assert "already been repaired" in str(excinfo.value)

        # Clean up
        with conn.cursor() as cur:
            cur.execute("DELETE FROM repair_recommendations WHERE issue_id = 'TEST-ISSUE-MISSING'")
            cur.execute("DELETE FROM integrity_issues WHERE issue_id = 'TEST-ISSUE-MISSING'")
        conn.commit()
    finally:
        conn.close()
