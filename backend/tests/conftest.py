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
    """Checks if XAMPP MySQL is active for integration tests."""
    status = test_database_connection()
    return status.get("connected", False)
