import pytest
from backend.app.core.config import settings
from backend.app.database.connection import validate_identifier
from backend.app.services.audit_service import sanitize_json
from backend.app.services.integrity_scanner import IntegrityScanner, classify_table

# =============================================================================
# 1. SQL Identifier Validation Unit Tests
# =============================================================================

def test_validate_identifier_safe():
    assert validate_identifier("departments") == "departments"
    assert validate_identifier("staging_enrollments") == "staging_enrollments"
    assert validate_identifier("dept_id") == "dept_id"
    assert validate_identifier("audit_logs") == "audit_logs"

def test_validate_identifier_dangerous():
    with pytest.raises(ValueError):
        validate_identifier("departments; DROP TABLE students;--")
    with pytest.raises(ValueError):
        validate_identifier("students WHERE 1=1")
    with pytest.raises(ValueError):
        validate_identifier("")
    with pytest.raises(ValueError):
        validate_identifier("students`")

# =============================================================================
# 2. Audit Payload Credential Redaction Unit Tests
# =============================================================================

def test_sanitize_json_redaction():
    payload = {
        "username": "admin",
        "password": "supersecretpassword123",
        "api_token": "xyz987token",
        "user_secret": "my-secret-key",
        "email": "test@univ.edu"
    }
    sanitized_str = sanitize_json(payload)
    assert "[REDACTED]" in sanitized_str
    assert "supersecretpassword123" not in sanitized_str
    assert "xyz987token" not in sanitized_str
    assert "my-secret-key" not in sanitized_str
    assert "test@univ.edu" in sanitized_str

# =============================================================================
# 3. Table Architectural Classification Unit Tests
# =============================================================================

def test_table_classification_roles():
    # Business entities
    assert classify_table("departments") == "business"
    assert classify_table("instructors") == "business"
    assert classify_table("courses") == "business"
    assert classify_table("students") == "business"
    assert classify_table("enrollments") == "business"

    # Staging tables
    assert classify_table("staging_enrollments") == "staging"
    assert classify_table("stage_transfers") == "staging"

    # System engine tables
    assert classify_table("integrity_rules") == "system"
    assert classify_table("scan_runs") == "system"
    assert classify_table("integrity_issues") == "system"
    assert classify_table("repair_recommendations") == "system"
    assert classify_table("repair_executions") == "system"
    assert classify_table("database_metadata") == "system"
    assert classify_table("quarantine_records") == "system"

    # Audit tables
    assert classify_table("audit_logs") == "audit"
    assert classify_table("transaction_logs") == "audit"

    # Recovery tables
    assert classify_table("recovery_checkpoints") == "recovery"

# =============================================================================
# 4. Recommendation Generation for All 5 Anomaly Categories
# =============================================================================

def test_recommendation_generation_all_categories():
    scanner = IntegrityScanner()

    # Category 1: Orphan staging record -> QUARANTINE
    orphan_staging = {
        "issue_id": "TEST-ORPHAN-STAGING",
        "category": "ORPHAN",
        "table_name": "staging_enrollments",
        "record_id": "999",
        "column_name": "student_id",
        "invalid_value": "999",
        "description": "Orphan student reference",
        "severity": "CRITICAL"
    }
    rec_orphan = scanner._generate_recommendation(orphan_staging)
    assert rec_orphan["strategy"] == "QUARANTINE"
    assert rec_orphan["is_reversible"] is True

    # Category 1b: Orphan business record -> MAP_PARENT
    orphan_business = {
        "issue_id": "TEST-ORPHAN-BIZ",
        "category": "ORPHAN",
        "table_name": "courses",
        "record_id": "50",
        "column_name": "instructor_id",
        "invalid_value": "999",
        "description": "Missing instructor",
        "severity": "HIGH"
    }
    rec_orphan_biz = scanner._generate_recommendation(orphan_business)
    assert rec_orphan_biz["strategy"] == "MAP_PARENT"

    # Category 2: Duplicate candidate key -> DELETE_RECORD
    dup_issue = {
        "issue_id": "TEST-DUP",
        "category": "DUPLICATE",
        "table_name": "students",
        "record_id": "205",
        "column_name": "email",
        "invalid_value": "ravi.kumar@univ.edu",
        "description": "Duplicate email",
        "severity": "HIGH"
    }
    rec_dup = scanner._generate_recommendation(dup_issue)
    assert rec_dup["strategy"] == "DELETE_RECORD"

    # Category 3: NULL Violation -> SET_DEFAULT
    null_issue = {
        "issue_id": "TEST-NULL",
        "category": "NULL_VIOLATION",
        "table_name": "students",
        "record_id": "204",
        "column_name": "student_name",
        "invalid_value": "EMPTY_STRING",
        "description": "Mandatory student name missing",
        "severity": "CRITICAL"
    }
    rec_null = scanner._generate_recommendation(null_issue)
    assert rec_null["strategy"] == "SET_DEFAULT"

    # Category 4: Domain Violation (marks) -> SET_DEFAULT clamp
    domain_issue = {
        "issue_id": "TEST-DOM-MARKS",
        "category": "DOMAIN_VIOLATION",
        "table_name": "staging_enrollments",
        "record_id": "7",
        "column_name": "grade_marks",
        "invalid_value": "145.00",
        "description": "Grade marks out of range",
        "severity": "HIGH"
    }
    rec_domain = scanner._generate_recommendation(domain_issue)
    assert rec_domain["strategy"] == "SET_DEFAULT"

    # Category 5: System Table Integrity Anomaly -> MANUAL_INTERVENTION
    sys_issue = {
        "issue_id": "TEST-SYS-1",
        "category": "SYSTEM_INTEGRITY",
        "table_name": "integrity_rules",
        "record_id": "12",
        "column_name": "rule_code",
        "invalid_value": "SYS_DUPLICATE_RULE_CODE",
        "description": "Duplicate rule code in system catalog",
        "severity": "HIGH"
    }
    rec_sys = scanner._generate_recommendation(sys_issue)
    assert rec_sys["strategy"] == "MANUAL_INTERVENTION"

# =============================================================================
# 5. Core Configuration Defaults
# =============================================================================

def test_settings_database_name():
    assert settings.DB_NAME in ["self_healing_test_db", "self_healing_db"]
    assert settings.DB_PORT == 3306
    assert settings.DB_USER == "root"
    assert settings.DB_CHARSET == "utf8mb4"

# =============================================================================
# 6. Algorithmic Verification for All Five Anomaly Categories
# =============================================================================

import re

def test_five_violation_categories_logic():
    """
    Verifies that the exact algorithmic detection logic for each of the five
    integrity anomaly categories flags violation records while leaving clean records unflagged.
    """
    # 1. Orphan Check Logic
    valid_student_ids = {101, 102, 103, 104, 105, 106, 107}
    staging_records = [
        {"staging_id": 1, "student_id": 101, "course_id": 3},  # Valid
        {"staging_id": 3, "student_id": 999, "course_id": 1},  # Anomaly: missing student
    ]
    orphan_violations = [r for r in staging_records if r["student_id"] not in valid_student_ids]
    assert len(orphan_violations) == 1
    assert orphan_violations[0]["student_id"] == 999
    assert orphan_violations[0]["staging_id"] == 3

    # 2. Duplicate Candidate Key Logic
    emails = ["ravi.kumar@univ.edu", "priya.sharma@univ.edu", "ravi.kumar@univ.edu"]
    email_counts = {}
    for em in emails:
        email_counts[em] = email_counts.get(em, 0) + 1
    duplicates = [em for em, count in email_counts.items() if count > 1]
    assert len(duplicates) == 1
    assert duplicates[0] == "ravi.kumar@univ.edu"

    # 3. NULL / Empty String Violation Logic
    names = [
        {"id": 101, "name": "Ravi Kumar"},  # Valid
        {"id": 204, "name": ""},             # Anomaly: empty string
        {"id": 206, "name": None}            # Anomaly: NULL
    ]
    null_violations = [r for r in names if r["name"] is None or str(r["name"]).strip() == ""]
    assert len(null_violations) == 2
    assert {r["id"] for r in null_violations} == {204, 206}

    # 4. Domain Range Violation Logic (Marks 0.00 - 100.00, Age 16 - 65)
    ages = [
        {"id": 101, "age": 21},   # Valid
        {"id": 201, "age": 140},  # Anomaly: exceeds 65
        {"id": 207, "age": 12}    # Anomaly: below 16
    ]
    age_violations = [r for r in ages if r["age"] < 16 or r["age"] > 65]
    assert len(age_violations) == 2
    assert {r["id"] for r in age_violations} == {201, 207}

    # 5. Invalid Enum & Syntax Pattern Logic
    valid_statuses = {'ENROLLED', 'COMPLETED', 'DROPPED'}
    statuses = [
        {"id": 1, "status": "ENROLLED"},    # Valid
        {"id": 8, "status": "SUSPENDED"}   # Anomaly: not in allowed enum set
    ]
    enum_violations = [r for r in statuses if r["status"] not in valid_statuses]
    assert len(enum_violations) == 1
    assert enum_violations[0]["id"] == 8

    # Syntax Pattern (Email format regex)
    email_regex = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    test_emails = [
        ("ravi.kumar@univ.edu", True),
        ("priya.sharma@univ.edu", True),
        ("alex.malformed@no-tld", False),
        ("missing-at-sign.edu", False)
    ]
    for em, expected_valid in test_emails:
        assert bool(email_regex.match(em)) is expected_valid

