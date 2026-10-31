# Testing Documentation & Verification Guide

## 1. Automated Test Suite (pytest)
The system includes comprehensive automated tests covering unit logic, database inspection, graph algorithms, transaction rollbacks, and API endpoints.

To run the test suite:
```powershell
pytest backend/tests -v
```

### Test Coverage Summary:
| Test File | Objective |
|---|---|
| `test_connection.py` | MySQL connectivity, server latency, allowlist SQL identifier validation. |
| `test_scanner.py` | Information Schema inspection, orphan detection, duplicate grouping, range bounds, and recommendation generation. |
| `test_dependency_analyzer.py` | NetworkX graph construction, cycle detection, parent/child traversal, blast radius impact calculation. |
| `test_repair_engine.py` | Non-destructive preview calculation, before/after diffs, destructive confirmation enforcement. |
| `test_transaction_manager.py` | ACID transaction mechanics: Commit durability, simulated failure rollback verification, and savepoints. |
| `test_audit_service.py` | Event logging, database insertion, and sensitive credential/password redaction. |
| `test_api_endpoints.py` | FastAPI REST routes, health checks, table listing, and status validation constraints. |

---

## 2. End-to-End Manual Testing Checklist

| Step | Feature Tested | Expected Result | Verified |
|---|---|---|---|
| 1 | MySQL Connection | Connection card on Dashboard displays "Active", table count = 16, latency < 100ms. | [x] |
| 2 | Explorer Inspection | Clicking "Inspect Schema" on `students` shows columns, PK, and live sample rows. | [x] |
| 3 | Demo Anomaly Injection | Clicking "Re-Inject Demonstration Violations" in Settings loads 10 controlled violations. | [x] |
| 4 | Integrity Scanning | Running a "Full Scan" detects orphans in `staging_enrollments` and domain violations in `students`. | [x] |
| 5 | Issue Management | Opening an issue reveals raw database row state; marking `REVIEWED` updates status. | [x] |
| 6 | Manual Status Constraint | Attempting to PATCH issue status to `REPAIRED` manually returns HTTP 400 rejection. | [x] |
| 7 | Dependency Visualizer | Selecting `courses` highlights parent tables (`departments`, `instructors`) and child table (`enrollments`). | [x] |
| 8 | Self-Healing Preview | Opening "Preview & Execute" on an orphan staging record displays SQL preview and quarantine diff. | [x] |
| 9 | Atomic Repair Execution | Executing quarantine removes row from `staging_enrollments`, inserts into `quarantine_records`, and marks issue `REPAIRED`. | [x] |
| 10 | Transaction Simulator | Running "Failure Simulation & Atomic Rollback" confirms initial count == final count and atomicity preserved. | [x] |
| 11 | Recovery Restoration | Creating a checkpoint on `students` and restoring verifies rows are re-applied atomically. | [x] |
| 12 | Audit Trail | Inspecting Audit Logs shows every scan, repair, and rollback event with sensitive data redacted. | [x] |
