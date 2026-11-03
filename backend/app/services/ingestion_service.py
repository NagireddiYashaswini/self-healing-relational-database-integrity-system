import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.database.connection import get_connection, validate_identifier
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

CORE_BUSINESS_TABLES = [
    "departments",
    "instructors",
    "courses",
    "students",
    "enrollments",
    "classrooms"
]

def is_db_generated_timestamp(data_type: Optional[str], default_val: Any, extra: Optional[str]) -> bool:
    """Detects whether a timestamp/datetime column has an automatic database-generated default."""
    dt = (data_type or "").lower()
    dv = str(default_val or "").strip().lower()
    ex = (extra or "").strip().lower()
    if dt in ("timestamp", "datetime"):
        if "current_timestamp" in dv or "now()" in dv or dv == "now":
            return True
        if "default_generated" in ex or "current_timestamp" in ex:
            return True
    return False

def is_sql_default_expr(value: Any) -> bool:
    """Checks if a value is an SQL default expression rather than a concrete datetime value."""
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    v = value.strip().lower()
    return v in (
        "",
        "current_timestamp",
        "current_timestamp()",
        "now()",
        "now",
        "default",
        "null"
    )

class IngestionService:
    @staticmethod
    def get_table_schema(table_name: str) -> Dict[str, Any]:
        table_name = validate_identifier(table_name.lower())
        if table_name not in CORE_BUSINESS_TABLES:
            raise ValueError(f"Table '{table_name}' is not one of the six core business tables ({', '.join(CORE_BUSINESS_TABLES)}).")

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.COLUMN_NAME,
                        c.DATA_TYPE,
                        c.IS_NULLABLE,
                        c.COLUMN_DEFAULT,
                        c.COLUMN_KEY,
                        c.EXTRA,
                        c.CHARACTER_MAXIMUM_LENGTH,
                        kcu.REFERENCED_TABLE_NAME,
                        kcu.REFERENCED_COLUMN_NAME
                    FROM information_schema.COLUMNS c
                    LEFT JOIN information_schema.KEY_COLUMN_USAGE kcu
                        ON c.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                        AND c.TABLE_NAME = kcu.TABLE_NAME
                        AND c.COLUMN_NAME = kcu.COLUMN_NAME
                        AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                    WHERE c.TABLE_SCHEMA = DATABASE()
                      AND c.TABLE_NAME = %s
                    ORDER BY c.ORDINAL_POSITION ASC
                """, (table_name,))
                rows = cur.fetchall()

                columns = []
                for r in rows:
                    is_pk = r["COLUMN_KEY"] == "PRI" or "auto_increment" in (r.get("EXTRA") or "").lower()
                    is_fk = bool(r.get("REFERENCED_TABLE_NAME"))
                    is_gen = is_db_generated_timestamp(r["DATA_TYPE"], r["COLUMN_DEFAULT"], r.get("EXTRA"))
                    columns.append({
                        "name": r["COLUMN_NAME"],
                        "data_type": r["DATA_TYPE"],
                        "is_nullable": r["IS_NULLABLE"] == "YES",
                        "default_value": r["COLUMN_DEFAULT"],
                        "is_primary_key": is_pk,
                        "is_foreign_key": is_fk,
                        "referenced_table": r.get("REFERENCED_TABLE_NAME"),
                        "referenced_column": r.get("REFERENCED_COLUMN_NAME"),
                        "max_length": r.get("CHARACTER_MAXIMUM_LENGTH"),
                        "extra": r.get("EXTRA"),
                        "is_generated_default": is_gen,
                    })

                # If FKs exist, get allowed parent options for easy UI selection
                fk_options = {}
                for col in columns:
                    if col["is_foreign_key"] and col["referenced_table"] and col["referenced_column"]:
                        ref_tbl = col["referenced_table"]
                        ref_col = col["referenced_column"]
                        try:
                            # Fetch display column if possible
                            display_col = ref_col
                            if ref_tbl == "departments": display_col = "dept_name"
                            elif ref_tbl == "instructors": display_col = "instructor_name"
                            elif ref_tbl == "courses": display_col = "course_name"
                            elif ref_tbl == "students": display_col = "student_name"

                            cur.execute(f"SELECT `{ref_col}`, `{display_col}` FROM `{ref_tbl}` LIMIT 50")
                            opts = cur.fetchall()
                            fk_options[col["name"]] = [
                                {"value": o[ref_col], "label": f"{o[ref_col]} - {o[display_col]}"}
                                for o in opts
                            ]
                        except Exception:
                            pass

                return {
                    "table_name": table_name,
                    "staging_table": f"staging_{table_name}",
                    "columns": columns,
                    "fk_options": fk_options
                }
        finally:
            conn.close()

    @staticmethod
    def ingest_record(
        table_name: str,
        record_data: Dict[str, Any],
        external_ref: Optional[str] = None,
        operator: str = "ADMIN_USER"
    ) -> Dict[str, Any]:
        table_name = validate_identifier(table_name.lower())
        if table_name not in CORE_BUSINESS_TABLES:
            raise ValueError(f"Table '{table_name}' is not one of the six core business tables.")

        staging_table = f"staging_{table_name}"
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Fetch column metadata for target business table
                cur.execute("""
                    SELECT 
                        c.COLUMN_NAME, c.DATA_TYPE, c.IS_NULLABLE, c.COLUMN_KEY, c.EXTRA, c.COLUMN_DEFAULT,
                        kcu.REFERENCED_TABLE_NAME, kcu.REFERENCED_COLUMN_NAME
                    FROM information_schema.COLUMNS c
                    LEFT JOIN information_schema.KEY_COLUMN_USAGE kcu
                        ON c.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                        AND c.TABLE_NAME = kcu.TABLE_NAME
                        AND c.COLUMN_NAME = kcu.COLUMN_NAME
                        AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                    WHERE c.TABLE_SCHEMA = DATABASE() AND c.TABLE_NAME = %s
                """, (table_name,))
                cols = {r["COLUMN_NAME"]: r for r in cur.fetchall()}
                pk_col = next((c for c, r in cols.items() if r["COLUMN_KEY"] == "PRI"), "id")

                # Clean record_data:
                # - Filter out non-existent columns and auto-increment PK
                # - Never insert literal SQL expressions (CURRENT_TIMESTAMP, NOW()) into datetime/timestamp columns
                # - If timestamp has a DB-generated default and no valid user-supplied datetime, omit it so MySQL default applies
                # - Preserve legitimate user-supplied timestamps/datetimes
                cleaned_data = {}
                for k, v in record_data.items():
                    if k not in cols or k == pk_col:
                        continue
                    if v is None or v == "":
                        continue

                    meta = cols[k]
                    dt = (meta.get("DATA_TYPE") or "").lower()
                    is_gen = is_db_generated_timestamp(dt, meta.get("COLUMN_DEFAULT"), meta.get("EXTRA"))

                    if dt in ("timestamp", "datetime"):
                        if is_sql_default_expr(v):
                            # Omit so MySQL default applies automatically
                            continue
                        cleaned_data[k] = v
                    elif dt == "date":
                        if is_sql_default_expr(v):
                            continue
                        cleaned_data[k] = v
                    else:
                        if isinstance(v, str) and v.strip().lower() == "default":
                            continue
                        cleaned_data[k] = v

                # 2. Stage the record in staging table first
                cur.execute(f"DESCRIBE `{staging_table}`")
                existing_staging_cols = {r["Field"] for r in cur.fetchall()}

                # Match staging columns with cleaned_data
                valid_staging_cols = [c for c in cleaned_data.keys() if c in existing_staging_cols]
                valid_staging_vals = [cleaned_data[c] for c in valid_staging_cols]

                if external_ref and "external_ref" in existing_staging_cols:
                    valid_staging_cols.append("external_ref")
                    valid_staging_vals.append(external_ref)

                insert_staging_sql = f"""
                    INSERT INTO `{staging_table}` ({', '.join([f'`{c}`' for c in valid_staging_cols])})
                    VALUES ({', '.join(['%s'] * len(valid_staging_cols))})
                """
                cur.execute(insert_staging_sql, tuple(valid_staging_vals))
                staging_id = cur.lastrowid

                # 3. Validation Pipeline
                validation_errors = []

                # A. Mandatory column checks
                for col_name, meta in cols.items():
                    if col_name == pk_col:
                        continue
                    is_gen = is_db_generated_timestamp(meta.get("DATA_TYPE"), meta.get("COLUMN_DEFAULT"), meta.get("EXTRA"))
                    if not is_gen and meta["IS_NULLABLE"] == "NO" and meta.get("COLUMN_DEFAULT") is None:
                        val = cleaned_data.get(col_name)
                        if val is None or str(val).strip() == "":
                            validation_errors.append(f"Column '{col_name}' is mandatory and cannot be null or empty.")

                # B. Datetime / Date format verification for explicitly provided values
                for col_name, val in cleaned_data.items():
                    if col_name in cols:
                        meta = cols[col_name]
                        dt = (meta.get("DATA_TYPE") or "").lower()
                        if dt in ("timestamp", "datetime"):
                            val_str = str(val).strip().replace("T", " ")
                            try:
                                datetime.fromisoformat(val_str)
                            except Exception:
                                validation_errors.append(f"Invalid timestamp/datetime format for '{col_name}': '{val}'.")
                        elif dt == "date":
                            val_str = str(val).strip()
                            try:
                                datetime.strptime(val_str, "%Y-%m-%d")
                            except Exception:
                                validation_errors.append(f"Invalid date format for '{col_name}': '{val}'. Expected YYYY-MM-DD.")

                # B. Foreign key parent existence check
                for col_name, meta in cols.items():
                    if meta.get("REFERENCED_TABLE_NAME") and meta.get("REFERENCED_COLUMN_NAME"):
                        val = cleaned_data.get(col_name)
                        if val is not None and str(val).strip() != "":
                            ref_tbl = meta["REFERENCED_TABLE_NAME"]
                            ref_col = meta["REFERENCED_COLUMN_NAME"]
                            cur.execute(f"SELECT COUNT(*) as c FROM `{ref_tbl}` WHERE `{ref_col}` = %s", (val,))
                            if cur.fetchone()["c"] == 0:
                                validation_errors.append(f"Foreign key reference failed: {col_name}={val} does not exist in parent table '{ref_tbl}'.")

                # C. Numerical & domain constraints
                if table_name == "students":
                    if "age" in cleaned_data:
                        try:
                            age_val = int(cleaned_data["age"])
                            if age_val < 16 or age_val > 65:
                                validation_errors.append(f"Student age {age_val} is out of permitted range (16 - 65).")
                        except ValueError:
                            validation_errors.append(f"Student age must be a valid integer.")
                    if "gpa" in cleaned_data:
                        try:
                            gpa_val = float(cleaned_data["gpa"])
                            if gpa_val < 0.0 or gpa_val > 4.0:
                                validation_errors.append(f"Student GPA {gpa_val} is out of permitted range (0.00 - 4.00).")
                        except ValueError:
                            validation_errors.append(f"Student GPA must be a valid decimal number.")
                    if "email" in cleaned_data and cleaned_data["email"]:
                        email = str(cleaned_data["email"]).strip()
                        if "@" not in email or "." not in email:
                            validation_errors.append(f"Email '{email}' has invalid syntax.")
                        else:
                            cur.execute("SELECT COUNT(*) as c FROM students WHERE email = %s", (email,))
                            if cur.fetchone()["c"] > 0:
                                validation_errors.append(f"Student email '{email}' already exists in production (Uniqueness violation).")

                elif table_name == "departments":
                    if "budget" in cleaned_data:
                        try:
                            budget_val = float(cleaned_data["budget"])
                            if budget_val < 0:
                                validation_errors.append(f"Department budget cannot be negative ({budget_val}).")
                        except ValueError:
                            validation_errors.append(f"Department budget must be a valid number.")
                    if "dept_code" in cleaned_data and cleaned_data["dept_code"]:
                        cur.execute("SELECT COUNT(*) as c FROM departments WHERE dept_code = %s", (cleaned_data["dept_code"],))
                        if cur.fetchone()["c"] > 0:
                            validation_errors.append(f"Department code '{cleaned_data['dept_code']}' already exists.")

                elif table_name == "courses":
                    if "credits" in cleaned_data:
                        try:
                            cred_val = int(cleaned_data["credits"])
                            if cred_val < 1 or cred_val > 12:
                                validation_errors.append(f"Course credits {cred_val} out of permitted range (1 - 12).")
                        except ValueError:
                            validation_errors.append("Course credits must be a valid integer.")
                    if "course_code" in cleaned_data and cleaned_data["course_code"]:
                        cur.execute("SELECT COUNT(*) as c FROM courses WHERE course_code = %s", (cleaned_data["course_code"],))
                        if cur.fetchone()["c"] > 0:
                            validation_errors.append(f"Course code '{cleaned_data['course_code']}' already exists.")

                elif table_name == "enrollments":
                    if "grade_marks" in cleaned_data and cleaned_data["grade_marks"] is not None:
                        try:
                            marks = float(cleaned_data["grade_marks"])
                            if marks < 0 or marks > 100:
                                validation_errors.append(f"Grade marks {marks} out of allowable range (0 - 100).")
                        except ValueError:
                            validation_errors.append("Grade marks must be a valid number.")
                    if "status" in cleaned_data and cleaned_data["status"]:
                        if cleaned_data["status"] not in ['ENROLLED', 'COMPLETED', 'DROPPED']:
                            validation_errors.append(f"Invalid enrollment status '{cleaned_data['status']}'. Must be ENROLLED, COMPLETED, or DROPPED.")
                    if "student_id" in cleaned_data and "course_id" in cleaned_data:
                        cur.execute("SELECT COUNT(*) as c FROM enrollments WHERE student_id = %s AND course_id = %s", (cleaned_data["student_id"], cleaned_data["course_id"]))
                        if cur.fetchone()["c"] > 0:
                            validation_errors.append("Student is already enrolled in this course (Duplicate enrollment violation).")

                elif table_name == "classrooms":
                    if "capacity" in cleaned_data:
                        try:
                            cap = int(cleaned_data["capacity"])
                            if cap < 1 or cap > 500:
                                validation_errors.append(f"Classroom capacity {cap} out of allowable range (1 - 500 seats).")
                        except ValueError:
                            validation_errors.append("Classroom capacity must be a valid integer.")
                    if "room_number" in cleaned_data and cleaned_data["room_number"]:
                        cur.execute("SELECT COUNT(*) as c FROM classrooms WHERE room_number = %s", (cleaned_data["room_number"],))
                        if cur.fetchone()["c"] > 0:
                            validation_errors.append(f"Room number '{cleaned_data['room_number']}' already exists in classrooms.")

                # 4. If VALID -> Transactionally insert into production business table
                if len(validation_errors) == 0:
                    prod_cols = [c for c in cleaned_data.keys() if c in cols]
                    prod_col_names = ", ".join([f"`{c}`" for c in prod_cols])
                    prod_placeholders = ", ".join(["%s"] * len(prod_cols))
                    prod_vals = [cleaned_data[c] for c in prod_cols]

                    cur.execute(f"INSERT INTO `{table_name}` ({prod_col_names}) VALUES ({prod_placeholders})", tuple(prod_vals))
                    prod_id = cur.lastrowid

                    # Update staging table
                    cur.execute(f"UPDATE `{staging_table}` SET validation_status = 'VALID', validation_error = NULL WHERE staging_id = %s", (staging_id,))
                    conn.commit()

                    AuditService.log_event(
                        event_type="DATA_INGESTION_SUCCESS",
                        action_description=f"Record ingested into staging and committed to production `{table_name}` with ID={prod_id}.",
                        actor=operator,
                        result="SUCCESS"
                    )

                    return {
                        "success": True,
                        "status": "COMMITTED_TO_PRODUCTION",
                        "staging_id": staging_id,
                        "production_pk": prod_id,
                        "quarantine_id": None,
                        "target_table": table_name,
                        "message": f"Record successfully validated and committed to production table `{table_name}` (ID={prod_id}).",
                        "validation_errors": []
                    }

                # 5. If INVALID -> Mark staging as REJECTED and archive into quarantine_records
                else:
                    err_msg = "; ".join(validation_errors)
                    cur.execute(f"UPDATE `{staging_table}` SET validation_status = 'REJECTED', validation_error = %s WHERE staging_id = %s", (err_msg, staging_id))
                    
                    # Insert into quarantine_records
                    cur.execute("""
                        INSERT INTO quarantine_records (
                            source_table, source_pk_value, issue_type, row_data_json, quarantine_reason, quarantined_by
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        staging_table,
                        str(staging_id),
                        "INGESTION_VALIDATION_FAILURE",
                        json.dumps(cleaned_data, default=str),
                        f"Ingestion rejected: {err_msg}",
                        operator
                    ))
                    quarantine_id = cur.lastrowid
                    conn.commit()

                    AuditService.log_event(
                        event_type="DATA_INGESTION_REJECTED",
                        action_description=f"Record rejected during ingestion into `{staging_table}` (ID={staging_id}) and moved to quarantine (ID={quarantine_id}): {err_msg}",
                        actor=operator,
                        result="FAILURE",
                        error_message=err_msg
                    )

                    return {
                        "success": False,
                        "status": "REJECTED_TO_QUARANTINE",
                        "staging_id": staging_id,
                        "production_pk": None,
                        "quarantine_id": quarantine_id,
                        "target_table": table_name,
                        "message": f"Validation failed! Record was rejected and quarantined (Quarantine ID: {quarantine_id}).",
                        "validation_errors": validation_errors
                    }

        except Exception as e:
            conn.rollback()
            logger.error(f"Ingestion error: {e}")
            raise e
        finally:
            conn.close()

