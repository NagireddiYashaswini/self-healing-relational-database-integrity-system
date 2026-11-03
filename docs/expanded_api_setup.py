"""
Chapter 15 and 17 Expanded Technical Specifications
Provides exhaustive REST API contracts, JSON payloads, and setup troubleshooting guides.
"""

def get_chapter15_sections():
    api_table = [
        ["Method", "Endpoint URI", "Category", "Request Body / Params", "Success Response Type"],
        ["GET", "/api/health", "System", "None", "HealthStatusSchema (status, latency_ms, db)"],
        ["GET", "/api/database/status", "Database", "None", "DbStatusSchema (tables, total_rows, engine)"],
        ["GET", "/api/database/tables", "Database", "None", "List[str] (all active table names)"],
        ["GET", "/api/database/tables/{table}/schema", "Database", "Path: table name", "List[ColumnMetadataSchema]"],
        ["GET", "/api/database/tables/{table}/data", "Database", "Query: limit=50, offset=0", "PaginatedDataSchema (rows, total, page)"],
        ["GET", "/api/dependencies/graph", "Topology", "None", "GraphTopologySchema (nodes, edges)"],
        ["GET", "/api/dependencies/cycles", "Topology", "None", "CycleReportSchema (has_cycle, cycles)"],
        ["POST", "/api/scanner/run", "Scanner", "ScanRequest (scope, table_name, rules)", "ScanResultSchema (run_id, issues_found)"],
        ["GET", "/api/scanner/runs", "Scanner", "Query: limit=20", "List[ScanRunSummarySchema]"],
        ["GET", "/api/scanner/runs/{run_id}", "Scanner", "Path: run_id", "ScanRunDetailSchema (issues, duration)"],
        ["GET", "/api/issues", "Triage", "Query: status, severity, table", "List[IntegrityIssueSchema]"],
        ["GET", "/api/issues/{id}", "Triage", "Path: issue_id", "IntegrityIssueDetailSchema (raw_row, rule)"],
        ["PATCH", "/api/issues/{id}", "Triage", "IssueUpdate (status, notes)", "IntegrityIssueSchema"],
        ["POST", "/api/repairs/preview", "Repair", "RepairPreviewRequest (issue_id, strategy)", "RepairPreviewSchema (before, after, hash)"],
        ["POST", "/api/repairs/execute", "Repair", "RepairExecuteRequest (issue_id, hash, actor)", "RepairExecutionResult (success, rows_affected)"],
        ["POST", "/api/transactions/simulate", "ACID Lab", "SimulationRequest (scenario_type)", "SimulationResult (steps, verified)"],
        ["GET", "/api/recovery/checkpoints", "Recovery", "Query: table_name", "List[CheckpointSchema]"],
        ["POST", "/api/recovery/checkpoints", "Recovery", "CreateCheckpointRequest (table_name, label)", "CheckpointSchema (id, row_count)"],
        ["POST", "/api/recovery/restore", "Recovery", "RestoreRequest (checkpoint_id)", "RestoreResultSchema (restored_rows, verified)"],
        ["GET", "/api/audit/logs", "Compliance", "Query: limit=50, event_type, actor", "List[AuditEntrySchema]"],
        ["GET", "/api/rules", "Policy", "None", "List[IntegrityRuleSchema]"],
        ["POST", "/api/rules/{id}/dry-run", "Policy", "Path: rule_id", "DryRunResultSchema (violation_count)"],
        ["POST", "/api/settings/inject-demo", "Lab", "None", "ActionStatus (injected_count, status)"],
        ["POST", "/api/settings/reset-baseline", "Lab", "None", "ActionStatus (reset_count, status)"]
    ]

    sections = [
        {
            "title": "15.1 Standardized RESTful Response Architecture & Envelope Pattern",
            "paragraphs": [
                "To ensure strict predictability and type safety across all frontend components, the FastAPI backend wraps every HTTP response in a standardized JSON envelope.",
                "Regardless of whether an endpoint delivers a scalar health metric, a graph topology payload, or a tabular schema dictionary, the payload structure adheres to the following formal contract:",
                "1. `success` (Boolean): Master execution indicator denoting whether the relational operation completed without unhandled exceptions.",
                "2. `data` (T | None): Generic typed payload containing the queried domain entity or mutation result. Evaluates to null on errors.",
                "3. `message` (String): Human-readable operational message describing the outcome of the request.",
                "4. `timestamp` (ISO-8601 String): High-precision UTC timestamp recording the moment of response generation on the backend server.",
                "5. `error_code` (String | Optional): Standardized error identifier (e.g., `CONCURRENCY_TOKEN_MISMATCH`, `REFERENTIAL_CASCADE_BLOCK`) provided during non-200 responses."
            ]
        },
        {
            "title": "15.2 The Comprehensive Catalog of All 24 REST Endpoints",
            "paragraphs": [
                "The table below documents every REST API route exposed by the FastAPI server, detailing HTTP verbs, URIs, operational categories, and payload contracts:"
            ],
            "table": {"data": api_table, "widths": [50, 150, 60, 130, 110]}
        },
        {
            "title": "15.3 Critical Mutation Contract: Automated Scan Dispatch (`POST /api/scanner/run`)",
            "paragraphs": [
                "This endpoint initiates a multi-threaded integrity scan across the relational schema. It accepts parameters specifying whether to scan all tables or target an individual relation.",
                "Below is the exact JSON request payload and corresponding successful response structure:"
            ],
            "code": (
                "-- Scan Trigger Request Payload (JSON)\n"
                "{\n"
                '  "scope": "ALL",\n'
                '  "target_table": null,\n'
                '  "enabled_rules": ["ORPHAN_ENROLLMENT_STUDENT", "NULL_STUDENT_EMAIL", "DOMAIN_STUDENT_AGE"]\n'
                "}\n\n"
                "-- Scan Response Payload (HTTP 200 OK)\n"
                "{\n"
                '  "success": true,\n'
                '  "data": {\n'
                '    "run_id": 42,\n'
                '    "scan_type": "FULL_SCHEMA",\n'
                '    "total_tables_scanned": 16,\n'
                '    "total_rows_examined": 1420,\n'
                '    "issues_detected": 11,\n'
                '    "duration_ms": 38.45,\n'
                '    "completed_at": "2026-11-03T00:15:22.104Z"\n'
                "  },\n"
                '  "message": "Full schema integrity scan completed successfully."\n'
                "}"
            )
        },
        {
            "title": "15.4 High-Safety Repair Preview Contract (`POST /api/repairs/preview`)",
            "paragraphs": [
                "Prior to applying any database mutation, the frontend must request a non-destructive repair preview. "
                "The backend evaluates the repair strategy, generates the parameter-bound SQL statement, captures the before/after state, "
                "and computes the SHA-256 row-version concurrency hash."
            ],
            "code": (
                "-- Repair Preview Request (JSON)\n"
                "{\n"
                '  "issue_id": 14,\n'
                '  "strategy": "SET_DEFAULT",\n'
                '  "custom_value": null\n'
                "}\n\n"
                "-- Repair Preview Response with Concurrency Token (HTTP 200 OK)\n"
                "{\n"
                '  "success": true,\n'
                '  "data": {\n'
                '    "issue_id": 14,\n'
                '    "target_table": "students",\n'
                '    "primary_key_val": 105,\n'
                '    "strategy": "SET_DEFAULT",\n'
                '    "current_value": "NOT_AN_EMAIL",\n'
                '    "proposed_value": "student_105@university.edu",\n'
                '    "preview_sql": "UPDATE students SET email = %s, updated_at = NOW() WHERE student_id = %s",\n'
                '    "blast_radius_tables": ["students", "enrollments"],\n'
                '    "risk_level": "LOW",\n'
                '    "expected_row_hash": "a1f9c832e65d2140bb7190e2f18392d449ac019482f34812f8490a1827498c11"\n'
                "  },\n"
                '  "message": "Repair preview synthesized with valid concurrency token."\n'
                "}"
            )
        },
        {
            "title": "15.5 Atomic Repair Execution Contract (`POST /api/repairs/execute`)",
            "paragraphs": [
                "The execution contract enforces strict concurrency controls. If another concurrent process has updated the record in the interim, "
                "the SHA-256 hash recalculation fails, returning HTTP 409 Conflict and aborting the transaction."
            ],
            "code": (
                "-- Repair Execution Request (JSON)\n"
                "{\n"
                '  "issue_id": 14,\n'
                '  "strategy": "SET_DEFAULT",\n'
                '  "expected_row_hash": "a1f9c832e65d2140bb7190e2f18392d449ac019482f34812f8490a1827498c11",\n'
                '  "actor": "ADMIN_OPERATOR"\n'
                "}\n\n"
                "-- Repair Execution Response (HTTP 200 OK)\n"
                "{\n"
                '  "success": true,\n'
                '  "data": {\n'
                '    "repair_log_id": 8,\n'
                '    "issue_id": 14,\n'
                '    "rows_affected": 1,\n'
                '    "status": "SUCCESS",\n'
                '    "restoration_token": "RESTORE_14_20261103_0015",\n'
                '    "audit_event_id": 104\n'
                "  },\n"
                '  "message": "Atomic database repair executed successfully and committed."\n'
                "}"
            )
        }
    ]
    return sections

def get_chapter17_sections():
    diag_table = [
        ["Diagnostic Symptom", "Probable Root Cause", "Investigative Command", "Remediation Procedure"],
        ["MySQL Connection Refused (10061)", "MySQL daemon is stopped or port blocked.", "netstat -ano | findstr 3306", "Start MySQL via XAMPP Control Panel or 'net start MySQL'."],
        ["Access Denied for 'root'@'localhost'", "MySQL root has a configured password.", "Check C:/xampp/phpMyAdmin/config.inc.php", "Set DB_PASSWORD in backend/.env to match local credential."],
        ["ModuleNotFoundError: pymysql", "Virtualenv missing required Python packages.", "pip list | findstr pymysql", "Execute 'pip install -r backend/requirements.txt'."],
        ["Vite: ECONNREFUSED :8000", "FastAPI backend server is not running.", "curl http://localhost:8000/api/health", "Launch backend via 'uvicorn backend.main:app --reload --port 8000'."],
        ["Vite Port 5173 In Use", "Previous node process still holds port.", "netstat -ano | findstr 5173", "Terminate orphan process via 'taskkill /PID <PID> /F' or use --port 5174."]
    ]

    sections = [
        {
            "title": "17.1 System Hardware & Software Prerequisites",
            "paragraphs": [
                "Before initiating local deployment, verify that the host machine satisfies the following engineering baseline specifications:",
                "1. Database Engine: MySQL Community Server 8.0+ or MariaDB 10.4+ (e.g., standard XAMPP or standalone installer) running on port 3306.",
                "2. Backend Runtime: Python 3.10, 3.11, 3.12, or 3.13 (with `pip` and standard development headers).",
                "3. Frontend Toolchain: Node.js 18.0+ or 20.0+ LTS along with `npm` (Node Package Manager).",
                "4. Operating System: Windows 10/11, macOS Sonoma/Sequoia, or Ubuntu Linux 22.04/24.04 LTS."
            ]
        },
        {
            "title": "17.2 The 1-Click Automated Setup Wizard (`setup_database.py`)",
            "paragraphs": [
                "To eliminate manual configuration errors and ensure that even non-technical evaluators can bootstrap the entire system in under 60 seconds, "
                "the project includes an automated setup script: `setup_database.py`.",
                "When executed via `python setup_database.py`, the script performs the following sequential automation pipeline:",
                "Step 1: Environment Discovery: Inspects `backend/.env` for host, user, password, and port settings. If absent, it queries default local root configurations.",
                "Step 2: Database Provisioning: Connects to the MySQL instance and executes `CREATE DATABASE IF NOT EXISTS self_healing_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci`.",
                "Step 3: Sequential SQL Script Execution: In topological foreign-key order, the wizard reads and executes:",
                "  - `01_create_database.sql`: Provisions all 16 InnoDB relational and telemetry tables.",
                "  - `02_seed_baseline_data.sql`: Populates valid academic entities (departments, instructors, courses, students, enrollments).",
                "  - `03_seed_rules.sql`: Registers the 16 active integrity validation rules.",
                "  - `04_create_audit_triggers.sql`: Compiles native MySQL `BEFORE UPDATE` and `BEFORE DELETE` immutability triggers.",
                "  - `05_demo_violations.sql`: Creates sandbox staging anomalies for immediate testing.",
                "Step 4: Verification Check: Queries `INFORMATION_SCHEMA.TABLES` to ensure all 16 tables exist and reports total record counts."
            ]
        },
        {
            "title": "17.3 Manual Step-by-Step Command Line Deployment Guide",
            "paragraphs": [
                "For developers who prefer granular terminal control, execute the following commands in separate shells to launch the application stack:"
            ],
            "code": (
                "# Terminal 1: Backend Setup & Server Launch\n"
                "cd self-healing-relational-database-integrity-system\n"
                "python -m venv venv\n"
                ".\\venv\\Scripts\\activate            # On macOS/Linux: source venv/bin/activate\n"
                "pip install -r backend/requirements.txt\n"
                "python setup_database.py           # Automated schema & data initialization\n"
                "uvicorn backend.main:app --reload --port 8000\n\n"
                "# Terminal 2: Frontend Setup & Dev Server Launch\n"
                "cd self-healing-relational-database-integrity-system/frontend\n"
                "npm install\n"
                "npm run dev\n"
                "# Open browser at http://localhost:5173"
            )
        },
        {
            "title": "17.4 Comprehensive Diagnostic & Troubleshooting Reference Matrix",
            "paragraphs": [
                "The matrix below outlines common development environment issues, diagnostic checks, and proven remediation procedures:"
            ],
            "table": {"data": diag_table, "widths": [110, 110, 130, 150]}
        }
    ]
    return sections

