# System Architecture Documentation

## 1. Architectural Overview
The **Self-Healing Relational Database Integrity System** is an enterprise-grade academic DBMS application designed to autonomously monitor, diagnose, and repair referential integrity violations, duplicate records, constraint breaches, and domain discrepancies in relational database engines.

```
+-------------------------------------------------------------------------+
|                              PRESENTATION LAYER                         |
|  React 18 + Vite SPA | Tailwind CSS | Recharts | Lucide React | Router  |
+-------------------------------------------------------------------------+
                                    |  JSON HTTP REST / API Proxy
                                    v
+-------------------------------------------------------------------------+
|                              APPLICATION LAYER                          |
|                             FastAPI (Python 3.13)                       |
|                                                                         |
|  +--------------------+  +----------------------+  +-----------------+  |
|  | Integrity Scanner  |  | Dependency Analyzer  |  |  Repair Engine  |  |
|  | (INFORMATION_SCHEMA|  | (NetworkX Topology & |  | (ACID Previews, |  |
|  | & Rule Execution)  |  | Cycle Detection)     |  | Safe Execution) |  |
|  +--------------------+  +----------------------+  +-----------------+  |
|                                                                         |
|  +--------------------+  +----------------------+  +-----------------+  |
|  | Transaction Manager|  |   Recovery Manager   |  |  Audit Logger   |  |
|  | (BEGIN/COMMIT/     |  | (Table Snapshots &   |  | (Immutable Trace|  |
|  | ROLLBACK/SAVEPOINT)|  | Restorations)        |  | & Redaction)    |  |
|  +--------------------+  +----------------------+  +-----------------+  |
+-------------------------------------------------------------------------+
                                    |  Parameterized PyMySQL / DictCursor
                                    v
+-------------------------------------------------------------------------+
|                                DATA LAYER                               |
|                  XAMPP MySQL / MariaDB (InnoDB Engine)                  |
|                                                                         |
|  [Business Tables]      [Staging & Quarantine]      [System Engine]     |
|  - departments          - staging_enrollments       - integrity_rules   |
|  - instructors          - quarantine_records        - scan_runs         |
|  - courses                                          - integrity_issues  |
|  - students                                         - repair_recs       |
|  - enrollments                                      - repair_execs      |
|                                                     - audit_logs        |
|                                                     - transaction_logs  |
|                                                     - recovery_checkpts |
|                                                     - database_metadata |
+-------------------------------------------------------------------------+
```

---

## 2. Core Modules Description

### A. Integrity Detection Engine (`integrity_scanner.py`)
- Direct queries against `information_schema.KEY_COLUMN_USAGE`, `TABLES`, and `COLUMNS`.
- Evaluates declared InnoDB foreign keys as well as configured logical rules.
- Scans across 5 fundamental integrity dimensions:
  1. **Orphans:** Unmatched parent foreign keys.
  2. **Duplicates:** Logical collisions across single or multi-column combinations.
  3. **NULL Infractions:** Missing mandatory attributes.
  4. **Domain Bounds:** Integer/decimal range breaches (e.g. marks [0-100], age [16-65], GPA [0.00-4.00]).
  5. **Enumeration & Syntax:** Unregistered status enums and malformed email patterns.

### B. Dependency Graph Analyzer (`dependency_analyzer.py`)
- Powered by `NetworkX` directed graph data structures (`nx.DiGraph`).
- Tables represent nodes; foreign keys represent directed dependency edges (`Parent -> Child`).
- Algorithms:
  - Cycle detection using `nx.simple_cycles`.
  - Topological sort (`nx.topological_sort`) to compute safe cascading deletion and migration orders.
  - Blast Radius calculation (`nx.descendants`) to preview ripple effects before modifying any record.

### C. Self-Healing & Repair Engine (`repair_engine.py`)
- Generates structured, non-destructive recommendations.
- Provides comprehensive before/after state diffs, risk classifications, and SQL previews.
- Executes modifications exclusively within ACID transactions with pre-repair checkpointing and immediate post-execution verification.
- Implements quarantine mechanism (`quarantine_records`) for corrupt staging data that cannot be mapped safely.

### D. Transaction Management & Recovery (`transaction_manager.py` & `recovery_manager.py`)
- Employs native MySQL InnoDB `START TRANSACTION`, `COMMIT`, `ROLLBACK`, and `SAVEPOINT`.
- Demonstrates atomicity through controlled simulated failure tests.
- Maintains snapshot recovery checkpoints for instant point-in-time table restoration.

### E. Audit Service (`audit_service.py`)
- Centralized traceability logger recording all lifecycle events.
- Automatically redacts passwords, tokens, and sensitive keys from JSON audit states.
