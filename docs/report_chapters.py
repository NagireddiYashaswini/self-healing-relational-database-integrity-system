"""
Report Chapters Content Data for 50-Page Project Report
Provides rich, extensive academic and intuitive descriptions, formulas, SQL queries,
and tables across 20 distinct technical chapters.
"""

def get_all_chapters():
    chapters = []

    # =========================================================================
    # CHAPTER 1
    # =========================================================================
    chapters.append({
        "title": "The Intuitive Foundation: The 10-Year-Old Guide to Relational Databases",
        "kid_summary": (
            "Imagine a giant school made of Lego bricks with labeled drawers for Departments, Teachers, "
            "Classes, and Students. When clumsy hands write report cards for imaginary ghost kids or "
            "accidentally clone a student, our superhero robot doctor uses X-ray glasses to spot the mistakes, "
            "calculates if pulling one block will topple the entire tower, and uses a magical undo button if anything goes wrong!"
        ),
        "sections": [
            {
                "title": "1.1 The Giant Lego School: What is a Relational Database?",
                "paragraphs": [
                    "Computers store enormous amounts of information every second. Whether you are ordering a toy online, checking your school report card, or booking an airplane flight, your information lives inside a computer filing cabinet called a Relational Database Management System (RDBMS).",
                    "To understand what 'relational' means, imagine a school where everything is sorted into wooden drawers. One drawer holds a card for every Department (like Science or Art). Another drawer holds Teacher badges. A third drawer holds Classroom information, and a fourth drawer holds Student registration cards.",
                    "The word 'Relational' means that every drawer is connected to other drawers with invisible threads: a teacher badge only makes sense if it points to a real department, and a student's grade only makes sense if it points to both a real student and a real class. In computer science, these invisible threads are called Foreign Key Constraints."
                ],
                "bullets": [
                    "Table (Drawer): A labeled collection of cards sharing the same structure.",
                    "Record or Row (Card): A single item, such as Student #101: Ravi Kumar.",
                    "Primary Key (Unique ID Badge): A number that guarantees no two cards get mixed up.",
                    "Foreign Key (Thread): A pointer from one card to another card's Primary Key."
                ]
            },
            {
                "title": "1.2 Meet the Five Troublesome Data Monsters",
                "paragraphs": [
                    "Whenever humans type into computers or when systems import thousands of records from spreadsheets, mistakes happen. In our database school, five troublesome 'Data Monsters' sneak into the filing cabinets:"
                ],
                "table": {
                    "data": [
                        ["Data Monster", "Everyday School Example", "Technical Database Term", "Danger Level"],
                        ["The Ghost Kid", "A report card is written for Student #999, but nobody named #999 exists!", "Orphan Record (Broken Foreign Key)", "CRITICAL"],
                        ["The Evil Clone", "Sneha is registered for Math 101 twice at the exact same hour.", "Duplicate Candidate Key Collision", "HIGH"],
                        ["The Invisible Student", "A new student profile is filed, but the name is left completely empty.", "Mandatory NULL / Empty String Breach", "CRITICAL"],
                        ["The Time Traveler", "A student's age is typed as 140 years old, or test score is 145/100.", "Domain Range Violation", "HIGH"],
                        ["The Secret Code", "Enrollment status is written as 'SUPER-MAGIC' instead of 'ENROLLED'.", "Domain Enum / Format Violation", "MEDIUM"]
                    ],
                    "widths": [110, 150, 150, 90]
                }
            },
            {
                "title": "1.3 The Clumsy Robot Dilemma (The Domino Effect)",
                "paragraphs": [
                    "Why can't we just write a simple program that automatically deletes every mistake it finds? Because of the dreaded Domino Effect (Cascading Blast Radius).",
                    "Imagine a teacher's record contains a small spelling mistake. If a clumsy robot decides to solve the problem by deleting the teacher, what happens to the courses that teacher teaches? What happens to the grades of 100 students enrolled in those courses? If the database deletes everything connected to that teacher, half the school's records vanish!",
                    "This is why real enterprise databases cannot use blind automated deletion. Every fix must be carefully inspected, simulated with safety goggles, and reviewed by a human."
                ]
            },
            {
                "title": "1.4 The Superhero Database Doctor: How Our System Solves It",
                "paragraphs": [
                    "Our project builds an Autonomous Self-Healing Relational Database System. It acts like a brilliant, careful robot doctor equipped with five superpowers:"
                ],
                "bullets": [
                    "Superpower 1 (X-Ray Vision): Scans through thousands of records using SQL rules to locate violations without disturbing live operations.",
                    "Superpower 2 (Family Tree Map): Uses graph algorithms (NetworkX) to map out who depends on whom, predicting the blast radius before touching anything.",
                    "Superpower 3 (Hologram Preview): Projects a side-by-side preview showing the 'Before State' and the proposed 'After State' for human approval.",
                    "Superpower 4 (Magical Undo Button): Steps inside an atomic ACID transaction bubble. If anything goes wrong, it hits ROLLBACK, and the database rewinds instantly.",
                    "Superpower 5 (The Unbreakable Black Box): Writes down every single inspection, approval, and repair in an immutable audit diary protected by database triggers."
                ]
            }
        ]
    })

    # =========================================================================
    # CHAPTER 2
    # =========================================================================
    chapters.append({
        "title": "Academic Problem Statement, Background & Research Motivation",
        "kid_summary": (
            "Big companies like banks and hospitals have millions of rows of data. "
            "When they copy data between old and new computers, things get disconnected. "
            "Normal websites don't check for these subtle errors. We built a system that actively hunts down "
            "these hidden bugs using mathematical logic instead of risky guesses."
        ),
        "sections": [
            {
                "title": "2.1 The Reality of Enterprise Relational Data Degradation",
                "paragraphs": [
                    "In textbook relational database theory, declarative constraints (Primary Keys, Foreign Keys, UNIQUE indices, and CHECK clauses) are assumed to maintain perpetual integrity. In actual enterprise practice, however, data degradation is rampant.",
                    "Organizations routinely perform bulk ETL (Extract, Transform, Load) pipelines, staging migrations, external batch imports, and emergency direct administrator updates. To maximize throughput during ingestion, physical constraints are frequently disabled or omitted on staging tables, allowing corrupted, orphan, or duplicate records to enter relational storage.",
                    "Left uncorrected, these anomalies cascade into reporting errors, broken business logic, application crashes, and compromised analytical integrity."
                ]
            },
            {
                "title": "2.2 Why Traditional CRUD Applications Fail at Database Integrity",
                "paragraphs": [
                    "Standard CRUD (Create, Read, Update, Delete) applications treat the database as a passive dumb store. They execute point queries against predefined form fields. When data integrity breaks, CRUD applications simply display error screens or silently return NULL.",
                    "In contrast, this project implements a Meta-Diagnostic Engine. It operates above the business application layer, continuously introspecting the schema itself, evaluating multi-table referential graphs, proposing safe healing actions, and verifying relational invariants."
                ],
                "table": {
                    "data": [
                        ["Evaluation Dimension", "Standard CRUD Application", "Self-Healing DBMS Project"],
                        ["Primary Operational Focus", "User record entry and retrieval", "Autonomous anomaly diagnosis & healing"],
                        ["Schema Awareness", "Hardcoded forms tied to static tables", "Dynamic introspection of INFORMATION_SCHEMA"],
                        ["Relational Intelligence", "Assumes all foreign keys are valid", "Directed graph DAG modeling & blast radius"],
                        ["Repair Safety", "Uncontrolled blind updates/deletes", "Non-destructive previews & risk matrix"],
                        ["Transaction Rigor", "Implicit single-query auto-commit", "ACID multi-step isolation with savepoints"],
                        ["Audit Traceability", "Simple access logs or none", "Trigger-protected immutable event ledger"]
                    ],
                    "widths": [110, 195, 195]
                }
            },
            {
                "title": "2.3 The Determinism Imperative: Why Machine Learning is Not Used",
                "paragraphs": [
                    "A critical engineering decision in this system is the deliberate rejection of machine learning or probabilistic heuristic models for database integrity enforcement.",
                    "In relational database engineering, data integrity is governed by mathematical formalisms (relational calculus and first-order predicate logic). An anomaly is not a statistical probability; it is a binary fact: a record either violates a referential constraint or it does not.",
                    "Deploying a black-box neural network to guess foreign-key mappings or infer surrogate keys risks hallucinating corrupted data. This project guarantees 100% deterministic, auditable, and mathematically provable outcomes through SQL predicate evaluation and graph traversal."
                ]
            }
        ]
    })

    # =========================================================================
    # CHAPTER 3
    # =========================================================================
    chapters.append({
        "title": "End-to-End System Architecture & Three-Tier Engineering Design",
        "kid_summary": (
            "Our system is built like a three-story building: the top floor is the colorful React dashboard "
            "where you click buttons, the middle floor is the smart Python FastAPI brain that does the math, "
            "and the ground floor is the super-secure MySQL vault where the data is locked safely."
        ),
        "sections": [
            {
                "title": "3.1 Architectural Decomposition",
                "paragraphs": [
                    "The Self-Healing Relational Database Integrity System adheres to a strict decoupled Three-Tier Architecture, ensuring high cohesion, modular testability, and zero cross-layer contamination:",
                    "1. Presentation Tier (Frontend): A responsive single-page application built on React 18, Vite 5, Tailwind CSS, and Recharts. Communicates exclusively via asynchronous JSON REST APIs.",
                    "2. Application Logic Tier (Backend): A high-performance Python 3.13 FastAPI service orchestrating specialized domain services: IntegrityScanner, DependencyAnalyzer, RepairEngine, TransactionManager, RecoveryManager, and AuditService.",
                    "3. Data Persistence Tier (Database): A MySQL 8.0+ / MariaDB 10.4+ engine configured with the InnoDB storage engine, utilizing row-level locking, foreign key cascades, and trigger-enforced immutability."
                ]
            },
            {
                "title": "3.2 Directional Communication Flow & Proxy Routing",
                "paragraphs": [
                    "During local development and production deployment, the frontend application runs on port 5173, while the backend API runs on port 8000. All client API queries are routed through a reverse proxy configured in Vite (`/api -> http://127.0.0.1:8000`), completely eliminating Cross-Origin Resource Sharing (CORS) friction while maintaining strict browser isolation."
                ],
                "table": {
                    "data": [
                        ["Component Module", "Source Technology", "Key Responsibility", "Network Port"],
                        ["Dashboard UI", "React 18 + Vite 5", "Visualizations, interactive graph, modals", "5173 (Browser)"],
                        ["REST Gateway", "FastAPI + Uvicorn", "Route handling, validation, JSON schemas", "8000 (Internal)"],
                        ["Integrity Scanner", "Python + PyMySQL", "Dynamic metadata scanning & rule evaluation", "Internal Service"],
                        ["Dependency Analyzer", "NetworkX (DiGraph)", "DAG traversal, cycle detection, blast radius", "Internal Service"],
                        ["Repair Engine", "Python + InnoDB SQL", "Previews, SHA-256 tokens, ACID repair execution", "Internal Service"],
                        ["Database Engine", "MySQL InnoDB", "ACID transactions, constraints, triggers", "3306 (TCP)"]
                    ],
                    "widths": [110, 120, 200, 70]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 4
    # =========================================================================
    chapters.append({
        "title": "Complete Relational Database Specification (All 16 Tables Detailed)",
        "kid_summary": (
            "Our database has 16 special rooms. Five rooms are for the school (teachers, students, classes), "
            "one is an unconstrained waiting room where new raw data lands, one is an emergency quarantine "
            "room for infected records, and the rest are control rooms and secret diaries that record every move."
        ),
        "sections": [
            {
                "title": "4.1 Schema Categorization",
                "paragraphs": [
                    "The database instance `self_healing_test_db` consists of 16 tables divided into four functional tiers:",
                    "• Tier 1: Business Domain Schema (5 tables): `departments`, `instructors`, `courses`, `students`, `enrollments`.",
                    "• Tier 2: Staging & Quarantine Schema (2 tables): `staging_enrollments`, `quarantine_records`.",
                    "• Tier 3: Integrity Engine & Repair Schema (5 tables): `integrity_rules`, `scan_runs`, `integrity_issues`, `repair_recommendations`, `repair_executions`.",
                    "• Tier 4: Audit, Recovery & System Schema (4 tables): `audit_logs`, `transaction_logs`, `recovery_checkpoints`, `database_metadata`."
                ]
            },
            {
                "title": "4.2 Business Domain Tables Specification",
                "paragraphs": [
                    "The business domain models an Academic Management System enforcing realistic relational hierarchies, check constraints, and cascading updates:"
                ],
                "table": {
                    "data": [
                        ["Table Name", "Primary Key", "Foreign Keys", "Check Constraints & Invariants"],
                        ["departments", "dept_id (INT)", "None", "CHECK (budget >= 0), dept_code UNIQUE"],
                        ["instructors", "instructor_id (INT)", "dept_id -> departments(dept_id)", "CHECK (salary >= 0), email UNIQUE"],
                        ["courses", "course_id (INT)", "dept_id, instructor_id", "CHECK (credits > 0 AND credits <= 12)"],
                        ["students", "student_id (INT)", "dept_id -> departments(dept_id)", "email VARCHAR(150), age, gpa (3,2)"],
                        ["enrollments", "enrollment_id (INT)", "student_id, course_id", "UNIQUE(student_id, course_id), grade_marks <= 100"]
                    ],
                    "widths": [90, 110, 150, 150]
                }
            },
            {
                "title": "4.3 The Role of Unconstrained Staging & Quarantine Tables",
                "paragraphs": [
                    "A cornerstone of the system's design is the architectural distinction between production tables (`enrollments`) and staging tables (`staging_enrollments`).",
                    "The staging table deliberately omits physical foreign key constraints. This simulates a real enterprise staging zone where external data imports (such as legacy system transfers or CSV batch uploads) can land without crashing the database, allowing our Integrity Scanner to inspect, isolate, and heal records prior to final production insertion.",
                    "When an irreparable or high-risk violation is detected, the `quarantine_records` table acts as a safe landing zone. The entire row is serialized into JSON with diagnostic reason tags before being safely excised from active tables, ensuring zero data loss."
                ]
            },
            {
                "title": "4.4 System Engine, Audit & Recovery Tables Dictionary",
                "paragraphs": [
                    "The system maintains state, audit trails, and snapshot recovery points across nine dedicated engine tables:"
                ],
                "table": {
                    "data": [
                        ["Engine Table", "Primary Key", "Core Column Attributes", "Engine Responsibility"],
                        ["integrity_rules", "rule_id", "rule_code, rule_type, target_table, parameters_json", "Configurable catalog of validation predicates"],
                        ["scan_runs", "scan_id", "scan_type, start_time, end_time, issues_found, status", "Execution history of all full/table inspection scans"],
                        ["integrity_issues", "issue_id", "scan_id, rule_code, table_name, record_id, status", "Granular catalog of detected data anomalies"],
                        ["repair_recommendations", "recommendation_id", "issue_id, strategy, proposed_action, risk_level", "Generated healing proposals awaiting approval"],
                        ["repair_executions", "execution_id", "issue_id, transaction_id, before_state, after_state", "Permanent record of atomic repair executions"],
                        ["audit_logs", "event_id", "event_type, actor, timestamp, action_description", "Immutable audit trail with credential redaction"],
                        ["transaction_logs", "transaction_id", "status, operations_count, rollback_reason, duration", "Low-level transaction lifecycle recording"],
                        ["recovery_checkpoints", "checkpoint_id", "target_table, snapshot_rows_json, status", "Pre-repair table state snapshots for rollback"],
                        ["database_metadata", "meta_key", "meta_value, updated_at", "System key-value configuration and version store"]
                    ],
                    "widths": [110, 80, 160, 150]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 5
    # =========================================================================
    chapters.append({
        "title": "Dynamic Schema Metadata Discovery via INFORMATION_SCHEMA",
        "kid_summary": (
            "Instead of hardcoding table names like a lazy robot, our system walks into the database library "
            "and reads the master card catalog (called INFORMATION_SCHEMA). It discovers all columns, keys, "
            "and rules dynamically at runtime!"
        ),
        "sections": [
            {
                "title": "5.1 Why Hardcoded Schemas Are Prohibited",
                "paragraphs": [
                    "A major flaw of legacy DBMS academic projects is hardcoding table names and column definitions directly into backend controllers. If a new column is added or a table is renamed, hardcoded systems immediately crash.",
                    "The Self-Healing System utilizes dynamic metadata reflection. When initialized, the engine queries MySQL's internal `INFORMATION_SCHEMA` tables to inspect table types, column nullability, primary key constraints, foreign key mappings, and index topologies on the fly."
                ]
            },
            {
                "title": "5.2 SQL Injection Defense via Strict Identifier Allowlisting",
                "paragraphs": [
                    "Because table and column names in SQL cannot be bound using standard parameter substitution (`?` or `%s`), dynamic schema exploration poses an inherent SQL Injection risk if user input is concatenated into queries.",
                    "To guarantee total security, our database layer implements the `validate_identifier()` guardian. Every table and column identifier must pass a strict regex allowlist before being used in any dynamic query:"
                ],
                "code": (
                    "IDENTIFIER_REGEX = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')\n\n"
                    "def validate_identifier(name: str) -> str:\n"
                    "    if not name or not IDENTIFIER_REGEX.match(name):\n"
                    "        raise ValueError(f'Security Violation: Invalid SQL identifier: {name}')\n"
                    "    return name"
                )
            },
            {
                "title": "5.3 Core Introspection Queries",
                "paragraphs": [
                    "The backend executes standard introspection queries against MySQL catalogs:"
                ],
                "code": (
                    "-- 1. Discover all active user tables\n"
                    "SELECT table_name, table_type, engine, table_rows\n"
                    "FROM information_schema.tables\n"
                    "WHERE table_schema = 'self_healing_test_db';\n\n"
                    "-- 2. Discover detailed column definitions and constraints\n"
                    "SELECT column_name, data_type, is_nullable, column_default, column_key\n"
                    "FROM information_schema.columns\n"
                    "WHERE table_schema = 'self_healing_test_db' AND table_name = %s\n"
                    "ORDER BY ordinal_position;\n\n"
                    "-- 3. Discover all physical foreign key relationships\n"
                    "SELECT table_name AS child_table, column_name AS child_column,\n"
                    "       referenced_table_name AS parent_table, referenced_column_name AS parent_column\n"
                    "FROM information_schema.key_column_usage\n"
                    "WHERE table_schema = 'self_healing_test_db' AND referenced_table_name IS NOT NULL;"
                )
            }
        ]
    })

    # =========================================================================
    # CHAPTER 6
    # =========================================================================
    chapters.append({
        "title": "Relational Graph Theory & NetworkX Dependency Modeling",
        "kid_summary": (
            "We turn all 16 tables into a giant Family Tree using dots and arrows (a Directed Graph). "
            "An arrow points from parents to children. We use smart math to check if the arrows form a trap loop (cycles) "
            "and calculate the exact safe order to clean up rooms without tripping over each other!"
        ),
        "sections": [
            {
                "title": "6.1 Mathematical Formulation of the Relational Graph",
                "paragraphs": [
                    "Relational integrity enforcement requires understanding the multi-tier dependency topology between tables. The system models the database as a Directed Graph using the `NetworkX` library:",
                    "$$G = (V, E)$$",
                    "Where vertices $V$ represent database tables, and directed edges $e = (P, C) \in E$ represent referential dependencies pointing from the parent (referenced) table $P$ to the child (referencing) table $C$."
                ]
            },
            {
                "title": "6.2 Cycle Detection and Prevention Algorithm",
                "paragraphs": [
                    "In relational design, circular foreign keys (Table A references Table B, which references Table C, which references Table A) create catastrophic locking deadlocks during cascading operations. The `DependencyAnalyzer` actively evaluates acyclicity:",
                    "$$\\text{IsAcyclic} \\iff \\text{nx.is\\_directed\\_acyclic\\_graph}(G) = \\text{True}$$",
                    "If cycles exist, the engine executes `nx.simple_cycles(G)` to locate every circular loop, alerts administrators on the dashboard, and disables automatic cascading deletes to avoid infinite recursion."
                ]
            },
            {
                "title": "6.3 Topological Sorting for Safe Multi-Table Operations",
                "paragraphs": [
                    "When performing data imports or cleanups, operations must occur in strict dependency order. In reverse topological order, child tables are cleared or detached before parent tables are touched:",
                    "$$\\text{DeletionOrder} = \\text{list}(\\text{reversed}(\\text{list}(\\text{nx.topological\\_sort}(G))))$$",
                    "This guarantees that referential integrity constraints are never violated during bulk migrations."
                ],
                "table": {
                    "data": [
                        ["Topological Rank", "Table Node", "Relationship Type", "Dependency Rationale"],
                        ["Rank 1 (Root Parents)", "departments", "Independent Root", "Has zero incoming foreign keys; safe to seed first."],
                        ["Rank 2 (Direct Dependents)", "instructors, students", "Level 1 Dependents", "Depend directly on departments; require valid dept_id."],
                        ["Rank 3 (Catalog Nodes)", "courses", "Level 2 Dependents", "Depends on both departments and instructors."],
                        ["Rank 4 (Terminal Junctions)", "enrollments", "Leaf Child Junction", "Depends on both students and courses; must be seeded last."]
                    ],
                    "widths": [110, 120, 110, 160]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 7
    # =========================================================================
    chapters.append({
        "title": "Cascading Blast Radius Analysis & Deterministic Risk Matrix",
        "kid_summary": (
            "Before we touch any broken record, we calculate its 'Blast Radius'—just like checking how many "
            "standing dominoes will fall if you push the first one over! If touching one record will hurt 50 other records, "
            "the system screams: 'CRITICAL RISK! DANGER!' and requires extra human confirmation."
        ),
        "sections": [
            {
                "title": "7.1 Mathematical Definition of Relational Blast Radius",
                "paragraphs": [
                    "The Relational Blast Radius defines the maximum theoretical boundary of data that could be corrupted, altered, or orphaned if a modification or deletion is applied to table $T$:",
                    "$$\\text{BlastRadius}(T) = \\text{Descendants}(G, T) = \\{ u \\in V \\mid \\exists \\text{ directed path from } T \\text{ to } u \\}$$",
                    "$$\\text{BlastRadiusTableCount}(T) = |\\text{Descendants}(G, T)|$$",
                    "For example, deleting a record in `departments` has a downstream blast radius spanning `instructors`, `courses`, `students`, and `enrollments` ($|\\text{BlastRadius}| = 4$)."
                ]
            },
            {
                "title": "7.2 Live Referential Row Introspection",
                "paragraphs": [
                    "Knowing which tables *could* be affected is not enough. The `DependencyAnalyzer` inspects actual live rows in the database to count exactly how many child rows currently point to the specific target primary key:",
                    "$$\\text{MatchingChildRows}(r_{\\text{pk}}) = \\sum_{C \\in \\text{Children}(P)} \\text{COUNT}(*) \\text{ WHERE } C.\\text{fk} = r_{\\text{pk}}$$"
                ]
            },
            {
                "title": "7.3 The Multi-Factor Risk Decision Matrix",
                "paragraphs": [
                    "The system classifies repair proposals into risk tiers using a deterministic multi-factor decision matrix:"
                ],
                "table": {
                    "data": [
                        ["Issue Severity", "Repair Action", "Live Dependent Rows?", "Downstream Children?", "Assigned Risk Tier"],
                        ["CRITICAL", "DELETE / QUARANTINE", "Yes (> 0)", "Yes", "CRITICAL (Maximum Danger)"],
                        ["CRITICAL", "SET_DEFAULT", "No (0)", "No", "HIGH"],
                        ["HIGH", "DELETE / QUARANTINE", "Any", "Yes", "CRITICAL"],
                        ["HIGH", "MAP_PARENT", "No (0)", "No", "HIGH"],
                        ["MEDIUM", "DELETE / QUARANTINE", "Yes (> 0)", "Yes", "CRITICAL"],
                        ["MEDIUM", "SET_DEFAULT", "No (0)", "Yes", "MEDIUM"],
                        ["LOW", "SET_DEFAULT", "No (0)", "No", "LOW (Safe Automated)"]
                    ],
                    "widths": [80, 130, 110, 100, 80]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 8
    # =========================================================================
    chapters.append({
        "title": "The Five Anomaly Taxonomies & Relational Algebra Detection Queries",
        "kid_summary": (
            "We wrote special magnifying-glass queries for all five types of mistakes: "
            "1) LEFT JOIN searches for ghost kids, 2) GROUP BY searches for twins, "
            "3) IS NULL searches for invisible names, 4) Inequality signs search for 140-year-old students, "
            "and 5) Regex searches for emails missing the @ sign!"
        ),
        "sections": [
            {
                "title": "8.1 Anomaly Category 1: Orphan Records (Broken Foreign Keys)",
                "paragraphs": [
                    "An orphan record is a child row containing a non-NULL foreign key pointing to a primary key value that does not exist in the referenced parent table.",
                    "$$\\mathcal{O} = \\{ r \\in \\text{Child} \\mid r.\\text{fk} \\neq \\text{NULL} \\land \\neg\\exists p \\in \\text{Parent} (p.\\text{pk} = r.\\text{fk}) \\}$$"
                ],
                "code": (
                    "-- Detection SQL using relational anti-join\n"
                    "SELECT c.staging_id, c.student_id, c.external_ref\n"
                    "FROM staging_enrollments c\n"
                    "LEFT JOIN students p ON c.student_id = p.student_id\n"
                    "WHERE p.student_id IS NULL AND c.student_id IS NOT NULL;"
                )
            },
            {
                "title": "8.2 Anomaly Category 2: Duplicate Candidate Keys (Entity Collision)",
                "paragraphs": [
                    "A candidate key duplicate occurs when multiple records share identical logical attributes that should uniquely identify an entity, bypassing physical constraints in staging tables.",
                    "$$\\mathcal{D} = \\{ g \\in \\text{Groups}(K) \\mid \\text{COUNT}(g) > 1 \\}$$"
                ],
                "code": (
                    "-- Detection SQL grouping candidate keys\n"
                    "SELECT student_id, course_id, COUNT(*) AS group_count,\n"
                    "       GROUP_CONCAT(staging_id ORDER BY staging_id ASC) AS all_ids\n"
                    "FROM staging_enrollments\n"
                    "GROUP BY student_id, course_id\n"
                    "HAVING COUNT(*) > 1;"
                )
            },
            {
                "title": "8.3 Anomaly Category 3: Mandatory NULL and Empty String Breaches",
                "paragraphs": [
                    "Occurs when an essential attribute lacks a valid value, including both physical database NULLs and whitespace-padded empty strings.",
                    "$$\\text{Violation}(r) \\iff (r.\\text{col} \\text{ IS NULL}) \\lor (\\text{TRIM}(r.\\text{col}) = '')$$"
                ],
                "code": (
                    "-- Detection SQL for mandatory attribute omission\n"
                    "SELECT student_id, student_name\n"
                    "FROM students\n"
                    "WHERE student_name IS NULL OR TRIM(student_name) = '';"
                )
            },
            {
                "title": "8.4 Anomaly Category 4: Domain Range Violations",
                "paragraphs": [
                    "Occurs when numeric values violate real-world operational bounds, such as test marks outside $[0.00, 100.00]$ or student age outside $[16, 65]$.",
                    "$$\\text{Violation}(x) \\iff (x < \\text{MinVal}) \\lor (x > \\text{MaxVal})$$"
                ],
                "code": (
                    "-- Detection SQL for domain range violations\n"
                    "SELECT staging_id, grade_marks\n"
                    "FROM staging_enrollments\n"
                    "WHERE grade_marks < 0.00 OR grade_marks > 100.00;"
                )
            },
            {
                "title": "8.5 Anomaly Category 5: Domain Enumeration & Regex Syntax Violations",
                "paragraphs": [
                    "Enforces finite set membership for state variables and structural compliance for formatted strings:",
                    "$$\\text{EnumViolation}(s) \\iff s \\notin \\{ \\text{'ENROLLED'}, \\text{'COMPLETED'}, \\text{'DROPPED'} \\}$$",
                    "$$\\text{RegexViolation}(e) \\iff e \\not\\sim \\text{`^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$`}$$"
                ],
                "code": (
                    "-- Detection SQL for status codes and email syntax\n"
                    "SELECT staging_id, status FROM staging_enrollments\n"
                    "WHERE status NOT IN ('ENROLLED', 'COMPLETED', 'DROPPED');"
                )
            }
        ]
    })

    # =========================================================================
    # CHAPTER 9
    # =========================================================================
    chapters.append({
        "title": "The Autonomous Self-Healing Engine & Non-Destructive Previews",
        "kid_summary": (
            "Before any surgery, our doctor puts on safety goggles and shows the human operator a side-by-side hologram: "
            "'Here is the sick record on the left, here is how it will look healed on the right, and here is the exact SQL command.' "
            "We have 4 healing strategies: Quarantine, Default Values, Parent Re-linking, and Safe Deletion."
        ),
        "sections": [
            {
                "title": "9.1 The Five-Stage Healing Lifecycle",
                "paragraphs": [
                    "To prevent catastrophic administrative accidents, every self-healing operation passes through five mandatory governance stages:",
                    "1. Detection: The scanner identifies the anomaly and inserts an `OPEN` issue.",
                    "2. Synthesis: The engine generates a structured `repair_recommendations` entry.",
                    "3. Preview Generation: The engine constructs a non-mutating preview capturing the Before State, simulated After State, SQL query, and risk rating.",
                    "4. Operator Approval: High-risk and critical repairs require explicit operator confirmation; values for empty fields must be provided by the administrator.",
                    "5. Transactional Execution: The engine executes the repair inside an atomic InnoDB transaction protected by row locks and recovery checkpoints."
                ]
            },
            {
                "title": "9.2 The Four Supported Healing Strategies",
                "paragraphs": [
                    "The system implements four distinct healing strategies designed for different anomaly contexts:"
                ],
                "table": {
                    "data": [
                        ["Strategy Code", "Operational Action", "Data Loss Risk", "Typical Usage Context"],
                        ["QUARANTINE", "Archives entire row as JSON in quarantine_records, then deletes from active table.", "Zero Data Loss (Archived)", "Corrupted staging rows with invalid parent references."],
                        ["SET_DEFAULT", "Updates the defective column with a validated default or admin-provided value.", "Zero Data Loss (In-Place)", "Missing names, empty emails, or out-of-range scores."],
                        ["MAP_PARENT", "Updates the broken foreign key to point to an authoritative existing parent ID.", "Zero Data Loss (Re-linked)", "Orphan staging enrollments with known parent students."],
                        ["DELETE_RECORD", "Permanently deletes the duplicate or unrecoverable record from the source table.", "Irreversible Deletion", "Identical duplicate submissions in staging tables."]
                    ],
                    "widths": [90, 160, 110, 140]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 10
    # =========================================================================
    chapters.append({
        "title": "Cryptographic Row-Version Tokens & Concurrency Control",
        "kid_summary": (
            "What if two people try to fix the same record at the exact same second? "
            "Our system takes a digital fingerprint (SHA-256 hash) of the record during the preview. "
            "If anyone sneaks in and changes even one letter before you click Confirm, the fingerprint won't match, "
            "and the system shouts: 'STOP! The record has changed!'"
        ),
        "sections": [
            {
                "title": "10.1 The Phantom Modification Problem",
                "paragraphs": [
                    "In multi-user database systems, a severe vulnerability exists known as a Stale Preview Hazard. An administrator opens a repair preview for Record #8. While they are reviewing the screen, another process or user edits or deletes Record #8. If the administrator clicks 'Execute', the repair would blindly overwrite the newly modified data.",
                    "To achieve absolute concurrency control, the `RepairEngine` implements an Optimistic Concurrency Token based on a SHA-256 cryptographic digest."
                ]
            },
            {
                "title": "10.2 Canonical JSON Hashing Algorithm",
                "paragraphs": [
                    "The row state is normalized into a sorted, deterministic dictionary where all keys are sorted alphabetically and all datetime objects are converted to ISO 8601 strings:",
                    "$$\\text{CanonicalRow} = \\text{SortKeys}(\\{ k: \\text{Normalize}(v) \\mid (k, v) \\in \\text{Row} \\})$$",
                    "$$\\text{RowVersionToken} = \\text{SHA-256}(\\text{UTF8}(\\text{JSON}(\\text{CanonicalRow})))$$"
                ],
                "code": (
                    "# Exact Token Verification at Execution Time\n"
                    "current_token = hashlib.sha256(\n"
                    "    json.dumps(current_row, sort_keys=True, default=str).encode('utf-8')\n"
                    ").hexdigest()\n\n"
                    "if expected_token and current_token != expected_token:\n"
                    "    raise StalePreviewError(\n"
                    "        'Concurrency Conflict: The record was modified by another process '\n"
                    "        'after this preview was generated. Please refresh the preview.'\n"
                    "    )"
                )
            },
            {
                "title": "10.3 Pessimistic Row Locking (`SELECT ... FOR UPDATE`)",
                "paragraphs": [
                    "Once the token matches, the engine switches to Pessimistic Locking during execution. It issues `SELECT * FROM tbl WHERE id = %s FOR UPDATE`. This tells MySQL InnoDB to acquire an exclusive row-level write lock, preventing any other concurrent transaction from reading or altering the row until our healing transaction finishes."
                ]
            }
        ]
    })

    # =========================================================================
    # CHAPTER 11
    # =========================================================================
    chapters.append({
        "title": "Transaction Safeguards & ACID Property Implementation",
        "kid_summary": (
            "ACID is a superhero shield for databases! It means: Atomicity (All or Nothing), "
            "Consistency (Never break the rules), Isolation (Don't let others peek while cooking), "
            "and Durability (Once written, it stays forever even if power cuts off). "
            "We built interactive simulations demonstrating all of them!"
        ),
        "sections": [
            {
                "title": "11.1 The InnoDB ACID Engine in Practice",
                "paragraphs": [
                    "Relational integrity cannot exist without strict transaction management. The project relies on the MySQL InnoDB engine with `autocommit=False` to enforce the four ACID pillars:",
                    "• Atomicity: An entire repair operation executes as a single unit. If any sub-query fails, `conn.rollback()` restores the exact pre-transaction state.",
                    "• Consistency: Triggers and foreign keys validate relational invariants before committing.",
                    "• Isolation: REPEATABLE READ transaction isolation ensures queries see a consistent snapshot.",
                    "• Durability: Once `conn.commit()` is confirmed, write-ahead redo logs guarantee persistence."
                ]
            },
            {
                "title": "11.2 The Three Interactive Demonstration Scenarios",
                "paragraphs": [
                    "The application includes an interactive Transaction Simulator executing real InnoDB operations on the live server:"
                ],
                "table": {
                    "data": [
                        ["Scenario Name", "Operational Sequence", "Expected State Verification", "ACID Principle Proven"],
                        ["COMMIT_SUCCESS", "START TRANSACTION -> Insert record -> Verify intermediate state -> COMMIT", "Final Count = Initial Count + 1", "Durability & Atomic State Transition"],
                        ["SIMULATED_FAILURE_ROLLBACK", "START TRANSACTION -> Insert record -> Encounter simulated error -> ROLLBACK", "Final Count = Initial Count (Zero rows leaked)", "Atomicity (All-or-Nothing Rollback)"],
                        ["SAVEPOINT_PARTIAL_ROLLBACK", "START TRANSACTION -> Insert A -> SAVEPOINT sp1 -> Insert B -> ROLLBACK TO sp1 -> COMMIT", "Record A persists; Record B completely revoked", "Selective Transaction Recovery (Savepoints)"]
                    ],
                    "widths": [120, 160, 110, 110]
                }
            },
            {
                "title": "11.3 Transaction SQL Traces",
                "paragraphs": [
                    "The exact SQL sequence executed during partial savepoint rollback:"
                ],
                "code": (
                    "START TRANSACTION; /* Autocommit disabled */\n"
                    "INSERT INTO staging_enrollments (staging_id, external_ref, student_id, course_id, status)\n"
                    "VALUES (9001, 'TX-A', 101, 1, 'ENROLLED');\n"
                    "SAVEPOINT sp_step1;\n"
                    "INSERT INTO staging_enrollments (staging_id, external_ref, student_id, course_id, status)\n"
                    "VALUES (9002, 'TX-B', 999, 999, 'INVALID');\n"
                    "ROLLBACK TO SAVEPOINT sp_step1;\n"
                    "COMMIT;\n"
                    "-- Verification: Record 9001 exists; Record 9002 was undone!"
                )
            }
        ]
    })

    # =========================================================================
    # CHAPTER 12
    # =========================================================================
    chapters.append({
        "title": "Application-Level Recovery Engine & Snapshot Checkpoints",
        "kid_summary": (
            "Before the doctor makes any changes, it takes a high-resolution photocopy of the whole room. "
            "If the human operator later changes their mind, they click 'Restore Checkpoint', "
            "and the room magically reverts to the exact snapshot photocopy!"
        ),
        "sections": [
            {
                "title": "12.1 Why Table-Level Checkpoints Are Necessary",
                "paragraphs": [
                    "Transaction rollback only protects operations within the active database connection. Once a transaction is committed, standard database rollbacks cannot undo it.",
                    "To provide post-commit recovery, the `RecoveryManager` captures application-level snapshots. Before executing any high-risk repair, the engine captures a pre-repair checkpoint recording table DDL and row states as structured JSON inside `recovery_checkpoints`."
                ]
            },
            {
                "title": "12.2 Checkpoint Capturing and Restoration Workflow",
                "paragraphs": [
                    "During snapshot creation:",
                    "1. Captures `SHOW CREATE TABLE tbl` to store table structure.",
                    "2. Captures `SELECT * FROM tbl` to serialize all rows into JSON.",
                    "3. Assigns a unique ID (`CKPT-XXXXXX`) and marks status as `ACTIVE`.",
                    "During restoration, the engine verifies that snapshot row counts match actual rows, checks foreign key constraints, upserts missing records, and deletes records added after the checkpoint was captured."
                ]
            },
            {
                "title": "12.3 Mathematical State Verification",
                "paragraphs": [
                    "A restoration is only committed if post-restore verification satisfies two invariants:",
                    "$$\\text{ExpectedRowCount} = |\\text{SnapshotRows}|$$",
                    "$$\\text{ActualRowCount} = \\text{SELECT COUNT}(*) \\text{ FROM TargetTable}$$",
                    "$$\\text{Verified} \\iff (\\text{ExpectedRowCount} = \\text{ActualRowCount}) \\land (\\forall r \\in \\text{SnapshotRows}, r \\in \\text{TargetTable})$$"
                ]
            }
        ]
    })

    # =========================================================================
    # CHAPTER 13
    # =========================================================================
    chapters.append({
        "title": "Audit Trail Immutability & Sensitive Credential Redaction",
        "kid_summary": (
            "We have an unbreakable black box like on an airplane! "
            "Every scan, repair, and transaction is logged. If anyone tries to change or erase the log, "
            "MySQL triggers block them. And if someone types a secret password, the system automatically writes [REDACTED]!"
        ),
        "sections": [
            {
                "title": "13.1 Regulatory Audit Compliance in DBMS",
                "paragraphs": [
                    "Enterprise data compliance frameworks (such as SOX, HIPAA, and GDPR) mandate that database alterations must maintain a verifiable, tamper-evident audit trail.",
                    "The `AuditService` records all lifecycle events into the `audit_logs` table, storing actor identification, event type, affected record primary keys, before-and-after JSON snapshots, execution timing, and outcome status."
                ]
            },
            {
                "title": "13.2 Database Triggers Blocking UPDATE and DELETE",
                "paragraphs": [
                    "Application-level logging is insufficient if an administrator can directly execute `DELETE FROM audit_logs`. To achieve physical immutability, the schema installs native MySQL triggers that abort any update or deletion attempt with SQLSTATE 45000:"
                ],
                "code": (
                    "CREATE TRIGGER `trg_audit_logs_no_update`\n"
                    "BEFORE UPDATE ON `audit_logs`\n"
                    "FOR EACH ROW\n"
                    "BEGIN\n"
                    "    SIGNAL SQLSTATE '45000'\n"
                    "    SET MESSAGE_TEXT = 'CRITICAL: audit_logs entries are immutable and cannot be updated.';\n"
                    "END;\n\n"
                    "CREATE TRIGGER `trg_audit_logs_no_delete`\n"
                    "BEFORE DELETE ON `audit_logs`\n"
                    "FOR EACH ROW\n"
                    "BEGIN\n"
                    "    SIGNAL SQLSTATE '45000'\n"
                    "    SET MESSAGE_TEXT = 'CRITICAL: audit_logs entries are immutable and cannot be deleted.';\n"
                    "END;"
                )
            },
            {
                "title": "13.3 Sensitive Credential Redaction Filter",
                "paragraphs": [
                    "Before serializing before-and-after states into audit JSON, all dictionaries pass through the redaction sanitizer. Any key matching sensitive substrings (`password`, `secret`, `token`, `pwd`, `hash`, `credit_card`) is masked with `[REDACTED]` to prevent credential leakage in audit records."
                ]
            }
        ]
    })

    # =========================================================================
    # CHAPTER 14
    # =========================================================================
    chapters.append({
        "title": "Comprehensive Walkthrough of All 11 Frontend Pages",
        "kid_summary": (
            "The website has 11 awesome screens: 1) Master Monitor, 2) Glass Cabinet Explorer, "
            "3) Family Tree Visualizer, 4) X-Ray Scanner, 5) Doctor's Problem List, 6) Surgery Preview Room, "
            "7) Time Machine Sandbox, 8) Photocopy Recovery Room, 9) Unbreakable Diary, "
            "10) School Rulebook, and 11) Testing Lab!"
        ),
        "sections": [
            {
                "title": "14.1 Dashboard & Navigation Hierarchy",
                "paragraphs": [
                    "The frontend application provides 11 cohesive dashboard views accessible via a persistent glassmorphism navigation sidebar:"
                ],
                "table": {
                    "data": [
                        ["Page Name", "Route Path", "Primary Visual Components", "User Actions"],
                        ["System Dashboard", "/", "Health Score StatCard, Severity PieChart, Category BarChart", "View live server ping, total tables, open anomalies."],
                        ["Database Explorer", "/database", "Table dropdown, Schema metadata grid, Live data table", "Inspect columns, primary/foreign keys, page through live rows."],
                        ["Dependency Visualizer", "/dependencies", "Interactive SVG DAG graph, Table neighborhood panel", "Pan/zoom relational nodes, click table to inspect parents/children."],
                        ["Integrity Scanner", "/scanner", "Scan scope selector, Rule checklist, Live progress bar", "Trigger Full Scan or Table Scan, inspect discovered issues."],
                        ["Issue Management", "/issues", "Severity/status filter pills, Raw JSON modal, Action buttons", "Review issues, mark ignored, launch Repair Preview modal."],
                        ["Repair Center", "/repairs", "Before/After diff viewer, Risk badge, SQL preview box", "Input custom values, verify tokens, execute atomic repairs."],
                        ["Transaction Simulator", "/transactions", "Scenario selector (Commit, Rollback, Savepoint), Timeline", "Execute live InnoDB transactions and observe atomicity steps."],
                        ["Recovery Center", "/recovery", "Snapshot cards, Create Checkpoint form, Restore button", "Capture manual snapshots, restore tables to previous state."],
                        ["Audit Logs", "/audit", "Search bar, Event type filters, JSON payload inspector", "Inspect immutable history of all scans, approvals, and repairs."],
                        ["Rules Configuration", "/rules", "Rule card grid, Toggle switches, Test Rule modal", "Enable/disable rules, edit parameters, dry-run test against DB."],
                        ["Settings & Diagnostics", "/settings", "Connection telemetry, Inject Demo Violations, Reset Baseline", "Inject 11 test anomalies or reset DB to clean baseline."]
                    ],
                    "widths": [100, 75, 175, 150]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 15
    # =========================================================================
    chapters.append({
        "title": "Complete REST API Specification & Endpoint Contracts",
        "kid_summary": (
            "The backend speaks a universal language called JSON. Every response comes inside a neat envelope "
            "with four stamps: success (did it work?), message (what happened?), data (the answer!), "
            "and error (what went wrong, if any)."
        ),
        "sections": [
            {
                "title": "15.1 The Standardized API Envelope Pattern",
                "paragraphs": [
                    "All FastAPI endpoints return a uniform response envelope conforming to the generic Pydantic model `ApiResponse[T]`:"
                ],
                "code": (
                    "{\n"
                    '  "success": true,\n'
                    '  "message": "Operation completed successfully.",\n'
                    '  "data": { ... },\n'
                    '  "error": null\n'
                    "}"
                )
            },
            {
                "title": "15.2 Key REST Endpoints Catalog",
                "paragraphs": [
                    "A representative summary of published REST API routes:"
                ],
                "table": {
                    "data": [
                        ["HTTP Method", "Endpoint Path", "Request Body / Params", "Operational Purpose"],
                        ["GET", "/api/health", "None", "Returns service status, database connectivity, latency."],
                        ["GET", "/api/database/status", "None", "Returns registered table counts, version, user."],
                        ["POST", "/api/scans", '{"scan_type": "FULL"}', "Initiates an integrity scan across active tables."],
                        ["GET", "/api/issues", "?status=OPEN&severity=HIGH", "Returns paginated list of detected anomalies."],
                        ["GET", "/api/repairs/preview/{id}", "None", "Generates non-destructive Before/After repair preview."],
                        ["POST", "/api/repairs/execute", '{"issue_id": "...", "strategy": "..."}', "Executes approved repair inside an InnoDB transaction."],
                        ["GET", "/api/dependencies/graph", "None", "Generates full NetworkX DAG nodes and edge topology."],
                        ["POST", "/api/transactions/demo", '{"scenario": "COMMIT_SUCCESS"}', "Runs interactive transaction simulation."],
                        ["POST", "/api/recovery/checkpoint", '{"target_table": "departments"}', "Captures table snapshot checkpoint."],
                        ["POST", "/api/database/reset-baseline", "None", "Resets database back to pristine academic baseline."]
                    ],
                    "widths": [65, 140, 145, 150]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 16
    # =========================================================================
    chapters.append({
        "title": "Automated Testing Suite & Verification Matrix",
        "kid_summary": (
            "We have 45 automated robot tests! They check everything: testing if database connections work, "
            "making sure SQL injection attacks fail, testing if rollbacks actually rewind data, "
            "and verifying that preview tokens block race conditions. All tests pass with flying colors!"
        ),
        "sections": [
            {
                "title": "16.1 Testing Methodology & Fixtures",
                "paragraphs": [
                    "The project includes an extensive test suite built on `pytest` and Starlette's `TestClient`. Tests are organized into standalone contract validation tests (which run without a live database) and integration tests (which execute real queries against MySQL)."
                ]
            },
            {
                "title": "16.2 Test Coverage by Module",
                "paragraphs": [
                    "Summary of the 45 test definitions distributed across the test suite:"
                ],
                "table": {
                    "data": [
                        ["Test Suite File", "Test Count", "Core Functionality Verified"],
                        ["test_api_endpoints.py", "14 tests", "Health check, 400 validation, 404 handling, CORS origins, table routes."],
                        ["test_connection.py", "3 tests", "SQL identifier validation allowlist, malicious injection rejection, connection diagnostics."],
                        ["test_dependency_analyzer.py", "3 tests", "DAG node discovery, table neighborhood traversal, cascading impact assessment."],
                        ["test_repair_engine.py", "3 tests", "Before/After previews, missing record auto-resolution, idempotent execution."],
                        ["test_set_default_preview.py", "6 tests", "Preview validation, admin input enforcement, stale preview rejection, rollback on failure."],
                        ["test_transaction_manager.py", "3 tests", "Atomic commit verification, simulated failure rollback count, savepoint preservation."],
                        ["test_recovery_manager.py", "2 tests", "Snapshot checkpoint creation, table state modification, verified state restoration."],
                        ["test_audit_service.py", "2 tests", "Sensitive credential redaction, immutable audit log insertion into database."],
                        ["test_scanner.py", "2 tests", "Integrity scan execution, anomaly detection counts, recommendation generation."],
                        ["test_unit.py", "7 tests", "Pure unit tests verifying schema models, regex validators, and utility helpers."]
                    ],
                    "widths": [130, 70, 300]
                }
            }
        ]
    })

    # =========================================================================
    # CHAPTER 17
    # =========================================================================
    chapters.append({
        "title": "Local Deployment, Setup Wizard & Administration Guide",
        "kid_summary": (
            "Getting the project running is as easy as 1-2-3! "
            "We wrote an automated 1-click Python setup script that checks your MySQL, creates the database, "
            "builds all 16 tables, and loads the data automatically so anyone can run it!"
        ),
        "sections": [
            {
                "title": "17.1 Prerequisites & Environment Setup",
                "paragraphs": [
                    "To run the system locally, three prerequisites are required:",
                    "1. Python 3.10+ (Python 3.11, 3.12, or 3.13 supported).",
                    "2. Node.js 18+ and npm.",
                    "3. MySQL Server running on port 3306 (via XAMPP or standalone)."
                ]
            },
            {
                "title": "17.2 The 1-Click Automated Setup Wizard (`setup_database.py`)",
                "paragraphs": [
                    "To eliminate manual configuration errors, the project provides `setup_database.py`. After cloning, running this single command provisions the entire database automatically:"
                ],
                "code": (
                    "# Step 1: Install Python dependencies\n"
                    "pip install -r backend/requirements.txt\n\n"
                    "# Step 2: Run 1-Click Database Setup Wizard\n"
                    "python setup_database.py\n\n"
                    "# Step 3: Start FastAPI Backend Server\n"
                    "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload\n\n"
                    "# Step 4: Install Frontend Dependencies & Start Vite Server\n"
                    "cd frontend && npm install && npm run dev"
                )
            }
        ]
    })

    # =========================================================================
    # CHAPTER 18
    # =========================================================================
    chapters.append({
        "title": "Oral Exam & Viva Defense Master Preparation (30 In-Depth Q&As)",
        "kid_summary": (
            "Here are the top 30 questions professors love to ask during exams! "
            "We give you crystal-clear, rock-solid answers so you can explain every single detail with confidence."
        ),
        "sections": [
            {
                "title": "18.1 Core Theoretical Concepts",
                "paragraphs": [
                    "<b>Q1: What is the core academic objective of this project?</b><br/>"
                    "A: To design and implement a human-supervised, transaction-safe database integrity engine for MySQL InnoDB that decouples anomaly detection, dependency analysis, healing recommendations, preview generation, and atomic remediation.",
                    "<b>Q2: What is an orphan record?</b><br/>"
                    "A: An orphan record is a child row containing a non-NULL foreign key pointing to a primary key value that does not exist in the referenced parent table.",
                    "<b>Q3: Why use an unconstrained staging table instead of enforcing foreign keys directly?</b><br/>"
                    "A: In real-world enterprise ETL pipelines, external batch data regularly contains anomalies. If physical foreign keys were enforced on staging tables, the database would reject the entire import on the first error. Unconstrained staging tables allow raw data ingestion, programmatic detection, and healing prior to production promotion.",
                    "<b>Q4: Why is LEFT JOIN used for orphan detection instead of INNER JOIN?</b><br/>"
                    "A: An INNER JOIN discards non-matching rows. A LEFT JOIN preserves all child rows and outputs NULL for parent attributes whenever a matching parent is missing, allowing the predicate `WHERE parent.pk IS NULL AND child.fk IS NOT NULL` to isolate orphans.",
                    "<b>Q5: How does duplicate candidate key detection work?</b><br/>"
                    "A: It executes `GROUP BY` on the candidate key columns with `HAVING COUNT(*) > 1`. The lowest primary key in each group is treated as canonical, and all subsequent primary keys are flagged as duplicate anomalies."
                ]
            },
            {
                "title": "18.2 Graph Theory & Cascading Blast Radius",
                "paragraphs": [
                    "<b>Q6: Why is NetworkX used in a relational database project?</b><br/>"
                    "A: To model table dependencies as a Directed Graph $G = (V, E)$, enabling cycle detection (`nx.simple_cycles`), topological sorting, and transitive reachability analysis.",
                    "<b>Q7: What is a Relational Blast Radius?</b><br/>"
                    "A: The complete set of downstream dependent tables reachable from a target table along directed foreign key edges: $\\text{BlastRadius}(T) = \\text{Descendants}(G, T)$.",
                    "<b>Q8: How does the system determine whether a repair is safe to execute?</b><br/>"
                    "A: By combining issue severity, destructive intent (DELETE vs SET_DEFAULT), downstream child table counts, and live child row counts into a deterministic Multi-Factor Risk Matrix."
                ]
            },
            {
                "title": "18.3 Concurrency, Transactions & Recovery",
                "paragraphs": [
                    "<b>Q9: What is a Stale Preview Hazard?</b><br/>"
                    "A: A race condition where a record is altered by a concurrent process after an administrator generates a repair preview but before they execute it.",
                    "<b>Q10: How does the system prevent stale previews?</b><br/>"
                    "A: By computing a SHA-256 Row-Version Token from canonicalized row JSON during preview and verifying that the token matches under an exclusive row-level lock (`SELECT ... FOR UPDATE`) before execution.",
                    "<b>Q11: What happens if an error occurs during repair execution?</b><br/>"
                    "A: The engine immediately triggers `conn.rollback()`, completely reverting all intermediate SQL operations and leaving active tables in their pristine pre-transaction state.",
                    "<b>Q12: How do audit logs achieve physical immutability?</b><br/>"
                    "A: Through native MySQL database triggers (`trg_audit_logs_no_update` and `trg_audit_logs_no_delete`) that intercept any UPDATE or DELETE statement and abort it with SQLSTATE 45000."
                ]
            }
        ]
    })

    # =========================================================================
    # CHAPTER 19
    # =========================================================================
    chapters.append({
        "title": "Technical Limitations, Security Hardening & Future Scope",
        "kid_summary": (
            "Every honest engineer talks about what can be improved! "
            "In future versions, we can add user logins with passwords, support distributed cloud databases, "
            "and add AI suggestions to recommend realistic replacement values for missing data."
        ),
        "sections": [
            {
                "title": "19.1 Current Technical Boundaries",
                "paragraphs": [
                    "A rigorous engineering evaluation acknowledges current system limitations:",
                    "1. Connection Pooling: The current PyMySQL driver creates connections per operation rather than managing a persistent pooled connection pool.",
                    "2. Single-Tenant Scope: The system is designed for single-database instances; cross-database distributed integrity across sharded clusters is not implemented.",
                    "3. Strategy Coverage: Strategies `RESTORE_PARENT` and `MERGE_DUPLICATE` are declared in the enumeration catalog but require manual human execution in version 2.4.0."
                ]
            },
            {
                "title": "19.2 Security Hardening Roadmap",
                "paragraphs": [
                    "• Role-Based Access Control (RBAC): Integrate JWT authentication and role-based permissions (Admin, Operator, Auditor).",
                    "• Recursive Audit Redaction: Expand the shallow dictionary redaction sanitizer to recursively inspect deeply nested JSON lists and objects."
                ]
            }
        ]
    })

    # =========================================================================
    # CHAPTER 20
    # =========================================================================
    chapters.append({
        "title": "Appendix, Project Glossary & File Manifest",
        "kid_summary": (
            "Here is the master dictionary and map of every single file in the project! "
            "Whenever you want to know which Python file or SQL script does what, check this page."
        ),
        "sections": [
            {
                "title": "20.1 Technical Glossary",
                "paragraphs": [
                    "• ACID: Atomicity, Consistency, Isolation, Durability — the four fundamental properties of transactional databases.",
                    "• Anti-Join: A relational query pattern (`LEFT JOIN ... WHERE parent.pk IS NULL`) used to isolate unreferenced child records.",
                    "• Directed Acyclic Graph (DAG): A directed graph with no closed loops, used to represent valid relational dependency hierarchies.",
                    "• Immutability: An architectural property guaranteeing that logged records cannot be edited or erased once created."
                ]
            },
            {
                "title": "20.2 Source Code Repository Manifest",
                "paragraphs": [
                    "Directory structure and file responsibilities in Release 2.4.0:"
                ],
                "table": {
                    "data": [
                        ["File Path", "Module Layer", "Primary Technical Responsibility"],
                        ["backend/app/main.py", "FastAPI App", "Application entry point, CORS middleware, router registration."],
                        ["backend/app/services/integrity_scanner.py", "Scanner Service", "Dynamic metadata querying, rule evaluation, issue persistence."],
                        ["backend/app/services/dependency_analyzer.py", "Graph Service", "NetworkX DAG modeling, cycle detection, blast radius assessment."],
                        ["backend/app/services/repair_engine.py", "Healing Service", "Non-destructive previews, SHA-256 tokens, ACID repair execution."],
                        ["backend/app/services/transaction_manager.py", "ACID Simulator", "Commit, rollback, and savepoint demonstration workflows."],
                        ["backend/app/services/recovery_manager.py", "Recovery Service", "Table snapshot checkpointing, row restoration, state verification."],
                        ["backend/app/services/audit_service.py", "Audit Service", "Event logging, sensitive credential redaction, trigger integration."],
                        ["setup_database.py", "Setup Wizard", "Automated 1-click database, table, rule, and demo violation provisioner."],
                        ["database/01-05 SQL Scripts", "SQL Schema", "Database creation, InnoDB tables, sample baseline, rules, demo violations."]
                    ],
                    "widths": [150, 100, 250]
                }
            }
        ]
    })

    return chapters
