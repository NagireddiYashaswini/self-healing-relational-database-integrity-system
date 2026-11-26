# -*- coding: utf-8 -*-
"""Chapters 10 to 14: Logs & Triggers, SQL Catalog, End-to-End Workflow, Viva Voce Q&A, Mappings"""

CH10_HTML = """
<div class="page-break">
  <h1>Chapter 10: Query History, Audit Logs & Immutability Triggers</h1>

  <h2>10.1 Query History vs Audit Logs</h2>
  <ul>
    <li><b>Query History (<code>transaction_logs</code>):</b> Tracks operational transaction telemetry, including transaction IDs, start times, completion times, status (<code>COMMITTED</code> / <code>ROLLED_BACK</code>), operations count, and execution latency in milliseconds.</li>
    <li><b>Audit Logs (<code>audit_logs</code>):</b> Business-level compliance ledger recording who (actor), what (action description), when (timestamp), where (target table and record identifier), why (related issue/scan ID), and the result (<code>SUCCESS</code> / <code>FAILURE</code>), along with sanitized before-and-after JSON snapshots.</li>
  </ul>

  <h2>10.2 Database-Level Immutability Triggers</h2>
  <p>
    To guarantee that audit records cannot be altered or purged—even by users with <code>UPDATE</code> or <code>DELETE</code> privileges—the database schema establishes four immutable SQL triggers in <code>database/02_create_tables.sql</code>:
  </p>
  <pre><code><span class="kw">DELIMITER</span> $$

<span class="kw">CREATE TRIGGER</span> <span class="fn">`trg_audit_logs_no_update`</span>
<span class="kw">BEFORE UPDATE ON</span> <span class="tbl">`audit_logs`</span> <span class="kw">FOR EACH ROW</span>
<span class="kw">BEGIN</span>
    <span class="kw">SIGNAL</span> SQLSTATE <span class="str">'45000'</span>
    <span class="kw">SET</span> MESSAGE_TEXT = <span class="str">'Security Policy Violation: Audit log records are immutable and cannot be modified.'</span>;
<span class="kw">END</span>$$

<span class="kw">CREATE TRIGGER</span> <span class="fn">`trg_audit_logs_no_delete`</span>
<span class="kw">BEFORE DELETE ON</span> <span class="tbl">`audit_logs`</span> <span class="kw">FOR EACH ROW</span>
<span class="kw">BEGIN</span>
    <span class="kw">SIGNAL</span> SQLSTATE <span class="str">'45000'</span>
    <span class="kw">SET</span> MESSAGE_TEXT = <span class="str">'Security Policy Violation: Audit log records are immutable and cannot be deleted.'</span>;
<span class="kw">END</span>$$

<span class="kw">CREATE TRIGGER</span> <span class="fn">`trg_transaction_logs_no_update`</span>
<span class="kw">BEFORE UPDATE ON</span> <span class="tbl">`transaction_logs`</span> <span class="kw">FOR EACH ROW</span>
<span class="kw">BEGIN</span>
    <span class="kw">SIGNAL</span> SQLSTATE <span class="str">'45000'</span>
    <span class="kw">SET</span> MESSAGE_TEXT = <span class="str">'Security Policy Violation: Transaction log records are immutable and cannot be modified.'</span>;
<span class="kw">END</span>$$

<span class="kw">CREATE TRIGGER</span> <span class="fn">`trg_transaction_logs_no_delete`</span>
<span class="kw">BEFORE DELETE ON</span> <span class="tbl">`transaction_logs`</span> <span class="kw">FOR EACH ROW</span>
<span class="kw">BEGIN</span>
    <span class="kw">SIGNAL</span> SQLSTATE <span class="str">'45000'</span>
    <span class="kw">SET</span> MESSAGE_TEXT = <span class="str">'Security Policy Violation: Transaction log records are immutable and cannot be deleted.'</span>;
<span class="kw">END</span>$$

<span class="kw">DELIMITER</span> ;</code></pre>
</div>
"""

CH11_HTML = """
<div class="page-break">
  <h1>Chapter 11: Consolidated SQL Execution Layer</h1>
  <p>The following reference groups all primary SQL queries executed by the backend services:</p>

  <h2>11.1 Schema Introspection Queries</h2>
  <pre><code><span class="cmt">-- Discover all tables and row estimates:</span>
<span class="kw">SELECT</span> TABLE_NAME, ENGINE, TABLE_ROWS 
<span class="kw">FROM</span> information_schema.TABLES <span class="kw">WHERE</span> TABLE_SCHEMA = <span class="fn">DATABASE</span>();

<span class="cmt">-- Discover column definitions, nullability, defaults:</span>
<span class="kw">SELECT</span> COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA
<span class="kw">FROM</span> information_schema.COLUMNS <span class="kw">WHERE</span> TABLE_SCHEMA = <span class="fn">DATABASE</span>() <span class="kw">AND</span> TABLE_NAME = %s;

<span class="cmt">-- Discover foreign key relationships:</span>
<span class="kw">SELECT</span> TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
<span class="kw">FROM</span> information_schema.KEY_COLUMN_USAGE
<span class="kw">WHERE</span> TABLE_SCHEMA = <span class="fn">DATABASE</span>() <span class="kw">AND</span> REFERENCED_TABLE_NAME <span class="kw">IS NOT NULL</span>;</code></pre>

  <h2>11.2 Anomaly Scanning Queries</h2>
  <pre><code><span class="cmt">-- Orphan check query (LEFT JOIN):</span>
<span class="kw">SELECT</span> t.enrollment_id, t.student_id 
<span class="kw">FROM</span> enrollments t <span class="kw">LEFT JOIN</span> students p <span class="kw">ON</span> t.student_id = p.student_id 
<span class="kw">WHERE</span> p.student_id <span class="kw">IS NULL AND</span> t.student_id <span class="kw">IS NOT NULL</span>;

<span class="cmt">-- Uniqueness check query (GROUP BY ... HAVING):</span>
<span class="kw">SELECT</span> email, <span class="fn">COUNT</span>(*) <span class="kw">FROM</span> instructors 
<span class="kw">WHERE</span> email <span class="kw">IS NOT NULL GROUP BY</span> email <span class="kw">HAVING COUNT</span>(*) > <span class="num">1</span>;</code></pre>

  <h2>11.3 Self-Healing & Transaction Queries</h2>
  <pre><code><span class="cmt">-- Lock row for update (Pessimistic Locking):</span>
<span class="kw">SELECT</span> * <span class="kw">FROM</span> departments <span class="kw">WHERE</span> dept_id = %s <span class="kw">FOR UPDATE</span>;

<span class="cmt">-- Quarantining a corrupted row:</span>
<span class="kw">INSERT INTO</span> quarantine_records (source_table, source_pk_value, issue_type, row_data_json, quarantine_reason)
<span class="kw">VALUES</span> (%s, %s, %s, %s, %s);
<span class="kw">DELETE FROM</span> departments <span class="kw">WHERE</span> dept_id = %s;

<span class="cmt">-- Remapping an orphan foreign key:</span>
<span class="kw">UPDATE</span> enrollments <span class="kw">SET</span> student_id = %s <span class="kw">WHERE</span> enrollment_id = %s;</code></pre>
</div>
"""

CH12_HTML = """
<div class="page-break">
  <h1>Chapter 12: End-to-End System Workflow Walkthrough</h1>

  <p>
    To illustrate how all layers operate together, consider a complete real-world scenario: <b>Ingesting, detecting, and healing an orphan enrollment record</b>.
  </p>

  <ol>
    <li>
      <b>Step 1: External Data Ingestion</b><br/>
      An administrator opens <code>/ingestion</code> and submits an enrollment with <code>student_id = 9999</code> (a student that does not exist in the database).
    </li>
    <li>
      <b>Step 2: Staging & Fault Isolation</b><br/>
      <code>IngestionService.ingest_record()</code> inserts the row into <code>staging_enrollments</code> with status <code>PENDING</code>. The validation pipeline checks parent existence:
      <code>SELECT COUNT(*) FROM students WHERE student_id = 9999;</code>
      The count is 0. Validation fails. The service moves the row into <code>quarantine_records</code> with reason <i>"Foreign key reference failed: student_id=9999 does not exist in students"</i> and marks <code>staging_enrollments</code> as <code>REJECTED</code>.
    </li>
    <li>
      <b>Step 3: Relational Anomaly Detection</b><br/>
      An orphan record exists in production (injected during testing). The administrator opens <code>/scanner</code> and clicks <b>"Execute Integrity Scan"</b>.
      The scanner executes <code>LEFT JOIN students ON enrollments.student_id = students.student_id</code>, detecting that <code>enrollment_id = 203</code> references missing student <code>9999</code>.
    </li>
    <li>
      <b>Step 4: Issue Cataloging</b><br/>
      The scanner inserts a record into <code>integrity_issues</code> (category <code>ORPHAN</code>, severity <code>CRITICAL</code>) and creates a recommendation in <code>repair_recommendations</code> proposing strategy <code>MAP_PARENT</code>.
    </li>
    <li>
      <b>Step 5: Recovery Center Inspection & Preview</b><br/>
      The administrator navigates to <code>/recovery?issue=ISSUE-ORPH-XXXX</code> and clicks <b>"Preview Self-Healing Action"</b>.
      The backend computes a SHA-256 row-version hash token and calculates the blast radius using <code>DependencyAnalyzer</code>. The UI displays the proposed SQL:
      <code>UPDATE enrollments SET student_id = ? WHERE enrollment_id = 203;</code>
    </li>
    <li>
      <b>Step 6: Authoritative Parent Selection</b><br/>
      The administrator selects verified student <code>101 (Alan Turing)</code>.
    </li>
    <li>
      <b>Step 7: Atomic Transactional Execution</b><br/>
      The administrator clicks <b>"Confirm & Execute"</b>.
      The backend begins a transaction (<code>START TRANSACTION</code>), acquires a row lock (<code>FOR UPDATE</code>), creates a pre-repair checkpoint, verifies the SHA-256 token, updates <code>enrollments.student_id = 101</code>, verifies the post-state, marks the issue <code>REPAIRED</code>, logs execution details, and commits (<code>COMMIT</code>).
    </li>
    <li>
      <b>Step 8: Audit Logging & Dashboard Update</b><br/>
      <code>AuditService</code> writes an immutable record to <code>audit_logs</code>. The Dashboard reflects <code>100.0%</code> integrity!
    </li>
  </ol>
</div>
"""

CH13_HTML = """
<div class="page-break">
  <h1>Chapter 13: Comprehensive DBMS Viva Voce Preparation (Evaluator Q&A)</h1>

  <p>
    This chapter prepares you to answer theoretical and code-specific questions from your external examiner with confidence.
  </p>

  <div class="callout callout-info">
    <div class="callout-title">Q1: What is Referential Integrity, and how does your project enforce and heal it?</div>
    <p><b>Model Answer:</b><br/>
    "Referential integrity is a relational database property ensuring that a foreign key value in a child table must always correspond to an existing, valid primary key in the referenced parent table, or be set to NULL if allowed.<br/>
    In our project, referential integrity is physically enforced at the database level by MySQL's InnoDB engine using <code>FOREIGN KEY ... REFERENCES ... ON DELETE RESTRICT / CASCADE</code>.<br/>
    Furthermore, our project includes an autonomous <b>Integrity Scanner</b> that identifies orphaned records by executing <code>LEFT JOIN</code> queries against <code>information_schema.KEY_COLUMN_USAGE</code>. When an orphan is found, our <b>Repair Engine</b> presents a safe healing strategy such as <code>MAP_PARENT</code> (re-pointing the foreign key to an authoritative parent) or <code>QUARANTINE</code> (safely archiving the corrupted row in <code>quarantine_records</code> before deletion), all executed within an atomic transaction."
    </p>
  </div>

  <div class="callout callout-info">
    <div class="callout-title">Q2: Explain the ACID properties and where they appear in your codebase.</div>
    <p><b>Model Answer:</b><br/>
    "ACID stands for Atomicity, Consistency, Isolation, and Durability:
    <ul>
      <li><b>Atomicity:</b> All operations succeed or all are rolled back. Implemented in <code>backend/app/services/repair_engine.py</code> using <code>conn.begin()</code>, <code>conn.commit()</code>, and <code>conn.rollback()</code> inside a <code>try...except</code> block.</li>
      <li><b>Consistency:</b> The database transitions from one valid state to another without violating constraints. Implemented via post-repair verification checks before issuing <code>COMMIT</code>.</li>
      <li><b>Isolation:</b> Transactions execute without interference from concurrent sessions. Implemented using pessimistic locking (<code>SELECT ... FOR UPDATE</code>) in <code>repair_engine.py</code> and InnoDB's default <code>REPEATABLE READ</code> isolation level.</li>
      <li><b>Durability:</b> Committed changes survive server crashes. Guaranteed by InnoDB write-ahead redo logging."</li>
    </ul>
    </p>
  </div>

  <div class="callout callout-info">
    <div class="callout-title">Q3: What is Optimistic Concurrency Control (OCC) and why is it needed in the Repair Engine?</div>
    <p><b>Model Answer:</b><br/>
    "Optimistic Concurrency Control allows multiple users to read and preview records without acquiring long-lived database locks, assuming conflicts are rare.<br/>
    In our Repair Engine, when an administrator generates a repair preview, we compute a deterministic cryptographic SHA-256 hash of the row state called the <code>row_version_token</code>. When the administrator later clicks 'Execute Repair', the backend re-fetches the live row under a short <code>FOR UPDATE</code> lock and re-computes the hash. If another administrator or process modified the row in the meantime, the tokens will not match, triggering a <code>StalePreviewError</code> and aborting the transaction. This completely prevents the classic <b>Lost Update Problem</b>."
    </p>
  </div>

  <div class="callout callout-info">
    <div class="callout-title">Q4: Why do you have separate Staging, Business, and Quarantine tables?</div>
    <p><b>Model Answer:</b><br/>
    "This represents a classic 3-tier ETL and data quality architecture:
    <ul>
      <li><b>Staging Tables (<code>staging_*</code>):</b> Unconstrained landing buffers where external data can arrive without triggering schema constraint crashes.</li>
      <li><b>Business Tables:</b> Strictly normalized, fully constrained production InnoDB tables that only contain verified, clean records.</li>
      <li><b>Quarantine Tables (<code>quarantine_records</code>):</b> Safe landing zones for rejected or corrupted records. Instead of dropping invalid rows into a black hole or aborting bulk ingestion pipelines, rejected rows are serialized into JSON and stored with their validation error reasons for administrator auditing and manual resolution."</li>
    </ul>
    </p>
  </div>

  <div class="callout callout-info">
    <div class="callout-title">Q5: What is a Directed Acyclic Graph (DAG) and how is Topological Sort used in your Dependency Visualizer?</div>
    <p><b>Model Answer:</b><br/>
    "In relational databases, foreign key relationships form a directed graph where nodes are tables and edges represent parent-child constraints.<br/>
    If foreign keys have no circular references, the graph is a Directed Acyclic Graph (DAG).<br/>
    In <code>backend/app/services/dependency_analyzer.py</code>, we use Python's <code>networkx</code> library to build the graph and compute a <b>Topological Sort</b> (<code>nx.topological_sort(G)</code>).<br/>
    Topological sorting gives us the exact dependency order for database operations:
    <ul>
      <li>When <b>inserting</b> data, parent tables must be populated before child tables (e.g. <code>departments</code> → <code>instructors</code> → <code>courses</code> → <code>students</code> → <code>enrollments</code>).</li>
      <li>When <b>deleting</b> or purging data, child tables must be cleared before parent tables to avoid foreign key restrict violations."</li>
    </ul>
    </p>
  </div>

  <div class="callout callout-info">
    <div class="callout-title">Q6: What happens if a database trigger or constraint fails during repair execution?</div>
    <p><b>Model Answer:</b><br/>
    "Because every repair in <code>RepairEngine.execute_repair()</code> is wrapped in a strict transaction (<code>conn.begin()</code>), any error—such as a MySQL constraint violation, foreign key failure, or trigger exception—immediately invokes the <code>except Exception</code> handler.<br/>
    The handler issues <code>conn.rollback()</code>, which completely undoes all intermediate table changes.<br/>
    It then logs a <code>REPAIR_FAILED</code> event in <code>audit_logs</code> and a <code>ROLLED_BACK</code> record in <code>transaction_logs</code>, ensuring zero partial corruption."
    </p>
  </div>
</div>
"""

CH14_HTML = """
<div class="page-break">
  <h1>Chapter 14: System Mapping & Verification Tables</h1>

  <h2>14.1 Frontend Page to API Endpoint & Database Table Mapping</h2>
  <table>
    <thead>
      <tr>
        <th>Frontend Page</th>
        <th>User Operations</th>
        <th>API Endpoint & Method</th>
        <th>Backend Route File</th>
        <th>Backend Service</th>
        <th>Primary Database Tables</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>DashboardPage</b></td>
        <td>View metrics, launch scan</td>
        <td><code>GET /api/database/status</code>, <code>POST /api/scans</code></td>
        <td><code>api/database.py</code>, <code>api/scans.py</code></td>
        <td><code>connection.py</code>, <code>integrity_scanner.py</code></td>
        <td><code>information_schema</code>, <code>scan_runs</code>, <code>integrity_issues</code>, <code>audit_logs</code></td>
      </tr>
      <tr>
        <td><b>DatabaseExplorerPage</b></td>
        <td>Inspect schema, view samples</td>
        <td><code>GET /api/database/tables</code>, <code>GET /api/database/tables/{name}</code></td>
        <td><code>api/database.py</code></td>
        <td><code>database.py:get_table_detail</code></td>
        <td><code>information_schema.COLUMNS</code>, <code>KEY_COLUMN_USAGE</code>, all 22 tables</td>
      </tr>
      <tr>
        <td><b>IntegrityScannerPage</b></td>
        <td>Configure & run scan</td>
        <td><code>POST /api/scans</code>, <code>GET /api/rules</code></td>
        <td><code>api/scans.py</code>, <code>api/rules.py</code></td>
        <td><code>integrity_scanner.py:run_scan</code></td>
        <td><code>integrity_rules</code>, <code>scan_runs</code>, <code>integrity_issues</code>, 6 business tables</td>
      </tr>
      <tr>
        <td><b>RecoveryCenterPage</b></td>
        <td>Preview, execute repair, rollback</td>
        <td><code>POST /api/repairs/preview</code>, <code>POST /api/repairs/execute</code></td>
        <td><code>api/repairs.py</code>, <code>api/recovery.py</code></td>
        <td><code>repair_engine.py</code>, <code>recovery_manager.py</code></td>
        <td><code>integrity_issues</code>, <code>repair_recommendations</code>, <code>repair_executions</code>, <code>recovery_checkpoints</code></td>
      </tr>
      <tr>
        <td><b>DependencyVisualizerPage</b></td>
        <td>Inspect FK DAG & blast radius</td>
        <td><code>GET /api/dependencies/graph</code>, <code>GET /api/dependencies/table/{name}</code></td>
        <td><code>api/dependencies.py</code></td>
        <td><code>dependency_analyzer.py:build_graph</code></td>
        <td><code>information_schema.KEY_COLUMN_USAGE</code>, 6 business tables</td>
      </tr>
      <tr>
        <td><b>DataIngestionPage</b></td>
        <td>Ingest external records</td>
        <td><code>GET /api/ingestion/schema/{name}</code>, <code>POST /api/ingestion/insert</code></td>
        <td><code>api/ingestion.py</code></td>
        <td><code>ingestion_service.py:ingest_record</code></td>
        <td><code>staging_*</code>, <code>quarantine_records</code>, 6 business tables</td>
      </tr>
      <tr>
        <td><b>TransactionSimulatorPage</b></td>
        <td>Simulate commit, rollback</td>
        <td><code>POST /api/transactions/demo</code></td>
        <td><code>api/transactions.py</code></td>
        <td><code>transaction_manager.py:run_demonstration</code></td>
        <td><code>staging_enrollments</code>, <code>transaction_logs</code>, <code>audit_logs</code></td>
      </tr>
      <tr>
        <td><b>AuditLogsPage</b></td>
        <td>Search and inspect audit logs</td>
        <td><code>GET /api/audit-logs</code></td>
        <td><code>api/audit.py</code></td>
        <td><code>audit_service.py:log_event</code></td>
        <td><code>audit_logs</code>, <code>transaction_logs</code></td>
      </tr>
      <tr>
        <td><b>RulesConfigurationPage</b></td>
        <td>Add, toggle, test rules</td>
        <td><code>GET /api/rules</code>, <code>POST /api/rules/{id}/test</code></td>
        <td><code>api/rules.py</code></td>
        <td><code>rules.py:test_rule</code></td>
        <td><code>integrity_rules</code>, 6 business tables</td>
      </tr>
      <tr>
        <td><b>SettingsPage</b></td>
        <td>Test connection, reset data</td>
        <td><code>POST /api/database/test-connection</code>, <code>POST /api/database/reset</code></td>
        <td><code>api/database.py</code></td>
        <td><code>database.py:reset_demo_data</code></td>
        <td><code>departments</code>, <code>instructors</code>, <code>courses</code>, <code>students</code>, <code>enrollments</code></td>
      </tr>
    </tbody>
  </table>
</div>
"""
