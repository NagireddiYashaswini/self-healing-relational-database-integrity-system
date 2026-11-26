import pytest
from backend.app.services.integrity_scanner import IntegrityScanner

def test_scanner_rule_filtering_all_enabled():
    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="FULL", rule_codes=None)
    assert res["status"] == "COMPLETED"
    assert res["issues_found"] > 0
    assert "ORPHAN" in res["issues_by_category"]

def test_scanner_rule_filtering_empty_rules():
    scanner = IntegrityScanner()
    # Explicitly empty rule selection must execute ZERO rules
    res = scanner.run_scan(scan_type="FULL", rule_codes=[])
    assert res["status"] == "COMPLETED"
    assert res["issues_found"] == 0
    assert len(res["issues"]) == 0
    assert res["issues_by_category"]["ORPHAN"] == 0
    assert res["issues_by_category"]["DUPLICATE"] == 0

def test_scanner_rule_filtering_single_category():
    scanner = IntegrityScanner()
    # Only duplicate rules
    dup_codes = [
        "RULE_DUP_COURSE_CODE",
        "RULE_DUP_DEPT_CODE",
        "RULE_DUP_DEPT_NAME",
        "RULE_DUP_STUDENT_EMAIL"
    ]
    res = scanner.run_scan(scan_type="FULL", rule_codes=dup_codes)
    assert res["status"] == "COMPLETED"
    assert res["issues_by_category"]["ORPHAN"] == 0
    assert res["issues_by_category"]["NULL_VIOLATION"] == 0
    assert res["issues_by_category"]["DOMAIN_VIOLATION"] == 0
    assert res["issues_by_category"]["DUPLICATE"] == res["issues_found"]

def test_scanner_rule_filtering_table_scope():
    scanner = IntegrityScanner()
    res = scanner.run_scan(scan_type="TABLE", target_tables=["departments"], rule_codes=None)
    assert res["status"] == "COMPLETED"
    assert all(i["table_name"] == "departments" for i in res["issues"])
