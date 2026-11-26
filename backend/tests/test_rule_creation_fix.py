import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.connection import get_connection

client = TestClient(app)

def cleanup_rule(rule_code: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM integrity_rules WHERE rule_code = %s", (rule_code,))
        conn.commit()
    finally:
        conn.close()

def test_create_rule_numeric_code_52():
    """Test Case 1: Create rule with numeric code '52'"""
    rule_code = "52"
    cleanup_rule(rule_code)

    payload = {
        "rule_code": rule_code,
        "name": "Test Numeric Rule 52",
        "description": "Validates numeric rule code 52 support",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "gpa",
        "parameters_json": {"min_value": 0.0, "max_value": 4.0},
        "severity": "HIGH",
        "is_enabled": True
    }

    try:
        response = client.post("/api/rules", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["data"]["rule_code"] == "52"

        # Verify in database
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM integrity_rules WHERE rule_code = %s", (rule_code,))
                row = cur.fetchone()
                assert row is not None
                assert row["rule_code"] == "52"
                assert row["target_table"] == "students"
                assert row["target_column"] == "gpa"
        finally:
            conn.close()
    finally:
        cleanup_rule(rule_code)

def test_create_rule_alphanumeric_code():
    """Test Case 2: Create rule with alphanumeric code 'RULE_STUDENT_GPA'"""
    rule_code = "RULE_STUDENT_GPA"
    cleanup_rule(rule_code)

    payload = {
        "rule_code": rule_code,
        "name": "Student GPA Verification",
        "description": "Validates that student GPA is within allowable academic bounds",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "gpa",
        "parameters_json": {"min_value": 0.0, "max_value": 4.0},
        "severity": "CRITICAL",
        "is_enabled": True
    }

    try:
        response = client.post("/api/rules", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert data["data"]["rule_code"] == "RULE_STUDENT_GPA"

        # Verify in database
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM integrity_rules WHERE rule_code = %s", (rule_code,))
                row = cur.fetchone()
                assert row is not None
                assert row["rule_code"] == "RULE_STUDENT_GPA"
                assert row["target_table"] == "students"
                assert row["target_column"] == "gpa"
        finally:
            conn.close()
    finally:
        cleanup_rule(rule_code)

def test_reject_invalid_table_identifier():
    """Test Case 3: Verify invalid target table identifier is rejected safely"""
    payload = {
        "rule_code": "RULE_INVALID_TABLE_TEST",
        "name": "Invalid Table Test",
        "description": "Testing rejection of non-existent or invalid table",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "nonexistent_table_xyz",
        "target_column": "student_id",
        "severity": "LOW",
        "is_enabled": True
    }
    response = client.post("/api/rules", json=payload)
    assert response.status_code == 400
    res_data = response.json()
    err_text = res_data.get("message") or res_data.get("error") or ""
    assert "does not exist in the database" in err_text or "Invalid SQL identifier" in err_text

    # Test SQL injection in table name
    payload["target_table"] = "students; DROP TABLE students;--"
    response = client.post("/api/rules", json=payload)
    assert response.status_code == 400
    res_data = response.json()
    err_text = res_data.get("message") or res_data.get("error") or ""
    assert "Invalid SQL identifier" in err_text

def test_reject_invalid_column_identifier():
    """Test Case 4: Verify invalid column identifier is rejected safely"""
    payload = {
        "rule_code": "RULE_INVALID_COL_TEST",
        "name": "Invalid Column Test",
        "description": "Testing rejection of non-existent column",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "non_existent_column_123",
        "severity": "LOW",
        "is_enabled": True
    }
    response = client.post("/api/rules", json=payload)
    assert response.status_code == 400
    res_data = response.json()
    err_text = res_data.get("message") or res_data.get("error") or ""
    assert "does not exist in table 'students'" in err_text

def test_reject_duplicate_rule_code():
    """Test Case 5: Verify duplicate rule code produces a clear, meaningful error"""
    rule_code = "RULE_DUP_TEST_CODE"
    cleanup_rule(rule_code)

    payload = {
        "rule_code": rule_code,
        "name": "Original Rule",
        "description": "First instance",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "gpa",
        "severity": "MEDIUM",
        "is_enabled": True
    }

    try:
        # First creation succeeds
        res1 = client.post("/api/rules", json=payload)
        assert res1.status_code == 200

        # Second creation with identical rule_code must fail with clear duplicate error
        payload["name"] = "Second Instance"
        res2 = client.post("/api/rules", json=payload)
        assert res2.status_code == 400
        res2_data = res2.json()
        err_text = res2_data.get("message") or res2_data.get("error") or ""
        assert f"Rule code '{rule_code}' already exists" in err_text
    finally:
        cleanup_rule(rule_code)

def test_data_ingestion_resilience():
    """Verify ingestion succeeds without column validation_status errors"""
    from backend.app.services.ingestion_service import IngestionService
    # Ingest a valid student
    res = IngestionService.ingest_record(
        table_name="students",
        record_data={
            "student_name": "Test Ingestion Resilient",
            "email": "resilient.student@univ.edu",
            "age": 22,
            "gpa": 3.75,
            "dept_id": 1,
            "enrollment_year": 2024
        },
        external_ref="EXT-RESILIENT",
        operator="ADMIN_USER"
    )
    assert res["success"] is True
    assert res["status"] == "COMMITTED_TO_PRODUCTION"

    # Cleanup inserted record
    prod_id = res["production_pk"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE student_id = %s", (prod_id,))
        conn.commit()
    finally:
        conn.close()
