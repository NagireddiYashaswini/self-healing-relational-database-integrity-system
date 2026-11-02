"""
Database Setup Script for Self-Healing Relational Database Integrity System
Automatically provisions the MySQL database, tables, seed data, and integrity rules.
Works across Windows, macOS, and Linux without requiring the mysql CLI binary.
"""

import os
import sys
import getpass
import re
from pathlib import Path

# Try to import pymysql
try:
    import pymysql
    import pymysql.cursors
except ImportError:
    print("\n[!] PyMySQL is not installed. Please install dependencies first:")
    print("    pip install -r backend/requirements.txt\n")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
ENV_FILE = BACKEND_DIR / ".env"
ENV_EXAMPLE = BACKEND_DIR / ".env.example"
DATABASE_DIR = PROJECT_ROOT / "database"

SQL_FILES = [
    ("01_create_database.sql", "Creating database self_healing_test_db"),
    ("02_create_tables.sql", "Creating 16 InnoDB tables, constraints, and triggers"),
    ("03_insert_sample_data.sql", "Inserting baseline academic dataset"),
    ("04_integrity_rules.sql", "Seeding integrity rules catalog"),
    ("05_demo_violations.sql", "Injecting controlled demo anomalies for scanner")
]

def load_env(env_path: Path) -> dict:
    config = {
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "",
        "DB_NAME": "self_healing_test_db"
    }
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip().strip("'\"")
    return config

def save_env_password(env_path: Path, password: str):
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(env_path, "w", encoding="utf-8") as f:
        replaced = False
        for line in lines:
            if line.startswith("DB_PASSWORD="):
                f.write(f"DB_PASSWORD={password}\n")
                replaced = True
            else:
                f.write(line)
        if not replaced:
            f.write(f"DB_PASSWORD={password}\n")

def parse_sql_statements(sql_text: str) -> list:
    statements = []
    current = []
    delim = ";"
    for line in sql_text.splitlines():
        s = line.strip()
        if s.upper().startswith("DELIMITER"):
            parts = s.split()
            if len(parts) > 1:
                delim = parts[1]
            continue
        if not current and (s.startswith("--") or (s.startswith("/*") and s.endswith("*/"))):
            continue
        current.append(line)
        if s.endswith(delim):
            stmt = "\n".join(current)[:-len(delim)].strip()
            if stmt:
                statements.append(stmt)
            current = []
    if current:
        stmt = "\n".join(current).strip()
        if stmt:
            statements.append(stmt)
    return statements

def main():
    print("=" * 70)
    print(" Self-Healing Relational Database Integrity System - Setup Wizard")
    print("=" * 70)

    # 1. Ensure backend/.env exists
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            print("\n[+] Creating backend/.env from backend/.env.example...")
            ENV_FILE.write_text(ENV_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            print("\n[!] backend/.env.example not found.")

    env_config = load_env(ENV_FILE)
    host = env_config.get("DB_HOST", "127.0.0.1")
    port = int(env_config.get("DB_PORT", 3306))
    user = env_config.get("DB_USER", "root")
    password = env_config.get("DB_PASSWORD", "")
    db_name = env_config.get("DB_NAME", "self_healing_test_db")

    print(f"\nTarget Database Server: {host}:{port}")
    print(f"Target Database Name  : {db_name}")
    print(f"Database Username     : {user}")

    # 2. Test Connection to MySQL Server
    conn = None
    for attempt in range(3):
        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=5
            )
            break
        except pymysql.MySQLError as e:
            err_code = e.args[0] if e.args else 0
            err_msg = str(e)
            if err_code == 1045 or "Access denied" in err_msg:
                print(f"\n[!] MySQL access denied for '{user}' (password may be incorrect or blank).")
                try:
                    password = getpass.getpass("    Enter your MySQL root password: ")
                    save_env_password(ENV_FILE, password)
                except (KeyboardInterrupt, EOFError):
                    print("\nAborted.")
                    sys.exit(1)
            elif err_code == 2003 or "Can't connect to MySQL server" in err_msg:
                print("\n[X] Could not connect to MySQL server at 127.0.0.1:3306.")
                print("    Please ensure MySQL is running (e.g., start MySQL in XAMPP Control Panel).")
                sys.exit(1)
            else:
                print(f"\n[X] Database error: {e}")
                sys.exit(1)

    if not conn:
        print("\n[X] Failed to authenticate with MySQL server. Please verify credentials in backend/.env.")
        sys.exit(1)

    print("\n[V] Successfully connected to MySQL server!")

    # 3. Execute SQL Scripts
    try:
        with conn.cursor() as cur:
            for filename, description in SQL_FILES:
                sql_path = DATABASE_DIR / filename
                if not sql_path.exists():
                    print(f"\n[!] Missing file: {sql_path}")
                    sys.exit(1)

                print(f"[>] {description} ({filename})...")
                sql_content = sql_path.read_text(encoding="utf-8")
                statements = parse_sql_statements(sql_content)

                for stmt in statements:
                    cur.execute(stmt)

        # 4. Verify Final Database State
        with conn.cursor() as cur:
            cur.execute("USE `self_healing_test_db`;")
            cur.execute("SELECT COUNT(*) AS c FROM information_schema.tables WHERE table_schema = 'self_healing_test_db';")
            table_count = cur.fetchone()["c"]

            cur.execute("SHOW TABLES;")
            tables = [list(r.values())[0] for r in cur.fetchall()]

        print("\n" + "=" * 70)
        print(f"[SUCCESS] Database '{db_name}' initialized successfully with {table_count} tables!")
        print("=" * 70)
        print("Installed Tables:")
        for i, t in enumerate(tables, 1):
            print(f"  {i:2d}. {t}")
        print("\nYou can now start the backend and frontend:")
        print("  Backend : python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload")
        print("  Frontend: cd frontend && npm run dev")
        print("=" * 70)

    except Exception as e:
        print(f"\n[X] Failed during database initialization: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()

