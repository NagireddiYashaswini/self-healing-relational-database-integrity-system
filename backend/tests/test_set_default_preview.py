import pytest
import uuid
from backend.app.services.repair_engine import RepairEngine, AlreadyRepairedError, StalePreviewError
from backend.app.services.dependency_analyzer import DependencyAnalyzer
from backend.app.database.connection import get_connection

@pytest.fixture(autouse=True)
def require_customers_table(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'customers';")
            res = cur.fetchone()
        conn.close()
        if not res:
            pytest.skip("Test suite requires retail schema table 'customers'")
    except Exception:
        pytest.skip("Database connection failed")

def test_test_a_preview_missing_customer_name(mysql_available):
    """Test A: Preview for missing customer name requires admin input, rejects placeholders, disables execution."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    engine = RepairEngine()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT issue_id FROM integrity_issues
                WHERE table_name = 'customers' AND record_id = '8' AND status = 'OPEN'
                LIMIT 1
            """)
            iss = cur.fetchone()
            if not iss:
                pytest.skip("No open issue on customers record 8 found.")
            issue_id = iss["issue_id"]

        preview = engine.get_repair_preview(issue_id)
        
        # 1. Warning displayed that original value is missing
        assert preview["warning"] is not None
        assert "missing" in preview["warning"].lower()
        
        # 2. Input field is required for administrator
        assert preview["requires_admin_input"] is True
        assert preview["input_field_name"] == "customer_name"
        
        # 3. Fabricated placeholder is strictly prohibited
        assert "[PROPOSED: Unspecified Customer]" not in str(preview["after_state"].get("customer_name"))
        assert preview["after_state"]["customer_name"] == "<Awaiting Administrator Replacement Value>"
        
        # 4. Critical risk is not downgraded to LOW
        assert preview["risk_level"] == "CRITICAL"
        
        # 5. Execution without admin input must be rejected
        with pytest.raises(ValueError) as exc:
            engine.execute_repair(issue_id, strategy="SET_DEFAULT", repair_parameters=None, confirmed=True)
        assert "Administrator replacement value is required" in str(exc.value)

    finally:
        conn.close()

def test_test_b_admin_provided_value_validation(mysql_available):
    """Test B: Entering valid admin value updates preview, produces parameterized SQL, rejects placeholders."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    engine = RepairEngine()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT issue_id FROM integrity_issues
                WHERE table_name = 'customers' AND record_id = '8' AND status = 'OPEN'
                LIMIT 1
            """)
            iss = cur.fetchone()
            if not iss:
                pytest.skip("No open issue on customers record 8 found.")
            issue_id = iss["issue_id"]

        # Prohibited placeholder rejected
        prev_ph = engine.get_repair_preview(issue_id, repair_parameters={"value": "[PROPOSED: Invalid]"})
        assert prev_ph["requires_admin_input"] is True
        assert prev_ph["validation_error"] is not None
        assert "placeholder pattern and is prohibited" in prev_ph["validation_error"]

        # Empty string rejected
        prev_empty = engine.get_repair_preview(issue_id, repair_parameters={"value": "   "})
        assert prev_empty["requires_admin_input"] is True

        # Valid business name accepted
        valid_name = "Ramesh Gupta"
        prev_valid = engine.get_repair_preview(issue_id, repair_parameters={"value": valid_name})
        assert prev_valid["requires_admin_input"] is False
        assert prev_valid["validation_error"] is None
        assert prev_valid["after_state"]["customer_name"] == valid_name
        assert any("%s" in s for s in prev_valid["sql_preview"])
        assert prev_valid["row_version_token"] is not None

    finally:
        conn.close()

def test_test_c_foreign_key_dependency_detection(mysql_available):
    """Test C: Foreign key dependencies identified (direct child orders, downstream order_items, payments)."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    analyzer = DependencyAnalyzer()
    impact = analyzer.assess_repair_impact("customers", "8", "SET_DEFAULT", issue_severity="CRITICAL")

    # Direct child table
    assert "orders" in impact["direct_children"]

    # Downstream dependent tables
    assert "order_items" in impact["downstream_tables"]
    assert "payments" in impact["downstream_tables"]

    # Accurate dependent records count
    assert impact["matching_child_records_count"] == 0
    assert impact["has_dependent_records"] is False

    # Risk level preserved as CRITICAL
    assert impact["risk_level"] == "CRITICAL"
    assert "Schema dependencies detected" in impact["foreign_key_consequences"]

def test_test_d_repair_failure_handling_and_rollback(mysql_available):
    """Test D: Repair execution failure rolls back atomically, leaves record unchanged, and logs failure."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    engine = RepairEngine()
    conn = get_connection()
    test_id = f"TEST-FAIL-{uuid.uuid4().hex[:6].upper()}"
    try:
        # Create isolated test issue and recommendation on customers row 8
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO integrity_issues (
                    issue_id, scan_id, rule_id, rule_code, category, severity,
                    table_name, record_id, column_name, invalid_value, description, status
                ) VALUES (
                    %s, 'SCAN-TEST', 1, 'RULE_TEST_FAIL', 'NULL_EMPTY', 'HIGH',
                    'customers', '8', 'customer_name', '', 'Test rollback issue', 'OPEN'
                )
            """, (test_id,))
            cur.execute("""
                INSERT INTO repair_recommendations (
                    issue_id, strategy, problem_description, proposed_action,
                    reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                ) VALUES (
                    %s, 'SET_DEFAULT', 'Test fail', 'Test fail action',
                    'Test reason', 'Test impact', 'HIGH', FALSE, FALSE, 'APPROVED'
                )
            """, (test_id,))
            cur.execute("SELECT customer_name FROM customers WHERE customer_id = 8")
            orig_name = cur.fetchone()["customer_name"]
        conn.commit()

        # Trigger execution with invalid value that fails validation
        with pytest.raises(ValueError):
            engine.execute_repair(test_id, strategy="SET_DEFAULT", repair_parameters={"value": ""}, confirmed=True)

        # Verify record remains unchanged in database
        with conn.cursor() as cur:
            cur.execute("SELECT customer_name FROM customers WHERE customer_id = 8")
            assert cur.fetchone()["customer_name"] == orig_name

            # Verify audit log recorded failure
            cur.execute("SELECT * FROM audit_logs WHERE related_issue_id = %s AND result = 'FAILURE'", (test_id,))
            fail_log = cur.fetchone()
            assert fail_log is not None
            assert fail_log["event_type"] == "REPAIR_FAILED"

    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM repair_recommendations WHERE issue_id = %s", (test_id,))
            cur.execute("DELETE FROM integrity_issues WHERE issue_id = %s", (test_id,))
            cur.execute("DELETE FROM audit_logs WHERE related_issue_id = %s", (test_id,))
        conn.commit()
        conn.close()

def test_test_e_and_f_successful_repair_and_duplicate_prevention(mysql_available):
    """Test E & F: Successful repair execution updates record, status, audit, and prevents duplicate execution."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    engine = RepairEngine()
    conn = get_connection()
    test_issue_id = f"TEST-EXEC-{uuid.uuid4().hex[:6].upper()}"
    test_cust_id = 99991
    try:
        # Create an isolated test customer row and corresponding issue
        with conn.cursor() as cur:
            cur.execute("DELETE FROM customers WHERE customer_id = %s", (test_cust_id,))
            cur.execute("""
                INSERT INTO customers (customer_id, customer_name, email, phone, city, registration_date)
                VALUES (%s, '', 'test99991@example.com', '9999999991', 'Delhi', '2026-03-15')
            """, (test_cust_id,))
            cur.execute("""
                INSERT INTO integrity_issues (
                    issue_id, scan_id, rule_id, rule_code, category, severity,
                    table_name, record_id, column_name, invalid_value, description, status
                ) VALUES (
                    %s, 'SCAN-TEST', 1, 'RULE_TEST_EXEC', 'NULL_EMPTY', 'CRITICAL',
                    'customers', %s, 'customer_name', '', 'Test successful execution issue', 'OPEN'
                )
            """, (test_issue_id, str(test_cust_id)))
            cur.execute("""
                INSERT INTO repair_recommendations (
                    issue_id, strategy, problem_description, proposed_action,
                    reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                ) VALUES (
                    %s, 'SET_DEFAULT', 'Missing name', 'Set verified name',
                    'Required for business identity', 'Entity restored', 'CRITICAL', FALSE, FALSE, 'APPROVED'
                )
            """, (test_issue_id,))
        conn.commit()

        # Execute valid repair with admin replacement value
        replacement_name = "Vikram Aditya"
        res = engine.execute_repair(
            issue_id=test_issue_id,
            strategy="SET_DEFAULT",
            repair_parameters={"value": replacement_name},
            confirmed=True
        )
        assert res["status"] == "SUCCESS"

        # Verify database record updated
        with conn.cursor() as cur:
            cur.execute("SELECT customer_name FROM customers WHERE customer_id = %s", (test_cust_id,))
            assert cur.fetchone()["customer_name"] == replacement_name

            # Verify issue status marked REPAIRED
            cur.execute("SELECT status FROM integrity_issues WHERE issue_id = %s", (test_issue_id,))
            assert cur.fetchone()["status"] == "REPAIRED"

            # Verify recommendation marked APPROVED
            cur.execute("SELECT approval_status FROM repair_recommendations WHERE issue_id = %s", (test_issue_id,))
            assert cur.fetchone()["approval_status"] == "APPROVED"

            # Verify repair execution logged
            cur.execute("SELECT * FROM repair_executions WHERE issue_id = %s", (test_issue_id,))
            exec_entry = cur.fetchone()
            assert exec_entry is not None
            assert exec_entry["status"] == "SUCCESS"

            # Verify audit trail logged
            cur.execute("SELECT * FROM audit_logs WHERE related_issue_id = %s AND event_type = 'REPAIR_EXECUTED'", (test_issue_id,))
            assert cur.fetchone() is not None

        # Test F: Duplicate execution attempt on same issue MUST raise AlreadyRepairedError
        with pytest.raises(AlreadyRepairedError) as exc:
            engine.execute_repair(
                issue_id=test_issue_id,
                strategy="SET_DEFAULT",
                repair_parameters={"value": "Another Name"},
                confirmed=True
            )
        assert "already been repaired" in str(exc.value)

    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM repair_executions WHERE issue_id = %s", (test_issue_id,))
            cur.execute("DELETE FROM audit_logs WHERE related_issue_id = %s", (test_issue_id,))
            cur.execute("DELETE FROM repair_recommendations WHERE issue_id = %s", (test_issue_id,))
            cur.execute("DELETE FROM integrity_issues WHERE issue_id = %s", (test_issue_id,))
            cur.execute("DELETE FROM customers WHERE customer_id = %s", (test_cust_id,))
        conn.commit()
        conn.close()

def test_test_g_stale_preview_rejection(mysql_available):
    """Test G: Stale preview is detected and rejected if record changes between preview and execution."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    engine = RepairEngine()
    conn = get_connection()
    test_issue_id = f"TEST-STALE-{uuid.uuid4().hex[:6].upper()}"
    test_cust_id = 99992
    try:
        # Create test customer row and issue
        with conn.cursor() as cur:
            cur.execute("DELETE FROM customers WHERE customer_id = %s", (test_cust_id,))
            cur.execute("""
                INSERT INTO customers (customer_id, customer_name, email, phone, city, registration_date)
                VALUES (%s, '', 'stale_test@example.com', '9999999992', 'Pune', '2026-03-15')
            """, (test_cust_id,))
            cur.execute("""
                INSERT INTO integrity_issues (
                    issue_id, scan_id, rule_id, rule_code, category, severity,
                    table_name, record_id, column_name, invalid_value, description, status
                ) VALUES (
                    %s, 'SCAN-TEST', 1, 'RULE_TEST_STALE', 'NULL_EMPTY', 'HIGH',
                    'customers', %s, 'customer_name', '', 'Test stale preview issue', 'OPEN'
                )
            """, (test_issue_id, str(test_cust_id)))
            cur.execute("""
                INSERT INTO repair_recommendations (
                    issue_id, strategy, problem_description, proposed_action,
                    reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                ) VALUES (
                    %s, 'SET_DEFAULT', 'Missing name', 'Set verified name',
                    'Required', 'Restored', 'HIGH', FALSE, FALSE, 'APPROVED'
                )
            """, (test_issue_id,))
        conn.commit()

        # 1. Generate preview and capture row_version_token
        preview = engine.get_repair_preview(test_issue_id, repair_parameters={"value": "Initial Proposed"})
        token = preview["row_version_token"]
        assert token is not None

        # 2. Simulate concurrent modification to the database record
        with conn.cursor() as cur:
            cur.execute("UPDATE customers SET city = 'Mumbai' WHERE customer_id = %s", (test_cust_id,))
        conn.commit()

        # 3. Attempting execution with the old token MUST raise StalePreviewError
        with pytest.raises(StalePreviewError) as exc:
            engine.execute_repair(
                issue_id=test_issue_id,
                strategy="SET_DEFAULT",
                repair_parameters={"value": "Initial Proposed"},
                confirmed=True,
                row_version_token=token
            )
        assert "modified since the preview was generated" in str(exc.value)

    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM repair_recommendations WHERE issue_id = %s", (test_issue_id,))
            cur.execute("DELETE FROM integrity_issues WHERE issue_id = %s", (test_issue_id,))
            cur.execute("DELETE FROM customers WHERE customer_id = %s", (test_cust_id,))
        conn.commit()
        conn.close()

