# Academic DBMS Project Report

## Project Title
**Autonomous Self-Healing Relational Database Integrity System**

---

## 1. Executive Summary & Abstract
In enterprise relational database management systems (RDBMS), data integrity is paramount. While foreign keys, constraints, and check triggers are specified in database design, real-world systems regularly suffer from data degradation caused by legacy data migrations, bulk staging imports, accidental administrator edits, partial system outages, and unconstrained operational schemas.

This project implements an **Autonomous Self-Healing Relational Database Integrity System** on **MySQL InnoDB** (via local XAMPP) paired with a high-performance **FastAPI (Python 3.13)** backend and a **React 18 + Vite** dashboard. Unlike traditional CRUD applications, this system introduces automated schema inspection via `INFORMATION_SCHEMA`, directed graph dependency modeling via `NetworkX`, transaction-safe atomic self-healing workflows, checkpoint-based recovery, and immutable audit trails.

---

## 2. Problem Statement & Motivation
Modern database systems face frequent integrity challenges:
1. **Orphan Records:** Staging or legacy tables reference non-existent parent primary keys.
2. **Duplicate Entities:** Multiple submissions cause collision on logical candidate keys without triggering physical unique constraints.
3. **Mandatory Field Omissions:** Empty strings or null values bypass validation during bulk ingestion.
4. **Domain Out-of-Bounds:** Values breach permissible business rules (e.g., student age > 65, marks > 100).
5. **Cascading Side-Effects:** Blindly deleting or updating an inconsistent row can corrupt dependent child tables across relational chains.

---

## 3. How This System Differs from a Normal CRUD Application

| Dimension | Standard CRUD Application | Self-Healing DBMS Project |
|---|---|---|
| **Primary Focus** | User data entry and record retrieval. | Autonomous meta-analysis, integrity enforcement, and anomaly diagnosis. |
| **Schema Awareness** | Hardcoded forms tied to specific fixed tables. | Dynamic querying of `INFORMATION_SCHEMA` metadata, keys, indexes, and constraints. |
| **Relational Intelligence** | Assumes relationships are static. | Builds dynamic directed dependency graphs, detects cycles, and calculates cascading blast radius. |
| **Repair Operations** | Blind overwrites or uncontrolled deletions. | Non-destructive previews, risk-rated proposals, checkpointing, and verification before commit. |
| **Transaction Rigor** | Simple commit per request. | Multi-step ACID transactions with savepoints, simulated failure rollbacks, and undo logs. |
| **Audit Traceability** | None or simple access logging. | Granular before-and-after state tracking with automatic redaction of sensitive credentials. |

---

## 4. System Architecture & Algorithms

### 4.1 Integrity Detection Algorithm
1. Retrieve active rules from `integrity_rules` and physical foreign keys from `information_schema.KEY_COLUMN_USAGE`.
2. For each rule:
   - **Orphan Check:** Execute `LEFT JOIN` between child table `T` and parent table `P` where `P.parent_col IS NULL`.
   - **Duplicate Check:** Execute `GROUP BY` on specified candidate key columns with `HAVING COUNT(*) > 1`.
   - **NULL Check:** Inspect column for `IS NULL OR TRIM(col) = ''`.
   - **Domain Check:** Evaluate parameterized range boundaries, allowed enum arrays, and regex syntax.
3. Persist detected issues into `integrity_issues` and automatically synthesize self-healing proposals into `repair_recommendations`.

### 4.2 Directed Dependency Graph Algorithm
- Nodes $V$ represent database tables.
- Directed edges $E$ represent foreign key dependencies $P \to C$ where $P$ is parent and $C$ is child.
- **Cycle Detection:** Identifies circular references using `nx.simple_cycles`.
- **Topological Sorting:** Computes reverse dependency deletion order where child tables are cleaned before parents.
- **Blast Radius Calculation:** Computes the set of all downstream reachable tables $\text{Descendants}(T)$ that would be affected if rows in $T$ are modified.

### 4.3 Transaction-Safe Self-Healing Workflow
```
[Select Issue] ➔ [Generate Preview & Impact] ➔ [Require Human Approval]
       |
       v
[Take Recovery Checkpoint] ➔ [START TRANSACTION] ➔ [Execute Repair SQL]
       |
       v
[Verify Data Integrity via Post-Check Query]
       |
       +--- [All Checks Pass] ➔ [COMMIT] ➔ [Mark REPAIRED in Issue Catalog]
       |
       +--- [Any Check Fails] ➔ [ROLLBACK] ➔ [Mark FAILED & Record Audit Log]
```

---

## 5. Relational Schema Summary
- **Business Tables:** `departments`, `instructors`, `courses`, `students`, `enrollments`.
- **Staging Table:** `staging_enrollments` (unconstrained table for ingestion simulation).
- **Quarantine Table:** `quarantine_records` (secure isolation table for corrupt rows).
- **System Tables:** `integrity_rules`, `scan_runs`, `integrity_issues`, `repair_recommendations`, `repair_executions`, `audit_logs`, `transaction_logs`, `recovery_checkpoints`, `database_metadata`.

---

## 6. Verification and Test Results
- **Pytest Suite:** 22 automated test cases passing in 1.80s covering database connectivity, identifier validation, graph construction, transaction rollbacks, and REST API contracts.
- **Frontend Production Build:** Built cleanly with Vite in 23.8s with zero syntax or bundle errors.
- **Live MySQL Integration:** Verified against active XAMPP MySQL server running on port 3306.

---

## 7. Limitations & Future Scope
- **Current Limitation:** Application-level checkpoints snapshot table rows and DDL; they do not replace physical operating-system crash recovery or native MySQL binary logs (`mysqlbinlog`).
- **Future Scope:** Implement real-time Change Data Capture (CDC) via MySQL binlog streaming to detect integrity anomalies immediately as they occur.
