"""
Massive Chapter Data Builder
Generates an extensive, publication-grade academic report content file
designed to reach ~50 pages in PDF format.
"""

import sys
from pathlib import Path

# Import the base structure
import report_chapters

def expand():
    chapters = report_chapters.get_all_chapters()
    
    # -------------------------------------------------------------------------
    # 1. Expand Chapter 4 (All 16 Tables with full technical profiles)
    # -------------------------------------------------------------------------
    ch4 = chapters[3] # Chapter 4
    
    table_profiles = [
        ("departments", "Academic department organizational unit", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["dept_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate primary identifier for department."],
            ["dept_code", "VARCHAR(20) NOT NULL", "UNIQUE", "Human-readable unique code (e.g., 'CS', 'EE')."],
            ["dept_name", "VARCHAR(100) NOT NULL", "UNIQUE", "Full official academic department name."],
            ["building", "VARCHAR(100) NULL", "None", "Physical campus building location."],
            ["budget", "DECIMAL(12,2) NOT NULL DEFAULT 100000.00", "CHECK (budget >= 0)", "Operating academic budget (must be non-negative)."],
            ["created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Record inception timestamp."],
            ["updated_at", "TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "None", "Record last modification timestamp."]
        ]),
        ("instructors", "Faculty instructor personnel entity", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["instructor_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate primary identifier for instructor."],
            ["instructor_name", "VARCHAR(100) NOT NULL", "None", "Full legal name of faculty instructor."],
            ["email", "VARCHAR(150) NOT NULL", "UNIQUE", "Institutional contact email address."],
            ["dept_id", "INT NULL", "FK -> departments(dept_id)", "Department assignment (SET NULL on delete)."],
            ["salary", "DECIMAL(10,2) NOT NULL DEFAULT 50000.00", "CHECK (salary >= 0)", "Annual salary (must be non-negative)."],
            ["hire_date", "DATE NULL", "None", "Official date of academic appointment."],
            ["created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Record creation timestamp."],
            ["updated_at", "TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "None", "Record update timestamp."]
        ]),
        ("courses", "Curricular course catalog offering", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["course_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate primary identifier for course."],
            ["course_code", "VARCHAR(20) NOT NULL", "UNIQUE", "Catalog course code (e.g., 'CS101', 'EE101')."],
            ["course_name", "VARCHAR(150) NOT NULL", "None", "Full descriptive title of academic course."],
            ["credits", "INT NOT NULL DEFAULT 3", "CHECK (credits > 0 AND credits <= 12)", "Academic credit weighting (1 to 12)."],
            ["dept_id", "INT NULL", "FK -> departments(dept_id)", "Offering academic department."],
            ["instructor_id", "INT NULL", "FK -> instructors(instructor_id)", "Assigned primary course instructor."],
            ["created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Course registration timestamp."],
            ["updated_at", "TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "None", "Course catalog revision timestamp."]
        ]),
        ("students", "Enrolled student scholar entity", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["student_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate primary identifier for student."],
            ["student_name", "VARCHAR(100) NOT NULL", "None", "Full student legal name."],
            ["email", "VARCHAR(150) NOT NULL", "None (Logical Candidate)", "Student email address."],
            ["age", "INT NULL", "None (Domain Checked)", "Student age in years (Domain bound 16-65)."],
            ["gpa", "DECIMAL(3,2) NULL", "None (Domain Checked)", "Cumulative grade point average (0.00-4.00)."],
            ["dept_id", "INT NULL", "FK -> departments(dept_id)", "Major academic department."],
            ["enrollment_year", "INT NULL", "None", "Calendar year of matriculation."],
            ["created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Matriculation record timestamp."],
            ["updated_at", "TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "None", "Profile update timestamp."]
        ]),
        ("enrollments", "Official student course enrollment junction", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["enrollment_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate primary key for enrollment."],
            ["student_id", "INT NOT NULL", "FK -> students(student_id)", "Enrolled student reference (RESTRICT on delete)."],
            ["course_id", "INT NOT NULL", "FK -> courses(course_id)", "Enrolled course reference (RESTRICT on delete)."],
            ["enrolled_on", "DATE NOT NULL", "None", "Date registration was confirmed."],
            ["grade_marks", "DECIMAL(5,2) NULL", "CHECK (NULL or 0.00-100.00)", "Exam grade marks percentage."],
            ["status", "ENUM('ENROLLED','COMPLETED','DROPPED')", "DEFAULT 'ENROLLED'", "Academic lifecycle registration status."],
            ["created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Registration timestamp."],
            ["updated_at", "TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "None", "Grade modification timestamp."]
        ]),
        ("staging_enrollments", "Unconstrained raw staging data import sandbox", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["staging_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Staging record unique sequence identifier."],
            ["external_ref", "VARCHAR(50) NULL", "None", "External legacy batch tracking identifier."],
            ["student_id", "INT NULL", "None (Unconstrained)", "External student reference (monitored by scanner)."],
            ["course_id", "INT NULL", "None (Unconstrained)", "External course reference (monitored by scanner)."],
            ["student_email", "VARCHAR(150) NULL", "None", "Imported contact email."],
            ["enrolled_on", "DATE NULL", "None", "Imported registration date."],
            ["grade_marks", "DECIMAL(5,2) NULL", "None (Unconstrained)", "Imported raw score."],
            ["status", "VARCHAR(50) NULL", "None", "Raw imported status string."],
            ["notes", "VARCHAR(255) NULL", "None", "Staging diagnostic notes."],
            ["imported_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Staging ingestion timestamp."]
        ]),
        ("quarantine_records", "Safe isolation landing zone for corrupted rows", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["quarantine_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate primary key for quarantine entry."],
            ["source_table", "VARCHAR(100) NOT NULL", "INDEX", "Originating table from which row was excised."],
            ["source_pk_value", "VARCHAR(100) NOT NULL", "INDEX", "Original primary key of quarantined record."],
            ["issue_type", "VARCHAR(50) NOT NULL", "None", "Categorical violation tag (ORPHAN, DUPLICATE)."],
            ["row_data_json", "LONGTEXT NOT NULL", "None", "Full JSON serialization of complete original row."],
            ["quarantine_reason", "TEXT NOT NULL", "None", "Human-readable explanation of why row was quarantined."],
            ["quarantined_by", "VARCHAR(100) DEFAULT 'SYSTEM'", "None", "Operator or service identity performing quarantine."],
            ["quarantined_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Exact isolation timestamp."],
            ["resolved", "BOOLEAN DEFAULT FALSE", "None", "Flag indicating whether record has been reviewed."],
            ["resolution_notes", "TEXT NULL", "None", "Administrator remediation notes."]
        ]),
        ("integrity_rules", "Configurable database integrity rulebook", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["rule_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate rule identifier."],
            ["rule_code", "VARCHAR(50) NOT NULL", "UNIQUE", "Standardized rule code (e.g. RULE_ORPHAN_STUDENT)."],
            ["name", "VARCHAR(150) NOT NULL", "None", "Descriptive human-readable rule title."],
            ["description", "TEXT NOT NULL", "None", "Detailed explanation of rule invariant."],
            ["rule_type", "ENUM('ORPHAN','DUPLICATE','NULL_CHECK','DOMAIN_CHECK','RELATIONAL_CONSISTENCY')", "INDEX", "Rule anomaly classification."],
            ["target_table", "VARCHAR(100) NOT NULL", "INDEX", "Table inspected by this rule."],
            ["target_column", "VARCHAR(100) NOT NULL", "None", "Primary column evaluated."],
            ["parent_table", "VARCHAR(100) NULL", "None", "Referenced parent table for orphan rules."],
            ["parent_column", "VARCHAR(100) NULL", "None", "Referenced parent column for orphan rules."],
            ["parameters_json", "LONGTEXT NULL", "None", "Dynamic parameters (min, max, enum, regex)."],
            ["severity", "ENUM('LOW','MEDIUM','HIGH','CRITICAL')", "DEFAULT 'MEDIUM'", "Risk severity weighting."],
            ["is_enabled", "BOOLEAN NOT NULL DEFAULT TRUE", "None", "Runtime active toggle flag."]
        ]),
        ("scan_runs", "Full and table scan execution historical record", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["scan_id", "VARCHAR(50) NOT NULL", "PRIMARY KEY", "Unique scan identifier (SCAN-YYYYMMDD-HEX)."],
            ["scan_type", "ENUM('FULL','TABLE') NOT NULL", "DEFAULT 'FULL'", "Scope of scan execution."],
            ["target_tables", "TEXT NULL", "None", "Comma-separated target tables if TABLE scan."],
            ["start_time", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP", "INDEX", "Scan commencement timestamp."],
            ["end_time", "TIMESTAMP NULL", "None", "Scan completion timestamp."],
            ["status", "ENUM('RUNNING','COMPLETED','FAILED')", "INDEX", "Lifecycle execution status."],
            ["total_rows_inspected", "INT DEFAULT 0", "None", "Total live rows evaluated across tables."],
            ["issues_found", "INT DEFAULT 0", "None", "Count of deduplicated violations discovered."],
            ["critical_count", "INT DEFAULT 0", "None", "Count of CRITICAL severity violations."],
            ["high_count", "INT DEFAULT 0", "None", "Count of HIGH severity violations."],
            ["medium_count", "INT DEFAULT 0", "None", "Count of MEDIUM severity violations."],
            ["low_count", "INT DEFAULT 0", "None", "Count of LOW severity violations."],
            ["error_message", "TEXT NULL", "None", "Diagnostic error trace if scan failed."]
        ]),
        ("integrity_issues", "Granular catalog of detected schema anomalies", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["issue_id", "VARCHAR(50) NOT NULL", "PRIMARY KEY", "Unique issue identifier (ISS-YYYYMMDD-HEX)."],
            ["scan_id", "VARCHAR(50) NOT NULL", "INDEX", "Originating scan run identifier."],
            ["rule_id", "INT NULL", "None", "Referenced integrity_rules row."],
            ["rule_code", "VARCHAR(50) NOT NULL", "None", "Rule code that detected violation."],
            ["category", "ENUM('ORPHAN','DUPLICATE','NULL_VIOLATION','DOMAIN_VIOLATION','RELATIONAL_VIOLATION','SYSTEM_INTEGRITY')", "None", "Violation taxonomy."],
            ["severity", "ENUM('LOW','MEDIUM','HIGH','CRITICAL')", "None", "Severity level assigned."],
            ["table_name", "VARCHAR(100) NOT NULL", "INDEX", "Table containing the defective row."],
            ["record_id", "VARCHAR(100) NOT NULL", "None", "Primary key value of defective row."],
            ["column_name", "VARCHAR(100) NULL", "None", "Specific column breaching integrity."],
            ["invalid_value", "TEXT NULL", "None", "Current invalid value in database."],
            ["description", "TEXT NOT NULL", "None", "Human-readable diagnostic description."],
            ["status", "ENUM('OPEN','REVIEWED','APPROVED','REPAIRED','IGNORED','FAILED')", "INDEX", "Governance lifecycle state."],
            ["ignored_reason", "TEXT NULL", "None", "Administrator rationale if marked IGNORED."],
            ["detected_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Detection timestamp."],
            ["repaired_at", "TIMESTAMP NULL", "None", "Atomic repair completion timestamp."]
        ]),
        ("repair_recommendations", "Synthesized remediation action proposals", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["recommendation_id", "INT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate proposal identifier."],
            ["issue_id", "VARCHAR(50) NOT NULL", "INDEX", "Referenced integrity_issues row."],
            ["strategy", "ENUM('RESTORE_PARENT','MAP_PARENT','QUARANTINE','DELETE_RECORD','MERGE_DUPLICATE','SET_DEFAULT','MANUAL_INTERVENTION')", "None", "Proposed healing action."],
            ["problem_description", "TEXT NOT NULL", "None", "Summary of condition requiring repair."],
            ["proposed_action", "TEXT NOT NULL", "None", "Specific healing remediation proposal."],
            ["reason", "TEXT NOT NULL", "None", "Technical rationale for proposed strategy."],
            ["expected_impact", "TEXT NOT NULL", "None", "Downstream schema impact summary."],
            ["risk_level", "ENUM('LOW','MEDIUM','HIGH','CRITICAL')", "None", "Calculated risk classification."],
            ["is_reversible", "BOOLEAN NOT NULL DEFAULT TRUE", "None", "Reversibility indicator flag."],
            ["requires_approval", "BOOLEAN NOT NULL DEFAULT TRUE", "None", "Human approval requirement."],
            ["approval_status", "ENUM('PENDING','APPROVED','REJECTED')", "INDEX", "Governance approval state."],
            ["created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Recommendation generation timestamp."]
        ]),
        ("repair_executions", "Permanent ledger of executed healing transactions", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["execution_id", "VARCHAR(50) NOT NULL", "PRIMARY KEY", "Unique execution trace ID."],
            ["recommendation_id", "INT NULL", "None", "Referenced recommendation ID."],
            ["issue_id", "VARCHAR(50) NOT NULL", "INDEX", "Referenced issue ID."],
            ["transaction_id", "VARCHAR(50) NOT NULL", "None", "Referenced InnoDB transaction ID."],
            ["status", "ENUM('SUCCESS','FAILED','ROLLED_BACK')", "INDEX", "Final transaction outcome."],
            ["executed_by", "VARCHAR(100) NOT NULL DEFAULT 'ADMIN_USER'", "None", "Operator identity."],
            ["executed_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Execution timestamp."],
            ["before_state_json", "LONGTEXT NULL", "None", "Pre-repair row state JSON."],
            ["after_state_json", "LONGTEXT NULL", "None", "Post-repair row state JSON."],
            ["sql_executed", "TEXT NULL", "None", "Actual SQL DML statement executed."],
            ["error_message", "TEXT NULL", "None", "Error details if rolled back."],
            ["execution_time_ms", "INT DEFAULT 0", "None", "Execution duration in milliseconds."]
        ]),
        ("audit_logs", "Immutable event and state change ledger", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["event_id", "BIGINT AUTO_INCREMENT NOT NULL", "PRIMARY KEY", "Surrogate audit sequence."],
            ["event_type", "VARCHAR(50) NOT NULL", "INDEX", "Event type tag (SCAN_COMPLETED, REPAIR_EXECUTED)."],
            ["actor", "VARCHAR(100) NOT NULL DEFAULT 'SYSTEM'", "None", "Originating user or system actor."],
            ["timestamp", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "INDEX", "Immutable event timestamp."],
            ["related_scan_id", "VARCHAR(50) NULL", "None", "Linked scan run ID."],
            ["related_issue_id", "VARCHAR(50) NULL", "None", "Linked issue ID."],
            ["related_transaction_id", "VARCHAR(50) NULL", "None", "Linked transaction ID."],
            ["action_description", "TEXT NOT NULL", "None", "Narrative description of action."],
            ["target_table", "VARCHAR(100) NULL", "INDEX", "Table affected by event."],
            ["record_identifier", "VARCHAR(100) NULL", "None", "Primary key affected."],
            ["result", "ENUM('SUCCESS','FAILURE','INFO','WARNING')", "None", "Outcome indicator."],
            ["before_values_json", "LONGTEXT NULL", "None", "Pre-event state with redaction."],
            ["after_values_json", "LONGTEXT NULL", "None", "Post-event state with redaction."],
            ["error_message", "TEXT NULL", "None", "Failure message if applicable."]
        ]),
        ("transaction_logs", "Low-level InnoDB transaction lifecycle audit", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["transaction_id", "VARCHAR(50) NOT NULL", "PRIMARY KEY", "Surrogate transaction trace ID."],
            ["execution_id", "VARCHAR(50) NULL", "None", "Linked repair execution ID."],
            ["start_time", "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP", "INDEX", "Transaction begin timestamp."],
            ["end_time", "TIMESTAMP NULL", "None", "Transaction completion timestamp."],
            ["status", "ENUM('COMMITTED','ROLLED_BACK','FAILED')", "INDEX", "Transaction resolution status."],
            ["operations_count", "INT DEFAULT 1", "None", "Number of distinct SQL statements."],
            ["savepoints_used", "INT DEFAULT 0", "None", "Count of SAVEPOINT bookmarks set."],
            ["rollback_reason", "TEXT NULL", "None", "Reason for abort if rolled back."],
            ["duration_ms", "INT DEFAULT 0", "None", "Transaction duration in milliseconds."]
        ]),
        ("recovery_checkpoints", "Table state snapshots for point-in-time rollback", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["checkpoint_id", "VARCHAR(50) NOT NULL", "PRIMARY KEY", "Surrogate checkpoint identifier (CKPT-XXXXXX)."],
            ["checkpoint_name", "VARCHAR(150) NOT NULL", "None", "Descriptive checkpoint name."],
            ["created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "None", "Snapshot creation timestamp."],
            ["checkpoint_type", "ENUM('PRE_REPAIR','MANUAL','SCHEDULED')", "None", "Trigger context of checkpoint."],
            ["target_table", "VARCHAR(100) NOT NULL", "None", "Table captured by snapshot."],
            ["snapshot_metadata_json", "LONGTEXT NOT NULL", "None", "Table DDL and column schema JSON."],
            ["snapshot_rows_json", "LONGTEXT NOT NULL", "None", "Complete row dataset JSON."],
            ["status", "ENUM('ACTIVE','RESTORED','EXPIRED')", "INDEX", "Checkpoint availability status."]
        ]),
        ("database_metadata", "System key-value persistent configuration store", [
            ["Column Name", "Type & Nullability", "Key / Constraint", "Functional Purpose"],
            ["meta_key", "VARCHAR(100) NOT NULL", "PRIMARY KEY", "Unique configuration key name."],
            ["meta_value", "TEXT NOT NULL", "None", "Stored configuration or timestamp value."],
            ["updated_at", "TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "None", "Last modification timestamp."]
        ])
    ]

    for name, desc, data in table_profiles:
        ch4["sections"].append({
            "title": f"4.{len(ch4['sections'])+1} Table Profile: `{name}`",
            "paragraphs": [f"Technical specification and column schema dictionary for the `{name}` table ({desc}):"],
            "table": {"data": data, "widths": [110, 140, 120, 130]}
        })

    # -------------------------------------------------------------------------
    # 2. Expand Chapter 8 (Detail all 16 Seeded Integrity Rules)
    # -------------------------------------------------------------------------
    ch8 = chapters[7] # Chapter 8
    
    rule_profiles = [
        ("RULE_ORPHAN_STAGING_STUDENT", "ORPHAN", "staging_enrollments", "student_id", "students", "student_id",
         "Detects enrollment records in staging table referencing non-existent student IDs in the students parent table.",
         '{"allow_null": false, "strategy": "RESTORE_PARENT"}', "CRITICAL"),
        ("RULE_ORPHAN_STAGING_COURSE", "ORPHAN", "staging_enrollments", "course_id", "courses", "course_id",
         "Detects enrollment records in staging table referencing non-existent course IDs in the courses parent table.",
         '{"allow_null": false, "strategy": "RESTORE_PARENT"}', "CRITICAL"),
        ("RULE_ORPHAN_STUDENT_DEPT", "ORPHAN", "students", "dept_id", "departments", "dept_id",
         "Verifies that foreign key dept_id in students table correctly resolves to a registered department.",
         '{"allow_null": true, "strategy": "MAP_PARENT"}', "HIGH"),
        ("RULE_ORPHAN_COURSE_INSTRUCTOR", "ORPHAN", "courses", "instructor_id", "instructors", "instructor_id",
         "Verifies that foreign key instructor_id in courses points to a valid active instructor.",
         '{"allow_null": true, "strategy": "MAP_PARENT"}', "HIGH"),
        ("RULE_DUP_STAGING_STUDENT_COURSE", "DUPLICATE", "staging_enrollments", "student_id, course_id", None, None,
         "Identifies duplicate staging registration attempts where the same student is enrolled in the same course multiple times.",
         '{"group_by": ["student_id", "course_id"], "keep": "FIRST"}', "HIGH"),
        ("RULE_DUP_STUDENT_EMAIL", "DUPLICATE", "students", "email", None, None,
         "Enforces unique candidate key constraint on student email addresses across the student registry.",
         '{"group_by": ["email"], "case_sensitive": false}', "HIGH"),
        ("RULE_NULL_STUDENT_NAME", "NULL_CHECK", "students", "student_name", None, None,
         "Identifies student profiles with missing, NULL, or empty string names.",
         '{"disallow_empty_string": true}', "CRITICAL"),
        ("RULE_NULL_COURSE_NAME", "NULL_CHECK", "courses", "course_name", None, None,
         "Ensures all academic courses possess a non-null, non-empty catalog name.",
         '{"disallow_empty_string": true}', "HIGH"),
        ("RULE_DOMAIN_STAGING_GRADE", "DOMAIN_CHECK", "staging_enrollments", "grade_marks", None, None,
         "Validates that raw imported marks fall strictly within the allowable academic percentage interval [0.00, 100.00].",
         '{"min_value": 0.00, "max_value": 100.00}', "HIGH"),
        ("RULE_DOMAIN_STUDENT_AGE", "DOMAIN_CHECK", "students", "age", None, None,
         "Enforces valid matriculation age boundaries for students [16, 65].",
         '{"min_value": 16, "max_value": 65}', "MEDIUM"),
        ("RULE_DOMAIN_STUDENT_GPA", "DOMAIN_CHECK", "students", "gpa", None, None,
         "Validates that cumulative Grade Point Average falls within the standard 4.0 scale [0.00, 4.00].",
         '{"min_value": 0.00, "max_value": 4.00}', "HIGH"),
        ("RULE_DOMAIN_STUDENT_EMAIL", "DOMAIN_CHECK", "students", "email", None, None,
         "Validates structural RFC-compliant email syntax using anchored regular expressions.",
         '{"regex_pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$"}', "MEDIUM"),
        ("RULE_DOMAIN_STAGING_STATUS", "DOMAIN_CHECK", "staging_enrollments", "status", None, None,
         "Validates that staging enrollment status string matches permitted enumeration values.",
         '{"allowed_values": ["ENROLLED", "COMPLETED", "DROPPED"]}', "MEDIUM"),
        ("RULE_DOMAIN_ENROLLMENT_STATUS", "DOMAIN_CHECK", "enrollments", "status", None, None,
         "Enforces valid production enrollment status domain enum states.",
         '{"allowed_values": ["ENROLLED", "COMPLETED", "DROPPED"]}', "HIGH"),
        ("RULE_DOMAIN_COURSE_CREDITS", "DOMAIN_CHECK", "courses", "credits", None, None,
         "Verifies that course credits conform to curriculum bounds between 1 and 12 credit units.",
         '{"min_value": 1, "max_value": 12}', "HIGH"),
        ("RULE_DOMAIN_DEPT_BUDGET", "DOMAIN_CHECK", "departments", "budget", None, None,
         "Guarantees that departmental operating budgets remain strictly non-negative (>= 0.00).",
         '{"min_value": 0.00}', "HIGH")
    ]

    rule_table = [["Rule Code", "Category", "Target Table", "Target Column", "Severity", "Strategy"]]
    for r in rule_profiles:
        strat = "QUARANTINE / SET_DEFAULT" if "DOMAIN" in r[1] or "NULL" in r[1] else ("RESTORE / MAP" if r[1] == "ORPHAN" else "MERGE / DELETE")
        rule_table.append([r[0], r[1], r[2], r[3], r[8], strat])

    ch8["sections"].append({
        "title": "8.6 The Complete Catalog of 16 Seeded Integrity Rules",
        "paragraphs": [
            "The system initializes with 16 active integrity rules spanning all five theoretical categories. "
            "Below is the complete rule configuration matrix:"
        ],
        "table": {"data": rule_table, "widths": [140, 75, 95, 80, 50, 60]}
    })

    # -------------------------------------------------------------------------
    # 3. Expand Chapter 14 (Dedicated Component Deep Dive for all 11 Pages)
    # -------------------------------------------------------------------------
    from chapter14_components import get_chapter14_sections
    ch14 = chapters[13] # Chapter 14
    ch14["sections"] = get_chapter14_sections()

    # -------------------------------------------------------------------------
    # 4. Expand Chapter 18 (All 30 Viva Questions with full multi-paragraph answers)
    # -------------------------------------------------------------------------
    ch18 = chapters[17] # Chapter 18
    ch18["sections"] = [] # Rebuild completely with 30 comprehensive questions
    
    viva_qas = [
        ("1. System Purpose & Architecture", [
            ("Q1: What is the primary purpose of this project and what problem does it solve?",
             "The project implements an autonomous, human-supervised, transaction-safe database integrity detection, dependency analysis, self-healing, and audit traceability engine for MySQL InnoDB. It addresses the reality that enterprise databases regularly suffer from data degradation caused by bulk ETL imports, partial staging runs, accidental administrator edits, and unconstrained operational schemas. It bridges the gap between passive databases and active integrity management without using unpredictable machine learning."),
            ("Q2: How does this project differ from a standard CRUD application?",
             "A standard CRUD application simply performs point inserts, reads, updates, and deletes against predefined forms. It treats the database as a passive dumb store. This project is a Meta-Diagnostic Engine operating above the business data layer. It inspects schema structure dynamically via INFORMATION_SCHEMA, constructs directed dependency graphs using NetworkX to calculate cascading blast radiuses, generates non-destructive repair previews with cryptographic row-version tokens, and executes repairs inside genuine ACID rollback-guaranteed transactions."),
            ("Q3: What are the three architectural tiers of the system?",
             "The system is organized into: 1) Presentation Tier (React 18, Vite 5, Tailwind CSS, Recharts) providing 11 dashboard views; 2) Application Logic Tier (Python 3.13, FastAPI, Uvicorn, PyMySQL, NetworkX) orchestrating detection, graph analysis, preview synthesis, and transaction execution; and 3) Data Persistence Tier (MySQL InnoDB via local XAMPP) managing 16 relational and engine tables with full foreign keys, check bounds, and immutability triggers."),
            ("Q4: Why was MySQL InnoDB chosen as the database storage engine instead of MyISAM?",
             "InnoDB provides genuine ACID transaction compliance, row-level locking (SELECT ... FOR UPDATE), foreign key referential integrity enforcement, and write-ahead redo logging. In contrast, older engines like MyISAM only support table-level locking, have no foreign key enforcement, and cannot execute ROLLBACK statements, making transactional self-healing impossible."),
            ("Q5: What role does PyMySQL play in the backend architecture?",
             "PyMySQL is a pure-Python MySQL client driver. It allows FastAPI services to execute raw, high-performance parameterized SQL queries, inspect cursor metadata, manage explicit multi-statement transactions (autocommit=False), and handle native database exceptions directly without the abstraction overhead of heavy Object-Relational Mappers (ORMs).")
        ]),
        ("2. Relational Schema & Anomaly Detection", [
            ("Q6: Why is there an unconstrained staging table (`staging_enrollments`) in the database?",
             "In real-world enterprise databases (such as universities or financial institutions), external batch data imported from legacy files or third-party APIs regularly contains errors. If physical foreign keys were enforced directly on staging tables, the database engine would reject the entire batch file on the first bad record. Having an unconstrained staging table allows raw data to land safely, enabling our Integrity Scanner to inspect, isolate, and heal records prior to final promotion into production tables."),
            ("Q7: What is an orphan record, and how is it detected mathematically?",
             "An orphan record is a child row containing a non-NULL foreign key pointing to a primary key value that does not exist in the referenced parent table. In relational algebra, it is defined as: O = { r in Child | r.fk != NULL and not exists p in Parent with p.pk = r.fk }. The scanner detects orphans using a relational anti-join: `SELECT c.* FROM child c LEFT JOIN parent p ON c.fk = p.pk WHERE p.pk IS NULL AND c.fk IS NOT NULL`."),
            ("Q8: Why is a LEFT JOIN used for orphan detection instead of an INNER JOIN?",
             "An INNER JOIN discards non-matching rows and only returns records where parent and child both exist. A LEFT JOIN preserves all child rows regardless of parent existence. When a parent record is missing, the LEFT JOIN populates all parent columns with NULL. This allows the predicate `WHERE p.pk IS NULL` to cleanly isolate orphan records."),
            ("Q9: How does duplicate candidate key detection work?",
             "Duplicate detection evaluates logical entity uniqueness across unconstrained tables. It executes a `GROUP BY` query on the candidate key columns (e.g. `student_id, course_id`) with `HAVING COUNT(*) > 1`. The engine sorts the conflicting primary keys ascending, designates the lowest ID as the canonical record, and generates violation issues for all subsequent duplicate IDs."),
            ("Q10: What is the difference between a physical NULL and an empty string breach?",
             "A physical database NULL represents the complete absence of a value. An empty string (`''`) or whitespace string (`'   '`) is physically non-NULL in SQL but semantically violates business rules for mandatory attributes (such as student names). Our scanner checks both using the condition `WHERE col IS NULL OR TRIM(col) = ''`."),
            ("Q11: How are domain range violations detected?",
             "Domain range checks evaluate numeric columns against parameterized business boundaries defined in `integrity_rules.parameters_json`. For example, grade marks must satisfy `min_value: 0.00` and `max_value: 100.00`. The scanner executes `WHERE val < min_value OR val > max_value` to detect out-of-bounds anomalies."),
            ("Q12: How are domain enumeration violations detected?",
             "Enumeration checks enforce finite set membership for categorical columns. For staging enrollment status, allowed values are `['ENROLLED', 'COMPLETED', 'DROPPED']`. The scanner evaluates `WHERE status NOT IN ('ENROLLED', 'COMPLETED', 'DROPPED')` to detect invalid status strings like `'SUSPENDED'` or `'MAGIC'`."),
            ("Q13: How does the scanner prevent duplicate issues during re-scans?",
             "The scanner implements deduplication hashing based on a unique composite key: `(table_name, record_id, column_name, category)`. If an issue matching this key is already recorded in `integrity_issues` with status `OPEN`, the scanner skips re-insertion, preventing catalog clutter.")
        ]),
        ("3. Graph Theory, Dependencies & Blast Radius", [
            ("Q14: Why is the NetworkX library used in this DBMS project?",
             "NetworkX models relational table dependencies as a Directed Graph G = (V, E). Nodes V represent tables, and directed edges E represent foreign key relationships pointing from parent tables to child tables. This enables computational graph algorithms such as cycle detection, topological sorting, and transitive reachability analysis."),
            ("Q15: What is a circular dependency, and why is it dangerous in databases?",
             "A circular dependency (cycle) occurs when a chain of foreign keys loops back on itself (Table A references Table B, which references Table C, which references Table A). Cycles make it impossible to insert or delete rows cleanly without constraint violations and can cause catastrophic locking deadlocks during cascading operations. The system detects cycles using `nx.simple_cycles(G)`."),
            ("Q16: What is a Relational Blast Radius?",
             "The Relational Blast Radius defines the maximum theoretical boundary of downstream data that could be corrupted, altered, or orphaned if a modification or deletion is applied to a target table. It is mathematically calculated as the transitive closure of all reachable descendant nodes: BlastRadius(T) = Descendants(G, T)."),
            ("Q17: How does the system calculate live referential child counts?",
             "Beyond schema-level graph reachability, the `DependencyAnalyzer` executes live SQL queries against all direct physical child tables, issuing `SELECT COUNT(*) WHERE fk_col = %s` for the specific target primary key. This reveals exactly how many actual live records are attached to the record being repaired."),
            ("Q18: What is topological sorting and how does it assist in safe database operations?",
             "Topological sorting linearly orders directed graph vertices such that for every directed edge (u, v), vertex u comes before v. In database migrations, reverse topological sorting provides the exact safe deletion order: leaf child records are detached or deleted before parent records are touched, preventing foreign key constraint violations.")
        ]),
        ("4. Concurrency, Previews & Repair Execution", [
            ("Q19: What is a Stale Preview Hazard (Race Condition) in database repairs?",
             "A Stale Preview Hazard occurs in multi-user database environments when an administrator reviews a repair preview for Record #8, but another process alters or deletes Record #8 before the administrator clicks 'Execute'. If executed blindly, the repair would overwrite newly modified data."),
            ("Q20: How does the cryptographic Row-Version Token prevent stale previews?",
             "During preview generation, the engine normalizes the target row into a sorted dictionary and computes a SHA-256 hash token: `Token = SHA256(JSON(CanonicalRow))`. Before executing the repair inside the transaction, the engine acquires an exclusive lock and re-computes the hash. If the hashes differ, the engine aborts execution immediately with a `StalePreviewError`."),
            ("Q21: What is the purpose of `SELECT ... FOR UPDATE` during repair execution?",
             "`SELECT ... FOR UPDATE` acquires an exclusive pessimistic row-level write lock in MySQL InnoDB. It ensures that no other concurrent transaction can read, modify, or delete the target record while our healing transaction is verifying tokens and applying fixes."),
            ("Q22: How does the `QUARANTINE` repair strategy work?",
             "`QUARANTINE` is our safest data removal strategy. Instead of permanently deleting a corrupted record, the engine serializes the entire row into structured JSON, inserts it into `quarantine_records` along with the source table, primary key, issue type, reason, and operator identity, and only then deletes the row from the source table. This guarantees zero data loss."),
            ("Q23: How does the `SET_DEFAULT` repair strategy handle mandatory missing values?",
             "For missing mandatory attributes (like a student's name), `SET_DEFAULT` strictly prohibits fabricated fake placeholders like '[PROPOSED: Default]'. The preview flags `requires_admin_input: True`, and the engine forces the human administrator to enter an authoritative legal replacement value before the repair can be executed."),
            ("Q24: How does the `MAP_PARENT` repair strategy resolve orphan records?",
             "`MAP_PARENT` re-links an orphan child record to an existing, valid parent primary key. The engine verifies that the target parent ID actually exists in the parent table, and then issues an `UPDATE child SET fk_col = %s WHERE id = %s` inside an atomic transaction.")
        ]),
        ("5. Transactions, Recovery & Auditing", [
            ("Q25: What does ACID stand for and how is each property enforced in this project?",
             "ACID stands for Atomicity (guaranteed by explicit BEGIN, COMMIT, and automatic ROLLBACK on failure), Consistency (guaranteed by foreign keys, check bounds, and pre-repair verification), Isolation (guaranteed by InnoDB REPEATABLE READ isolation and row-level write locks), and Durability (guaranteed by InnoDB write-ahead redo logs after commit)."),
            ("Q26: What is a SAVEPOINT in MySQL transactions?",
             "A SAVEPOINT is a bookmark created within an active transaction using `SAVEPOINT savepoint_name`. It allows the application to execute a partial rollback (`ROLLBACK TO SAVEPOINT savepoint_name`) undoing only operations executed after the bookmark while preserving all preceding operations within the same transaction."),
            ("Q27: How does application-level checkpoint recovery work?",
             "Before high-risk repairs, the `RecoveryManager` captures table DDL and serializes all current table rows into JSON, storing the snapshot in `recovery_checkpoints`. During restoration, the engine verifies primary keys, checks foreign key bounds, upserts snapshot rows, and deletes newly added post-snapshot rows inside a transaction, mathematically verifying that post-restore row counts exactly match snapshot row counts."),
            ("Q28: How do native database triggers enforce audit log immutability?",
             "The SQL schema installs `BEFORE UPDATE` and `BEFORE DELETE` triggers on `audit_logs` and `transaction_logs`. If any user or application attempts to update or delete a log entry, the trigger executes `SIGNAL SQLSTATE '45000'` with a critical error, causing MySQL to reject the operation physically at the engine level."),
            ("Q29: How does the audit redaction filter protect sensitive credentials?",
             "Before logging event payloads to `audit_logs`, the `AuditService` sanitizes dictionaries. Any key containing substrings like `password`, `secret`, `token`, `pwd`, `hash`, or `credit_card` has its value replaced with the mask `'[REDACTED]'`, preventing credential leaks in persistent logs."),
            ("Q30: Why is this system described as a 'human-supervised self-healing system' rather than fully autonomous?",
             "In relational database engineering, fully autonomous remediation without human oversight is dangerous because business intent cannot be inferred by an algorithm alone. For example, if a student's name is missing, only a human can supply the real name. The system autonomously detects, models dependencies, classifies risks, and generates previews, but requires human approval for high-risk operations to ensure maximum safety.")
        ])
    ]

    for cat_title, qas in viva_qas:
        p_list = []
        for q, a in qas:
            p_list.append(f"<b>{q}</b><br/>{a}<br/>")
        ch18["sections"].append({
            "title": f"18.{len(ch18['sections'])+1} {cat_title}",
            "paragraphs": p_list
        })

    # -------------------------------------------------------------------------
    # 5. Expand Chapter 11 (Detailed Transaction State Step Tables)
    # -------------------------------------------------------------------------
    ch11 = chapters[10] # Chapter 11
    
    tx_step_table = [
        ["Step #", "Operation Executed", "SQL Statement Dispatched", "Intermediate DB State", "Isolation Level"],
        ["Step 1", "BEGIN TRANSACTION", "START TRANSACTION /* Autocommit=0 */", "Snapshot isolation view established", "REPEATABLE READ"],
        ["Step 2", "INSERT RECORD A", "INSERT INTO staging_enrollments VALUES (9001, 'TX-A', ...)", "Dirty row visible ONLY inside connection", "Uncommitted"],
        ["Step 3", "SET SAVEPOINT", "SAVEPOINT step_a_complete", "Named transaction recovery bookmark saved", "Savepoint Active"],
        ["Step 4", "INSERT RECORD B", "INSERT INTO staging_enrollments VALUES (9002, 'TX-B', ...)", "Temporary invalid row staged", "Uncommitted"],
        ["Step 5", "SIMULATED FAILURE", "Runtime Exception Triggered (Constraint / Network Error)", "Engine traps error and halts execution", "Error Trapped"],
        ["Step 6", "PARTIAL ROLLBACK", "ROLLBACK TO SAVEPOINT step_a_complete", "Record B undone; Record A state preserved!", "Partial Revert"],
        ["Step 7", "COMMIT TRANSACTION", "COMMIT /* Redo log written to disk */", "Record A permanently persisted to InnoDB tables", "DURABLE"]
    ]
    ch11["sections"].append({
        "title": "11.4 Granular Step-by-Step Transaction Execution Matrix",
        "paragraphs": [
            "Below is the exact execution trace and state transition matrix recorded by `TransactionManager` "
            "during a `SAVEPOINT_PARTIAL_ROLLBACK` operational run:"
        ],
        "table": {"data": tx_step_table, "widths": [45, 95, 160, 120, 80]}
    })

    # -------------------------------------------------------------------------
    # 6. Expand Chapter 16 (Complete Catalog of all 45 Test Scenarios)
    # -------------------------------------------------------------------------
    ch16 = chapters[15] # Chapter 16
    
    test_catalog = [
        ["#", "Test Function Name", "Source Test File", "Scope / Assertion Validated"],
        ["1", "test_api_health", "test_api_endpoints.py", "Verifies /api/health returns 200, service name, and version."],
        ["2", "test_api_cannot_manually_mark_repaired", "test_api_endpoints.py", "Verifies client cannot manually PATCH status to REPAIRED."],
        ["3", "test_cors_trusted_origin_allowed", "test_api_endpoints.py", "Verifies http://localhost:5173 is accepted with credentials."],
        ["4", "test_cors_untrusted_origin_rejected", "test_api_endpoints.py", "Verifies malicious origin is rejected by CORS middleware."],
        ["5", "test_invalid_sql_identifier_returns_400", "test_api_endpoints.py", "Verifies SQL injection identifiers trigger HTTP 400."],
        ["6", "test_api_database_status", "test_api_endpoints.py", "Verifies database status returns registered table counts."],
        ["7", "test_api_database_tables", "test_api_endpoints.py", "Verifies table list contains at least 10 active schema tables."],
        ["8", "test_api_list_rules", "test_api_endpoints.py", "Verifies rules endpoint returns at least 5 configured rules."],
        ["9", "test_api_dependency_graph", "test_api_endpoints.py", "Verifies dependency graph returns nodes and edges arrays."],
        ["10", "test_api_audit_logs", "test_api_endpoints.py", "Verifies audit logs endpoint returns items array."],
        ["11", "test_nonexistent_scan_issues_returns_404", "test_api_endpoints.py", "Verifies invalid scan ID returns HTTP 404."],
        ["12", "test_valid_scan_issues_regression", "test_api_endpoints.py", "Verifies existing scan returns HTTP 200 with issues."],
        ["13", "test_nonexistent_table_neighborhood_returns_404", "test_api_endpoints.py", "Verifies non-existent table returns HTTP 404."],
        ["14", "test_valid_table_neighborhood_regression", "test_api_endpoints.py", "Verifies valid table returns direct parents and children."],
        ["15", "test_validate_identifier_safe", "test_connection.py", "Verifies safe alphanumeric table and column names pass."],
        ["16", "test_validate_identifier_dangerous", "test_connection.py", "Verifies malicious SQL injection strings raise ValueError."],
        ["17", "test_mysql_connection_diagnostics", "test_connection.py", "Verifies live MySQL server latency, user, and version telemetry."],
        ["18", "test_dependency_graph_structure", "test_dependency_analyzer.py", "Verifies DiGraph contains core relational schema tables."],
        ["19", "test_table_neighborhood", "test_dependency_analyzer.py", "Verifies neighborhood extraction returns parent/child lists."],
        ["20", "test_repair_impact_assessment", "test_dependency_analyzer.py", "Verifies deleting parent with dependents flags CRITICAL risk."],
        ["21", "test_repair_preview", "test_repair_engine.py", "Verifies non-destructive preview generates SQL and states."],
        ["22", "test_destructive_repair_requires_confirmation", "test_repair_engine.py", "Verifies destructive actions enforce approval guard."],
        ["23", "test_missing_record_handling_and_auto_resolution", "test_repair_engine.py", "Verifies preview on deleted row auto-marks issue REPAIRED."],
        ["24", "test_test_a_preview_missing_customer_name", "test_set_default_preview.py", "Verifies missing mandatory attribute requires admin input."],
        ["25", "test_test_b_preview_missing_customer_email", "test_set_default_preview.py", "Verifies email preview requires valid format input."],
        ["26", "test_test_c_foreign_key_dependency_detection", "test_set_default_preview.py", "Verifies foreign key dependencies are detected before fix."],
        ["27", "test_test_d_repair_failure_handling_and_rollback", "test_set_default_preview.py", "Verifies failure rolls back atomically and logs event."],
        ["28", "test_test_e_and_f_successful_repair_and_duplicate", "test_set_default_preview.py", "Verifies successful repair commits and prevents dupes."],
        ["29", "test_test_g_stale_preview_rejection", "test_set_default_preview.py", "Verifies modified row triggers StalePreviewError."],
        ["30", "test_transaction_demo_commit", "test_transaction_manager.py", "Verifies COMMIT increases record count by exactly 1."],
        ["31", "test_transaction_demo_rollback", "test_transaction_manager.py", "Verifies ROLLBACK restores initial count with zero leaks."],
        ["32", "test_transaction_demo_savepoint", "test_transaction_manager.py", "Verifies SAVEPOINT rollback preserves preceding operations."],
        ["33", "test_recovery_manager_class_exists", "test_recovery_manager.py", "Verifies RecoveryManager interface exposes required methods."],
        ["34", "test_recovery_checkpoint_and_restoration", "test_recovery_manager.py", "Verifies full table snapshot creation and restoration."],
        ["35", "test_sanitize_json_redaction", "test_audit_service.py", "Verifies password and token keys are replaced with [REDACTED]."],
        ["36", "test_audit_log_persisted", "test_audit_service.py", "Verifies audit events are inserted into MySQL audit_logs."],
        ["37", "test_scanner_detection_run", "test_scanner.py", "Verifies full scan detects injected demo violations."],
        ["38", "test_recommendation_generation", "test_scanner.py", "Verifies scanner generates structured healing proposals."],
        ["39", "test_unit_rule_model_validation", "test_unit.py", "Verifies Pydantic rule schema validation and type parsing."],
        ["40", "test_unit_issue_severity_enums", "test_unit.py", "Verifies severity enum values strictly match allowed types."],
        ["41", "test_unit_email_regex_positive", "test_unit.py", "Verifies RFC-compliant email strings pass regex filter."],
        ["42", "test_unit_email_regex_negative", "test_unit.py", "Verifies invalid email formats are correctly rejected."],
        ["43", "test_unit_row_token_deterministic", "test_unit.py", "Verifies identical row states produce identical SHA-256 tokens."],
        ["44", "test_unit_row_token_sensitivity", "test_unit.py", "Verifies 1-character modification alters SHA-256 token."],
        ["45", "test_unit_audit_redaction_clean", "test_unit.py", "Verifies non-sensitive dictionaries remain untouched."]
    ]

    ch16["sections"].append({
        "title": "16.3 Complete Specification of All 45 Automated Test Cases",
        "paragraphs": [
            "The project test harness contains 45 formal test functions validating every layer of the architecture. "
            "Below is the complete quality assurance test catalog:"
        ],
        "table": {"data": test_catalog, "widths": [25, 145, 110, 220]}
    })

    # -------------------------------------------------------------------------
    # 7. Expand Chapter 20 (Appendix B: Mathematical Notation Guide)
    # -------------------------------------------------------------------------
    ch20 = chapters[19] # Chapter 20
    
    math_symbols = [
        ["Symbol / Notation", "Mathematical Definition", "Context in Relational Integrity System"],
        ["G = (V, E)", "Directed Graph with Vertices V and Edges E", "V represents tables; E represents foreign key references."],
        ["O", "Orphan Record Set", "Child rows with non-NULL FK lacking matching parent PK."],
        ["D", "Candidate Key Duplicate Group", "Group of records sharing identical logical candidate keys."],
        ["BlastRadius(T)", "Transitive Reachable Descendants", "Set of all downstream dependent tables affected by modifying T."],
        ["SHA-256(Row)", "Cryptographic Hash Function", "Deterministic row-version signature for optimistic concurrency control."],
        ["P -> C", "Referential Constraint Mapping", "Arrow pointing from parent table P to referencing child table C."],
        ["sigma_{cond}(R)", "Relational Selection Operator", "Filtering rows matching violation criteria (WHERE clause)."],
        ["pi_{cols}(R)", "Relational Projection Operator", "Selecting specific columns for inspection or preview (SELECT clause)."],
        ["R bowtie_{cond} S", "Relational Theta Join", "Joining child and parent relations along referential attributes."],
        ["Delta_{rollback}", "Transaction Undo Delta", "Reverting uncommitted database state changes upon exception."]
    ]
    ch20["sections"].append({
        "title": "20.3 Formal Mathematical Notation & Relational Calculus Guide",
        "paragraphs": [
            "Below is the reference glossary of formal mathematical symbols, relational algebra operators, "
            "and graph theory notation employed throughout this report:"
        ],
        "table": {"data": math_symbols, "widths": [110, 160, 230]}
    })

    # -------------------------------------------------------------------------
    # 8. Expand Chapter 5 (EXPLAIN Query Execution Plan Analysis)
    # -------------------------------------------------------------------------
    ch5 = chapters[4] # Chapter 5
    explain_data = [
        ["Select Type", "Table Scanned", "Access Type", "Possible Keys", "Key Used", "Rows Examined", "Filter Rationale"],
        ["SIMPLE", "c (staging_enrollments)", "ALL", "None", "None", "8", "Full staging scan for external batch inspection."],
        ["SIMPLE", "p (students)", "eq_ref", "PRIMARY", "PRIMARY", "1", "Index primary key lookup per child row."],
        ["SIMPLE", "departments", "ALL", "None", "None", "4", "Full table metadata reflection during scan bootstrap."],
        ["SIMPLE", "integrity_issues", "ref", "idx_issue_status", "idx_issue_status", "11", "Indexed status search for OPEN triage issues."]
    ]
    ch5["sections"].append({
        "title": "5.4 Query Optimization & MySQL EXPLAIN Plan Inspection",
        "paragraphs": [
            "To guarantee that detection queries do not cause locking contention or table degradation on large datasets, "
            "every query was profiled using MySQL's `EXPLAIN` optimizer. Below is the optimizer execution profile for the core anti-join:"
        ],
        "table": {"data": explain_data, "widths": [65, 105, 65, 80, 80, 50, 135]}
    })

    # -------------------------------------------------------------------------
    # 9. Expand Chapter 3 (InnoDB Lock Escalation & Concurrency Mechanics)
    # -------------------------------------------------------------------------
    ch3 = chapters[2] # Chapter 3
    lock_data = [
        ["Lock Primitive", "InnoDB Lock Type", "Scope / Resource Protected", "Concurrency Impact"],
        ["Record Lock", "LOCK_REC", "Locks the exact physical index record.", "Other transactions can modify adjacent records."],
        ["Gap Lock", "LOCK_GAP", "Locks the gap before an index record.", "Prevents phantom insertions into ranges."],
        ["Next-Key Lock", "LOCK_X | LOCK_GAP", "Combines record lock and gap lock.", "Default in REPEATABLE READ to eliminate phantom rows."],
        ["Table Intention", "LOCK_IX", "Intention-exclusive lock on table.", "Enables fast table-level DDL conflict checks."]
    ]
    ch3["sections"].append({
        "title": "3.3 InnoDB Concurrency & Lock Escalation Architecture",
        "paragraphs": [
            "To guarantee that our self-healing repairs do not introduce concurrency deadlocks while operating in multi-threaded environments, "
            "the system relies on InnoDB's sophisticated lock escalation hierarchy. When a repair issues `SELECT ... FOR UPDATE`, "
            "InnoDB establishes Next-Key Locks across the index range, preventing phantom records from materializing during repair synthesis."
        ],
        "table": {"data": lock_data, "widths": [100, 110, 150, 140]}
    })

    # -------------------------------------------------------------------------
    # 10. Expand Chapter 19 (Distributed Consensus & Multi-Tenant Partitioning)
    # -------------------------------------------------------------------------
    ch19 = chapters[18] # Chapter 19
    ch19["sections"].append({
        "title": "19.3 Future Research: Distributed Graph Consensus & Cross-Shard Integrity",
        "paragraphs": [
            "In hyperscale cloud architectures (such as Google Cloud Spanner, AWS Aurora, or Vitess), tables are frequently sharded across multiple physical nodes. "
            "In such distributed topologies, evaluating a global referential Directed Acyclic Graph requires distributed consensus algorithms.",
            "Future iterations of this system could implement a Two-Phase Commit (2PC) or Raft-backed graph consensus engine where local shard agents "
            "compute partitioned subgraphs and coordinate with a distributed metadata sequencer to calculate cross-shard blast radiuses with zero distributed deadlocks."
        ]
    })

    # -------------------------------------------------------------------------
    # 11. Expand Chapter 15 (REST API Specification with all 24 Endpoints)
    # -------------------------------------------------------------------------
    from expanded_api_setup import get_chapter15_sections, get_chapter17_sections
    ch15 = chapters[14]
    ch15["sections"] = get_chapter15_sections()

    # -------------------------------------------------------------------------
    # 12. Expand Chapter 17 (Automated Setup Wizard & Diagnostics Matrix)
    # -------------------------------------------------------------------------
    ch17 = chapters[16]
    ch17["sections"] = get_chapter17_sections()

    return chapters

if __name__ == "__main__":
    new_chapters = expand()
    print(f"Total expanded chapters: {len(new_chapters)}")
    for i, c in enumerate(new_chapters, 1):
        print(f"  Ch {i:2d}: {c['title']} ({len(c.get('sections', []))} sections)")
