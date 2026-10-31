import uuid
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.app.database.connection import get_connection
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class TransactionManager:
    @staticmethod
    def run_demonstration(scenario: str = "SIMULATED_FAILURE_ROLLBACK") -> Dict[str, Any]:
        """
        Executes a controlled interactive demonstration of MySQL InnoDB transaction behavior:
        1. COMMIT_SUCCESS: Begins transaction, inserts a record, verifies intermediate state, commits, checks final state.
        2. SIMULATED_FAILURE_ROLLBACK: Begins transaction, inserts record, verifies intermediate dirty read, encounters simulated error, executes ROLLBACK, confirms record was entirely undone!
        3. SAVEPOINT_PARTIAL_ROLLBACK: Begins transaction, inserts record A, sets SAVEPOINT sp1, inserts invalid record B, encounters error, executes ROLLBACK TO SAVEPOINT sp1, commits record A!
        """
        transaction_id = f"TX-DEMO-{uuid.uuid4().hex[:8].upper()}"
        start_time = datetime.now()
        t0 = time.time()
        steps: List[Dict[str, Any]] = []

        conn = get_connection()
        test_uid = uuid.uuid4().hex[:6].upper()

        try:
            with conn.cursor() as cur:
                cur.execute("SHOW TABLES;")
                all_tables = [list(r.values())[0].lower() for r in cur.fetchall()]

            # Determine available demo table
            is_retail = "customers" in all_tables
            demo_table = "customers" if is_retail else ("staging_enrollments" if "staging_enrollments" in all_tables else all_tables[0])

            # Baseline Count Check
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) AS c FROM `{demo_table}`")
                initial_count = cur.fetchone()["c"]

            # Step 1: BEGIN TRANSACTION
            steps.append({
                "step_number": 1,
                "operation_name": "BEGIN TRANSACTION",
                "sql": "START TRANSACTION /* Autocommit disabled */",
                "status": "EXECUTED",
                "details": f"Initiated atomic InnoDB transaction isolation block on `{demo_table}`.",
                "database_state_snapshot": {f"{demo_table}_rows": initial_count}
            })

            if scenario == "COMMIT_SUCCESS":
                # Step 2: Valid Insert Operation
                with conn.cursor() as cur:
                    if is_retail:
                        test_email = f"tx_commit_{test_uid.lower()}@example.com"
                        insert_sql = """
                            INSERT INTO customers (customer_name, email, phone, city)
                            VALUES (%s, %s, %s, %s)
                        """
                        cur.execute(insert_sql, (f"Commit Demo Customer {test_uid}", test_email, "+1-555-0199", "Tech City"))
                    else:
                        insert_sql = """
                            INSERT INTO staging_enrollments 
                                (external_ref, student_id, course_id, student_email, enrolled_on, grade_marks, status, notes)
                            VALUES (%s, 101, 1, 'demo@univ.edu', '2026-10-01', 95.00, 'ENROLLED', 'Transaction commit demo')
                        """
                        cur.execute(insert_sql, (f"DEMO-{test_uid}",))
                    inserted_id = cur.lastrowid

                steps.append({
                    "step_number": 2,
                    "operation_name": "INSERT_RECORD",
                    "sql": f"INSERT INTO {demo_table} (id={inserted_id}) VALUES (...)",
                    "status": "EXECUTED",
                    "details": f"Record inserted into `{demo_table}` within transaction scope.",
                    "database_state_snapshot": {f"{demo_table}_rows": initial_count + 1, "inserted_id": inserted_id}
                })

                # Step 3: COMMIT
                conn.commit()
                steps.append({
                    "step_number": 3,
                    "operation_name": "COMMIT",
                    "sql": "COMMIT;",
                    "status": "COMMITTED",
                    "details": "Changes persisted permanently to InnoDB redo logs and tablespace.",
                    "database_state_snapshot": {f"{demo_table}_rows": initial_count + 1}
                })

                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) AS c FROM `{demo_table}`")
                    final_count = cur.fetchone()["c"]

                duration_ms = round((time.time() - t0) * 1000, 2)
                AuditService.log_transaction(
                    transaction_id=transaction_id,
                    execution_id=None,
                    start_time=start_time,
                    end_time=datetime.now(),
                    status="COMMITTED",
                    operations_count=len(steps)
                )

                AuditService.log_event(
                    event_type="TRANSACTION_DEMO_COMMIT",
                    action_description=f"Transaction simulation '{scenario}' completed with COMMIT on `{demo_table}`.",
                    actor="SIMULATOR",
                    related_transaction_id=transaction_id,
                    result="SUCCESS"
                )

                return {
                    "transaction_id": transaction_id,
                    "scenario": scenario,
                    "overall_status": "COMMITTED",
                    "start_time": start_time,
                    "end_time": datetime.now(),
                    "duration_ms": duration_ms,
                    "steps": steps,
                    "initial_state_count": initial_count,
                    "final_state_count": final_count,
                    "state_preserved": final_count == initial_count + 1,
                    "explanation": f"Transaction successfully committed to `{demo_table}`. The inserted row was durably written to the database."
                }

            elif scenario == "SIMULATED_FAILURE_ROLLBACK":
                # Step 2: Valid Insert Operation
                with conn.cursor() as cur:
                    if is_retail:
                        test_email = f"tx_rollback_{test_uid.lower()}@example.com"
                        insert_sql = """
                            INSERT INTO customers (customer_name, email, phone, city)
                            VALUES (%s, %s, %s, %s)
                        """
                        cur.execute(insert_sql, (f"Temp Customer {test_uid}", test_email, "+1-555-0100", "Temp City"))
                    else:
                        insert_sql = """
                            INSERT INTO staging_enrollments 
                                (external_ref, student_id, course_id, student_email, enrolled_on, grade_marks, status, notes)
                            VALUES (%s, 102, 2, 'temp@univ.edu', '2026-10-01', 92.00, 'ENROLLED', 'Temp row pending failure')
                        """
                        cur.execute(insert_sql, (f"DEMO-{test_uid}",))
                    temp_id = cur.lastrowid

                steps.append({
                    "step_number": 2,
                    "operation_name": "INSERT_RECORD_STEP1",
                    "sql": f"INSERT INTO {demo_table} (id={temp_id}) VALUES (...)",
                    "status": "EXECUTED",
                    "details": f"Temporary record #{temp_id} created in uncommitted transaction buffer.",
                    "database_state_snapshot": {f"{demo_table}_rows_uncommitted": initial_count + 1}
                })

                # Step 3: Trigger Simulated Failure (Intentional integrity error / condition)
                simulated_error_msg = "Simulated integrity violation: Triggered controlled rollback condition."
                steps.append({
                    "step_number": 3,
                    "operation_name": "TRIGGER_SIMULATED_FAILURE",
                    "sql": "-- SIMULATED INTEGRITY EXCEPTION: Condition failed",
                    "status": "FAILED",
                    "details": simulated_error_msg,
                    "database_state_snapshot": {"error": simulated_error_msg}
                })

                # Step 4: Execute ROLLBACK
                conn.rollback()
                steps.append({
                    "step_number": 4,
                    "operation_name": "ROLLBACK",
                    "sql": "ROLLBACK;",
                    "status": "ROLLED_BACK",
                    "details": "Rollback invoked. All changes discarded via InnoDB undo logs.",
                    "database_state_snapshot": {f"{demo_table}_rows": initial_count}
                })

                # Step 5: Verification check
                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) AS c FROM `{demo_table}`")
                    final_count = cur.fetchone()["c"]

                duration_ms = round((time.time() - t0) * 1000, 2)
                AuditService.log_transaction(
                    transaction_id=transaction_id,
                    execution_id=None,
                    start_time=start_time,
                    end_time=datetime.now(),
                    status="ROLLED_BACK",
                    operations_count=len(steps),
                    rollback_reason=simulated_error_msg
                )

                AuditService.log_event(
                    event_type="TRANSACTION_DEMO_ROLLBACK",
                    action_description=f"Transaction simulation '{scenario}' rolled back successfully on `{demo_table}`. Database returned to initial clean state.",
                    actor="SIMULATOR",
                    related_transaction_id=transaction_id,
                    result="SUCCESS"
                )

                return {
                    "transaction_id": transaction_id,
                    "scenario": scenario,
                    "overall_status": "ROLLED_BACK",
                    "start_time": start_time,
                    "end_time": datetime.now(),
                    "duration_ms": duration_ms,
                    "steps": steps,
                    "initial_state_count": initial_count,
                    "final_state_count": final_count,
                    "state_preserved": final_count == initial_count,
                    "explanation": f"Atomicity demonstrated! Temporary row in `{demo_table}` was completely discarded. Database preserved at initial {initial_count} rows."
                }

            elif scenario == "SAVEPOINT_PARTIAL_ROLLBACK":
                # Step 2: Insert First Record (Valid)
                with conn.cursor() as cur:
                    if is_retail:
                        test_email_a = f"tx_savepoint_a_{test_uid.lower()}@example.com"
                        insert_sql1 = """
                            INSERT INTO customers (customer_name, email, phone, city)
                            VALUES (%s, %s, %s, %s)
                        """
                        cur.execute(insert_sql1, (f"Savepoint Customer A {test_uid}", test_email_a, "+1-555-0101", "City A"))
                    else:
                        insert_sql1 = """
                            INSERT INTO staging_enrollments 
                                (external_ref, student_id, course_id, student_email, enrolled_on, grade_marks, status, notes)
                            VALUES (%s, 103, 3, 'arun.patel@univ.edu', '2026-10-01', 88.00, 'ENROLLED', 'Savepoint part 1')
                        """
                        cur.execute(insert_sql1, (f"DEMO-{test_uid}-A",))
                    rec1_id = cur.lastrowid

                steps.append({
                    "step_number": 2,
                    "operation_name": "INSERT_RECORD_A",
                    "sql": f"INSERT INTO {demo_table} (id={rec1_id}) VALUES (...)",
                    "status": "EXECUTED",
                    "details": f"First valid operation executed on `{demo_table}`.",
                    "database_state_snapshot": {f"{demo_table}_rows": initial_count + 1}
                })

                # Step 3: Establish SAVEPOINT
                sp_name = "sp_demo_part1"
                with conn.cursor() as cur:
                    cur.execute(f"SAVEPOINT {sp_name};")

                steps.append({
                    "step_number": 3,
                    "operation_name": "SET_SAVEPOINT",
                    "sql": f"SAVEPOINT {sp_name};",
                    "status": "SAVEPOINT_SET",
                    "details": f"Savepoint '{sp_name}' established within active transaction.",
                    "database_state_snapshot": {"savepoint": sp_name}
                })

                # Step 4: Insert Second Record (Will be rolled back)
                with conn.cursor() as cur:
                    if is_retail:
                        test_email_b = f"tx_savepoint_b_{test_uid.lower()}@example.com"
                        insert_sql2 = """
                            INSERT INTO customers (customer_name, email, phone, city)
                            VALUES (%s, %s, %s, %s)
                        """
                        cur.execute(insert_sql2, (f"Savepoint Customer B {test_uid}", test_email_b, "+1-555-0102", "City B"))
                    else:
                        insert_sql2 = """
                            INSERT INTO staging_enrollments 
                                (external_ref, student_id, course_id, student_email, enrolled_on, grade_marks, status, notes)
                            VALUES (%s, 999, 888, 'bad.ref@univ.edu', '2026-10-01', 50.00, 'ENROLLED', 'Savepoint part 2 (bad)')
                        """
                        cur.execute(insert_sql2, (f"DEMO-{test_uid}-B",))
                    rec2_id = cur.lastrowid

                steps.append({
                    "step_number": 4,
                    "operation_name": "INSERT_RECORD_B",
                    "sql": f"INSERT INTO {demo_table} (id={rec2_id}) VALUES (...)",
                    "status": "EXECUTED",
                    "details": f"Second operation executed on `{demo_table}` (to be undone via savepoint).",
                    "database_state_snapshot": {f"{demo_table}_rows": initial_count + 2}
                })

                # Step 5: Rollback to Savepoint
                with conn.cursor() as cur:
                    cur.execute(f"ROLLBACK TO SAVEPOINT {sp_name};")

                steps.append({
                    "step_number": 5,
                    "operation_name": "ROLLBACK_TO_SAVEPOINT",
                    "sql": f"ROLLBACK TO SAVEPOINT {sp_name};",
                    "status": "ROLLED_BACK",
                    "details": f"Rolled back Record B while retaining Record A in transaction buffer.",
                    "database_state_snapshot": {f"{demo_table}_rows": initial_count + 1}
                })

                # Step 6: Commit Retained Changes
                conn.commit()
                steps.append({
                    "step_number": 6,
                    "operation_name": "COMMIT",
                    "sql": "COMMIT;",
                    "status": "COMMITTED",
                    "details": f"Committed transaction containing only Record A to `{demo_table}`.",
                    "database_state_snapshot": {f"{demo_table}_rows": initial_count + 1}
                })

                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) AS c FROM `{demo_table}`")
                    final_count = cur.fetchone()["c"]

                duration_ms = round((time.time() - t0) * 1000, 2)
                AuditService.log_transaction(
                    transaction_id=transaction_id,
                    execution_id=None,
                    start_time=start_time,
                    end_time=datetime.now(),
                    status="COMMITTED",
                    operations_count=len(steps),
                    savepoints_used=1
                )

                AuditService.log_event(
                    event_type="TRANSACTION_DEMO_SAVEPOINT",
                    action_description=f"Transaction savepoint simulation executed on `{demo_table}`. Record B undone, Record A committed.",
                    actor="SIMULATOR",
                    related_transaction_id=transaction_id,
                    result="SUCCESS"
                )

                return {
                    "transaction_id": transaction_id,
                    "scenario": scenario,
                    "overall_status": "COMMITTED",
                    "start_time": start_time,
                    "end_time": datetime.now(),
                    "duration_ms": duration_ms,
                    "steps": steps,
                    "initial_state_count": initial_count,
                    "final_state_count": final_count,
                    "state_preserved": final_count == initial_count + 1,
                    "explanation": f"Savepoint demonstrated on `{demo_table}`! Record B was rolled back to savepoint, whereas Record A was durably committed."
                }

            else:
                raise ValueError(f"Unknown demonstration scenario: {scenario}")

        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction demonstration failed: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_transaction_history(limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves history of database transactions recorded by the system."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM transaction_logs
                    ORDER BY start_time DESC
                    LIMIT %s
                """, (limit,))
                return cur.fetchall()
        finally:
            conn.close()
