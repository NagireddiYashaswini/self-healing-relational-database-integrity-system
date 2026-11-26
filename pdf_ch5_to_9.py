# -*- coding: utf-8 -*-
"""Chapters 5 to 9: Backend Architecture, Ingestion ETL, Scanner, Repairs & OCC, Transactions"""

from pdf_diagrams import SVG_INGESTION_FLOW

CH5_HTML = """
<div class="page-break">
  <h1>Chapter 5: Backend Architecture & Service Layer Breakdown</h1>
  <p>
    The backend is structured under <code>backend/app/</code> following clean separation of concerns:
  </p>

  <h2>5.1 Core Modules & Database Layer</h2>
  <ul>
    <li><b><code>backend/app/main.py</code>:</b> Application entry point. Configures CORS middleware for trusted frontend origins, defines global exception handlers (HTTP and RequestValidationError), includes the 10 API routers under <code>/api</code>, and manages the application lifespan. On startup, it connects to MySQL, verifies table counts, and invokes <code>ensure_system_tables_exist()</code>.</li>
    <li><b><code>backend/app/core/config.py</code>:</b> Pydantic <code>BaseSettings</code> configuration. Loads <code>backend/.env</code> and exposes parameters: <code>DB_HOST</code> (127.0.0.1), <code>DB_PORT</code> (3306), <code>DB_NAME</code> (self_healing_test_db), <code>DB_USER</code> (root), <code>DB_PASSWORD</code>, <code>FRONTEND_ORIGIN</code>, and <code>API_PREFIX</code>.</li>
    <li><b><code>backend/app/database/connection.py</code>:</b> Database connection management. Provides <code>get_connection()</code> initializing PyMySQL with <code>autocommit=False</code> and <code>DictCursor</code>. Implements <code>validate_identifier(name)</code> using regular expression <code>^[a-zA-Z_][a-zA-Z0-9_]*$</code> to strictly prevent SQL injection in metadata inspection queries. Provides <code>test_database_connection()</code> reporting server version, database presence, table count, and latency.</li>
    <li><b><code>backend/app/database/system_tables.py</code>:</b> Self-bootstrapping DDL engine. Checks and provisions all 10 system and audit tables if they do not exist.</li>
  </ul>

  <h2>5.2 Service Layer Engines</h2>
  <ul>
    <li><b><code>IntegrityScanner</code> (<code>backend/app/services/integrity_scanner.py</code>):</b> Groups tables from <code>information_schema.TABLES</code> into business, staging, system, audit, and recovery. Executes detection algorithms for active rules, runs foreign key assertions, deduplicates detected anomalies, persists issues into <code>integrity_issues</code>, and creates proposed recommendations in <code>repair_recommendations</code>.</li>
    <li><b><code>RepairEngine</code> (<code>backend/app/services/repair_engine.py</code>):</b> Implements transparent repair preview generation, blast radius calculation, cryptographic SHA-256 state hashing (OCC), row-level pessimistic locking (<code>SELECT ... FOR UPDATE</code>), pre-repair checkpoint creation, atomic strategy execution, post-repair state verification, and transaction commit/rollback.</li>
    <li><b><code>DependencyAnalyzer</code> (<code>backend/app/services/dependency_analyzer.py</code>):</b> Builds directed schema graphs using Python <code>networkx</code>. Computes cycle detection, topological sorting (<code>nx.topological_sort</code>), and direct/indirect descendant blast radius impact.</li>
    <li><b><code>IngestionService</code> (<code>backend/app/services/ingestion_service.py</code>):</b> Manages the multi-stage ETL pipeline from staging buffers (<code>staging_*</code>) through data type and constraint validation to production table insertion or quarantine isolation.</li>
    <li><b><code>TransactionManager</code> (<code>backend/app/services/transaction_manager.py</code>):</b> Coordinates live interactive transaction demonstrations (<code>COMMIT_SUCCESS</code>, <code>SIMULATED_FAILURE_ROLLBACK</code>, <code>SAVEPOINT_PARTIAL_ROLLBACK</code>) against MySQL tables.</li>
    <li><b><code>RecoveryManager</code> (<code>backend/app/services/recovery_manager.py</code>):</b> Manages table snapshots in <code>recovery_checkpoints</code> and performs transactional table restoration by synchronizing rows against the snapshot state.</li>
    <li><b><code>AuditService</code> (<code>backend/app/services/audit_service.py</code>):</b> Persists operational events into <code>audit_logs</code> with automatic sensitive key redaction, and records transaction metrics into <code>transaction_logs</code>.</li>
  </ul>
</div>
"""

CH6_RAW = """
<div class="page-break">
  <h1>Chapter 6: Data Ingestion & Multi-Stage ETL Pipeline</h1>
  
  <p>
    Production database systems face severe reliability risks when external data feeds are directly inserted into core business tables. An invalid foreign key, duplicate identifier, or out-of-range value triggers a fatal database exception, aborting entire batch jobs.
  </p>
  <p>
    To solve this, the project implements a decoupled <b>3-tier ETL (Extract-Transform-Load) architecture</b>:
  </p>

  <div class="diagram-box">
    __SVG_INGESTION_FLOW__
    <div class="diagram-caption">Figure 6.1: Multi-Stage Data Ingestion & Validation Pipeline</div>
  </div>

  <h2>6.1 Staging Buffers vs Production vs Quarantine</h2>
  <table>
    <thead>
      <tr>
        <th>Tier</th>
        <th>Target Tables</th>
        <th>Constraint Strictness</th>
        <th>Operational Role</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Staging Tier</b></td>
        <td><code>staging_departments</code>, <code>staging_instructors</code>, <code>staging_courses</code>, <code>staging_students</code>, <code>staging_enrollments</code>, <code>staging_classrooms</code></td>
        <td>Unconstrained (Nullable, no physical foreign key blocks)</td>
        <td>Landing zone for raw external batches. Records have status <code>PENDING</code>, <code>VALID</code>, or <code>REJECTED</code>.</td>
      </tr>
      <tr>
        <td><b>Production Tier</b></td>
        <td><code>departments</code>, <code>instructors</code>, <code>courses</code>, <code>students</code>, <code>enrollments</code>, <code>classrooms</code></td>
        <td>Strict (NOT NULL, UNIQUE, physical FOREIGN KEY constraints)</td>
        <td>Active relational business domain. Only receives records that pass 100% of validation assertions.</td>
      </tr>
      <tr>
        <td><b>Quarantine Tier</b></td>
        <td><code>quarantine_records</code></td>
        <td>Flexible JSON storage with audit metadata</td>
        <td>Fault-isolation buffer. Rejected records are preserved as JSON snapshots with violation error reasons.</td>
      </tr>
    </tbody>
  </table>

  <h2>6.2 Validation Pipeline Sequence</h2>
  <ol>
    <li><b>Mandatory Column Check:</b> Columns with <code>IS_NULLABLE = 'NO'</code> and no default must contain non-empty data.</li>
    <li><b>Date & Timestamp Formatting:</b> Rejects literal SQL default keywords (<code>CURRENT_TIMESTAMP</code>, <code>NOW()</code>) from string payloads; validates ISO <code>YYYY-MM-DD</code>.</li>
    <li><b>Foreign Key Parent Verification:</b> Performs live probe query:
      <code>SELECT COUNT(*) FROM parent_table WHERE parent_pk = %s;</code>
      If count is 0, the record is rejected as an orphan before touching production!</li>
    <li><b>Domain Range Bounds:</b> Evaluates business constraints (e.g., student GPA between <code>0.00</code> and <code>4.00</code>, age between <code>16</code> and <code>65</code>, credits between <code>1</code> and <code>12</code>, non-negative budget and salary).</li>
    <li><b>Production Uniqueness Collision:</b> Queries production to verify email addresses or department codes do not collide with existing committed records.</li>
  </ol>
</div>
"""
CH6_HTML = CH6_RAW.replace("__SVG_INGESTION_FLOW__", SVG_INGESTION_FLOW)

CH7_HTML = """
<div class="page-break">
  <h1>Chapter 7: Integrity Scanner & Rule Configuration Catalog</h1>

  <p>
    The Integrity Scanner (<code>backend/app/services/integrity_scanner.py</code>) proactively queries relational tables to discover latent violations. It compiles declarative rules stored in <code>integrity_rules</code> into executable SQL queries.
  </p>

  <h2>7.1 Anomaly Detection Categories & SQL Compilation</h2>

  <h3>1. ORPHAN Checks (Referential Integrity Violations)</h3>
  <p>Identifies child rows whose foreign key values reference non-existent parent primary keys. Executed via <code>LEFT OUTER JOIN</code>:</p>
  <pre><code><span class="kw">SELECT</span> t.<span class="tbl">`{child_pk}`</span> <span class="kw">AS</span> pk_val, t.<span class="tbl">`{child_fk}`</span> <span class="kw">AS</span> fk_val
<span class="kw">FROM</span> <span class="tbl">`{child_table}`</span> t
<span class="kw">LEFT JOIN</span> <span class="tbl">`{parent_table}`</span> p <span class="kw">ON</span> t.<span class="tbl">`{child_fk}`</span> = p.<span class="tbl">`{parent_pk}`</span>
<span class="kw">WHERE</span> p.<span class="tbl">`{parent_pk}`</span> <span class="kw">IS NULL AND</span> t.<span class="tbl">`{child_fk}`</span> <span class="kw">IS NOT NULL</span>;</code></pre>
  <p><b>Recommended Strategy:</b> <code>MAP_PARENT</code> for production entities, or <code>QUARANTINE</code> for staging entities.</p>

  <h3>2. DUPLICATE Checks (Entity Integrity & Uniqueness Violations)</h3>
  <p>Identifies duplicate candidate key occurrences. Groups rows and concatenates conflicting primary keys:</p>
  <pre><code><span class="kw">SELECT</span> <span class="tbl">`{unique_col}`</span>, <span class="fn">COUNT</span>(*) <span class="kw">AS</span> dup_count, 
       <span class="fn">GROUP_CONCAT</span>(<span class="tbl">`{pk_col}`</span> <span class="kw">ORDER BY</span> <span class="tbl">`{pk_col}`</span> <span class="kw">ASC</span>) <span class="kw">AS</span> conflicting_pks
<span class="kw">FROM</span> <span class="tbl">`{target_table}`</span>
<span class="kw">WHERE</span> <span class="tbl">`{unique_col}`</span> <span class="kw">IS NOT NULL AND TRIM</span>(<span class="tbl">`{unique_col}`</span>) != <span class="str">''</span>
<span class="kw">GROUP BY</span> <span class="tbl">`{unique_col}`</span> <span class="kw">HAVING COUNT</span>(*) > <span class="num">1</span>;</code></pre>
  <p><b>Recommended Strategy:</b> <code>DELETE_RECORD</code> for redundant duplicates, or <code>MERGE_DUPLICATION</code> if child records exist.</p>

  <h3>3. NULL_CHECK (Mandatory Column Completeness)</h3>
  <p>Identifies records where mandatory columns contain <code>NULL</code> or whitespace-only strings:</p>
  <pre><code><span class="kw">SELECT</span> <span class="tbl">`{pk_col}`</span> <span class="kw">AS</span> pk_val, <span class="tbl">`{target_col}`</span> <span class="kw">AS</span> col_val
<span class="kw">FROM</span> <span class="tbl">`{target_table}`</span>
<span class="kw">WHERE</span> <span class="tbl">`{target_col}`</span> <span class="kw">IS NULL OR TRIM</span>(<span class="tbl">`{target_col}`</span>) = <span class="str">''</span>;</code></pre>
  <p><b>Recommended Strategy:</b> <code>SET_DEFAULT</code>.</p>

  <h3>4. DOMAIN_CHECK (Range, Enum, and Syntax Validation)</h3>
  <p>Validates numerical bounds, allowed string sets, or regular expression patterns:</p>
  <pre><code><span class="cmt">-- Numerical range check:</span>
<span class="kw">SELECT</span> <span class="tbl">`{pk_col}`</span> <span class="kw">AS</span> pk_val, <span class="tbl">`{target_col}`</span> <span class="kw">AS</span> col_val
<span class="kw">FROM</span> <span class="tbl">`{target_table}`</span>
<span class="kw">WHERE</span> <span class="tbl">`{target_col}`</span> <span class="kw">IS NOT NULL AND</span> (<span class="tbl">`{target_col}`</span> < min_val <span class="kw">OR</span> <span class="tbl">`{target_col}`</span> > max_val);

<span class="cmt">-- Enumeration check:</span>
<span class="kw">SELECT</span> <span class="tbl">`{pk_col}`</span> <span class="kw">AS</span> pk_val, <span class="tbl">`{target_col}`</span> <span class="kw">AS</span> col_val
<span class="kw">FROM</span> <span class="tbl">`{target_table}`</span>
<span class="kw">WHERE</span> <span class="tbl">`{target_col}`</span> <span class="kw">IS NOT NULL AND</span> <span class="tbl">`{target_col}`</span> <span class="kw">NOT IN</span> (allowed_set);</code></pre>

  <h2>7.2 Severity Scoring Model</h2>
  <ul>
    <li><span class="badge badge-critical">CRITICAL</span> Assigned to orphaned records in core business entities and primary key / candidate key duplicate collisions. Immediate repair required to prevent application crashes.</li>
    <li><span class="badge badge-high">HIGH</span> Assigned to mandatory non-null violations, foreign key orphans in secondary entities, and out-of-range numerical fields.</li>
    <li><span class="badge badge-low">LOW</span> Assigned to minor domain format discrepancies and stale scan run records.</li>
  </ul>
</div>
"""

CH8_HTML = """
<div class="page-break">
  <h1>Chapter 8: Recovery Center, Repair Engine & Optimistic Concurrency</h1>

  <p>
    The Repair Engine (<code>backend/app/services/repair_engine.py</code>) executes self-healing operations under strict transactional safety guarantees.
  </p>

  <h2>8.1 The Seven Supported Self-Healing Strategies</h2>
  <table>
    <thead>
      <tr>
        <th>Strategy</th>
        <th>Trigger Condition</th>
        <th>SQL Modification Executed</th>
        <th>Reversibility</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>MAP_PARENT</b></td>
        <td>Orphan child records in business tables.</td>
        <td><code>UPDATE {child_table} SET {fk_col} = %s WHERE {pk_col} = %s;</code> (Validates parent existence before execution).</td>
        <td>Reversible</td>
      </tr>
      <tr>
        <td><b>SET_DEFAULT</b></td>
        <td>Missing mandatory values or domain range failures.</td>
        <td><code>UPDATE {table} SET {col} = %s WHERE {pk_col} = %s;</code> (Validates replacement against column metadata).</td>
        <td>Reversible</td>
      </tr>
      <tr>
        <td><b>QUARANTINE</b></td>
        <td>Corrupt staging rows or unrepairable business records.</td>
        <td>Copies row into <code>quarantine_records</code> as JSON snapshot, then: <code>DELETE FROM {table} WHERE {pk_col} = %s;</code></td>
        <td>Reversible via RESTORE_PARENT</td>
      </tr>
      <tr>
        <td><b>DELETE_RECORD</b></td>
        <td>Redundant duplicates with zero child dependencies.</td>
        <td>Evaluates blast radius; if no child records exist: <code>DELETE FROM {table} WHERE {pk_col} = %s;</code></td>
        <td>Reversible via recovery checkpoint</td>
      </tr>
      <tr>
        <td><b>RESTORE_PARENT</b></td>
        <td>Orphan child records whose parent exists in quarantine.</td>
        <td>Re-inserts parent row from quarantine JSON into parent table; marks quarantine row as resolved.</td>
        <td>Reversible</td>
      </tr>
      <tr>
        <td><b>MERGE_DUPLICATION</b></td>
        <td>Duplicate records having child foreign key references.</td>
        <td>Re-points child foreign keys to canonical parent row, archives duplicate to quarantine, and deletes duplicate.</td>
        <td>Reversible</td>
      </tr>
      <tr>
        <td><b>MANUAL_INTERVENTION</b></td>
        <td>Complex multi-table discrepancies.</td>
        <td>Zero automated modifications. Flags issue for administrative review.</td>
        <td>N/A</td>
      </tr>
    </tbody>
  </table>

  <h2>8.2 Optimistic Concurrency Control (OCC) & Stale Preview Prevention</h2>
  <p>
    In multi-user database environments, a user may inspect a proposed repair preview, but another user might update the row before the first user clicks "Execute". To prevent <b>lost updates</b>, the system uses cryptographic state hashing:
  </p>
  <pre><code><span class="kw">def</span> <span class="fn">compute_row_hash</span>(row_dict: Optional[Dict[str, Any]]) -> str:
    <span class="kw">if not</span> row_dict:
        <span class="kw">return</span> <span class="str">""</span>
    clean_row = {}
    <span class="kw">for</span> k, v <span class="kw">in</span> row_dict.items():
        clean_row[k] = v.isoformat() <span class="kw">if isinstance</span>(v, datetime) <span class="kw">else</span> (<span class="fn">str</span>(v) <span class="kw">if</span> v <span class="kw">is not None else None</span>)
    s = json.dumps(clean_row, sort_keys=<span class="kw">True</span>)
    <span class="kw">return</span> hashlib.sha256(s.encode(<span class="str">"utf-8"</span>)).hexdigest()</code></pre>
  <p>
    When previewing a repair, <code>row_version_token</code> is generated from this SHA-256 hash. During execution, the backend acquires a lock (<code>SELECT ... FOR UPDATE</code>) and re-computes the hash. If the hashes differ, a <code>StalePreviewError</code> is raised, rolling back the transaction.
  </p>
</div>
"""

CH9_HTML = """
<div class="page-break">
  <h1>Chapter 9: Transaction Management & ACID Concurrency Control</h1>

  <p>
    This chapter evaluates how transaction management, concurrency control, and ACID properties are implemented versus simulated.
  </p>

  <h2>9.1 Implementation vs Simulation Matrix</h2>
  <table>
    <thead>
      <tr>
        <th>DBMS Concept</th>
        <th>Implementation Status</th>
        <th>Source Location</th>
        <th>Technical Mechanism</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>ACID Atomicity</b></td>
        <td><span class="badge badge-success">Fully Implemented</span></td>
        <td><code>backend/app/services/repair_engine.py</code></td>
        <td>Wrapped in <code>conn.begin()</code>, <code>conn.commit()</code>, and <code>conn.rollback()</code> inside <code>try...except</code>.</td>
      </tr>
      <tr>
        <td><b>Pessimistic Row-Level Locking</b></td>
        <td><span class="badge badge-success">Fully Implemented</span></td>
        <td><code>repair_engine.py</code> (lines 579, 625)</td>
        <td>Executes <code>SELECT ... FOR UPDATE</code> on candidate rows, preventing concurrent modification.</td>
      </tr>
      <tr>
        <td><b>Optimistic Concurrency Control (OCC)</b></td>
        <td><span class="badge badge-success">Fully Implemented</span></td>
        <td><code>repair_engine.py:compute_row_hash</code></td>
        <td>SHA-256 hash comparison against <code>row_version_token</code> aborts stale writes.</td>
      </tr>
      <tr>
        <td><b>Savepoints</b></td>
        <td><span class="badge badge-success">Fully Implemented</span></td>
        <td><code>transaction_manager.py:run_demonstration</code></td>
        <td>Declares <code>SAVEPOINT sp1;</code> and executes <code>ROLLBACK TO SAVEPOINT sp1;</code> for partial undo.</td>
      </tr>
      <tr>
        <td><b>Database Immutability Triggers</b></td>
        <td><span class="badge badge-success">Fully Implemented</span></td>
        <td><code>database/02_create_tables.sql</code> (lines 383-421)</td>
        <td>Triggers <code>trg_audit_logs_no_update</code> and <code>trg_audit_logs_no_delete</code> raise SQLSTATE <code>45000</code>.</td>
      </tr>
      <tr>
        <td><b>Interactive ACID Demonstrator</b></td>
        <td><span class="badge badge-neutral">Interactive Simulator</span></td>
        <td><code>TransactionSimulatorPage.jsx</code></td>
        <td>Executes live SQL on MySQL tables to visualize atomicity, intermediate states, and rollback.</td>
      </tr>
      <tr>
        <td><b>Two-Phase Locking (2PL)</b></td>
        <td><span class="badge badge-neutral">Engine Level / Theoretical</span></td>
        <td>Handled by MySQL InnoDB</td>
        <td>InnoDB acquires locks during transaction execution and releases them at <code>COMMIT</code> / <code>ROLLBACK</code>.</td>
      </tr>
      <tr>
        <td><b>Isolation Levels</b></td>
        <td><span class="badge badge-neutral">Engine Level</span></td>
        <td>MySQL Server Default</td>
        <td>Uses <code>REPEATABLE READ</code> via InnoDB Multi-Version Concurrency Control (MVCC) and gap locking.</td>
      </tr>
    </tbody>
  </table>

  <h2>9.2 Transaction Lifecycle in Repair Engine</h2>
  <pre><code><span class="cmt"># Pseudocode of atomic repair execution:</span>
conn = get_connection()
conn.begin()  <span class="cmt"># START TRANSACTION</span>
<span class="kw">try</span>:
    <span class="cmt"># 1. Acquire row-level lock:</span>
    cur.execute(<span class="str">"SELECT * FROM `{table}` WHERE id = %s FOR UPDATE"</span>, (pk,))
    row = cur.fetchone()
    
    <span class="cmt"># 2. Check for stale preview (OCC):</span>
    <span class="kw">if</span> compute_row_hash(row) != row_version_token:
        <span class="kw">raise</span> StalePreviewError(<span class="str">"Record modified by another session."</span>)
        
    <span class="cmt"># 3. Create pre-repair snapshot:</span>
    RecoveryManager.create_checkpoint(table, <span class="str">"Pre-repair checkpoint"</span>)
    
    <span class="cmt"># 4. Set savepoint & execute strategy SQL:</span>
    cur.execute(<span class="str">"SAVEPOINT pre_repair_step;"</span>)
    cur.execute(repair_sql, params)
    
    <span class="cmt"># 5. Post-verification check:</span>
    <span class="kw">if not</span> verify_post_repair_state(cur, table, pk):
        <span class="kw">raise</span> RuntimeError(<span class="str">"Post-repair verification failed."</span>)
        
    <span class="cmt"># 6. Mark issue resolved:</span>
    cur.execute(<span class="str">"UPDATE integrity_issues SET status = 'REPAIRED' WHERE issue_id = %s"</span>, (issue_id,))
    
    conn.commit()  <span class="cmt"># Durable COMMIT to redo log</span>
<span class="kw">except</span> Exception <span class="kw">as</span> e:
    conn.rollback()  <span class="cmt"># Full ROLLBACK via undo log</span>
    AuditService.log_event(<span class="str">"REPAIR_FAILED"</span>, error=str(e))
    <span class="kw">raise</span> e</code></pre>
</div>
"""
