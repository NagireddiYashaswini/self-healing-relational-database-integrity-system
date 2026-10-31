import pymysql
import pymysql.cursors
import time
import re
from typing import Generator, Dict, Any, Optional, List
from contextlib import contextmanager
from backend.app.core.config import settings

# Allowed identifiers pattern to strictly prevent SQL injection in metadata inspection
IDENTIFIER_REGEX = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

def validate_identifier(name: str) -> str:
    """Strictly validates SQL identifier (table/column name) against allowlist pattern."""
    if not name or not IDENTIFIER_REGEX.match(name):
        raise ValueError(f"Invalid SQL identifier: {name}")
    return name

def get_connection(use_database: bool = True) -> pymysql.Connection:
    """Creates a new PyMySQL connection with dictionary cursor and autocommit=False."""
    return pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME if use_database else None,
        charset=settings.DB_CHARSET,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=5
    )

@contextmanager
def get_db_cursor(commit_on_exit: bool = False) -> Generator[pymysql.cursors.DictCursor, None, None]:
    """Context manager for obtaining a database cursor with safe resource reclamation."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
        if commit_on_exit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def test_database_connection() -> Dict[str, Any]:
    """
    Tests database connection and server status.
    Returns detailed diagnostics including latency, version, and database presence.
    """
    start_time = time.time()
    try:
        # Step 1: Connect to server without database
        server_conn = get_connection(use_database=False)
        with server_conn.cursor() as cur:
            cur.execute("SELECT VERSION() AS version, CURRENT_USER() AS user;")
            server_info = cur.fetchone()
        server_conn.close()

        # Step 2: Test specific database presence and table count
        db_conn = get_connection(use_database=True)
        with db_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = %s;", (settings.DB_NAME,))
            res = cur.fetchone()
            table_count = res["table_count"] if res else 0

            # Fetch table names
            cur.execute("SHOW TABLES;")
            tables = [list(row.values())[0] for row in cur.fetchall()]

        db_conn.close()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "connected": True,
            "database_exists": True,
            "database_name": settings.DB_NAME,
            "server_version": server_info["version"] if server_info else "Unknown",
            "connected_user": server_info["user"] if server_info else settings.DB_USER,
            "table_count": table_count,
            "tables": tables,
            "latency_ms": latency_ms,
            "message": "Successfully connected to XAMPP MySQL database."
        }
    except pymysql.MySQLError as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        err_msg = str(e)
        if "Access denied" in err_msg:
            hint = "Authentication failed. Please verify DB_USER and DB_PASSWORD in backend/.env"
        elif "Can't connect to MySQL server" in err_msg:
            hint = "Could not reach MySQL server. Ensure XAMPP Control Panel has MySQL started on port 3306."
        elif "Unknown database" in err_msg:
            hint = f"Database '{settings.DB_NAME}' does not exist. Please run database/01_create_database.sql."
        else:
            hint = "Check MySQL service and connection credentials."

        return {
            "connected": False,
            "database_exists": False,
            "database_name": settings.DB_NAME,
            "server_version": None,
            "connected_user": settings.DB_USER,
            "table_count": 0,
            "tables": [],
            "latency_ms": latency_ms,
            "error": err_msg,
            "hint": hint,
            "message": f"Connection failed: {hint}"
        }
