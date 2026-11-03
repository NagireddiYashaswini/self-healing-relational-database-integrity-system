import pytest
from datetime import datetime
from backend.app.services.ingestion_service import IngestionService, CORE_BUSINESS_TABLES
from backend.app.database.connection import get_connection

def test_ingestion_schema_retrieval(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    schema = IngestionService.get_table_schema("classrooms")
    assert schema["table_name"] == "classrooms"
    assert schema["staging_table"] == "staging_classrooms"
    assert len(schema["columns"]) > 0
    col_names = [c["name"] for c in schema["columns"]]
    assert "room_number" in col_names
    assert "building" in col_names
    assert "capacity" in col_names

def test_ingestion_schema_flags_db_generated_timestamp(mysql_available):
    """Verifies that timestamp columns with CURRENT_TIMESTAMP are detected and flagged."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    schema = IngestionService.get_table_schema("departments")
    cols_by_name = {c["name"]: c for c in schema["columns"]}
    
    assert "created_at" in cols_by_name
    assert cols_by_name["created_at"]["is_generated_default"] is True
    assert cols_by_name["dept_name"]["is_generated_default"] is False

def test_test1_and_test5_insert_department_without_created_at(mysql_available):
    """TEST 1 & TEST 5: Insert valid department without providing created_at -> auto timestamp generated in production."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    dept_code = "TST-DEP-01"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
        conn.commit()

        res = IngestionService.ingest_record(
            table_name="departments",
            record_data={
                "dept_code": dept_code,
                "dept_name": "Test Dept No Timestamp",
                "building": "North Wing",
                "budget": 250000.00
            },
            external_ref="EXT-TEST-01"
        )
        assert res["success"] is True
        assert res["status"] == "COMMITTED_TO_PRODUCTION"
        prod_pk = res["production_pk"]
        assert prod_pk is not None

        # Verify production record received automatic timestamp
        with conn.cursor() as cur:
            cur.execute("SELECT dept_id, dept_code, created_at FROM departments WHERE dept_id = %s", (prod_pk,))
            row = cur.fetchone()
            assert row is not None
            assert row["created_at"] is not None
            assert isinstance(row["created_at"], datetime)
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
        conn.commit()
        conn.close()

def test_test2_insert_department_with_explicit_valid_timestamp(mysql_available):
    """TEST 2: Insert valid department with explicit valid timestamp -> stored correctly."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    dept_code = "TST-DEP-02"
    explicit_ts = "2025-08-20 10:15:30"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
        conn.commit()

        res = IngestionService.ingest_record(
            table_name="departments",
            record_data={
                "dept_code": dept_code,
                "dept_name": "Test Dept Explicit TS",
                "building": "South Wing",
                "budget": 300000.00,
                "created_at": explicit_ts
            },
            external_ref="EXT-TEST-02"
        )
        assert res["success"] is True
        assert res["status"] == "COMMITTED_TO_PRODUCTION"
        prod_pk = res["production_pk"]

        with conn.cursor() as cur:
            cur.execute("SELECT dept_id, created_at FROM departments WHERE dept_id = %s", (prod_pk,))
            row = cur.fetchone()
            assert row is not None
            assert str(row["created_at"]) == explicit_ts
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
        conn.commit()
        conn.close()

def test_test3_and_test4_insert_with_literal_current_timestamp(mysql_available):
    """TEST 3 & TEST 4: Submit literal string CURRENT_TIMESTAMP -> not inserted as literal datetime string, omitted so DB default applies. Staging record receives timestamp automatically."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    dept_code = "TST-DEP-03"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
        conn.commit()

        # Ingestion with literal "CURRENT_TIMESTAMP" string (which previously caused 1292 error)
        res = IngestionService.ingest_record(
            table_name="departments",
            record_data={
                "dept_code": dept_code,
                "dept_name": "Test Dept Literal CURRENT_TIMESTAMP",
                "building": "West Wing",
                "budget": 180000.00,
                "created_at": "CURRENT_TIMESTAMP"
            },
            external_ref="EXT-TEST-03"
        )
        assert res["success"] is True
        assert res["status"] == "COMMITTED_TO_PRODUCTION"
        staging_id = res["staging_id"]
        prod_pk = res["production_pk"]

        # TEST 4: Verify staging record received timestamp automatically
        with conn.cursor() as cur:
            cur.execute("SELECT staging_id, imported_at, validation_status FROM staging_departments WHERE staging_id = %s", (staging_id,))
            stg_row = cur.fetchone()
            assert stg_row is not None
            assert stg_row["imported_at"] is not None
            assert isinstance(stg_row["imported_at"], datetime)
            assert stg_row["validation_status"] == "VALID"

        # Verify production record received valid DB default timestamp
        with conn.cursor() as cur:
            cur.execute("SELECT dept_id, created_at FROM departments WHERE dept_id = %s", (prod_pk,))
            prod_row = cur.fetchone()
            assert prod_row is not None
            assert prod_row["created_at"] is not None
            assert isinstance(prod_row["created_at"], datetime)
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
        conn.commit()
        conn.close()

def test_test6_invalid_department_rejected_and_quarantined(mysql_available):
    """TEST 6: Invalid department still rejected & quarantined correctly."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    dept_code = "TST-DEP-04"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
        conn.commit()

        res = IngestionService.ingest_record(
            table_name="departments",
            record_data={
                "dept_code": dept_code,
                "dept_name": "Negative Budget Department",
                "building": "East Wing",
                "budget": -99999.00,
                "created_at": "CURRENT_TIMESTAMP"
            },
            external_ref="EXT-TEST-04"
        )
        assert res["success"] is False
        assert res["status"] == "REJECTED_TO_QUARANTINE"
        assert res["quarantine_id"] is not None
        assert any("budget" in err.lower() for err in res["validation_errors"])

        # Check quarantine_records table
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM quarantine_records WHERE quarantine_id = %s", (res["quarantine_id"],))
            q_row = cur.fetchone()
            assert q_row is not None
            assert q_row["source_table"] == "staging_departments"
            assert "Negative Budget" in q_row["row_data_json"]

            # Verify production table was NOT mutated
            cur.execute("SELECT COUNT(*) as c FROM departments WHERE dept_code = %s", (dept_code,))
            assert cur.fetchone()["c"] == 0
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM departments WHERE dept_code = %s", (dept_code,))
            cur.execute("DELETE FROM staging_departments WHERE dept_code = %s", (dept_code,))
            if res.get("quarantine_id"):
                cur.execute("DELETE FROM quarantine_records WHERE quarantine_id = %s", (res["quarantine_id"],))
        conn.commit()
        conn.close()

def test_test7_works_across_all_six_tables(mysql_available):
    """TEST 7: Works dynamically across all 6 core business tables."""
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")

    assert len(CORE_BUSINESS_TABLES) == 6
    for tbl in CORE_BUSINESS_TABLES:
        schema = IngestionService.get_table_schema(tbl)
        assert schema["table_name"] == tbl
        assert schema["staging_table"] == f"staging_{tbl}"
        assert len(schema["columns"]) > 0

        # Verify any timestamp/datetime column with CURRENT_TIMESTAMP is flagged as is_generated_default
        for col in schema["columns"]:
            dt = (col["data_type"] or "").lower()
            dv = str(col["default_value"] or "").lower()
            if dt in ("timestamp", "datetime") and "current_timestamp" in dv:
                assert col["is_generated_default"] is True
