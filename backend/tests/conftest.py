import pytest
import os
import sys
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from backend.app.database.connection import test_database_connection

@pytest.fixture(scope="session")
def client():
    """Provides a TestClient for FastAPI routes."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="session")
def mysql_available():
    """Checks if XAMPP MySQL is active and the target database exists for integration tests."""
    try:
        status = test_database_connection()
        return bool(status.get("connected") and status.get("database_exists"))
    except Exception:
        return False
