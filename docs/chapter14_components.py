"""
Chapter 14 Component-by-Component Deep Dive
Detailed technical breakdown of every single visual and interactive component
across all 11 frontend pages in the application.
"""

def get_chapter14_sections():
    sections = []

    # =========================================================================
    # PAGE 1: SYSTEM HEALTH DASHBOARD (/)
    # =========================================================================
    sections.append({
        "title": "14.1 Page 1: System Health Dashboard (`/`) — Comprehensive Component Architecture",
        "paragraphs": [
            "The System Health Dashboard serves as the central flight control room of the application, rendering live database telemetry, anomaly distribution charts, and real-time operational event streams. Below is the granular breakdown of all five core components on this page:"
        ]
    })

    # Component 1.1
    sections.append({
        "title": "14.1.1 Component 1: Live Server Health & Latency Telemetry Gauge",
        "paragraphs": [
            "• Visual Wireframe Role: Header pill displaying a green pulsing status indicator, connected database name (`self_healing_test_db`), MySQL engine version, and round-trip TCP socket ping latency in milliseconds.",
            "• 10-Year-Old Explanation: The Doctor's Stethoscope. Just like a stethoscope listens to your heartbeat, this widget constantly pings the database vault to check if MySQL is awake and how fast it answers.",
            "• Underlying DBMS Concept: Client-Server Socket Communication and Telemetry Ping. Measures connection establishment overhead, network buffer round-trip time, and thread pool responsiveness in MySQL.",
            "• Directional Data Flow: On component mount, the React `useEffect` hook dispatches an asynchronous Axios GET request to `/api/health`. FastAPI invokes `test_database_connection()` via PyMySQL, which records start time, executes metadata queries, records completion time, and computes latency delta.",
            "• Mathematical Formula: Latency in milliseconds is calculated as: $$\\text{Latency}_{\\text{ms}} = (t_{\\text{response}} - t_{\\text{dispatch}}) \\times 1000$$"
        ],
        "code": (
            "-- Live Telemetry Diagnostic Query\n"
            "SELECT VERSION() AS server_version, CURRENT_USER() AS connected_user;\n"
            "-- Verifies that MySQL server process is alive and responsive."
        )
    })

    # Component 1.2
    sections.append({
        "title": "14.1.2 Component 2: Overall Database Health Score StatCard & Radial Progress Meter",
        "paragraphs": [
            "• Visual Wireframe Role: Prominent top card displaying an overall 0-100% database integrity purity score with dynamic color grading (Emerald Green > 90%, Amber 70-90%, Crimson Red < 70%) and a circular SVG progress track.",
            "• 10-Year-Old Explanation: The School Health Report Card. Like getting an A+ grade on a school test when all your homework is turned in, this gauge tells you how close your database is to 100% perfection.",
            "• Underlying DBMS Concept: Relational Integrity Ratio and Anomaly Prevalence Metric. Quantifies data consistency by measuring the proportion of clean records against unique records compromised by referential, domain, or candidate key violations.",
            "• Directional Data Flow: React fetches open issue counts from `/api/issues?status=OPEN` and total table row counts from `/api/database/status`. The frontend memoizes the score using `useMemo` and dynamically animates the SVG circular stroke offset.",
            "• Mathematical Formula: The Health Score formula balances total rows against unique compromised entities: $$\\text{Health Score} = \\max\\left(0, \\; 100 - \\left( \\frac{U_{\\text{issues}}}{N_{\\text{total\\_records}}} \\times 100 \\right)\\right)$$"
        ],
        "code": (
            "-- Query to calculate total schema records\n"
            "SELECT table_name, table_rows \n"
            "FROM information_schema.tables \n"
            "WHERE table_schema = 'self_healing_test_db';\n\n"
            "-- Query to count unique open anomalous records\n"
            "SELECT COUNT(DISTINCT table_name, record_id) AS unique_broken_rows \n"
            "FROM integrity_issues \n"
            "WHERE status = 'OPEN';"
        )
    })

    # Component 1.3
    sections.append({
        "title": "14.1.3 Component 3: Anomaly Severity Distribution Pie Chart",
        "paragraphs": [
            "• Visual Wireframe Role: Interactive Recharts SVG Pie Chart breaking down open violations into four color-coded slices: CRITICAL (Red `#EF4444`), HIGH (Orange `#F97316`), MEDIUM (Amber `#F59E0B`), and LOW (Blue `#3B82F6`), complete with animated tooltips and percentage legends.",
            "• 10-Year-Old Explanation: The Danger Pie. A colorful pizza chart showing how many big emergencies (broken bones) vs medium scrapes vs tiny papercuts exist in the school drawers.",
            "• Underlying DBMS Concept: Priority Queue Triage and Constraint Severity Weighting. Organizes database violations by their potential for catastrophic cascading side-effects.",
            "• Directional Data Flow: Backend groups `integrity_issues` by severity enum. The resulting JSON dictionary is mapped into Recharts `Pie` data array with custom `Cell` fills.",
            "• Mathematical Formula: S-slice percentage: $$\\text{Percentage}(s) = \\left( \\frac{\\text{Count}(s)}{\\sum_{k \\in \\{\\text{CRITICAL, HIGH, MEDIUM, LOW}\\}} \\text{Count}(k)} \\right) \\times 100$$"
        ],
        "code": (
            "-- Grouping open issues by severity tier\n"
            "SELECT severity, COUNT(*) AS issue_count \n"
            "FROM integrity_issues \n"
            "WHERE status = 'OPEN' \n"
            "GROUP BY severity \n"
            "ORDER BY FIELD(severity, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW');"
        )
    })

    # Component 1.4
    sections.append({
        "title": "14.1.4 Component 4: Anomaly Category Distribution Bar Chart",
        "paragraphs": [
            "• Visual Wireframe Role: Recharts Vertical Bar Chart displaying violation volume across the five fundamental anomaly taxonomies (ORPHAN, DUPLICATE, NULL_CHECK, DOMAIN_CHECK, RELATIONAL).",
            "• 10-Year-Old Explanation: The Monster Comparison Towers. Tower blocks showing whether we have more Ghost Kids, more Evil Twins, or more Missing Names.",
            "• Underlying DBMS Concept: Relational Algebra Anomaly Taxonomy. Distinguishes between referential foreign key anti-joins, candidate key collisions, domain boundary violations, and nullability breaches.",
            "• Directional Data Flow: API endpoint `/api/database/status` issues a SQL `GROUP BY category` query. Frontend transforms keys into human-readable labels and binds to SVG `<BarChart>`.",
            "• Mathematical Formula: Category Rank: $$\\text{Rank}(C) = \\text{ArgSort}(\\text{Count}(C))$$"
        ],
        "code": (
            "-- Grouping issues across categorical taxonomy\n"
            "SELECT category, COUNT(*) AS count \n"
            "FROM integrity_issues \n"
            "GROUP BY category \n"
            "ORDER BY count DESC;"
        )
    })

    # Component 1.5
    sections.append({
        "title": "14.1.5 Component 5: Recent Scan Runs & Live Audit Stream Feed",
        "paragraphs": [
            "• Visual Wireframe Role: Dual split scrollable data tables rendering the last 5 completed scan executions (Scan ID, Type, Issues Detected, Timing) and the last 5 audit events with user actor badges.",
            "• 10-Year-Old Explanation: The Doctor's Daily Diary. A running list showing who opened the drawers, who ran the x-ray machine, and what changes were made in the last hour.",
            "• Underlying DBMS Concept: Temporal Event Streaming and Transactional History Audit. Provides immediate situational awareness and operational traceability.",
            "• Directional Data Flow: Dispatched via parallel Axios `Promise.all([api.getScans({limit: 5}), api.getAuditLogs({limit: 5})])`. Renders responsive glassmorphic table rows."
        ],
        "code": (
            "-- Fetch recent scan runs\n"
            "SELECT scan_id, scan_type, start_time, total_rows_inspected, issues_found, status \n"
            "FROM scan_runs ORDER BY start_time DESC LIMIT 5;\n\n"
            "-- Fetch recent audit events\n"
            "SELECT event_id, event_type, actor, timestamp, action_description, result \n"
            "FROM audit_logs ORDER BY timestamp DESC LIMIT 5;"
        )
    })

    # =========================================================================
    # PAGE 2: DATABASE EXPLORER (/database)
    # =========================================================================
    sections.append({
        "title": "14.2 Page 2: Database Explorer (`/database`) — Interactive Catalog Inspection",
        "paragraphs": [
            "The Database Explorer allows administrators to inspect live schema structures, column data types, foreign key hierarchies, and paginated row data directly from MySQL catalogs."
        ]
    })

    # Component 2.1
    sections.append({
        "title": "14.2.1 Component 1: Searchable Table Selector Dropdown & Tier Badges",
        "paragraphs": [
            "• Visual Wireframe Role: Searchable combobox dropdown listing all 16 tables categorized with colored tier pills: Blue for Business Domain, Purple for Staging, Emerald for Safety/Quarantine, and Slate for System Engine.",
            "• 10-Year-Old Explanation: The Magic Drawer Key. You pick which drawer you want to open and inspect with your flashlight.",
            "• Underlying DBMS Concept: Data Catalog Reflection via `INFORMATION_SCHEMA.TABLES`. Avoids hardcoding and reflects new tables automatically upon database schema revision.",
            "• Directional Data Flow: When selected, updates React state `selectedTable`. Triggers parallel API requests to fetch schema columns (`/api/database/schema/{table}`) and live row data (`/api/database/tables/{table}/data`)."
        ],
        "code": (
            "SELECT table_name, table_type, engine, table_rows \n"
            "FROM information_schema.tables \n"
            "WHERE table_schema = 'self_healing_test_db' \n"
            "ORDER BY table_name ASC;"
        )
    })

    # Component 2.2
    sections.append({
        "title": "14.2.2 Component 2: Schema Metadata Specification Grid Tab",
        "paragraphs": [
            "• Visual Wireframe Role: Interactive specification table displaying Column Name, MySQL Physical Storage Type, Nullable Constraint (`YES`/`NO`), Default Expression, Primary Key badge (Gold Key icon), and Foreign Key target references.",
            "• 10-Year-Old Explanation: The Drawer's Instruction Manual. Shows what kind of Lego bricks fit into each slot (numbers, names, dates) and which slots are strictly required.",
            "• Underlying DBMS Concept: Data Definition Language (DDL) Dictionary. Dynamic query against `INFORMATION_SCHEMA.COLUMNS` exposing column ordinal positions and storage attributes.",
            "• Directional Data Flow: Renders column array into responsive styled table rows with copy-to-clipboard icons for quick column name reference."
        ],
        "code": (
            "SELECT column_name, data_type, column_type, is_nullable, column_default, column_key \n"
            "FROM information_schema.columns \n"
            "WHERE table_schema = 'self_healing_test_db' AND table_name = %s \n"
            "ORDER BY ordinal_position;"
        )
    })

    # Component 2.3
    sections.append({
        "title": "14.2.3 Component 3: Live Data Grid with Offset Pagination & Sorting",
        "paragraphs": [
            "• Visual Wireframe Role: Responsive data grid rendering live records with previous/next page controls, row limit selector (25, 50, 100), and clickable column sort headers.",
            "• 10-Year-Old Explanation: The Glass Window. Lets you look straight into the drawer to see the actual student cards and teacher badges.",
            "• Underlying DBMS Concept: Relational Selection ($\\sigma$), Projection ($\\pi$), and Offset-Based Buffer Pagination. Avoids memory exhaustion by fetching rows in bounded batches.",
            "• Mathematical Formula: $$\\text{Offset} = (\\text{PageNumber} - 1) \\times \\text{PageLimit}$$",
            "• Exact SQL: `SELECT * FROM \\`courses\\` ORDER BY \\`course_id\\` ASC LIMIT 50 OFFSET 0;`"
        ]
    })

    # Component 2.4
    sections.append({
        "title": "14.2.4 Component 4: Dynamic SQL Injection Prevention Guardian",
        "paragraphs": [
            "• Visual Wireframe Role: Security validation middleware intercepting any table or column parameter before SQL dispatch.",
            "• 10-Year-Old Explanation: The Security Bouncer. Checks every name card to make sure no trickster wrote code to blow up the school.",
            "• Underlying DBMS Concept: Identifier Allowlisting and Parameterized Isolation. Because table names in SQL cannot be bound with prepared statements, strict regex filtering is mandatory.",
            "• Mathematical Formula: $$\\text{IsValidIdentifier}(w) \\iff w \\in \\mathcal{L}\\left(\\text{`^[a-zA-Z_][a-zA-Z0-9_]*$`}\\right)$$"
        ]
    })

    # =========================================================================
    # PAGE 3: RELATIONAL DEPENDENCY VISUALIZER (/dependencies)
    # =========================================================================
    sections.append({
        "title": "14.3 Page 3: Relational Dependency Visualizer (`/dependencies`) — DAG Topology",
        "paragraphs": [
            "The Dependency Visualizer maps the complete relational schema as an interactive Directed Acyclic Graph (DAG), rendering parent-child foreign key hierarchies and computing cascading blast radiuses."
        ]
    })

    # Component 3.1
    sections.append({
        "title": "14.3.1 Component 1: Interactive SVG Directed Graph Canvas",
        "paragraphs": [
            "• Visual Wireframe Role: Full-screen interactive vector canvas rendering database tables as circular nodes and foreign keys as directed bezier curves with glowing arrowheads.",
            "• 10-Year-Old Explanation: The Big Family Tree Map. Circles represent drawers, and arrows show which drawer holds hands with which other drawer.",
            "• Underlying DBMS Concept: Directed Graph $G = (V, E)$ modeling foreign key relationships where edge $(P, C)$ represents child table $C$ referencing parent table $P$."
        ]
    })

    # Component 3.2
    sections.append({
        "title": "14.3.2 Component 2: Schema Acyclicity & Cycle Detection Indicator",
        "paragraphs": [
            "• Visual Wireframe Role: Header pill displaying a green checkmark 'Schema is Acyclic (DAG)' or a flashing red warning badge 'Circular Referential Loop Detected!'.",
            "• 10-Year-Old Explanation: The Loop Warning Bell. Rings if the arrows form a trap circle (A needs B, B needs C, C needs A) that would jam the computer forever.",
            "• Underlying DBMS Concept: Directed Cycle Detection and Deadlock Hazard Prevention using `NetworkX`.",
            "• Mathematical Formula: $$\\text{HasCycle}(G) \\iff \\text{nx.is\\_directed\\_acyclic\\_graph}(G) = \\text{False}$$"
        ]
    })

    # Component 3.3
    sections.append({
        "title": "14.3.3 Component 3: Table Neighborhood Inspector Sidebar",
        "paragraphs": [
            "• Visual Wireframe Role: Split sidebar panel displaying the selected table's Direct Parents, Direct Children, Upstream Ancestors, and Downstream Descendants.",
            "• 10-Year-Old Explanation: The Family Inspector. Click on 'courses' and it shows you its parents ('departments', 'instructors') and its children ('enrollments').",
            "• Underlying DBMS Concept: Subgraph Extraction, In-Degree/Out-Degree Analysis, and Transitive Reachability.",
            "• Mathematical Formulas: $$\\text{Parents}(T) = \\{ u \\mid (u, T) \\in E \\}, \\quad \\text{Children}(T) = \\{ v \\mid (T, v) \\in E \\}$$",
            "• Exact SQL: Queries `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` to isolate referenced and referencing table pairs."
        ]
    })

    # Component 3.4
    sections.append({
        "title": "14.3.4 Component 4: Cascading Blast Radius Calculator",
        "paragraphs": [
            "• Visual Wireframe Role: Interactive impact calculator allowing operators to enter a Record ID and compute exactly how many downstream child rows would be impacted by modification.",
            "• 10-Year-Old Explanation: The Domino Counter. Calculates how many standing dominoes will topple over if you knock down this one card.",
            "• Underlying DBMS Concept: Cascading Referential Integrity and Transitive Blast Radius Analysis.",
            "• Mathematical Formula: $$\\text{BlastRadius}(T) = \\text{Descendants}(G, T), \\quad |\\text{BlastRadius}| = \\text{TableCount}$$",
            "• Exact SQL: Executes `SELECT COUNT(*) FROM child WHERE fk_col = %s` for each child table."
        ]
    })

    # =========================================================================
    # PAGE 4: INTEGRITY SCANNER (/scanner)
    # =========================================================================
    sections.append({
        "title": "14.4 Page 4: Integrity Scanner (`/scanner`) — Anomaly Detection Console",
        "paragraphs": [
            "The Integrity Scanner provides fine-grained controls to execute automated validation passes across active database tables, evaluating rules and persisting discovered anomalies."
        ]
    })

    # Component 4.1
    sections.append({
        "title": "14.4.1 Component 1: Scan Scope Selector & Table Checkbox Matrix",
        "paragraphs": [
            "• Visual Wireframe Role: Scope toggle allowing operators to choose between a Full Database Scan (all 16 tables) or a Targeted Table Scan with multi-select checkboxes.",
            "• 10-Year-Old Explanation: The Search Zone Chooser. Tells the robot doctor whether to inspect the entire school or just check the Science classroom.",
            "• Underlying DBMS Concept: Scan Scope Partitioning and Workload Isolation. Allows testing single staging tables without incurring lock contention across production tables."
        ]
    })

    # Component 4.2
    sections.append({
        "title": "14.4.2 Component 2: Interactive Rule Selection Checklist",
        "paragraphs": [
            "• Visual Wireframe Role: Checklist displaying all 16 active rules with severity badges, allowing operators to include or bypass specific validation checks.",
            "• 10-Year-Old Explanation: The Rule Checklist. You can tell the robot: 'Only look for ghost kids today, ignore age checks for now.'",
            "• Underlying DBMS Concept: Predicate Dispatching and Rule Masking. Loads only enabled rules matching `is_enabled = TRUE` from `integrity_rules`."
        ]
    })

    # Component 4.3
    sections.append({
        "title": "14.4.3 Component 3: Scan Progress Meter & Millisecond Timer",
        "paragraphs": [
            "• Visual Wireframe Role: Animated progress bar showing live execution percentage, active table name being inspected, and elapsed time in milliseconds.",
            "• 10-Year-Old Explanation: The Progress Bar and Stopwatch. Shows you how fast the robot is reading the drawers.",
            "• Mathematical Formula: Scan Duration: $$\\Delta t = (t_{\\text{finish}} - t_{\\text{start}}) \\times 1000 \\text{ ms}$$"
        ]
    })

    # Component 4.4
    sections.append({
        "title": "14.4.4 Component 4: Discovered Anomalies Summary Grid",
        "paragraphs": [
            "• Visual Wireframe Role: Summary cards showing Total Rows Inspected, Total Issues Found, Critical Count, and High Count, followed by a detailed findings table with 'Inspect Issue' action buttons.",
            "• 10-Year-Old Explanation: The Results Board. Shows the total count of sick records found and gives you a button to fix each one.",
            "• Exact SQL: Inserts detected anomalies into `integrity_issues` with status `OPEN`."
        ]
    })

    # =========================================================================
    # PAGE 5: ISSUE MANAGEMENT CENTER (/issues)
    # =========================================================================
    sections.append({
        "title": "14.5 Page 5: Issue Management Center (`/issues`) — Triage & Governance",
        "paragraphs": [
            "The Issue Management Center provides an administrative triage console for filtering, inspecting, reviewing, and approving detected database violations."
        ]
    })

    # Component 5.1
    sections.append({
        "title": "14.5.1 Component 1: Multi-Filter Pill Bar (Status & Severity)",
        "paragraphs": [
            "• Visual Wireframe Role: Interactive filter pills allowing instant multi-criteria filtering by Lifecycle Status (`OPEN`, `REVIEWED`, `APPROVED`, `REPAIRED`, `IGNORED`, `FAILED`) and Severity.",
            "• 10-Year-Old Explanation: The Sorting Bins. Click 'Emergency' to see only the red cards, or click 'Fixed' to see cards the doctor already healed.",
            "• Underlying DBMS Concept: Finite State Machine (FSM) Lifecycle Governance. Enforces that issues transition through formal review states before healing.",
            "• Mathematical State Transition: $$\\text{OPEN} \\xrightarrow{\\text{review}} \\text{REVIEWED} \\xrightarrow{\\text{approve}} \\text{APPROVED} \\xrightarrow{\\text{execute}} \\text{REPAIRED}$$"
        ]
    })

    # Component 5.2
    sections.append({
        "title": "14.5.2 Component 2: Live Raw Record JSON Inspector Modal",
        "paragraphs": [
            "• Visual Wireframe Role: Modal window displaying the live database record formatted as syntax-highlighted JSON, allowing operators to verify the surrounding row context.",
            "• 10-Year-Old Explanation: The Record Magnifying Glass. Lets you read the entire student card to see their grade, email, and age all at once.",
            "• Underlying DBMS Concept: Point Primary Key Fetch. Issues a parameterized `SELECT * FROM tbl WHERE pk = %s` against the live InnoDB table."
        ]
    })

    # Component 5.3
    sections.append({
        "title": "14.5.3 Component 3: Administrative Triage Actions (Review & Ignore)",
        "paragraphs": [
            "• Visual Wireframe Role: Action buttons allowing operators to mark an issue as 'Reviewed' or mark as 'Ignored' with a mandatory modal prompting for administrator justification notes.",
            "• 10-Year-Old Explanation: The Doctor's Notes. You can stamp the card as 'Checked' or write: 'Ignore this because it's a test student.'",
            "• Exact SQL: `UPDATE integrity_issues SET status = 'IGNORED', ignored_reason = %s WHERE issue_id = %s;`"
        ]
    })

    # =========================================================================
    # PAGE 6: REPAIR CENTER & PREVIEW ROOM (/repairs)
    # =========================================================================
    sections.append({
        "title": "14.6 Page 6: Repair Center & Non-Destructive Preview Room (`/repairs`) — Safe Remediation",
        "paragraphs": [
            "The Repair Center is the surgical theater of the system, enforcing non-destructive Before/After comparisons, optimistic concurrency tokens, and human input validation before transaction dispatch."
        ]
    })

    # Component 6.1
    sections.append({
        "title": "14.6.1 Component 1: Before State vs Proposed After State Split Cards",
        "paragraphs": [
            "• Visual Wireframe Role: Side-by-side split cards comparing the exact current row in the database against the proposed healed state, with modified fields highlighted in emerald green.",
            "• 10-Year-Old Explanation: The Before-and-After Hologram. Shows what the card looks like right now on the left, and what it will look like when healed on the right.",
            "• Underlying DBMS Concept: Non-Destructive Simulation. Constructs the repaired row state in application memory without modifying the live database."
        ]
    })

    # Component 6.2
    sections.append({
        "title": "14.6.2 Component 2: Cryptographic SHA-256 Row-Version Token Card",
        "paragraphs": [
            "• Visual Wireframe Role: Card displaying the 64-character SHA-256 hash computed from the row state, guaranteeing that the record has not been altered since preview generation.",
            "• 10-Year-Old Explanation: The Digital Fingerprint. If anyone sneaks in and changes the card while you are looking at the screen, the fingerprint changes and the doctor stops!",
            "• Underlying DBMS Concept: Optimistic Concurrency Control (OCC) and Phantom Modification Defense.",
            "• Mathematical Formula: $$\\text{Token} = \\text{SHA-256}\\left( \\text{JSON}(\\text{SortKeys}(\\text{Row})) \\right)$$"
        ]
    })

    # Component 6.3
    sections.append({
        "title": "14.6.3 Component 3: Human Value Input Guardian Form",
        "paragraphs": [
            "• Visual Wireframe Role: Dynamic input form appearing whenever an empty mandatory attribute (like student name) is being healed, forcing the operator to type an authoritative legal replacement.",
            "• 10-Year-Old Explanation: The Missing Name Box. The robot will not guess a fake name; it makes the human type the student's real name.",
            "• Underlying DBMS Concept: Deterministic Imputation Guard. Rejects fabricated dummy placeholders and enforces real-world business accuracy."
        ]
    })

    # Component 6.4
    sections.append({
        "title": "14.6.4 Component 4: Parameterized SQL Preview Box",
        "paragraphs": [
            "• Visual Wireframe Role: Syntax-highlighted code block displaying the exact SQL statement (`UPDATE` or `INSERT ... DELETE`) that will be dispatched inside the transaction.",
            "• 10-Year-Old Explanation: The Exact Spell. Shows the exact magic words the computer will whisper to MySQL.",
            "• Exact SQL: Displays queries like `UPDATE students SET student_name = %s WHERE student_id = %s;`"
        ]
    })

    # Component 6.5
    sections.append({
        "title": "14.6.5 Component 5: Two-Stage Execution Confirmation Dialog",
        "paragraphs": [
            "• Visual Wireframe Role: Modal confirmation dialog requiring the operator to review the risk tier, check an 'I understand the impact' box, and click 'Confirm & Execute Repair'.",
            "• 10-Year-Old Explanation: The Double Safety Lock. Like pressing two red buttons at the same time to launch a spaceship, ensuring no accidental clicks."
        ]
    })

    # =========================================================================
    # PAGE 7: TRANSACTION SIMULATOR (/transactions)
    # =========================================================================
    sections.append({
        "title": "14.7 Page 7: Transaction Simulator (`/transactions`) — ACID Laboratory",
        "paragraphs": [
            "The Transaction Simulator provides an interactive educational laboratory demonstrating MySQL InnoDB transaction isolation, commit durability, automatic failure rollbacks, and partial savepoint recovery."
        ]
    })

    # Component 7.1
    sections.append({
        "title": "14.7.1 Component 1: Interactive Scenario Selector Cards",
        "paragraphs": [
            "• Visual Wireframe Role: Three selectable scenario cards: 1) `COMMIT_SUCCESS` (Atomicity & Durability), 2) `SIMULATED_FAILURE_ROLLBACK` (All-or-Nothing Rollback), and 3) `SAVEPOINT_PARTIAL_ROLLBACK` (Selective Undo).",
            "• 10-Year-Old Explanation: The Time Machine Game Mode. You pick whether you want to test saving the game, crashing and rewinding, or using a secret bookmark.",
            "• Underlying DBMS Concept: InnoDB Transaction Isolation and Multi-Statement ACID Boundaries."
        ]
    })

    # Component 7.2
    sections.append({
        "title": "14.7.2 Component 2: Step-by-Step Vertical Stepper Timeline",
        "paragraphs": [
            "• Visual Wireframe Role: Vertical timeline rendering each transaction milestone (`START TRANSACTION`, `INSERT`, `SAVEPOINT`, `ROLLBACK`, `COMMIT`) with millisecond duration timers.",
            "• 10-Year-Old Explanation: The Story Steps. Shows every move the computer made second-by-second.",
            "• Directional Data Flow: Dispatches `POST /api/transactions/demo` with scenario payload. Renders returned `steps` array into interactive stepper."
        ]
    })

    # Component 7.3
    sections.append({
        "title": "14.7.3 Component 3: State Snapshot & Atomicity Verification Badge",
        "paragraphs": [
            "• Visual Wireframe Role: Banner comparing Initial Table Row Count against Final Table Row Count, displaying a green 'Atomicity Verified: Initial Count = Final Count' badge on rollback.",
            "• 10-Year-Old Explanation: The Proof Badge. Proves that when the crash happened, zero fake cards were left behind.",
            "• Mathematical Verification: $$\\Delta N = N_{\\text{final}} - N_{\\text{initial}} = 0 \\quad (\\text{Atomic Rollback Confirmed})$$"
        ]
    })

    # =========================================================================
    # PAGE 8: RECOVERY CENTER (/recovery)
    # =========================================================================
    sections.append({
        "title": "14.8 Page 8: Recovery Center (`/recovery`) — Snapshot Management",
        "paragraphs": [
            "The Recovery Center manages application-level table snapshots, providing one-click point-in-time state restoration with mathematical row verification."
        ]
    })

    # Component 8.1
    sections.append({
        "title": "14.8.1 Component 1: Create Table Checkpoint Form",
        "paragraphs": [
            "• Visual Wireframe Role: Form allowing operators to select any table, assign a custom snapshot name, select snapshot type (`MANUAL`, `PRE_REPAIR`), and capture an instant checkpoint.",
            "• 10-Year-Old Explanation: The Photocopy Button. Takes a magic snapshot picture of the entire drawer and saves it in a safe vault.",
            "• Exact SQL: Executes `SHOW CREATE TABLE tbl` and `SELECT * FROM tbl` to serialize schema and data as JSON into `recovery_checkpoints`."
        ]
    })

    # Component 8.2
    sections.append({
        "title": "14.8.2 Component 2: Active Checkpoints History Grid",
        "paragraphs": [
            "• Visual Wireframe Role: Data table displaying Checkpoint ID (`CKPT-XXXXXX`), Target Table, Creation Timestamp, Captured Row Count, and Status (`ACTIVE`, `RESTORED`).",
            "• 10-Year-Old Explanation: The Snapshot Photo Album. Shows all the saved pictures you can restore back to.",
            "• Underlying DBMS Concept: Point-in-Time Application Recovery and Snapshot State Cataloging."
        ]
    })

    # Component 8.3
    sections.append({
        "title": "14.8.3 Component 3: One-Click Restore & Verification Modal",
        "paragraphs": [
            "• Visual Wireframe Role: Modal dialog that executes transactional restoration, deletes post-snapshot rows, upserts snapshot rows, and verifies post-state.",
            "• 10-Year-Old Explanation: The Magic Restore Wand. Pops the drawer back to exactly how it looked in the snapshot picture.",
            "• Mathematical Invariant: $$\\text{RestorationVerified} \\iff (\\text{Count}(\\text{Current}) = \\text{Count}(\\text{Snapshot})) \\land (\\text{PKs Match})$$"
        ]
    })

    # =========================================================================
    # PAGE 9: AUDIT TRAIL EXPLORER (/audit)
    # =========================================================================
    sections.append({
        "title": "14.9 Page 9: Audit Trail Explorer (`/audit`) — Compliance Ledger",
        "paragraphs": [
            "The Audit Trail Explorer exposes the immutable flight recorder of all system events, complete with credential redaction and trigger immutability notices."
        ]
    })

    # Component 9.1
    sections.append({
        "title": "14.9.1 Component 1: Audit Event Search & Filter Bar",
        "paragraphs": [
            "• Visual Wireframe Role: Search input filtering by Table Name, Record Identifier, Actor Identity (`ADMIN_USER`, `SYSTEM`), and Event Type (`SCAN_COMPLETED`, `REPAIR_EXECUTED`).",
            "• 10-Year-Old Explanation: The Secret Diary Searcher. Lets you search for any day or any student to see who touched their card.",
            "• Exact SQL: `SELECT * FROM audit_logs WHERE target_table = %s ORDER BY timestamp DESC LIMIT 50;`"
        ]
    })

    # Component 9.2
    sections.append({
        "title": "14.9.2 Component 2: Payload Inspector Modal with Redaction Tags",
        "paragraphs": [
            "• Visual Wireframe Role: Modal window displaying Before Values JSON and After Values JSON, showing sensitive keys masked with `[REDACTED]` tags.",
            "• 10-Year-Old Explanation: The Secret Marker. If someone wrote a password, the system covers it with black marker so nobody can steal it.",
            "• Underlying DBMS Concept: Data Privacy and Regulatory Masking (HIPAA / GDPR / SOX compliance)."
        ]
    })

    # Component 9.3
    sections.append({
        "title": "14.9.3 Component 3: Database Trigger Immutability Notice",
        "paragraphs": [
            "• Visual Wireframe Role: Permanent banner explaining that audit entries cannot be altered or deleted due to MySQL `BEFORE UPDATE` and `BEFORE DELETE` triggers.",
            "• 10-Year-Old Explanation: The Steel Lock. Explains that this diary is locked in steel; even the principal cannot erase pages.",
            "• Exact SQL: `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Audit logs are immutable.';`"
        ]
    })

    # =========================================================================
    # PAGE 10: RULES CONFIGURATION (/rules)
    # =========================================================================
    sections.append({
        "title": "14.10 Page 10: Rules Configuration (`/rules`) — Policy Management",
        "paragraphs": [
            "The Rules Configuration page allows administrators to inspect, toggle, edit, and dry-run test validation rules across the schema."
        ]
    })

    # Component 10.1
    sections.append({
        "title": "14.10.1 Component 1: Rule Cards Grid with Parameter Tags",
        "paragraphs": [
            "• Visual Wireframe Role: Responsive card grid displaying Rule Code, Target Table, Column, Severity Badge, and JSON parameter badges (e.g. `min: 16, max: 65`).",
            "• 10-Year-Old Explanation: The School Rulebook Posters. Cards on the wall showing the rules for each classroom.",
            "• Underlying DBMS Concept: Declarative Metadata Rule Catalog stored in `integrity_rules`."
        ]
    })

    # Component 10.2
    sections.append({
        "title": "14.10.2 Component 2: Runtime Active / Inactive Toggle Switches",
        "paragraphs": [
            "• Visual Wireframe Role: Instant toggle switches allowing operators to activate or deactivate any rule with immediate visual feedback.",
            "• 10-Year-Old Explanation: The Light Switches. Turn a rule on or off like flicking a classroom light switch.",
            "• Exact SQL: `UPDATE integrity_rules SET is_enabled = %s WHERE rule_id = %s;`"
        ]
    })

    # Component 10.3
    sections.append({
        "title": "14.10.3 Component 3: Dry-Run Test Rule Modal",
        "paragraphs": [
            "• Visual Wireframe Role: Modal that immediately executes the rule's SQL predicate against live tables and reports matching violation counts without modifying data.",
            "• 10-Year-Old Explanation: The Practice Drill. Tests the rule right now to see how many kids break it before officially turning it on.",
            "• Directional Data Flow: Dispatches `POST /api/rules/{id}/test`. Executes rule query via PyMySQL and returns detected count."
        ]
    })

    # =========================================================================
    # PAGE 11: SETTINGS & DIAGNOSTICS (/settings)
    # =========================================================================
    sections.append({
        "title": "14.11 Page 11: Settings & Diagnostics (`/settings`) — Testing Laboratory",
        "paragraphs": [
            "The Settings page provides system telemetry, environment configuration inspection, and demo data manipulation controls."
        ]
    })

    # Component 11.1
    sections.append({
        "title": "14.11.1 Component 1: Database Connection Telemetry Card",
        "paragraphs": [
            "• Visual Wireframe Role: Card displaying Host (`127.0.0.1`), Port (`3306`), Database (`self_healing_test_db`), Character Set (`utf8mb4`), and round-trip ping time.",
            "• 10-Year-Old Explanation: The Engine Room Speedometer. Shows the computer cables and how fast data is traveling.",
            "• Underlying DBMS Concept: Database Diagnostic Handshake and Connection Pool Health."
        ]
    })

    # Component 11.2
    sections.append({
        "title": "14.11.2 Component 2: 'Inject Demo Violations' Trigger Button",
        "paragraphs": [
            "• Visual Wireframe Role: Action button that executes `database/05_demo_violations.sql`, inserting 11 controlled anomalies across staging and student tables.",
            "• 10-Year-Old Explanation: The Practice Mess Maker. Plants 11 pretend mistakes into the school drawers so you can demonstrate the robot doctor to your teacher!",
            "• Exact SQL: Truncates `staging_enrollments` and inserts records with orphan student 999, orphan course 888, marks 145, age 140, GPA 4.95, and invalid status."
        ]
    })

    # Component 11.3
    sections.append({
        "title": "14.11.3 Component 3: 'Reset to Clean Baseline' Trigger Button",
        "paragraphs": [
            "• Visual Wireframe Role: Action button that executes `database/07_reset_demo_data.sql`, restoring pristine baseline academic data and clearing temporary anomalies.",
            "• 10-Year-Old Explanation: The Magic Eraser. Wipes away all the practice mistakes and makes the school 100% spotless and clean again.",
            "• Exact SQL: Deletes demo students with `student_id >= 200`, resets staging enrollments, and logs a baseline reset audit event."
        ]
    })

    return sections

