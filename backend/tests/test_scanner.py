import pytest
from backend.app.services.integrity_scanner import IntegrityScanner
from backend.app.database.connection import get_connection

def test_scanner_detection_run(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    
    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="FULL", operator="TEST_SUITE")
    
    assert res["status"] == "COMPLETED"
    assert res["scan_id"].startswith("SCAN-")
    assert res["total_rows_inspected"] > 0
    assert res["issues_found"] > 0
    assert isinstance(res["issues"], list)
    
    # Verify categories present in issues
    categories = {i["category"] for i in res["issues"]}
    assert "ORPHAN" in categories or "DOMAIN_VIOLATION" in categories or "DUPLICATE" in categories

def test_recommendation_generation():
    scanner = IntegrityScanner()
    sample_orphan_issue = {
        "issue_id": "TEST-ISSUE-1",
        "category": "ORPHAN",
        "table_name": "staging_enrollments",
        "record_id": "999",
        "column_name": "student_id",
        "invalid_value": "999",
        "description": "Orphan student reference",
        "severity": "CRITICAL"
    }
    rec = scanner._generate_recommendation(sample_orphan_issue)
    assert rec["strategy"] == "QUARANTINE"
    assert rec["is_reversible"] is True
    assert rec["requires_approval"] is True

    sample_dup_issue = {
        "issue_id": "TEST-ISSUE-2",
        "category": "DUPLICATE",
        "table_name": "students",
        "record_id": "205",
        "column_name": "email",
        "invalid_value": "dup@univ.edu",
        "description": "Duplicate email",
        "severity": "HIGH"
    }
    rec_dup = scanner._generate_recommendation(sample_dup_issue)
    assert rec_dup["strategy"] == "DELETE_RECORD"
