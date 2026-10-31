import pytest
from backend.app.core.config import settings
from backend.app.database.connection import test_database_connection as check_db_conn, validate_identifier

def test_validate_identifier_safe():
    assert validate_identifier("students") == "students"
    assert validate_identifier("dept_name") == "dept_name"
    assert validate_identifier("staging_enrollments") == "staging_enrollments"

def test_validate_identifier_dangerous():
    with pytest.raises(ValueError):
        validate_identifier("students; DROP TABLE students;--")
    with pytest.raises(ValueError):
        validate_identifier("students WHERE 1=1")
    with pytest.raises(ValueError):
        validate_identifier("")

def test_mysql_connection_diagnostics(mysql_available):
    if not mysql_available:
        pytest.skip("Local MySQL server not reachable")
    status = check_db_conn()
    assert status["connected"] is True
    assert status["database_exists"] is True
    assert status["database_name"] == settings.DB_NAME
    assert status["table_count"] >= 10
