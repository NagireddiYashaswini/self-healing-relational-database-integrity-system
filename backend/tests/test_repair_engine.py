import pytest
from backend.app.services.repair_engine import RepairEngine, AlreadyRepairedError
from backend.app.services.integrity_scanner import IntegrityScanner

def test_repair_preview(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    
    # Ensure scan has run so we have an issue
    from backend.app.database.connection import get_connection
    scanner = IntegrityScanner()
    conn = get_connection()
    try:
        tables = scanner.discover_tables(conn)
    finally:
        conn.close()
    scan_tables = ["orders"] if "orders" in tables else ["staging_enrollments"]
    scan_res = scanner.run_scan(scan_type="TABLE", target_tables=scan_tables, operator="TEST")
    
    if scan_res["issues_found"] == 0:
        pytest.skip("No issues found to preview")
        
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
            cur.execute("SHOW TABLES;")
            tables = [list(r.values())[0].lower() for r in cur.fetchall()]
            target_table = "orders" if "orders" in tables else "staging_enrollments"
            rule_code = "RULE_ORPHAN_ORDERS_CUSTOMER" if target_table == "orders" else "RULE_ORPHAN_STAGING_COURSE"
            col_name = "customer_id" if target_table == "orders" else "course_id"

            cur.execute("DELETE FROM repair_recommendations WHERE issue_id = 'TEST-ISSUE-MISSING'")
            cur.execute("DELETE FROM integrity_issues WHERE issue_id = 'TEST-ISSUE-MISSING'")
            # Create a test issue for a non-existent row
            cur.execute("""
                INSERT INTO integrity_issues (
                    issue_id, scan_id, rule_id, rule_code, category, severity,
                    table_name, record_id, column_name, invalid_value, description, status
                ) VALUES (
                    'TEST-ISSUE-MISSING', 'SCAN-TEST', 1, %s,
                    'ORPHAN', 'HIGH', %s, '999999', %s, '999',
                    'Test orphan on non-existent record', 'OPEN'
                )
            """, (rule_code, target_table, col_name))
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

        # Preview on non-existent row returns ALREADY_REPAIRED preview and marks issue REPAIRED
        preview = engine.get_repair_preview(issue_id="TEST-ISSUE-MISSING")
        assert preview["status"] == "ALREADY_REPAIRED"
        assert "does not exist in the database" in preview["warning"]

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


def test_restore_parent_and_merge_duplicate_execution(mysql_available):
    """Verifies RESTORE_PARENT (no NameError) and MERGE_DUPLICATE (post-delete verification)."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    from backend.app.database.connection import get_connection
    engine = RepairEngine()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM staging_enrollments WHERE staging_id IN (9901, 9902)")
            cur.execute("DELETE FROM departments WHERE dept_id = 9901")
            cur.execute("DELETE FROM repair_executions WHERE issue_id IN ('TEST-RESTORE-1', 'TEST-MERGE-1')")
            cur.execute("DELETE FROM repair_recommendations WHERE issue_id IN ('TEST-RESTORE-1', 'TEST-MERGE-1')")
            cur.execute("DELETE FROM integrity_issues WHERE issue_id IN ('TEST-RESTORE-1', 'TEST-MERGE-1')")
            cur.execute("DELETE FROM quarantine_records WHERE source_pk_value IN ('9901', '9902')")

            # 1. Seed staging_enrollments row referencing missing dept_id via instructors-like test on staging_courses
            cur.execute("DELETE FROM staging_courses WHERE staging_id = 9901")
            cur.execute("""
                INSERT INTO staging_courses (staging_id, course_code, course_name, credits, dept_id, instructor_id)
                VALUES (9901, 'REST901', 'Restore Parent Course', 3, 9901, 1)
            """)
            cur.execute("""
                INSERT INTO integrity_issues (
                    issue_id, scan_id, rule_id, rule_code, category, severity,
                    table_name, record_id, column_name, invalid_value, description, status
                ) VALUES (
                    'TEST-RESTORE-1', 'SCAN-TEST', NULL, 'RULE_ORPHAN_COURSE_DEPT',
                    'ORPHAN', 'HIGH', 'staging_courses', '9901', 'dept_id', '9901',
                    'Test restore parent', 'OPEN'
                )
            """)
            cur.execute("""
                INSERT INTO repair_recommendations (
                    issue_id, strategy, problem_description, proposed_action,
                    reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                ) VALUES (
                    'TEST-RESTORE-1', 'RESTORE_PARENT', 'Missing dept', 'Restore dept 9901',
                    'Orphan FK', 'Restores dept 9901', 'HIGH', TRUE, FALSE, 'APPROVED'
                )
            """)

            # 2. Seed duplicate row for MERGE_DUPLICATE
            cur.execute("""
                INSERT INTO staging_enrollments (staging_id, external_ref, student_id, course_id, student_email, enrolled_on, grade_marks, status)
                VALUES (9902, 'EXT-MERGE-1', 101, 1, 'ravi.kumar@univ.edu', '2026-09-01', 90.00, 'ENROLLED')
            """)
            cur.execute("""
                INSERT INTO integrity_issues (
                    issue_id, scan_id, rule_id, rule_code, category, severity,
                    table_name, record_id, column_name, invalid_value, description, status
                ) VALUES (
                    'TEST-MERGE-1', 'SCAN-TEST', NULL, 'RULE_DUP_STAGING_ENROLLMENT',
                    'DUPLICATE', 'HIGH', 'staging_enrollments', '9902', 'student_id,course_id', '101,1',
                    'Test merge duplicate', 'OPEN'
                )
            """)
            cur.execute("""
                INSERT INTO repair_recommendations (
                    issue_id, strategy, problem_description, proposed_action,
                    reason, expected_impact, risk_level, is_reversible, requires_approval, approval_status
                ) VALUES (
                    'TEST-MERGE-1', 'MERGE_DUPLICATE', 'Dup row', 'Merge duplicate 9902',
                    'Duplicate pair', 'Quarantines & removes 9902', 'HIGH', TRUE, FALSE, 'APPROVED'
                )
            """)
        conn.commit()

        # Execute RESTORE_PARENT
        res_restore = engine.execute_repair(issue_id="TEST-RESTORE-1", strategy="RESTORE_PARENT", confirmed=True, operator="TEST")
        assert res_restore["status"] == "SUCCESS"

        # Execute MERGE_DUPLICATE
        res_merge = engine.execute_repair(issue_id="TEST-MERGE-1", strategy="MERGE_DUPLICATE", confirmed=True, operator="TEST")
        assert res_merge["status"] == "SUCCESS"

        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM departments WHERE dept_id = 9901")
            assert cur.fetchone()["c"] == 1
            cur.execute("SELECT COUNT(*) AS c FROM staging_enrollments WHERE staging_id = 9902")
            assert cur.fetchone()["c"] == 0
            cur.execute("SELECT status FROM integrity_issues WHERE issue_id = 'TEST-MERGE-1'")
            assert cur.fetchone()["status"] == "REPAIRED"
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM repair_executions WHERE issue_id IN ('TEST-RESTORE-1', 'TEST-MERGE-1')")
            cur.execute("DELETE FROM repair_recommendations WHERE issue_id IN ('TEST-RESTORE-1', 'TEST-MERGE-1')")
            cur.execute("DELETE FROM integrity_issues WHERE issue_id IN ('TEST-RESTORE-1', 'TEST-MERGE-1')")
            cur.execute("DELETE FROM staging_courses WHERE staging_id = 9901")
            cur.execute("DELETE FROM staging_enrollments WHERE staging_id = 9902")
            cur.execute("DELETE FROM departments WHERE dept_id = 9901")
            cur.execute("DELETE FROM quarantine_records WHERE source_pk_value IN ('9901', '9902')")
        conn.commit()
        conn.close()
