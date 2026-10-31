# Self-Healing Relational Database Integrity System

[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B%20%7C%20MariaDB-blue.svg?logo=mysql)](https://www.mysql.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB.svg?logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg?logo=vite)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/pytest-22%20passed-brightgreen.svg)]()

> A full-stack academic DBMS project implementing an autonomous, transaction-safe database integrity detection, dependency analysis, self-healing, and audit traceability engine for MySQL InnoDB.

---

## 1. Project Abstract & Objectives
Relational database management systems rely heavily on declarative constraints, primary keys, and foreign keys to ensure data integrity. However, in practice, bulk staging imports, partial ETL runs, accidental administrator actions, and unconstrained legacy tables regularly introduce **orphan records**, **duplicate candidate keys**, **null value breaches**, and **domain range violations**.

This project delivers a **Self-Healing Relational Database Integrity System** that:
- Inspects database schema metadata dynamically via `INFORMATION_SCHEMA`.
- Maps relational table dependencies as a directed graph using `NetworkX` to detect cycles and calculate cascading repair blast radius.
- Recommends structured, non-destructive self-healing strategies (parent mapping, default values, quarantine, and safe removal).
- Executes repairs inside genuine **MySQL InnoDB ACID transactions** (`BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`) with pre-repair recovery checkpoints and automated rollback on failure.
- Maintains an immutable, redacted audit trail of all scans, approvals, and transaction outcomes.

---

## 2. Technology Stack

### Frontend
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS (Dark Glassmorphism Theme)
- **Routing:** React Router v6
- **Data Visualization:** Recharts (Severity Pie Chart, Category Bar Chart)
- **Icons:** Lucide React
- **HTTP Client:** Axios with backend proxy

### Backend
- **Framework:** Python 3.13, FastAPI, Uvicorn
- **Database Driver:** PyMySQL with dictionary cursor & connection pooling
- **Schema Validation:** Pydantic v2 & Pydantic-Settings
- **Graph Algorithms:** NetworkX (Directed Graph, Cycle Detection, Topological Sort)
- **Testing:** Pytest & HTTPX TestClient

### Database
- **Engine:** MySQL 8.0+ / MariaDB 10.4+ supplied via local **XAMPP**
- **Storage Engine:** InnoDB (Full ACID transaction & Foreign Key enforcement)
- **Administration:** phpMyAdmin and MySQL command-line client

---

## 3. Directory Structure

```
DBMS PROJECT/
├── backend/
│   ├── app/
│   │   ├── api/                 # REST endpoints (database, scans, issues, repairs, etc.)
│   │   ├── core/                # Environment configuration (Pydantic settings)
│   │   ├── database/            # PyMySQL connection pool, diagnostics, allowlist validator
│   │   ├── models/              # Pydantic schemas and request/response models
│   │   ├── services/
│   │   │   ├── integrity_scanner.py     # Real metadata scanner & rule evaluator
│   │   │   ├── dependency_analyzer.py   # NetworkX directed graph & blast radius
│   │   │   ├── repair_engine.py         # Safe repair proposals, previews & ACID execution
│   │   │   ├── transaction_manager.py   # Transaction simulator (Commit, Rollback, Savepoint)
│   │   │   ├── recovery_manager.py      # Table snapshot checkpoints & restoration
│   │   │   └── audit_service.py         # Traceability logging with credential redaction
│   │   └── main.py              # FastAPI application entry point with CORS & error handlers
│   ├── tests/                   # 22 automated test cases with pytest
│   ├── requirements.txt         # Backend Python dependencies
│   ├── .env                     # Local environment settings
│   └── .env.example             # Template environment configuration
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/          # Badges, Buttons, StatCards, Modals, ConfirmDialogs
│   │   │   └── graph/           # Interactive Relational Dependency Graph (SVG canvas)
│   │   ├── layouts/             # AppLayout with responsive sidebar & top navbar
│   │   ├── pages/               # 11 complete dashboard views
│   │   ├── services/            # Axios API service client
│   │   ├── App.jsx              # React Router configuration
│   │   ├── main.jsx             # React DOM root
│   │   └── index.css            # Tailwind directives & glassmorphic styles
│   ├── public/                  # SVG assets & logos
│   ├── package.json             # Frontend Node dependencies
│   └── vite.config.js           # Vite dev server & backend API proxy
│
├── database/
│   ├── 01_create_database.sql   # Database initialization (utf8mb4, InnoDB)
│   ├── 02_create_tables.sql     # Academic business, staging, quarantine & system schemas
│   ├── 03_insert_sample_data.sql# Clean baseline relational data
│   ├── 04_integrity_rules.sql   # Predefined integrity rules (orphans, duplicates, domains)
│   ├── 05_demo_violations.sql   # Controlled anomaly injection for demonstration
│   ├── 06_test_queries.sql      # Manual verification queries
│   ├── 07_reset_demo_data.sql   # Safe baseline data reset script
│   └── README.md                # Detailed database import instructions
│
├── docs/
│   ├── architecture.md          # Architectural diagrams & module breakdown
│   ├── database_schema.md       # Complete schema definitions & dictionary
│   ├── api_documentation.md     # REST API endpoint reference
│   ├── testing.md               # Automated tests & end-to-end verification checklist
│   └── project_report.md        # Complete academic DBMS group project report
│
├── .gitignore                   # Git ignore configuration
└── README.md                    # Project master documentation
```

---

## 4. Setup & Installation Instructions

### Prerequisites
1. **XAMPP** installed with MySQL service running on port 3306.
2. **Python 3.10+** (Python 3.13 tested).
3. **Node.js 18+** & **npm** installed.

---

### Step 1: Database Setup via XAMPP MySQL
Ensure MySQL is started in your XAMPP Control Panel.

#### Option A: Import via MySQL Command Line Client (PowerShell)
```powershell
cd "c:\Users\Sridevinivas\Documents\DBMS PROJECT"

# Execute SQL scripts sequentially:
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -proot123 -h 127.0.0.1 < database\01_create_database.sql"
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -proot123 -h 127.0.0.1 self_healing_db < database\02_create_tables.sql"
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -proot123 -h 127.0.0.1 self_healing_db < database\03_insert_sample_data.sql"
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -proot123 -h 127.0.0.1 self_healing_db < database\04_integrity_rules.sql"
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -proot123 -h 127.0.0.1 self_healing_db < database\05_demo_violations.sql"
```

#### Option B: Import via phpMyAdmin GUI
1. Open `http://localhost/phpmyadmin/` in your browser.
2. Click **Import** and upload `database/01_create_database.sql`.
3. Select `self_healing_db` from the left sidebar.
4. Sequentially import `02_create_tables.sql`, `03_insert_sample_data.sql`, `04_integrity_rules.sql`, and `05_demo_violations.sql`.

---

### Step 2: Backend Setup & Startup
1. Open a terminal in the project directory:
   ```powershell
   cd "c:\Users\Sridevinivas\Documents\DBMS PROJECT"
   ```
2. Verify or update `backend/.env` with your XAMPP credentials:
   ```ini
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_NAME=self_healing_db
   DB_USER=root
   DB_PASSWORD=root123
   DB_CHARSET=utf8mb4
   FRONTEND_ORIGIN=http://localhost:5173
   DEBUG=True
   ```
3. Install backend dependencies:
   ```powershell
   pip install -r backend/requirements.txt
   ```
4. Run automated test suite:
   ```powershell
   pytest backend/tests -v
   ```
5. Start the FastAPI development server:
   ```powershell
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *FastAPI Interactive Docs will be accessible at:* `http://localhost:8000/docs`

---

### Step 3: Frontend Setup & Startup
1. Open a new terminal in the project directory:
   ```powershell
   cd "c:\Users\Sridevinivas\Documents\DBMS PROJECT\frontend"
   ```
2. Install frontend dependencies:
   ```powershell
   npm install
   ```
3. Start the Vite React development server:
   ```powershell
   npm run dev
   ```
   *The web application dashboard will be live at:* `http://localhost:5173`

---

## 5. Step-by-Step Demonstration Script

### Walkthrough Scenario for Examiners & Evaluators:
1. **System Health & Dashboard (`/`)**:
   - Verify that the database indicator shows **MySQL Connected** (`10.4.28-MariaDB`), with 16 tables discovered and active latency.
   - Review live metrics, severity breakdown pie chart, and category bar chart.
2. **Database Explorer (`/explorer`)**:
   - Inspect table schemas. Click **Inspect Schema** on `courses` to inspect columns, data types, primary keys, and foreign keys.
   - Switch to **Sample Data** to view live rows queried directly from MySQL.
3. **Integrity Scanner (`/scanner`)**:
   - Click **Run Scan Now** to trigger a real scan.
   - The scanner evaluates the active rules against `INFORMATION_SCHEMA` and detects the 9 seeded violations across orphan enrollments, duplicate emails, and out-of-range marks.
4. **Issue Management (`/issues`)**:
   - Filter by `Severity: Critical` or `Category: Orphan`.
   - Click **Inspect** to see the raw database row data.
   - Click **Mark Reviewed** to update the issue lifecycle.
5. **Dependency Graph Visualizer (`/dependencies`)**:
   - Observe the interactive directed dependency graph.
   - Select the `courses` table to highlight parent entities (`departments`, `instructors`) and child entities (`enrollments`).
   - View the calculated **Blast Radius** and verify that no circular dependencies exist.
6. **Self-Healing Repair Center (`/repairs`)**:
   - Locate the orphan staging enrollment recommendation.
   - Click **Preview & Execute**.
   - Review the before/after state diff, generated SQL statement, and child dependency check.
   - Click **Execute Transaction Safe Repair**.
   - The engine takes a pre-repair checkpoint, executes the change within an InnoDB transaction, verifies data consistency, commits, and logs the execution.
7. **Transaction Simulator (`/simulator`)**:
   - Select **Failure Simulation & Atomic Rollback**.
   - Click **Run Real Scenario**.
   - Watch the step timeline: `START TRANSACTION` ➔ `INSERT` ➔ `SIMULATED FAILURE` ➔ `ROLLBACK`.
   - Confirm that the database row count remains unchanged, proving true ACID atomicity!
8. **Recovery Center (`/recovery`)**:
   - Review the automatic snapshot checkpoints captured prior to repairs.
   - Click **Create Checkpoint** on `students` to take a manual snapshot.
   - Click **Restore State** to verify that data can be cleanly re-applied via an atomic upsert transaction.
9. **Audit Logs (`/audit`)**:
   - Review the searchable event timeline.
   - Click **Inspect** on any event to see the exact before/after JSON states with passwords and tokens safely redacted.
10. **Rules Configuration (`/rules`)**:
    - Click **Test** on any rule to dry-run the detection logic against current database records in real-time.

---

## 6. Academic Deliverables
For comprehensive academic documentation, refer to the `docs/` folder:
- [System Architecture](file:///docs/architecture.md)
- [Database Schema Specification](file:///docs/database_schema.md)
- [REST API Reference](file:///docs/api_documentation.md)
- [Testing Verification Report](file:///docs/testing.md)
- [Complete Academic Project Report](file:///docs/project_report.md)
