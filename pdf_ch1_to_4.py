# -*- coding: utf-8 -*-
"""Chapters 1 to 4: Architecture, 22 Tables Schema, Page-by-Page Deep Dive, Button Flows"""

from pdf_diagrams import SVG_SYSTEM_ARCHITECTURE, SVG_SEQUENCE_FLOW, SVG_RELATIONAL_ER

CH1_HTML = f"""
<div class="page-break">
  <h1>Chapter 1: System Overview & Complete Architecture</h1>
  
  <p>
    The <b>Self-Healing Relational Database Integrity System</b> (Version 2.4.0) is an enterprise-grade academic DBMS group project developed to provide automated, transactional, and transparent data integrity maintenance. Rather than treating database anomalies as terminal application crashes, this system continuously inspects MySQL InnoDB relational tables, discovers dangling foreign key references, detects candidate key duplications, flags domain range violations, and executes reversible, transaction-safe self-healing operations without taking the database offline.
  </p>

  <div class="callout callout-info">
    <div class="callout-title">System Identification & Runtime Environment</div>
    <table style="margin: 4px 0; border: none;">
      <tr style="background: transparent;"><td style="border: none; padding: 2px 6px; width: 180px;"><b>Project Title:</b></td><td style="border: none; padding: 2px 6px;">Self-Healing Relational Database Integrity System</td></tr>
      <tr style="background: transparent;"><td style="border: none; padding: 2px 6px;"><b>Database Server:</b></td><td style="border: none; padding: 2px 6px;">MySQL / MariaDB via XAMPP (10.4.32-MariaDB) on Port 3306</td></tr>
      <tr style="background: transparent;"><td style="border: none; padding: 2px 6px;"><b>Active Target Database:</b></td><td style="border: none; padding: 2px 6px;"><code>self_healing_test_db</code> (utf8mb4 / utf8mb4_unicode_ci)</td></tr>
      <tr style="background: transparent;"><td style="border: none; padding: 2px 6px;"><b>Backend Framework:</b></td><td style="border: none; padding: 2px 6px;">FastAPI 0.110+, Python 3.13, Uvicorn ASGI Server (Port 8000)</td></tr>
      <tr style="background: transparent;"><td style="border: none; padding: 2px 6px;"><b>Frontend Stack:</b></td><td style="border: none; padding: 2px 6px;">React 18, Vite 5, Tailwind CSS, Lucide React, Axios (Port 5173)</td></tr>
      <tr style="background: transparent;"><td style="border: none; padding: 2px 6px;"><b>Relational Engine:</b></td><td style="border: none; padding: 2px 6px;">InnoDB Storage Engine (Strict Foreign Key & Transaction Support)</td></tr>
    </table>
  </div>

  <h2>1.1 Four-Tier Architecture Model</h2>
  <p>
    The project is decoupled into four functional tiers to guarantee that data ingestion, scanning, self-healing, and audit logging cannot compromise the operational stability of core production business entities:
  </p>
  <ul>
    <li><b>Tier 1: Presentation Tier (React 18 + Vite):</b> Comprises 11 administrative single-page dashboard interfaces rendered client-side. Employs Axios HTTP interceptors communicating via a Vite proxy (<code>/api</code> targeting <code>http://127.0.0.1:8000</code>).</li>
    <li><b>Tier 2: Application / Engine Tier (FastAPI + Python):</b> Hosts modular autonomous engines including the Integrity Scanner, Repair Engine, Dependency Analyzer (NetworkX DAG), Ingestion Service, Transaction Manager, and Audit Service.</li>
    <li><b>Tier 3: Connection & Persistence Layer (PyMySQL):</b> Maintains isolated database connections with <code>autocommit=False</code>, strict SQL identifier regex validation (preventing injection), and dictionary result-set mapping.</li>
    <li><b>Tier 4: Relational Storage Tier (MySQL InnoDB):</b> Contains 22 tables grouped into four distinct functional schemas (Business Domain, Staging Buffers, System Engine, and Immutable Audit Trails).</li>
  </ul>

  <div class="diagram-box">
    {SVG_SYSTEM_ARCHITECTURE}
    <div class="diagram-caption">Figure 1.1: Complete 4-Tier Architectural Diagram of the Self-Healing DBMS</div>
  </div>

  <h2>1.2 End-to-End Request-Response Execution Lifecycle</h2>
  <p>
    Every interaction—from initiating a full scan to executing a transactional repair—follows a strict, deterministic sequence ensuring that unverified operations cannot mutate the database:
  </p>
  <div class="diagram-box">
    {SVG_SEQUENCE_FLOW}
    <div class="diagram-caption">Figure 1.2: End-to-End Sequence Flow from UI Action to MySQL Transaction Commit</div>
  </div>
</div>
"""

CH2_HTML = f"""
<div class="page-break">
  <h1>Chapter 2: Database Schema & Relational Modeling</h1>
  
  <p>
    The underlying database, <code>self_healing_test_db</code>, is fully provisioned using the MySQL <b>InnoDB storage engine</b> to support physical foreign key constraints, row-level locking, and strict ACID transaction semantics. The database is organized into <b>22 tables</b> distributed across 4 functional tiers:
  </p>

  <div class="diagram-box">
    {SVG_RELATIONAL_ER}
    <div class="diagram-caption">Figure 2.1: Entity-Relationship (ER) Diagram of the 22 Tables Across 4 Functional Tiers</div>
  </div>

  <h2>2.1 Tier 1: Business Domain Schema (6 InnoDB Tables)</h2>
  <p>Models an academic university management system with realistic relational hierarchies:</p>

  <table>
    <thead>
      <tr>
        <th>Table Name</th>
        <th>Primary Key</th>
        <th>Foreign Keys</th>
        <th>Key Attributes & Constraints</th>
        <th>Relational Purpose</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>departments</b></td>
        <td><code>dept_id</code> (INT AI)</td>
        <td>None (Root Reference Table)</td>
        <td><code>dept_code</code> (VARCHAR 20 NOT NULL), <code>dept_name</code> (VARCHAR 100 NOT NULL), <code>budget</code> (DECIMAL 12,2 DEFAULT 100000.00)</td>
        <td>Parent organizational entity for instructors, courses, students, and classrooms.</td>
      </tr>
      <tr>
        <td><b>instructors</b></td>
        <td><code>instructor_id</code> (INT AI)</td>
        <td><code>dept_id</code> -> <code>departments.dept_id</code> (ON DELETE SET NULL ON UPDATE CASCADE)</td>
        <td><code>instructor_name</code> (VARCHAR 100 NOT NULL), <code>email</code> (VARCHAR 150 NOT NULL), <code>salary</code> (DECIMAL 10,2 DEFAULT 50000.00), <code>hire_date</code> (DATE)</td>
        <td>Faculty member records. Child of departments.</td>
      </tr>
      <tr>
        <td><b>courses</b></td>
        <td><code>course_id</code> (INT AI)</td>
        <td>
          1. <code>dept_id</code> -> <code>departments.dept_id</code><br/>
          2. <code>instructor_id</code> -> <code>instructors.instructor_id</code>
        </td>
        <td><code>course_code</code> (VARCHAR 20 NOT NULL), <code>course_name</code> (VARCHAR 150 NOT NULL), <code>credits</code> (INT DEFAULT 3)</td>
        <td>Academic curriculum offerings. Child of departments and instructors.</td>
      </tr>
      <tr>
        <td><b>students</b></td>
        <td><code>student_id</code> (INT AI)</td>
        <td><code>dept_id</code> -> <code>departments.dept_id</code> (ON DELETE SET NULL)</td>
        <td><code>student_name</code> (VARCHAR 100 NOT NULL), <code>email</code> (VARCHAR 150 NOT NULL), <code>age</code> (INT), <code>gpa</code> (DECIMAL 3,2), <code>enrollment_year</code> (INT)</td>
        <td>Undergraduate and graduate student registry. Child of departments.</td>
      </tr>
      <tr>
        <td><b>enrollments</b></td>
        <td><code>enrollment_id</code> (INT AI)</td>
        <td>
          1. <code>student_id</code> -> <code>students.student_id</code> (ON DELETE RESTRICT)<br/>
          2. <code>course_id</code> -> <code>courses.course_id</code> (ON DELETE RESTRICT)
        </td>
        <td><code>enrolled_on</code> (DATE NOT NULL), <code>grade_marks</code> (DECIMAL 5,2), <code>status</code> (ENUM: 'ENROLLED', 'COMPLETED', 'DROPPED')</td>
        <td>Many-to-many junction entity associating students with course registrations.</td>
      </tr>
      <tr>
        <td><b>classrooms</b></td>
        <td><code>classroom_id</code> (INT AI)</td>
        <td><code>dept_id</code> -> <code>departments.dept_id</code> (ON DELETE SET NULL)</td>
        <td><code>room_number</code> (VARCHAR 50 NOT NULL), <code>building</code> (VARCHAR 100 NOT NULL), <code>capacity</code> (INT DEFAULT 30)</td>
        <td>Physical facilities and lecture halls assigned to academic departments.</td>
      </tr>
    </tbody>
  </table>

  <h2>2.2 Tier 2: Staging & Quarantine Schema (7 InnoDB Tables)</h2>
  <ul>
    <li><b>6 Staging Buffers (<code>staging_departments</code>, <code>staging_instructors</code>, <code>staging_courses</code>, <code>staging_students</code>, <code>staging_enrollments</code>, <code>staging_classrooms</code>):</b> Unconstrained landing tables containing identical columns to business tables plus <code>staging_id</code> (PK AI), <code>external_ref</code> (VARCHAR 50), <code>validation_status</code> (ENUM: 'PENDING', 'VALID', 'REJECTED', 'QUARANTINED'), and <code>validation_error</code> (TEXT). These tables decouple external batch ingestion from core production constraints.</li>
    <li><b><code>quarantine_records</code> (1 Table):</b> Fault-isolation landing zone for rejected, corrupt, or orphan rows. Contains <code>quarantine_id</code> (INT PK AI), <code>source_table</code> (VARCHAR 100), <code>source_pk_value</code> (VARCHAR 100), <code>issue_type</code> (VARCHAR 50), <code>row_data_json</code> (LONGTEXT), <code>quarantine_reason</code> (TEXT), <code>quarantined_by</code> (VARCHAR 100), <code>quarantined_at</code> (TIMESTAMP), <code>resolved</code> (BOOLEAN DEFAULT FALSE), and <code>resolution_notes</code> (TEXT).</li>
  </ul>

  <h2>2.3 Tier 3: System Engine & Repair Schema (5 InnoDB Tables)</h2>
  <ul>
    <li><b><code>integrity_rules</code>:</b> Dynamic catalog of integrity assertions. Columns: <code>rule_id</code> (PK AI), <code>rule_code</code> (VARCHAR 50 UNIQUE), <code>name</code>, <code>description</code>, <code>rule_type</code> (ENUM: 'ORPHAN', 'DUPLICATE', 'NULL_CHECK', 'DOMAIN_CHECK'), <code>target_table</code>, <code>target_column</code>, <code>parent_table</code>, <code>parent_column</code>, <code>parameters_json</code>, <code>severity</code> (ENUM: 'CRITICAL', 'HIGH', 'LOW'), <code>is_enabled</code> (BOOLEAN).</li>
    <li><b><code>scan_runs</code>:</b> Execution history of scanner invocations. Columns: <code>scan_id</code> (VARCHAR 50 PK), <code>scan_type</code> ('FULL'/'TABLE'), <code>target_tables</code>, <code>start_time</code>, <code>end_time</code>, <code>status</code> ('RUNNING', 'COMPLETED', 'FAILED'), <code>total_rows_inspected</code>, <code>issues_found</code>, <code>critical_count</code>, <code>high_count</code>, <code>low_count</code>, <code>error_message</code>.</li>
    <li><b><code>integrity_issues</code>:</b> Granular catalog of detected relational anomalies. Columns: <code>issue_id</code> (VARCHAR 50 PK), <code>scan_id</code>, <code>rule_id</code>, <code>rule_code</code>, <code>category</code>, <code>severity</code>, <code>table_name</code>, <code>record_id</code>, <code>column_name</code>, <code>invalid_value</code>, <code>description</code>, <code>status</code> ('OPEN', 'REVIEWED', 'APPROVED', 'REPAIRED', 'IGNORED').</li>
    <li><b><code>repair_recommendations</code>:</b> Proposed self-healing strategies for detected issues. Columns: <code>recommendation_id</code> (PK AI), <code>issue_id</code>, <code>strategy</code> (ENUM: 'MAP_PARENT', 'SET_DEFAULT', 'QUARANTINE', 'DELETE_RECORD', 'RESTORE_PARENT', 'MERGE_DUPLICATION', 'MANUAL_INTERVENTION'), <code>problem_description</code>, <code>proposed_action</code>, <code>reason</code>, <code>expected_impact</code>, <code>risk_level</code>, <code>is_reversible</code>, <code>requires_approval</code>, <code>approval_status</code> ('PENDING', 'APPROVED', 'REJECTED').</li>
    <li><b><code>repair_executions</code>:</b> Historical trace of executed repairs. Columns: <code>execution_id</code> (VARCHAR 50 PK), <code>issue_id</code>, <code>transaction_id</code>, <code>status</code> ('SUCCESS', 'FAILED', 'ROLLED_BACK'), <code>executed_by</code>, <code>executed_at</code>, <code>before_state_json</code>, <code>after_state_json</code>, <code>sql_executed</code>, <code>execution_time_ms</code>.</li>
  </ul>

  <h2>2.4 Tier 4: Audit Trails & Immutable Logs (4 InnoDB Tables)</h2>
  <ul>
    <li><b><code>audit_logs</code>:</b> Chronological log of administrative actions. Protected by database-level immutability triggers (<code>trg_audit_logs_no_update</code>, <code>trg_audit_logs_no_delete</code>). Columns: <code>event_id</code> (BIGINT PK AI), <code>event_type</code>, <code>actor</code>, <code>timestamp</code>, <code>related_scan_id</code>, <code>related_issue_id</code>, <code>related_transaction_id</code>, <code>action_description</code>, <code>target_table</code>, <code>record_identifier</code>, <code>result</code>, <code>before_values_json</code>, <code>after_values_json</code>, <code>error_message</code>.</li>
    <li><b><code>transaction_logs</code>:</b> Low-level transaction monitoring. Protected by triggers. Columns: <code>transaction_id</code> (VARCHAR 50 PK), <code>execution_id</code>, <code>start_time</code>, <code>end_time</code>, <code>status</code> ('COMMITTED', 'ROLLED_BACK'), <code>operations_count</code>, <code>duration_ms</code>.</li>
    <li><b><code>recovery_checkpoints</code>:</b> Point-in-time table state snapshots. Columns: <code>checkpoint_id</code> (VARCHAR 50 PK), <code>checkpoint_name</code>, <code>checkpoint_type</code> ('PRE_REPAIR', 'MANUAL'), <code>target_table</code>, <code>snapshot_metadata_json</code>, <code>snapshot_rows_json</code>, <code>status</code> ('ACTIVE', 'RESTORED').</li>
    <li><b><code>database_metadata</code>:</b> System key-value configuration. Columns: <code>meta_key</code> (VARCHAR 100 PK), <code>meta_value</code>, <code>updated_at</code>.</li>
  </ul>
</div>
"""

CH3_HTML = """
<div class="page-break">
  <h1>Chapter 3: Page-by-Page Source-Code Deep Dive</h1>
  <p>
    This chapter provides a source-code-verified analysis of all 11 user-facing frontend pages. Each page is examined across its architectural role, UI elements, React implementation, API endpoints, executing SQL queries, and underlying DBMS principles.
  </p>

  <h2>3.1 Dashboard (<code>DashboardPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>The Executive Mission Control Center provides high-level observability over database health, active database connectivity, integrity scores, table counts, open violations by severity, and recent audit events.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Header Bar:</b> System title, live status badge (<code>MySQL Connected</code> on port 3306), active database badge (<code>self_healing_test_db</code>).</li>
    <li><b>Buttons:</b> <code>Scan Entire Database</code> (triggers full scan and routes to <code>/scanner</code>), <code>Refresh Metrics</code> (re-fetches dashboard state).</li>
    <li><b>4 Metric StatCards:</b> Database Connection status, Relational Integrity Score (healthy row percentage), Total Managed Tables (22), Open Violations count.</li>
    <li><b>Severity Breakdown Card:</b> Color-coded pill counts for <code>CRITICAL</code>, <code>HIGH</code>, <code>LOW</code> violations.</li>
    <li><b>Quick Action Navigation:</b> Direct links to Recovery Center, Relational Explorer, Audit Trail, and Rules Catalog.</li>
    <li><b>Recent Scans Table:</b> Scan ID, scan type, inspected rows, issues count, and timestamp.</li>
    <li><b>Latest Audit Trail:</b> Live chronological feed of the last 6 administrative events.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/DashboardPage.jsx</code>. Uses React hooks <code>useState</code> for metrics and <code>useEffect</code> calling <code>loadDashboardData()</code>, which executes concurrent API calls via <code>Promise.all</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Dispatches concurrent requests to: <code>GET /api/database/status</code>, <code>GET /api/database/tables</code>, <code>GET /api/rules</code>, <code>GET /api/scans?limit=5</code>, <code>GET /api/issues?limit=100</code>, <code>GET /api/repairs/recommendations?approval_status=PENDING</code>, <code>GET /api/repairs/executions?limit=5</code>, and <code>GET /api/audit-logs?limit=6</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="cmt">-- 1. Introspect server version and active database user:</span>
<span class="kw">SELECT</span> <span class="fn">VERSION</span>() <span class="kw">AS</span> version, <span class="fn">CURRENT_USER</span>() <span class="kw">AS</span> user;

<span class="cmt">-- 2. Fetch table metadata across all 22 tables:</span>
<span class="kw">SELECT</span> t.TABLE_NAME, t.ENGINE, t.TABLE_ROWS, <span class="fn">COUNT</span>(<span class="kw">DISTINCT</span> c.COLUMN_NAME) <span class="kw">AS</span> col_count
<span class="kw">FROM</span> information_schema.TABLES t
<span class="kw">LEFT JOIN</span> information_schema.COLUMNS c 
  <span class="kw">ON</span> t.TABLE_SCHEMA = c.TABLE_SCHEMA <span class="kw">AND</span> t.TABLE_NAME = c.TABLE_NAME
<span class="kw">WHERE</span> t.TABLE_SCHEMA = <span class="fn">DATABASE</span>()
<span class="kw">GROUP BY</span> t.TABLE_NAME, t.ENGINE, t.TABLE_ROWS;

<span class="cmt">-- 3. Live row count queries per table:</span>
<span class="kw">SELECT</span> <span class="fn">COUNT</span>(*) <span class="kw">AS</span> live_count <span class="kw">FROM</span> <span class="tbl">`departments`</span>;
<span class="kw">SELECT</span> <span class="fn">COUNT</span>(*) <span class="kw">AS</span> live_count <span class="kw">FROM</span> <span class="tbl">`students`</span>;</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Metadata dictionary introspection via <code>information_schema</code>, non-blocking asynchronous state polling, mathematical integrity score heuristics.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.2 Database Schema & Object Explorer (<code>DatabaseExplorerPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Provides an interactive data dictionary allowing administrators to inspect physical table schemas, column data types, nullability, defaults, primary/foreign keys, indexes, and sample records.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Tier Filter Buttons:</b> Filter tables by <code>ALL</code>, <code>BUSINESS</code> (6), <code>STAGING</code> (6), <code>QUARANTINE</code> (1), <code>SYSTEM</code> (9).</li>
    <li><b>Search Bar & View Toggle:</b> Filter table names; toggle between compact List view and Card Grid view.</li>
    <li><b>Table Card/Row:</b> Shows table name, category badge, live row count, column count, PK flag, FK count, and storage engine.</li>
    <li><b>Inspect Schema Button (Eye Icon):</b> Opens the deep inspection modal.</li>
    <li><b>Scan This Table Button (ScanSearch Icon):</b> Deep-links to <code>/scanner?table={name}</code>.</li>
    <li><b>Modal Tabs:</b> Columns (data types, nullability, defaults), Indexes (BTREE mappings), Sample Data (top 50 rows).</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/DatabaseExplorerPage.jsx</code>. Uses <code>openTableDetails(tableName)</code> calling <code>databaseApi.getTableDetail(tableName)</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoints: <code>GET /api/database/tables</code> and <code>GET /api/database/tables/{tableName}</code> in <code>backend/app/api/database.py</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="cmt">-- Introspect column definitions:</span>
<span class="kw">SELECT</span> COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA
<span class="kw">FROM</span> information_schema.COLUMNS
<span class="kw">WHERE</span> TABLE_SCHEMA = <span class="fn">DATABASE</span>() <span class="kw">AND</span> TABLE_NAME = <span class="str">'students'</span>
<span class="kw">ORDER BY</span> ORDINAL_POSITION <span class="kw">ASC</span>;

<span class="cmt">-- Introspect foreign key relationships:</span>
<span class="kw">SELECT</span> COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME, CONSTRAINT_NAME
<span class="kw">FROM</span> information_schema.KEY_COLUMN_USAGE
<span class="kw">WHERE</span> TABLE_SCHEMA = <span class="fn">DATABASE</span>() <span class="kw">AND</span> TABLE_NAME = <span class="str">'students'</span> <span class="kw">AND</span> REFERENCED_TABLE_NAME <span class="kw">IS NOT NULL</span>;

<span class="cmt">-- Sample data query:</span>
<span class="kw">SELECT</span> * <span class="kw">FROM</span> <span class="tbl">`students`</span> <span class="kw">LIMIT</span> <span class="num">50</span>;</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Relational data dictionary introspection, physical schema design, candidate key constraints, BTREE index discovery.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.3 Integrity Scanner (<code>IntegrityScannerPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Core detection engine. Proactively scans relational tables to uncover foreign key orphans, duplicate candidate keys, domain boundary failures, and missing mandatory values.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Scan Mode Selector:</b> Toggle between <code>Full Database Scan</code> and <code>Selected Table Scan</code>.</li>
    <li><b>Table Checkbox Matrix:</b> Multi-select for the 6 business tables.</li>
    <li><b>Rules Checklist:</b> Checklist of active integrity rules.</li>
    <li><b>Button "Execute Integrity Scan":</b> Triggers the detection engine.</li>
    <li><b>KPI Cards:</b> Rows inspected, scan duration (ms), issues count, severity breakdown.</li>
    <li><b>Results Filters:</b> Severity, violation category, target table, text search.</li>
    <li><b>Detected Issues Table:</b> Issue ID, target table, column, violating record ID, invalid value, description, strategy badge, and button <code>Repair Issue</code>.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/IntegrityScannerPage.jsx</code>. Dispatches <code>scansApi.triggerScan({ scan_type, target_tables, rule_codes })</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoint: <code>POST /api/scans</code> in <code>backend/app/api/scans.py</code> handled by <code>IntegrityScanner.run_scan()</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="cmt">-- 1. Orphan Detection via LEFT OUTER JOIN:</span>
<span class="kw">SELECT</span> t.<span class="tbl">`instructor_id`</span> <span class="kw">AS</span> pk_val, t.<span class="tbl">`dept_id`</span> <span class="kw">AS</span> fk_val
<span class="kw">FROM</span> <span class="tbl">`instructors`</span> t
<span class="kw">LEFT JOIN</span> <span class="tbl">`departments`</span> p <span class="kw">ON</span> t.<span class="tbl">`dept_id`</span> = p.<span class="tbl">`dept_id`</span>
<span class="kw">WHERE</span> p.<span class="tbl">`dept_id`</span> <span class="kw">IS NULL AND</span> t.<span class="tbl">`dept_id`</span> <span class="kw">IS NOT NULL</span>;

<span class="cmt">-- 2. Duplicate Detection via GROUP BY ... HAVING COUNT(*) > 1:</span>
<span class="kw">SELECT</span> <span class="tbl">`email`</span>, <span class="fn">COUNT</span>(*) <span class="kw">as</span> dup_count, <span class="fn">GROUP_CONCAT</span>(<span class="tbl">`instructor_id`</span> <span class="kw">ORDER BY</span> <span class="tbl">`instructor_id`</span> <span class="kw">ASC</span>) <span class="kw">as</span> conflicting_pks
<span class="kw">FROM</span> <span class="tbl">`instructors`</span>
<span class="kw">WHERE</span> <span class="tbl">`email`</span> <span class="kw">IS NOT NULL AND TRIM</span>(<span class="tbl">`email`</span>) != <span class="str">''</span>
<span class="kw">GROUP BY</span> <span class="tbl">`email`</span> <span class="kw">HAVING COUNT</span>(*) > <span class="num">1</span>;

<span class="cmt">-- 3. Domain Range Out-of-Bounds Check:</span>
<span class="kw">SELECT</span> <span class="tbl">`dept_id`</span> <span class="kw">AS</span> pk_val, <span class="tbl">`budget`</span> <span class="kw">AS</span> col_val 
<span class="kw">FROM</span> <span class="tbl">`departments`</span> 
<span class="kw">WHERE</span> <span class="tbl">`budget`</span> <span class="kw">IS NOT NULL AND</span> (<span class="tbl">`budget`</span> < <span class="num">0.0</span>);</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Referential integrity validation, entity integrity enforcement, domain constraint boundaries, idempotent issue registration.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.4 Recovery & Self-Healing Center (<code>RecoveryCenterPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Autonomous self-healing cockpit where administrators inspect proposed repairs, evaluate blast radius impacts, supply authoritative replacement parameters, and execute atomic repairs inside InnoDB transactions.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Tabs:</b> <code>Self-Healing & Repairs</code> vs <code>Snapshots & Rollbacks</code>.</li>
    <li><b>Recommendations List:</b> Risk badge, strategy badge (<code>MAP_PARENT</code>, <code>SET_DEFAULT</code>, <code>QUARANTINE</code>, <code>DELETE_RECORD</code>, etc.), problem description, expected impact, button <code>Preview Self-Healing Action</code>.</li>
    <li><b>Preview Modal:</b> Before vs After JSON state diff, blast radius tree (direct children, downstream tables, child rows count), SQL preview block, SHA-256 row-version hash token, admin input fields, button <code>Confirm & Execute Repair</code>.</li>
    <li><b>Checkpoints View:</b> Button <code>Create Manual Checkpoint</code>, snapshots table, button <code>Rollback Table</code>.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/RecoveryCenterPage.jsx</code> (and alias <code>RepairCenterPage.jsx</code>). Calls <code>repairsApi.previewRepair()</code> and <code>repairsApi.executeRepair()</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoints: <code>POST /api/repairs/preview</code>, <code>POST /api/repairs/execute</code>, <code>POST /api/recovery/checkpoints</code>, <code>POST /api/recovery/rollback</code> in <code>backend/app/api/repairs.py</code> and <code>recovery.py</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="cmt">-- 1. Pessimistic Row Lock:</span>
<span class="kw">SELECT</span> * <span class="kw">FROM</span> <span class="tbl">`departments`</span> <span class="kw">WHERE</span> <span class="tbl">`dept_id`</span> = <span class="num">905</span> <span class="kw">FOR UPDATE</span>;

<span class="cmt">-- 2. Pre-Repair Checkpoint Snapshot:</span>
<span class="kw">INSERT INTO</span> <span class="tbl">`recovery_checkpoints`</span> (checkpoint_id, checkpoint_name, target_table, snapshot_rows_json)
<span class="kw">VALUES</span> (<span class="str">'CKPT-PRE-905'</span>, <span class="str">'Pre-repair checkpoint'</span>, <span class="str">'departments'</span>, <span class="str">'[{"dept_id": 905, "budget": -50000.00}]'</span>);

<span class="cmt">-- 3. Self-Healing Execution within Atomic Transaction:</span>
<span class="kw">START TRANSACTION</span>;
<span class="kw">SAVEPOINT</span> pre_repair_step;
<span class="kw">UPDATE</span> <span class="tbl">`departments`</span> <span class="kw">SET</span> <span class="tbl">`budget`</span> = <span class="str">'100000.00'</span> <span class="kw">WHERE</span> <span class="tbl">`dept_id`</span> = <span class="num">905</span>;
<span class="kw">SELECT</span> * <span class="kw">FROM</span> <span class="tbl">`departments`</span> <span class="kw">WHERE</span> <span class="tbl">`dept_id`</span> = <span class="num">905</span>; <span class="cmt">-- Post-verification check</span>
<span class="kw">UPDATE</span> <span class="tbl">`integrity_issues`</span> <span class="kw">SET</span> status = <span class="str">'REPAIRED'</span>, repaired_at = <span class="fn">NOW</span>() <span class="kw">WHERE</span> issue_id = %s;
<span class="kw">INSERT INTO</span> <span class="tbl">`repair_executions`</span> (...) <span class="kw">VALUES</span> (...);
<span class="kw">COMMIT</span>;</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>ACID atomicity, pessimistic row-level locking (<code>FOR UPDATE</code>), Optimistic Concurrency Control (SHA-256 state hashing), point-in-time recovery checkpoints.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.5 Relational Dependency & Topology Analyzer (<code>DependencyVisualizerPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Visualizes the database schema as a mathematical Directed Graph (DAG). It analyzes foreign key hierarchies, detects illegal circular references, computes safe topological sorting for bulk loading/deleting, and calculates the blast radius of modifying any table.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Interactive SVG Graph Canvas:</b> Renders tables as nodes and foreign key constraints as directed edges (Parent -> Child).</li>
    <li><b>Topology Statistics Bar:</b> Cycle detection badge (<code>Acyclic DAG Verified</code>), topological sort order chain.</li>
    <li><b>Table Selector Dropdown:</b> Select any core business table.</li>
    <li><b>Neighborhood Inspector:</b> Direct parents, direct children, ancestors, descendants, and blast radius table count.</li>
    <li><b>Button "Refresh Topology":</b> Re-analyzes foreign keys from <code>information_schema.KEY_COLUMN_USAGE</code>.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/DependencyVisualizerPage.jsx</code>. Calls <code>dependenciesApi.getGraph()</code> and <code>dependenciesApi.getTableDependencies(tableName)</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoints: <code>GET /api/dependencies/graph</code> and <code>GET /api/dependencies/table/{tableName}</code> in <code>backend/app/api/dependencies.py</code> handled by <code>DependencyAnalyzer</code> using Python <code>networkx</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="kw">SELECT</span> TABLE_NAME <span class="kw">AS</span> child_table, COLUMN_NAME <span class="kw">AS</span> child_column,
       REFERENCED_TABLE_NAME <span class="kw">AS</span> parent_table, REFERENCED_COLUMN_NAME <span class="kw">AS</span> parent_column,
       CONSTRAINT_NAME <span class="kw">AS</span> constraint_name
<span class="kw">FROM</span> information_schema.KEY_COLUMN_USAGE
<span class="kw">WHERE</span> TABLE_SCHEMA = <span class="fn">DATABASE</span>() <span class="kw">AND</span> REFERENCED_TABLE_NAME <span class="kw">IS NOT NULL</span>
  <span class="kw">AND</span> TABLE_NAME <span class="kw">IN</span> (<span class="str">'departments'</span>, <span class="str">'instructors'</span>, <span class="str">'courses'</span>, <span class="str">'students'</span>, <span class="str">'enrollments'</span>, <span class="str">'classrooms'</span>);</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Graph theory in relational databases, topological sorting for foreign key insertion/deletion order, cycle detection and deadlock prevention, cascade blast radius calculation.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.6 Data Ingestion & Staging Pipeline (<code>DataIngestionPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Implements a production-grade ETL ingestion pipeline. Raw external records land in an unconstrained staging table (<code>staging_*</code>), undergo a multi-phase validation pipeline, and are either committed to production or isolated in <code>quarantine_records</code>.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Table Selector:</b> Select from the 6 business tables.</li>
    <li><b>Schema-Driven Form:</b> Form inputs generated dynamically from column definitions.</li>
    <li><b>Parent FK Dropdowns:</b> Pre-populated with actual valid parent records (<code>fk_options</code>).</li>
    <li><b>External Batch ID:</b> Auto-generated tracking reference (<code>EXT-XXXX</code>).</li>
    <li><b>Button "Ingest Record via Staging Pipeline":</b> Submits record to backend.</li>
    <li><b>Outcome Alert Banner:</b> Green <code>Committed to Production</code> or Red <code>Rejected & Quarantined</code> with detailed validation error reasons.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/DataIngestionPage.jsx</code>. Calls <code>ingestionApi.getSchema(tableName)</code> and <code>ingestionApi.insertRecord(payload)</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoints: <code>GET /api/ingestion/schema/{tableName}</code> and <code>POST /api/ingestion/insert</code> in <code>backend/app/api/ingestion.py</code> handled by <code>IngestionService</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="cmt">-- 1. Insert into Staging Buffer:</span>
<span class="kw">INSERT INTO</span> <span class="tbl">`staging_students`</span> (student_name, email, age, gpa, dept_id, external_ref)
<span class="kw">VALUES</span> (<span class="str">'John Doe'</span>, <span class="str">'john.doe@univ.edu'</span>, <span class="num">21</span>, <span class="num">3.85</span>, <span class="num">1</span>, <span class="str">'EXT-8891'</span>);

<span class="cmt">-- 2. Foreign Key Parent Existence Check:</span>
<span class="kw">SELECT</span> <span class="fn">COUNT</span>(*) <span class="kw">AS</span> c <span class="kw">FROM</span> <span class="tbl">`departments`</span> <span class="kw">WHERE</span> <span class="tbl">`dept_id`</span> = <span class="num">1</span>;

<span class="cmt">-- 3a. IF VALID: Commit to Production Business Table:</span>
<span class="kw">INSERT INTO</span> <span class="tbl">`students`</span> (student_name, email, age, gpa, dept_id)
<span class="kw">VALUES</span> (<span class="str">'John Doe'</span>, <span class="str">'john.doe@univ.edu'</span>, <span class="num">21</span>, <span class="num">3.85</span>, <span class="num">1</span>);
<span class="kw">UPDATE</span> <span class="tbl">`staging_students`</span> <span class="kw">SET</span> validation_status = <span class="str">'VALID'</span> <span class="kw">WHERE</span> staging_id = <span class="num">42</span>;

<span class="cmt">-- 3b. IF INVALID: Move to Quarantine:</span>
<span class="kw">UPDATE</span> <span class="tbl">`staging_students`</span> <span class="kw">SET</span> validation_status = <span class="str">'REJECTED'</span>, validation_error = %s <span class="kw">WHERE</span> staging_id = <span class="num">42</span>;
<span class="kw">INSERT INTO</span> <span class="tbl">`quarantine_records`</span> (source_table, source_pk_value, issue_type, row_data_json, quarantine_reason)
<span class="kw">VALUES</span> (<span class="str">'staging_students'</span>, <span class="str">'42'</span>, <span class="str">'INGESTION_VALIDATION_FAILURE'</span>, %s, %s);</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Decoupled staging buffers, quarantine fault-isolation, schema-driven validation, two-phase transactional promotion.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.7 Transaction & Rollback Simulator (<code>TransactionSimulatorPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Provides an interactive visual demonstration of MySQL InnoDB ACID transaction mechanics: <code>START TRANSACTION</code>, <code>COMMIT</code>, <code>ROLLBACK</code>, and <code>SAVEPOINT</code>.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>3 Scenario Cards:</b> Failure Simulation & Rollback, Multi-Step Commit, Savepoint Partial Rollback.</li>
    <li><b>Button "Execute Transaction Simulation":</b> Runs simulation live against MySQL.</li>
    <li><b>Execution Trace Panel:</b> Sequential steps with step number, operation name, exact SQL statement, execution status, and live row count snapshot.</li>
    <li><b>ACID Explanation Box:</b> Real-time breakdown of Atomicity, Consistency, Isolation, and Durability observed in the simulation.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/TransactionSimulatorPage.jsx</code>. Calls <code>transactionsApi.runDemo(scenarioId)</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoint: <code>POST /api/transactions/demo?scenario={scenarioId}</code> in <code>backend/app/api/transactions.py</code> handled by <code>TransactionManager</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="kw">START TRANSACTION</span>;
<span class="kw">SELECT</span> <span class="fn">COUNT</span>(*) <span class="kw">AS</span> c <span class="kw">FROM</span> <span class="tbl">`staging_enrollments`</span>; <span class="cmt">-- Initial Count = 10</span>
<span class="kw">INSERT INTO</span> <span class="tbl">`staging_enrollments`</span> (external_ref, student_id, course_id, status) <span class="kw">VALUES</span> (<span class="str">'DEMO-FAIL'</span>, <span class="num">101</span>, <span class="num">1</span>, <span class="str">'ENROLLED'</span>);
<span class="kw">SELECT</span> <span class="fn">COUNT</span>(*) <span class="kw">AS</span> c <span class="kw">FROM</span> <span class="tbl">`staging_enrollments`</span>; <span class="cmt">-- Uncommitted Count = 11</span>
<span class="kw">ROLLBACK</span>; <span class="cmt">-- Atomically restores state!</span>
<span class="kw">SELECT</span> <span class="fn">COUNT</span>(*) <span class="kw">AS</span> c <span class="kw">FROM</span> <span class="tbl">`staging_enrollments`</span>; <span class="cmt">-- Restored Count = 10</span></code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>ACID atomicity, undo log rollback mechanics, savepoint partial undo, transaction durability.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.8 Query History & Audit Logs (<code>AuditLogsPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Immutable chronological compliance ledger tracking every scan, detected issue, repair execution, ACID transaction, and recovery checkpoint.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Search Bar:</b> Search action description, table name, actor, or transaction ID.</li>
    <li><b>Filters:</b> Event type dropdown, result filter dropdown (<code>SUCCESS</code>, <code>FAILURE</code>, <code>WARNING</code>, <code>INFO</code>).</li>
    <li><b>Audit Logs Table:</b> Event ID, timestamp, event type, actor, target table, record identifier, result badge, action description.</li>
    <li><b>Inspect Modal (Eye Button):</b> Displays sanitized before/after JSON states, related IDs, and error messages.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/AuditLogsPage.jsx</code>. Calls <code>auditApi.getLogs(params)</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoint: <code>GET /api/audit-logs</code> in <code>backend/app/api/audit.py</code> handled by <code>AuditService</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="kw">SELECT</span> event_id, event_type, actor, timestamp, related_scan_id, related_issue_id,
       related_transaction_id, action_description, target_table, record_identifier,
       result, before_values_json, after_values_json, error_message
<span class="kw">FROM</span> <span class="tbl">`audit_logs`</span>
<span class="kw">WHERE</span> <span class="num">1</span>=<span class="num">1</span> <span class="kw">ORDER BY</span> timestamp <span class="kw">DESC LIMIT</span> <span class="num">100 OFFSET</span> <span class="num">0</span>;</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Immutable audit trails (enforced by triggers <code>trg_audit_logs_no_update</code> and <code>trg_audit_logs_no_delete</code>), sensitive data redaction, non-repudiation.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.9 Rules Configuration Catalog (<code>RulesConfigurationPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>Declarative catalog administration allowing engineers to inspect, configure, activate, deactivate, test, create, and delete rules in <code>integrity_rules</code>.</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Filters:</b> Search input, category filters (<code>ORPHAN</code>, <code>DUPLICATE</code>, <code>NULL_CHECK</code>, <code>DOMAIN_CHECK</code>), severity filters.</li>
    <li><b>Button "Add New Integrity Rule":</b> Opens rule creation modal.</li>
    <li><b>Rules Table:</b> Rule Code, Rule Name, Category, Target Table & Column, Parent Table & Column, Severity, Status toggle switch.</li>
    <li><b>Action Button "Test Rule" (Play Icon):</b> Evaluates rule on live data without a full scan.</li>
    <li><b>Action Button "Delete Rule" (Trash Icon):</b> Removes custom rules.</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/RulesConfigurationPage.jsx</code>. Calls <code>rulesApi.getRules()</code>, <code>rulesApi.updateRule()</code>, <code>rulesApi.testRule()</code>, <code>rulesApi.createRule()</code>, and <code>rulesApi.deleteRule()</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoints: <code>GET /api/rules</code>, <code>POST /api/rules</code>, <code>PATCH /api/rules/{id}</code>, <code>POST /api/rules/{id}/test</code>, <code>DELETE /api/rules/{id}</code> in <code>backend/app/api/rules.py</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="kw">SELECT</span> * <span class="kw">FROM</span> <span class="tbl">`integrity_rules`</span> <span class="kw">ORDER BY</span> rule_id <span class="kw">ASC</span>;
<span class="kw">UPDATE</span> <span class="tbl">`integrity_rules`</span> <span class="kw">SET</span> is_enabled = <span class="kw">NOT</span> is_enabled <span class="kw">WHERE</span> rule_id = %s;
<span class="cmt">-- Rule test query:</span>
<span class="kw">SELECT</span> * <span class="kw">FROM</span> <span class="tbl">`departments`</span> <span class="kw">WHERE</span> <span class="tbl">`budget`</span> < <span class="num">0.0</span>;</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Declarative constraint modeling, dynamic runtime SQL compilation, metadata decoupling.</p>

  <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;"/>

  <h2>3.10 System Configuration & Maintenance (<code>SettingsPage.jsx</code>)</h2>
  <h3>1. Purpose</h3>
  <p>System health diagnostics, server configuration inspection, connectivity testing, and database maintenance controls (injecting controlled demo anomalies or resetting to baseline).</p>

  <h3>2. UI Components & Elements</h3>
  <ul>
    <li><b>Connection Diagnostics Card:</b> Host (<code>127.0.0.1</code>), Port (<code>3306</code>), Database (<code>self_healing_test_db</code>), User (<code>root</code>), Charset (<code>utf8mb4</code>), Latency, Server Version.</li>
    <li><b>Button "Test MySQL Connection":</b> Actively tests connectivity and updates latency.</li>
    <li><b>Maintenance Controls:</b> Button <code>Inject Demo Violations</code> (runs <code>05_demo_violations.sql</code>), Button <code>Reset to Clean Baseline</code> (runs <code>07_reset_demo_data.sql</code>).</li>
    <li><b>Environment Settings:</b> Application Environment (<code>development</code>), Frontend Origin (<code>http://localhost:5173</code>), API Prefix (<code>/api</code>), Version (<code>2.4.0</code>).</li>
  </ul>

  <h3>3. Frontend Source Code</h3>
  <p><b>File:</b> <code>frontend/src/pages/SettingsPage.jsx</code>. Calls <code>databaseApi.getStatus()</code>, <code>databaseApi.testConnection()</code>, <code>databaseApi.injectViolations()</code>, and <code>databaseApi.resetData()</code>.</p>

  <h3>4. Backend Connection</h3>
  <p>Endpoints: <code>GET /api/database/status</code>, <code>POST /api/database/test-connection</code>, <code>POST /api/database/inject-violations</code>, <code>POST /api/database/reset</code> in <code>backend/app/api/database.py</code>.</p>

  <h3>5. SQL Queries Executed</h3>
  <pre><code><span class="kw">SELECT</span> <span class="fn">VERSION</span>() <span class="kw">AS</span> version, <span class="fn">CURRENT_USER</span>() <span class="kw">AS</span> user;
<span class="cmt">-- Anomaly injection:</span>
<span class="kw">SET FOREIGN_KEY_CHECKS</span> = <span class="num">0</span>;
<span class="kw">INSERT INTO</span> <span class="tbl">`departments`</span> (dept_id, dept_code, dept_name, budget) <span class="kw">VALUES</span> (<span class="num">905</span>, <span class="str">'DEFICIT'</span>, <span class="str">'Deficit Lab'</span>, <span class="num">-50000.00</span>);
<span class="kw">SET FOREIGN_KEY_CHECKS</span> = <span class="num">1</span>;
<span class="cmt">-- Reset cleanup:</span>
<span class="kw">DELETE FROM</span> <span class="tbl">`departments`</span> <span class="kw">WHERE</span> dept_id >= <span class="num">900</span>;</code></pre>

  <h3>6. DBMS Concepts Implemented</h3>
  <p>Server diagnostics and latency measurement, controlled administrative foreign key check overrides, state restoration scripting.</p>
</div>
"""

CH4_HTML = """
<div class="page-break">
  <h1>Chapter 4: Button-by-Button Master Execution Flow</h1>
  <p>
    The following consolidated trace details what occurs inside the system across every button click on every page:
  </p>

  <table>
    <thead>
      <tr>
        <th>Button Clicked</th>
        <th>Page</th>
        <th>Frontend Function</th>
        <th>API Endpoint & Method</th>
        <th>Backend Route & Function</th>
        <th>SQL Executed & Tables Accessed</th>
        <th>Transaction Protocol</th>
        <th>Post-Execution UI State</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>"Scan Entire Database"</b></td>
        <td>Dashboard / Scanner</td>
        <td><code>handleScanNow()</code> / <code>handleExecuteScan()</code></td>
        <td><code>POST /api/scans</code></td>
        <td><code>scans.py:trigger_scan</code> → <code>IntegrityScanner.run_scan()</code></td>
        <td><code>INSERT INTO scan_runs</code>; <code>SELECT COUNT(*)</code> on 6 tables; <code>SELECT</code> rules; <code>LEFT JOIN</code> for orphans; <code>GROUP BY</code> for duplicates; <code>INSERT INTO integrity_issues</code></td>
        <td>Autocommit per setup step; full scan logged in <code>audit_logs</code></td>
        <td>Re-renders KPI cards, displays detected issues table with severity badges</td>
      </tr>
      <tr>
        <td><b>"Preview Self-Healing Action"</b></td>
        <td>Recovery Center</td>
        <td><code>handleOpenPreview(rec)</code></td>
        <td><code>POST /api/repairs/preview</code></td>
        <td><code>repairs.py:preview_repair</code> → <code>RepairEngine.get_repair_preview()</code></td>
        <td><code>SELECT * FROM integrity_issues</code>; <code>SELECT * FROM target_table</code>; computes SHA-256 row hash; queries <code>KEY_COLUMN_USAGE</code> for blast radius</td>
        <td>Read-only; zero database mutations committed</td>
        <td>Opens modal showing Before vs After JSON, SQL preview, and blast radius</td>
      </tr>
      <tr>
        <td><b>"Confirm & Execute Repair"</b></td>
        <td>Recovery Center</td>
        <td><code>handleExecuteRepair()</code></td>
        <td><code>POST /api/repairs/execute</code></td>
        <td><code>repairs.py:execute_repair</code> → <code>RepairEngine.execute_repair()</code></td>
        <td><code>SELECT ... FOR UPDATE</code>; verifies hash; <code>INSERT INTO recovery_checkpoints</code>; executes <code>UPDATE</code>/<code>DELETE</code>/<code>QUARANTINE</code>; <code>UPDATE integrity_issues SET status='REPAIRED'</code>; <code>INSERT INTO repair_executions</code></td>
        <td><b>Atomic InnoDB Transaction:</b> <code>START TRANSACTION</code> → <code>SAVEPOINT</code> → execute → verify → <code>COMMIT</code>. On error: <code>ROLLBACK</code></td>
        <td>Issue marked <code>REPAIRED</code>, row removed from pending recommendations, execution logged</td>
      </tr>
      <tr>
        <td><b>"Create Manual Checkpoint"</b></td>
        <td>Recovery Center</td>
        <td><code>handleCreateCheckpoint()</code></td>
        <td><code>POST /api/recovery/checkpoints</code></td>
        <td><code>recovery.py:create_checkpoint</code> → <code>RecoveryManager.create_checkpoint()</code></td>
        <td><code>SHOW CREATE TABLE {tbl}</code>; <code>SELECT * FROM {tbl}</code>; <code>INSERT INTO recovery_checkpoints</code> (snapshots metadata & rows JSON)</td>
        <td>Committed immediately; logged to <code>audit_logs</code></td>
        <td>Checkpoint appears in active snapshots list</td>
      </tr>
      <tr>
        <td><b>"Rollback Table"</b></td>
        <td>Recovery Center</td>
        <td><code>handleRollback(id)</code></td>
        <td><code>POST /api/recovery/rollback</code></td>
        <td><code>recovery.py:restore_checkpoint</code> → <code>RecoveryManager.restore_from_checkpoint()</code></td>
        <td>Reads snapshot rows; deletes unrecorded rows; updates altered rows; inserts missing rows; verifies row count matches snapshot</td>
        <td><b>Atomic InnoDB Transaction:</b> Full table restoration wrapped in transaction with rollback on count mismatch</td>
        <td>Table data restored to snapshot state; notification banner displayed</td>
      </tr>
      <tr>
        <td><b>"Ingest Record"</b></td>
        <td>Data Ingestion</td>
        <td><code>handleFormSubmit()</code></td>
        <td><code>POST /api/ingestion/insert</code></td>
        <td><code>ingestion.py:insert_record</code> → <code>IngestionService.ingest_record()</code></td>
        <td><code>INSERT INTO staging_{tbl}</code>; validates PK, FK parent existence, regex/domain; if valid: <code>INSERT INTO {tbl}</code> + <code>UPDATE staging</code>; if invalid: <code>INSERT INTO quarantine_records</code></td>
        <td>Atomic transaction; updates both staging and production/quarantine simultaneously</td>
        <td>Green success banner or Red quarantine alert with exact validation errors</td>
      </tr>
      <tr>
        <td><b>"Execute Transaction Simulation"</b></td>
        <td>Transaction Simulator</td>
        <td><code>handleRunSimulation(id)</code></td>
        <td><code>POST /api/transactions/demo</code></td>
        <td><code>transactions.py:run_transaction_demo</code> → <code>TransactionManager.run_demonstration()</code></td>
        <td><code>START TRANSACTION</code>; <code>INSERT</code>; intermediate count; simulated error / savepoint; <code>ROLLBACK</code> / <code>COMMIT</code>; final count check</td>
        <td>Demonstrates live InnoDB rollback, commit, or savepoint partial rollback</td>
        <td>Renders step-by-step visual execution trace with SQL and row count snapshots</td>
      </tr>
      <tr>
        <td><b>"Test Rule"</b></td>
        <td>Rules Configuration</td>
        <td><code>handleTestRule(id)</code></td>
        <td><code>POST /api/rules/{id}/test</code></td>
        <td><code>rules.py:test_rule</code></td>
        <td>Compiles rule condition into SQL; executes <code>SELECT</code> query on target table; counts matching records</td>
        <td>Read-only inspection query</td>
        <td>Displays rule test results modal with matching violation count and sample row</td>
      </tr>
      <tr>
        <td><b>"Toggle Rule Status"</b></td>
        <td>Rules Configuration</td>
        <td><code>handleToggleRule(rule)</code></td>
        <td><code>PATCH /api/rules/{id}</code></td>
        <td><code>rules.py:update_rule</code></td>
        <td><code>UPDATE integrity_rules SET is_enabled = NOT is_enabled WHERE rule_id = %s</code></td>
        <td>Direct single-row update committed to database</td>
        <td>Toggle switch toggles state; affects target scope of subsequent scans</td>
      </tr>
      <tr>
        <td><b>"Reset to Clean Baseline"</b></td>
        <td>Settings</td>
        <td><code>handleResetData()</code></td>
        <td><code>POST /api/database/reset</code></td>
        <td><code>database.py:reset_demo_data</code></td>
        <td>Reads <code>07_reset_demo_data.sql</code>; executes sequential cleanup queries deleting anomaly rows with IDs >= 900</td>
        <td>Wrapped in transaction; logged in <code>audit_logs</code></td>
        <td>Confirms database reset; resets open issues and restores clean baseline</td>
      </tr>
    </tbody>
  </table>
</div>
"""
