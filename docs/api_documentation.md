# REST API Documentation

All API endpoints follow a standardized JSON envelope structure:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "error": null
}
```

Interactive OpenAPI Swagger UI is available at: `http://localhost:8000/docs`

---

## 1. System Health & Database Diagnostics

### `GET /api/health`
Returns system health, backend service status, and MySQL database connection diagnostics.

### `GET /api/database/status`
Returns database connection status, active database name, table count, and latency in milliseconds.

### `POST /api/database/test-connection`
Actively runs a ping and query against the MySQL server on port 3306.

### `GET /api/database/tables`
Returns a list of all tables with classified types (`BUSINESS`, `STAGING`, `SYSTEM`, `QUARANTINE`), live row counts, and column counts.

### `GET /api/database/tables/{table_name}`
Returns column definitions, data types, nullability, primary/foreign key flags, indexes, and sample rows.

### `GET /api/database/relationships`
Returns declared foreign keys and logical integrity relationships.

### `POST /api/database/reset`
Resets staging records and removes temporary demo anomalies, restoring clean baseline state.

### `POST /api/database/inject-violations`
Injects 10 controlled demonstration violations across orphans, duplicates, range out-of-bounds, and malformed emails.

---

## 2. Integrity Scans

### `POST /api/scans`
Triggers an automated integrity scan across the database.
- **Request Body:**
  ```json
  {
    "scan_type": "FULL",
    "target_tables": ["students", "staging_enrollments"],
    "rule_codes": ["RULE_ORPHAN_STAGING_STUDENT"]
  }
  ```

### `GET /api/scans`
Retrieves past scan execution history.

### `GET /api/scans/{scan_id}`
Retrieves summary details for a specific scan run.

### `GET /api/scans/{scan_id}/issues`
Retrieves all integrity issues detected during a specific scan.

---

## 3. Issues Management

### `GET /api/issues`
Retrieves paginated issues with filtering by `status`, `severity`, `category`, `table_name`, and free text `search`.

### `GET /api/issues/{issue_id}`
Returns complete details of an issue including raw database row state.

### `PATCH /api/issues/{issue_id}/status`
Updates issue status (`REVIEWED`, `IGNORED`).
*Enforces rule: `REPAIRED` cannot be set manually; it is only assigned after verified repair execution.*

---

## 4. Self-Healing & Repairs

### `GET /api/repairs/recommendations`
Returns repair recommendations for detected issues.

### `POST /api/repairs/preview`
Generates an impact analysis, state diff, and SQL preview without executing any database change.

### `POST /api/repairs/approve`
Approves a recommendation for execution.

### `POST /api/repairs/execute`
Executes a repair inside an atomic ACID transaction with automatic pre-repair checkpointing and rollback on verification failure.
- **Request Body:**
  ```json
  {
    "issue_id": "ISSUE-ORPH-123456",
    "strategy": "QUARANTINE",
    "confirmed": true,
    "operator": "ADMIN_USER"
  }
  ```

### `GET /api/repairs/executions`
Returns history of executed repairs with transaction IDs, SQL statements, and latencies.

---

## 5. Relational Dependencies

### `GET /api/dependencies/graph`
Returns nodes, directed foreign key edges, cycle detection flags, and topological sort order.

### `GET /api/dependencies/table/{table_name}`
Returns direct parents, direct children, ancestors, and downstream blast radius tables.

### `GET /api/dependencies/impact`
Evaluates cascading effects before deleting or modifying a row.

---

## 6. Transactions & Recovery

### `POST /api/transactions/demo`
Runs interactive transaction scenarios:
- `COMMIT_SUCCESS`
- `SIMULATED_FAILURE_ROLLBACK`
- `SAVEPOINT_PARTIAL_ROLLBACK`

### `GET /api/transactions`
Retrieves low-level transaction logs.

### `GET /api/recovery/checkpoints`
Returns application recovery checkpoints.

### `POST /api/recovery/checkpoints`
Creates a manual snapshot checkpoint of a table.

### `POST /api/recovery/rollback`
Restores table state from a previously captured recovery checkpoint.

---

## 7. Audit & Rules

### `GET /api/audit-logs`
Searchable audit trail with filters for `event_type`, `result`, and `search`.

### `GET /api/rules`
Lists configured integrity rules.

### `POST /api/rules`
Creates a new integrity rule.

### `PATCH /api/rules/{rule_id}`
Updates rule parameters, severity, or enabled state.

### `POST /api/rules/{rule_id}/test`
Dry-runs a rule against live data without persisting a scan.
