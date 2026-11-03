import pytest
import json
from backend.app.services.integrity_scanner import IntegrityScanner
from backend.app.services.repair_engine import RepairEngine, AlreadyRepairedError
from backend.app.database.connection import get_connection

SIX_TABLES = [
    "departments",
    "instructors",
    "courses",
    "students",
    "enrollments",
    "staging_enrollments"
]

FOUR_CATEGORIES = [
    "ORPHAN",
    "DUPLICATE",
    "NULL_VIOLATION",
    "DOMAIN_VIOLATION"
]

def test_full_database_scan_covers_all_six_tables(mysql_available):
    """Verifies that a FULL scan inspects all six tables and identifies violations."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="FULL", operator="TEST_SIX_TABLES")

    assert res["status"] == "COMPLETED"
    assert res["total_rules"] == 45
    assert res["total_rows_inspected"] > 0
    assert res["issues_found"] > 0

    # Verify all 6 tables are present in rules_by_table
    for tbl in SIX_TABLES:
        assert tbl in res["rules_by_table"], f"Table {tbl} missing from rules_by_table"
        assert res["rules_by_table"][tbl] >= 5, f"Table {tbl} has fewer than 5 rules"

    # Verify all 6 tables have detected violations from seeded demo anomalies
    for tbl in SIX_TABLES:
        assert tbl in res["issues_by_table"], f"Table {tbl} missing from issues_by_table"
        assert res["issues_by_table"][tbl] > 0, f"Table {tbl} expected to have issues but had 0"

    # Verify all 4 integrity categories are detected
    categories = res["issues_by_category"]
    for cat in FOUR_CATEGORIES:
        assert categories.get(cat, 0) > 0, f"Category {cat} had 0 detected violations"


@pytest.mark.parametrize("target_table", SIX_TABLES)
def test_individual_table_scans(mysql_available, target_table):
    """Verifies scanning each of the six tables independently."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="TABLE", target_tables=[target_table], operator="TEST_ISOLATION")

    assert res["status"] == "COMPLETED"
    assert res["target_tables"] == [target_table]
    assert res["issues_found"] > 0, f"Expected issues in isolated scan of {target_table}"

    # Confirm that all returned issues belong strictly to target_table
    for issue in res["issues"]:
        assert issue["table_name"] == target_table, f"Expected {target_table}, got {issue['table_name']}"
        assert issue["record_id"] is not None
        assert issue["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


def test_orphan_checks_across_child_tables(mysql_available):
    """Verifies orphan detection across all child-to-parent relationships."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="FULL", operator="TEST_ORPHAN")
    orphan_issues = [i for i in res["issues"] if i["category"] == "ORPHAN"]
    orphan_tables = {i["table_name"] for i in orphan_issues}

    # Expected child tables with foreign key orphan checks
    expected_children = {"instructors", "courses", "students", "enrollments", "staging_enrollments"}
    for child in expected_children:
        assert child in orphan_tables, f"Child table '{child}' did not report orphan violations"


def test_duplicate_checks_across_tables(mysql_available):
    """Verifies duplicate detection across candidate keys and logical pairs."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="FULL", operator="TEST_DUP")
    dup_issues = [i for i in res["issues"] if i["category"] == "DUPLICATE"]
    dup_tables = {i["table_name"] for i in dup_issues}

    # Duplicate checks must cover departments (name/code), instructors (email), courses (code),
    # students (email), enrollments (pair), staging_enrollments (pair/ref)
    for tbl in SIX_TABLES:
        assert tbl in dup_tables, f"Table '{tbl}' did not report duplicate violations"


def test_null_checks_across_tables(mysql_available):
    """Verifies NOT NULL and TRIM whitespace checks across tables."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="FULL", operator="TEST_NULL")
    null_issues = [i for i in res["issues"] if i["category"] == "NULL_VIOLATION"]
    null_tables = {i["table_name"] for i in null_issues}

    for tbl in SIX_TABLES:
        assert tbl in null_tables, f"Table '{tbl}' did not report NULL violations"


def test_domain_checks_across_tables(mysql_available):
    """Verifies domain constraints (budget, salary, credits, gpa, age, status enum, marks, email)."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="FULL", operator="TEST_DOMAIN")
    domain_issues = [i for i in res["issues"] if i["category"] == "DOMAIN_VIOLATION"]
    domain_tables = {i["table_name"] for i in domain_issues}

    for tbl in SIX_TABLES:
        assert tbl in domain_tables, f"Table '{tbl}' did not report domain violations"


def test_quarantine_repair_transaction_safety(mysql_available):
    """Verifies that QUARANTINE serializes the row to quarantine_records and deletes it from source transactionally."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Clean up any residual test row first
            cur.execute("DELETE FROM staging_enrollments WHERE staging_id = 8888")
            cur.execute("DELETE FROM quarantine_records WHERE source_table = 'staging_enrollments' AND source_pk_value = '8888'")
            # Insert a temporary orphan record in staging_enrollments for quarantine testing
            cur.execute("""
                INSERT INTO staging_enrollments (
                    staging_id, student_id, course_id, student_email, grade_marks, status, external_ref, notes
                ) VALUES (
                    8888, 99999, 88888, 'quarantine.test@univ.edu', 55, 'ENROLLED', 'EXT-QUAR-TEST', 'Orphan test row'
                )
            """)
        conn.commit()

        scanner = IntegrityScanner()
        scan_res = scanner.run_scan(scan_type="TABLE", target_tables=["staging_enrollments"], operator="TEST_QUARANTINE")
        orphan_issues = [i for i in scan_res["issues"] if str(i["record_id"]) == "8888" and i["category"] == "ORPHAN"]
        assert len(orphan_issues) > 0, "Seeded staging orphan was not detected"

        target_issue = orphan_issues[0]
        engine = RepairEngine()

        # 1. Preview QUARANTINE
        preview = engine.get_repair_preview(issue_id=target_issue["issue_id"], strategy_override="QUARANTINE")
        assert preview["strategy"] == "QUARANTINE"
        assert preview["is_destructive"] is True
        assert any("DELETE FROM `staging_enrollments`" in s for s in preview["sql_preview"])

        # 2. Approve and Execute QUARANTINE
        engine.approve_recommendation(recommendation_id=target_issue["issue_id"], operator="TEST_ADMIN")
        exec_res = engine.execute_repair(
            issue_id=target_issue["issue_id"],
            strategy="QUARANTINE",
            row_version_token=preview["row_version_token"],
            confirmed=True,
            operator="TEST_ADMIN"
        )
        assert exec_res["status"] == "SUCCESS"

        # Advance snapshot view to verify committed data
        conn.commit()

        # 3. Verify row in quarantine_records
        with conn.cursor() as cur:
            cur.execute("""
                SELECT row_data_json, source_table, source_pk_value, issue_type
                FROM quarantine_records
                WHERE source_table = 'staging_enrollments' AND source_pk_value = '8888'
                ORDER BY quarantine_id DESC LIMIT 1
            """)
            q_row = cur.fetchone()
            assert q_row is not None, "Quarantine record was not found in quarantine_records!"
            orig_data = json.loads(q_row["row_data_json"])
            assert orig_data["staging_id"] == 8888
            assert orig_data["student_email"] == "quarantine.test@univ.edu"

            # 4. Verify row was deleted from source table
            cur.execute("SELECT COUNT(*) AS c FROM staging_enrollments WHERE staging_id = 8888")
            assert cur.fetchone()["c"] == 0, "Record was not removed from source table!"

            # 5. Verify issue status is marked REPAIRED
            cur.execute("SELECT status FROM integrity_issues WHERE issue_id = %s", (target_issue["issue_id"],))
            assert cur.fetchone()["status"] == "REPAIRED"

    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM staging_enrollments WHERE staging_id = 8888")
            cur.execute("DELETE FROM quarantine_records WHERE source_table = 'staging_enrollments' AND source_pk_value = '8888'")
        conn.commit()
        conn.close()


def test_set_default_repair_preview_and_execution(mysql_available):
    """Verifies SET_DEFAULT preview and execution on domain violation."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Clean up any residual test row first
            cur.execute("DELETE FROM departments WHERE dept_id = 777")
            # Insert a temporary test department with negative budget
            cur.execute("""
                INSERT INTO departments (dept_id, dept_code, dept_name, budget, building)
                VALUES (777, 'TST7', 'Test Dept For Healing', -5000.00, 'Test Hall')
            """)
        conn.commit()

        scanner = IntegrityScanner()
        scan_res = scanner.run_scan(scan_type="TABLE", target_tables=["departments"], operator="TEST_SET_DEFAULT")
        budget_issues = [i for i in scan_res["issues"] if str(i["record_id"]) == "777" and "budget" in i.get("column_name", "").lower()]
        assert len(budget_issues) > 0, "Seeded department negative budget violation not detected"

        target_issue = budget_issues[0]
        engine = RepairEngine()

        # 1. Preview SET_DEFAULT initially
        initial_preview = engine.get_repair_preview(
            issue_id=target_issue["issue_id"],
            strategy_override="SET_DEFAULT"
        )
        assert initial_preview["strategy"] == "SET_DEFAULT"
        assert "after_state" in initial_preview

        # 2. Preview SET_DEFAULT with custom replacement
        preview = engine.get_repair_preview(
            issue_id=target_issue["issue_id"],
            strategy_override="SET_DEFAULT",
            repair_parameters={"value": 150000.00}
        )
        assert preview["strategy"] == "SET_DEFAULT"
        assert preview["requires_admin_input"] is False
        assert float(preview["after_state"]["budget"]) == 150000.00

        # 3. Execute SET_DEFAULT
        engine.approve_recommendation(recommendation_id=target_issue["issue_id"], operator="TEST_ADMIN")
        exec_res = engine.execute_repair(
            issue_id=target_issue["issue_id"],
            strategy="SET_DEFAULT",
            repair_parameters={"value": 150000.00},
            row_version_token=preview["row_version_token"],
            confirmed=True,
            operator="TEST_ADMIN"
        )
        assert exec_res["status"] == "SUCCESS"

        # Advance snapshot view
        conn.commit()

        # 3. Verify in database
        with conn.cursor() as cur:
            cur.execute("SELECT budget FROM departments WHERE dept_id = 777")
            row = cur.fetchone()
            assert float(row["budget"]) == 150000.00

    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_id = 777")
        conn.commit()
        conn.close()
