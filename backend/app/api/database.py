from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import os
from backend.app.database.connection import get_connection, test_database_connection, validate_identifier
from backend.app.core.config import settings
from backend.app.models.schemas import ApiResponse, TableSummary, TableDetail, ColumnInfo, ForeignKeyInfo, IndexInfo
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/database", tags=["Database Explorer & Diagnostics"])

@router.get("/status", response_model=ApiResponse[Dict[str, Any]])
def get_db_status():
    """Returns database connection status and server diagnostics."""
    status_info = test_database_connection()
    return ApiResponse(
        success=status_info["connected"],
        message=status_info["message"],
        data={
            **status_info,
            "config": settings.get_safe_config()
        }
    )

@router.post("/test-connection", response_model=ApiResponse[Dict[str, Any]])
def test_connection():
    """Actively tests connection to the configured MySQL instance."""
    status_info = test_database_connection()
    return ApiResponse(
        success=status_info["connected"],
        message="Database connectivity test completed." if status_info["connected"] else status_info.get("hint", "Connection failed."),
        data=status_info,
        error=status_info.get("error")
    )

@router.get("/tables", response_model=ApiResponse[List[TableSummary]])
def list_tables():
    """Lists all tables in the database with row counts, engines, and classification."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    t.TABLE_NAME, 
                    t.ENGINE, 
                    t.TABLE_ROWS,
                    COUNT(DISTINCT c.COLUMN_NAME) AS col_count
                FROM information_schema.TABLES t
                LEFT JOIN information_schema.COLUMNS c 
                    ON t.TABLE_SCHEMA = c.TABLE_SCHEMA AND t.TABLE_NAME = c.TABLE_NAME
                WHERE t.TABLE_SCHEMA = DATABASE()
                GROUP BY t.TABLE_NAME, t.ENGINE, t.TABLE_ROWS
                ORDER BY t.TABLE_NAME ASC
            """)
            table_rows = cur.fetchall()

            summaries = []
            for row in table_rows:
                t_name = row["TABLE_NAME"]
                
                # Classification
                if t_name.startswith("staging_") or t_name.startswith("legacy_"):
                    t_type = "STAGING"
                elif t_name == "quarantine_records":
                    t_type = "QUARANTINE"
                elif t_name in ["integrity_rules", "scan_runs", "integrity_issues", 
                                "repair_recommendations", "repair_executions", 
                                "audit_logs", "transaction_logs", "recovery_checkpoints", 
                                "database_metadata"]:
                    t_type = "SYSTEM"
                else:
                    t_type = "BUSINESS"

                # Check PK
                cur.execute("""
                    SELECT COUNT(*) AS c 
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = DATABASE() 
                      AND TABLE_NAME = %s 
                      AND CONSTRAINT_NAME = 'PRIMARY'
                """, (t_name,))
                has_pk = cur.fetchone()["c"] > 0

                # Check FK count
                cur.execute("""
                    SELECT COUNT(*) AS c 
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = DATABASE() 
                      AND TABLE_NAME = %s 
                      AND REFERENCED_TABLE_NAME IS NOT NULL
                """, (t_name,))
                fk_count = cur.fetchone()["c"]

                # Actual live row count
                cur.execute(f"SELECT COUNT(*) AS live_count FROM `{validate_identifier(t_name)}`")
                live_count = cur.fetchone()["live_count"]

                summaries.append(TableSummary(
                    table_name=t_name,
                    row_count=live_count,
                    column_count=row["col_count"] or 0,
                    engine=row["ENGINE"] or "InnoDB",
                    table_type=t_type,
                    has_primary_key=has_pk,
                    foreign_key_count=fk_count
                ))

            return ApiResponse(
                success=True,
                message=f"Discovered {len(summaries)} database tables.",
                data=summaries
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

def _get_single_table_detail(cur, table_name: str) -> TableDetail:
    """Helper to inspect and compile complete schema metadata for a single table."""
    cur.execute("""
        SELECT COUNT(*) as c FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
    """, (table_name,))
    if cur.fetchone()["c"] == 0:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' does not exist.")

    cur.execute("""
        SELECT 
            COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, COLUMN_COMMENT
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION ASC
    """, (table_name,))
    col_rows = cur.fetchall()

    cur.execute("""
        SELECT 
            CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() 
          AND TABLE_NAME = %s 
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """, (table_name,))
    fk_rows = cur.fetchall()
    fk_col_set = {f["COLUMN_NAME"] for f in fk_rows}

    columns = [
        ColumnInfo(
            name=c["COLUMN_NAME"],
            data_type=c["DATA_TYPE"],
            is_nullable=(c["IS_NULLABLE"] == "YES"),
            default_value=str(c["COLUMN_DEFAULT"]) if c["COLUMN_DEFAULT"] is not None else None,
            is_primary_key=(c["COLUMN_KEY"] == "PRI"),
            is_foreign_key=(c["COLUMN_NAME"] in fk_col_set),
            comment=c["COLUMN_COMMENT"] or None
        )
        for c in col_rows
    ]

    foreign_keys = [
        ForeignKeyInfo(
            constraint_name=f["CONSTRAINT_NAME"],
            column_name=f["COLUMN_NAME"],
            referenced_table=f["REFERENCED_TABLE_NAME"],
            referenced_column=f["REFERENCED_COLUMN_NAME"]
        )
        for f in fk_rows
    ]

    cur.execute(f"SHOW INDEX FROM `{table_name}`")
    idx_rows = cur.fetchall()
    indexes = [
        IndexInfo(
            index_name=i["Key_name"],
            column_name=i["Column_name"],
            is_unique=(i["Non_unique"] == 0),
            is_primary=(i["Key_name"] == "PRIMARY")
        )
        for i in idx_rows
    ]

    cur.execute(f"SELECT * FROM `{table_name}` LIMIT 25")
    sample_rows = cur.fetchall()

    cur.execute(f"SELECT COUNT(*) AS c FROM `{table_name}`")
    row_count = cur.fetchone()["c"]

    if table_name.startswith("staging_") or table_name.startswith("stage_"):
        t_type = "STAGING"
    elif table_name == "quarantine_records":
        t_type = "QUARANTINE"
    elif table_name in ["integrity_rules", "scan_runs", "integrity_issues", 
                        "repair_recommendations", "repair_executions", 
                        "audit_logs", "transaction_logs", "recovery_checkpoints", 
                        "database_metadata"]:
        t_type = "SYSTEM"
    else:
        t_type = "BUSINESS"

    return TableDetail(
        table_name=table_name,
        row_count=row_count,
        columns=columns,
        foreign_keys=foreign_keys,
        indexes=indexes,
        table_type=t_type,
        sample_rows=sample_rows
    )

@router.get("/schema", response_model=ApiResponse[List[TableDetail]])
def get_full_database_schema():
    """Retrieves full dynamic schema information for all discovered tables."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TABLE_NAME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_NAME ASC
            """)
            table_names = [r["TABLE_NAME"] for r in cur.fetchall()]

            full_schema = []
            for t_name in table_names:
                detail = _get_single_table_detail(cur, t_name)
                full_schema.append(detail)

            return ApiResponse(
                success=True,
                message=f"Discovered full schema for {len(full_schema)} database tables.",
                data=full_schema
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/tables/{table_name}", response_model=ApiResponse[TableDetail])
def get_table_detail(table_name: str):
    """Retrieves schema metadata (columns, data types, constraints, indexes) and sample rows."""
    try:
        table_name = validate_identifier(table_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            detail = _get_single_table_detail(cur, table_name)
            return ApiResponse(
                success=True,
                message=f"Retrieved schema details for '{table_name}'.",
                data=detail
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/relationships", response_model=ApiResponse[List[Dict[str, Any]]])
def get_relationships():
    """Retrieves all relational links (declared foreign keys and configured logical rules)."""
    conn = get_connection()
    try:
        relationships = []
        with conn.cursor() as cur:
            # Physical FKs
            cur.execute("""
                SELECT 
                    TABLE_NAME AS child_table,
                    COLUMN_NAME AS child_column,
                    REFERENCED_TABLE_NAME AS parent_table,
                    REFERENCED_COLUMN_NAME AS parent_column,
                    CONSTRAINT_NAME AS constraint_name
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE() 
                  AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            for r in cur.fetchall():
                relationships.append({
                    "from_table": r["parent_table"],
                    "to_table": r["child_table"],
                    "parent_column": r["parent_column"],
                    "child_column": r["child_column"],
                    "constraint_name": r["constraint_name"],
                    "relationship_type": "PHYSICAL_FK"
                })

            # Logical rules
            cur.execute("""
                SELECT 
                    target_table AS child_table,
                    target_column AS child_column,
                    parent_table,
                    parent_column,
                    rule_code AS constraint_name
                FROM integrity_rules
                WHERE rule_type = 'ORPHAN' AND parent_table IS NOT NULL AND is_enabled = TRUE
            """)
            for lr in cur.fetchall():
                relationships.append({
                    "from_table": lr["parent_table"],
                    "to_table": lr["child_table"],
                    "parent_column": lr["parent_column"],
                    "child_column": lr["child_column"],
                    "constraint_name": lr["constraint_name"],
                    "relationship_type": "LOGICAL_RULE"
                })

        return ApiResponse(
            success=True,
            message=f"Discovered {len(relationships)} relational relationships.",
            data=relationships
        )
    finally:
        conn.close()

@router.post("/reset", response_model=ApiResponse[Dict[str, Any]])
def reset_database_data():
    """Safely restores clean baseline demo data without altering schemas or deleting business records."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check active schema tables
            cur.execute("SHOW TABLES;")
            all_tables = [list(r.values())[0] for r in cur.fetchall()]

            if "students" in all_tables and "staging_enrollments" in all_tables:
                # Academic schema reset
                cur.execute("DELETE FROM `students` WHERE `student_id` >= 200")
                cur.execute("TRUNCATE TABLE `staging_enrollments`")
                cur.execute("""
                    INSERT INTO `staging_enrollments` 
                        (`staging_id`, `external_ref`, `student_id`, `course_id`, `student_email`, `enrolled_on`, `grade_marks`, `status`, `notes`)
                    VALUES 
                        (1, 'EXT-1001', 101, 3, 'ravi.kumar@univ.edu', '2026-09-01', 89.00, 'ENROLLED', 'Valid transfer record'),
                        (2, 'EXT-1002', 102, 2, 'priya.sharma@univ.edu', '2026-09-01', 94.50, 'ENROLLED', 'Valid elective registration'),
                        (3, 'EXT-1003', 103, 1, 'arun.patel@univ.edu', '2026-09-01', 85.00, 'ENROLLED', 'Valid regular registration')
                """)

            # Clear quarantine records
            if "quarantine_records" in all_tables:
                cur.execute("TRUNCATE TABLE `quarantine_records`")

            # Clean up issues and recommendations
            if "repair_recommendations" in all_tables:
                cur.execute("DELETE FROM `repair_recommendations`")
            if "integrity_issues" in all_tables:
                cur.execute("DELETE FROM `integrity_issues`")
        conn.commit()

        AuditService.log_event(
            event_type="DATABASE_RESET",
            action_description="Reset scan results and baseline state while preserving business records.",
            actor="ADMIN_USER",
            result="SUCCESS"
        )

        return ApiResponse(
            success=True,
            message="Database state successfully reset.",
            data={"status": "CLEAN_BASELINE"}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/inject-violations", response_model=ApiResponse[Dict[str, Any]])
def inject_violations():
    """Verifies and reports controlled integrity anomalies available for scanning."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES;")
            all_tables = [list(r.values())[0] for r in cur.fetchall()]

            if "students" in all_tables and "staging_enrollments" in all_tables:
                # Academic schema violation injection
                cur.execute("TRUNCATE TABLE `staging_enrollments`")
                cur.execute("""
                    INSERT INTO `staging_enrollments` 
                        (`staging_id`, `external_ref`, `student_id`, `course_id`, `student_email`, `enrolled_on`, `grade_marks`, `status`, `notes`)
                    VALUES 
                        (1, 'EXT-1001', 101, 3, 'ravi.kumar@univ.edu', '2026-09-01', 89.00, 'ENROLLED', 'Valid transfer record'),
                        (2, 'EXT-1002', 102, 2, 'priya.sharma@univ.edu', '2026-09-01', 94.50, 'ENROLLED', 'Valid elective registration'),
                        (3, 'EXT-1003', 999, 1, 'ghost.student@univ.edu', '2026-09-01', 75.00, 'ENROLLED', 'Orphan: Missing parent student record'),
                        (4, 'EXT-1004', 103, 888, 'arun.patel@univ.edu', '2026-09-01', 82.00, 'ENROLLED', 'Orphan: Missing parent course record'),
                        (5, 'EXT-1005', 104, 1, 'sneha.reddy@univ.edu', '2026-09-01', 88.00, 'ENROLLED', 'Original registration entry'),
                        (6, 'EXT-1006', 104, 1, 'sneha.reddy@univ.edu', '2026-09-01', 88.00, 'ENROLLED', 'Duplicate submission anomaly'),
                        (7, 'EXT-1007', 105, 1, 'vikram.malhotra@univ.edu', '2026-09-01', 145.00, 'ENROLLED', 'Domain violation: Grade marks out of 0-100 range'),
                        (8, 'EXT-1008', 106, 3, 'ananya.roy@univ.edu', '2026-09-01', 85.00, 'SUSPENDED', 'Domain violation: Invalid status code')
                """)
                cur.execute("DELETE FROM `students` WHERE `student_id` >= 200")
                cur.execute("""
                    INSERT INTO `students` (`student_id`, `student_name`, `email`, `age`, `gpa`, `dept_id`, `enrollment_year`)
                    VALUES 
                        (201, 'Walter Elder', 'walter.elder@univ.edu', 140, 3.20, 1, 2024),
                        (202, 'Luna Genius', 'luna.genius@univ.edu', 20, 4.95, 1, 2025),
                        (203, 'Alex Malformed', 'alex.malformed@no-tld', 22, 3.10, 2, 2023),
                        (204, '', 'ghost.name@univ.edu', 21, 2.90, 3, 2024)
                """)
                count = 10
            else:
                # Retail schema: Anomalies are already embedded in customers, products, orders, order_items, payments, inventory
                count = 11

        conn.commit()

        AuditService.log_event(
            event_type="DEMO_VIOLATIONS_READY",
            action_description=f"Verified {count} controlled integrity violations ready for scanning.",
            actor="ADMIN_USER",
            result="SUCCESS"
        )

        return ApiResponse(
            success=True,
            message=f"Controlled integrity violations verified ({count} test anomalies active in schema). Ready for scanning.",
            data={"violations_count": count}
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
