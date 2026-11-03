import logging
import json
import pymysql
from backend.app.database.connection import get_connection

logger = logging.getLogger(__name__)

SYSTEM_TABLES_DDL = """
-- Quarantine Records Table
CREATE TABLE IF NOT EXISTS `quarantine_records` (
    `quarantine_id` INT AUTO_INCREMENT PRIMARY KEY,
    `source_table` VARCHAR(100) NOT NULL,
    `source_pk_value` VARCHAR(100) NOT NULL,
    `issue_type` VARCHAR(50) NOT NULL,
    `row_data_json` LONGTEXT NOT NULL,
    `quarantine_reason` TEXT NOT NULL,
    `quarantined_by` VARCHAR(100) DEFAULT 'SYSTEM',
    `quarantined_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `resolved` BOOLEAN DEFAULT FALSE,
    `resolution_notes` TEXT NULL,
    INDEX `idx_quarantine_src` (`source_table`, `source_pk_value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Integrity Rules Configuration Table
CREATE TABLE IF NOT EXISTS `integrity_rules` (
    `rule_id` INT AUTO_INCREMENT PRIMARY KEY,
    `rule_code` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(150) NOT NULL,
    `description` TEXT NOT NULL,
    `rule_type` ENUM('ORPHAN', 'DUPLICATE', 'NULL_CHECK', 'DOMAIN_CHECK', 'RELATIONAL_CONSISTENCY') NOT NULL,
    `target_table` VARCHAR(100) NOT NULL,
    `target_column` VARCHAR(100) NOT NULL,
    `parent_table` VARCHAR(100) NULL,
    `parent_column` VARCHAR(100) NULL,
    `parameters_json` LONGTEXT NULL,
    `severity` ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'MEDIUM',
    `is_enabled` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_rule_type` (`rule_type`),
    INDEX `idx_target_table` (`target_table`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Scan Runs Execution History
CREATE TABLE IF NOT EXISTS `scan_runs` (
    `scan_id` VARCHAR(50) PRIMARY KEY,
    `scan_type` ENUM('FULL', 'TABLE') NOT NULL DEFAULT 'FULL',
    `target_tables` TEXT NULL,
    `start_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `end_time` TIMESTAMP NULL,
    `status` ENUM('RUNNING', 'COMPLETED', 'FAILED') NOT NULL DEFAULT 'RUNNING',
    `total_rows_inspected` INT DEFAULT 0,
    `issues_found` INT DEFAULT 0,
    `critical_count` INT DEFAULT 0,
    `high_count` INT DEFAULT 0,
    `medium_count` INT DEFAULT 0,
    `low_count` INT DEFAULT 0,
    `error_message` TEXT NULL,
    INDEX `idx_scan_status` (`status`),
    INDEX `idx_scan_time` (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Integrity Issues Catalog
CREATE TABLE IF NOT EXISTS `integrity_issues` (
    `issue_id` VARCHAR(50) PRIMARY KEY,
    `scan_id` VARCHAR(50) NOT NULL,
    `rule_id` INT NULL,
    `rule_code` VARCHAR(50) NOT NULL,
    `category` ENUM('ORPHAN', 'DUPLICATE', 'NULL_VIOLATION', 'DOMAIN_VIOLATION', 'RELATIONAL_VIOLATION', 'SYSTEM_INTEGRITY') NOT NULL,
    `severity` ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'MEDIUM',
    `table_name` VARCHAR(100) NOT NULL,
    `record_id` VARCHAR(100) NOT NULL,
    `column_name` VARCHAR(100) NULL,
    `invalid_value` TEXT NULL,
    `description` TEXT NOT NULL,
    `status` ENUM('OPEN', 'REVIEWED', 'APPROVED', 'REPAIRED', 'IGNORED', 'FAILED') NOT NULL DEFAULT 'OPEN',
    `ignored_reason` TEXT NULL,
    `detected_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `repaired_at` TIMESTAMP NULL,
    INDEX `idx_issue_status` (`status`),
    INDEX `idx_issue_table` (`table_name`),
    INDEX `idx_issue_scan` (`scan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Repair Recommendations Table
CREATE TABLE IF NOT EXISTS `repair_recommendations` (
    `recommendation_id` INT AUTO_INCREMENT PRIMARY KEY,
    `issue_id` VARCHAR(50) NOT NULL,
    `strategy` ENUM('RESTORE_PARENT', 'MAP_PARENT', 'QUARANTINE', 'DELETE_RECORD', 'MERGE_DUPLICATE', 'SET_DEFAULT', 'MANUAL_INTERVENTION') NOT NULL,
    `problem_description` TEXT NOT NULL,
    `proposed_action` TEXT NOT NULL,
    `reason` TEXT NOT NULL,
    `expected_impact` TEXT NOT NULL,
    `risk_level` ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'MEDIUM',
    `is_reversible` BOOLEAN NOT NULL DEFAULT TRUE,
    `requires_approval` BOOLEAN NOT NULL DEFAULT TRUE,
    `approval_status` ENUM('PENDING', 'APPROVED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_rec_issue` (`issue_id`),
    INDEX `idx_rec_approval` (`approval_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Repair Executions Tracking
CREATE TABLE IF NOT EXISTS `repair_executions` (
    `execution_id` VARCHAR(50) PRIMARY KEY,
    `recommendation_id` INT NULL,
    `issue_id` VARCHAR(50) NOT NULL,
    `transaction_id` VARCHAR(50) NOT NULL,
    `status` ENUM('SUCCESS', 'FAILED', 'ROLLED_BACK') NOT NULL,
    `executed_by` VARCHAR(100) NOT NULL DEFAULT 'ADMIN_USER',
    `executed_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `before_state_json` LONGTEXT NULL,
    `after_state_json` LONGTEXT NULL,
    `sql_executed` TEXT NULL,
    `error_message` TEXT NULL,
    `execution_time_ms` INT DEFAULT 0,
    INDEX `idx_exec_issue` (`issue_id`),
    INDEX `idx_exec_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS `audit_logs` (
    `event_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(50) NOT NULL,
    `actor` VARCHAR(100) NOT NULL DEFAULT 'SYSTEM',
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `related_scan_id` VARCHAR(50) NULL,
    `related_issue_id` VARCHAR(50) NULL,
    `related_transaction_id` VARCHAR(50) NULL,
    `action_description` TEXT NOT NULL,
    `target_table` VARCHAR(100) NULL,
    `record_identifier` VARCHAR(100) NULL,
    `result` ENUM('SUCCESS', 'FAILURE', 'INFO', 'WARNING') NOT NULL DEFAULT 'SUCCESS',
    `before_values_json` LONGTEXT NULL,
    `after_values_json` LONGTEXT NULL,
    `error_message` TEXT NULL,
    INDEX `idx_audit_timestamp` (`timestamp`),
    INDEX `idx_audit_event_type` (`event_type`),
    INDEX `idx_audit_table` (`target_table`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transaction Logs Table
CREATE TABLE IF NOT EXISTS `transaction_logs` (
    `transaction_id` VARCHAR(50) PRIMARY KEY,
    `execution_id` VARCHAR(50) NULL,
    `start_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `end_time` TIMESTAMP NULL,
    `status` ENUM('COMMITTED', 'ROLLED_BACK', 'FAILED') NOT NULL,
    `operations_count` INT DEFAULT 1,
    `savepoints_used` INT DEFAULT 0,
    `rollback_reason` TEXT NULL,
    `duration_ms` INT DEFAULT 0,
    INDEX `idx_tx_status` (`status`),
    INDEX `idx_tx_start` (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Recovery Checkpoints Table
CREATE TABLE IF NOT EXISTS `recovery_checkpoints` (
    `checkpoint_id` VARCHAR(50) PRIMARY KEY,
    `checkpoint_name` VARCHAR(150) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `checkpoint_type` ENUM('PRE_REPAIR', 'MANUAL', 'SCHEDULED') NOT NULL DEFAULT 'PRE_REPAIR',
    `target_table` VARCHAR(100) NOT NULL,
    `snapshot_metadata_json` LONGTEXT NOT NULL,
    `snapshot_rows_json` LONGTEXT NOT NULL,
    `status` ENUM('ACTIVE', 'RESTORED', 'EXPIRED') NOT NULL DEFAULT 'ACTIVE',
    INDEX `idx_ckpt_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Database Metadata Key-Value Store
CREATE TABLE IF NOT EXISTS `database_metadata` (
    `meta_key` VARCHAR(100) PRIMARY KEY,
    `meta_value` TEXT NOT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

ACADEMIC_INTEGRITY_RULES = [
    {
        "rule_code": "RULE_DUP_DEPT_CODE",
        "name": "Duplicate Department Code",
        "description": "Enforces logical uniqueness for department code identifiers (e.g., CS, EE).",
        "rule_type": "DUPLICATE",
        "target_table": "departments",
        "target_column": "dept_code",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "dept_code"
            ],
            "case_sensitive": False
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DUP_DEPT_NAME",
        "name": "Duplicate Department Name",
        "description": "Detects redundant department records having identical human-readable department names.",
        "rule_type": "DUPLICATE",
        "target_table": "departments",
        "target_column": "dept_name",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "dept_name"
            ]
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_DEPT_CODE",
        "name": "Mandatory Department Code",
        "description": "Ensures department records possess a non-empty departmental acronym.",
        "rule_type": "NULL_CHECK",
        "target_table": "departments",
        "target_column": "dept_code",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_DEPT_NAME",
        "name": "Mandatory Department Name",
        "description": "Ensures that all academic departments possess an official non-empty title.",
        "rule_type": "NULL_CHECK",
        "target_table": "departments",
        "target_column": "dept_name",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_DEPT_BUDGET",
        "name": "Department Operating Budget Non-Negative",
        "description": "Validates that departmental operating budgets are non-negative values.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "departments",
        "target_column": "budget",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 0.0,
            "allow_None": False
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_INSTRUCTOR_DEPT",
        "name": "Instructor Missing Department Reference",
        "description": "Verifies that foreign key dept_id in instructors resolves to a registered department.",
        "rule_type": "ORPHAN",
        "target_table": "instructors",
        "target_column": "dept_id",
        "parent_table": "departments",
        "parent_column": "dept_id",
        "parameters_json": {
            "allow_None": True,
            "strategy": "MAP_PARENT"
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DUP_INSTRUCTOR_EMAIL",
        "name": "Duplicate Instructor Email",
        "description": "Enforces unique contact email addresses across faculty instructor profiles.",
        "rule_type": "DUPLICATE",
        "target_table": "instructors",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "email"
            ]
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_INSTRUCTOR_NAME",
        "name": "Mandatory Instructor Name",
        "description": "Ensures that faculty instructor records do not contain empty or NULL names.",
        "rule_type": "NULL_CHECK",
        "target_table": "instructors",
        "target_column": "instructor_name",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_INSTRUCTOR_EMAIL",
        "name": "Mandatory Instructor Email",
        "description": "Ensures that all faculty members have a primary contact email specified.",
        "rule_type": "NULL_CHECK",
        "target_table": "instructors",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_INSTRUCTOR_SALARY",
        "name": "Faculty Salary Non-Negative",
        "description": "Ensures faculty compensation is greater than or equal to zero.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "instructors",
        "target_column": "salary",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 0.0,
            "allow_None": False
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_INSTRUCTOR_EMAIL",
        "name": "Instructor Email Syntax Validation",
        "description": "Ensures instructor email addresses conform to valid RFC-compliant user@domain syntax.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "instructors",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "regex_pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
        },
        "severity": "MEDIUM",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_COURSE_DEPT",
        "name": "Course Department Reference Check",
        "description": "Ensures that dept_id in courses correctly points to an existing academic department.",
        "rule_type": "ORPHAN",
        "target_table": "courses",
        "target_column": "dept_id",
        "parent_table": "departments",
        "parent_column": "dept_id",
        "parameters_json": {
            "allow_None": True,
            "strategy": "MAP_PARENT"
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_COURSE_INSTRUCTOR",
        "name": "Course Missing Assigned Instructor",
        "description": "Verifies that foreign key instructor_id in courses points to a valid active instructor.",
        "rule_type": "ORPHAN",
        "target_table": "courses",
        "target_column": "instructor_id",
        "parent_table": "instructors",
        "parent_column": "instructor_id",
        "parameters_json": {
            "allow_None": True,
            "strategy": "MAP_PARENT"
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DUP_COURSE_CODE",
        "name": "Duplicate Course Code",
        "description": "Ensures catalog course codes (e.g. CS101, EE101) are strictly unique.",
        "rule_type": "DUPLICATE",
        "target_table": "courses",
        "target_column": "course_code",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "course_code"
            ]
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_COURSE_CODE",
        "name": "Mandatory Course Code",
        "description": "Ensures all courses possess a non-empty curricular course code.",
        "rule_type": "NULL_CHECK",
        "target_table": "courses",
        "target_column": "course_code",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_COURSE_NAME",
        "name": "Mandatory Course Name",
        "description": "Validates that all courses possess a descriptive title and not NULL.",
        "rule_type": "NULL_CHECK",
        "target_table": "courses",
        "target_column": "course_name",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_COURSE_CREDITS",
        "name": "Mandatory Course Credits",
        "description": "Validates that courses have an explicit credit value assigned.",
        "rule_type": "NULL_CHECK",
        "target_table": "courses",
        "target_column": "credits",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_COURSE_CREDITS",
        "name": "Permitted Course Credits Range (1-12)",
        "description": "Ensures academic credit weightings fall between 1 and 12 credits.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "courses",
        "target_column": "credits",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 1,
            "max_value": 12,
            "allow_None": False
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_STUDENT_DEPT",
        "name": "Student Missing Department Reference",
        "description": "Verifies that foreign key dept_id in students table correctly resolves to a registered department.",
        "rule_type": "ORPHAN",
        "target_table": "students",
        "target_column": "dept_id",
        "parent_table": "departments",
        "parent_column": "dept_id",
        "parameters_json": {
            "allow_None": True,
            "strategy": "MAP_PARENT"
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DUP_STUDENT_EMAIL",
        "name": "Duplicate Student Email Address",
        "description": "Enforces logical uniqueness for student contact emails to prevent profile collision.",
        "rule_type": "DUPLICATE",
        "target_table": "students",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "email"
            ],
            "case_sensitive": False
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_STUDENT_NAME",
        "name": "Mandatory Student Name",
        "description": "Ensures that student records do not contain empty or NULL student names.",
        "rule_type": "NULL_CHECK",
        "target_table": "students",
        "target_column": "student_name",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_STUDENT_EMAIL",
        "name": "Mandatory Student Email",
        "description": "Ensures that student identity records have a non-empty contact email.",
        "rule_type": "NULL_CHECK",
        "target_table": "students",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_STUDENT_AGE",
        "name": "Student Age Range (16-65)",
        "description": "Validates that student ages fall within collegiate admission range between 16 and 65.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "age",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 16,
            "max_value": 65,
            "allow_None": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_STUDENT_GPA",
        "name": "Student GPA Scale (0.00 - 4.00)",
        "description": "Validates that academic GPA records strictly conform to the 4.00 maximum point scale.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "gpa",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 0.0,
            "max_value": 4.0,
            "allow_None": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_EMAIL_FORMAT",
        "name": "Valid Email Syntax Pattern",
        "description": "Ensures email values conform to a standard user@domain format.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "regex_pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
        },
        "severity": "MEDIUM",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_STUDENT_ENROLL_YEAR",
        "name": "Student Matriculation Year Range",
        "description": "Validates that enrollment year falls within legitimate bounds (1950 to 2030).",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "students",
        "target_column": "enrollment_year",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 1950,
            "max_value": 2030,
            "allow_None": True
        },
        "severity": "MEDIUM",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_ENROLLMENT_STUDENT",
        "name": "Enrollment Orphan Student Reference",
        "description": "Verifies that student_id in enrollments resolves to an existing registered student.",
        "rule_type": "ORPHAN",
        "target_table": "enrollments",
        "target_column": "student_id",
        "parent_table": "students",
        "parent_column": "student_id",
        "parameters_json": {
            "allow_None": False,
            "strategy": "MAP_PARENT"
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_ENROLLMENT_COURSE",
        "name": "Enrollment Orphan Course Reference",
        "description": "Verifies that course_id in enrollments resolves to an active course in the catalog.",
        "rule_type": "ORPHAN",
        "target_table": "enrollments",
        "target_column": "course_id",
        "parent_table": "courses",
        "parent_column": "course_id",
        "parameters_json": {
            "allow_None": False,
            "strategy": "MAP_PARENT"
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DUP_ENROLLMENT_PAIR",
        "name": "Duplicate Student Course Enrollment",
        "description": "Prevents duplicate enrollment pairs of the same student in the same course.",
        "rule_type": "DUPLICATE",
        "target_table": "enrollments",
        "target_column": "student_id,course_id",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "student_id",
                "course_id"
            ]
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_ENROLLMENT_STUDENT",
        "name": "Mandatory Enrollment Student ID",
        "description": "Ensures student_id foreign key in enrollments is NOT NULL.",
        "rule_type": "NULL_CHECK",
        "target_table": "enrollments",
        "target_column": "student_id",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_ENROLLMENT_COURSE",
        "name": "Mandatory Enrollment Course ID",
        "description": "Ensures course_id foreign key in enrollments is NOT NULL.",
        "rule_type": "NULL_CHECK",
        "target_table": "enrollments",
        "target_column": "course_id",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_ENROLLMENT_STATUS",
        "name": "Mandatory Enrollment Status",
        "description": "Ensures that enrollment records contain a valid non-empty enrollment status.",
        "rule_type": "NULL_CHECK",
        "target_table": "enrollments",
        "target_column": "status",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_ENROLLMENT_DATE",
        "name": "Mandatory Enrollment Date",
        "description": "Ensures that the date of enrollment is recorded and not NULL.",
        "rule_type": "NULL_CHECK",
        "target_table": "enrollments",
        "target_column": "enrolled_on",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_ENROLLMENT_GRADE",
        "name": "Enrollment Grade Marks Range (0-100)",
        "description": "Ensures final evaluation grade marks are within 0.00 and 100.00.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "enrollments",
        "target_column": "grade_marks",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 0.0,
            "max_value": 100.0,
            "allow_None": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_ENROLLMENT_STATUS_ENUM",
        "name": "Allowed Enrollment Status Values",
        "description": "Restricts enrollment status to allowed enum values: ENROLLED, COMPLETED, DROPPED.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "enrollments",
        "target_column": "status",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "allowed_values": [
                "ENROLLED",
                "COMPLETED",
                "DROPPED"
            ],
            "allow_None": False
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_STAGING_STUDENT",
        "name": "Staging Enrollment Orphan Student Reference",
        "description": "Detects enrollment records in staging table referencing non-existent student IDs in students table.",
        "rule_type": "ORPHAN",
        "target_table": "staging_enrollments",
        "target_column": "student_id",
        "parent_table": "students",
        "parent_column": "student_id",
        "parameters_json": {
            "allow_None": False,
            "strategy": "RESTORE_PARENT"
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_ORPHAN_STAGING_COURSE",
        "name": "Staging Enrollment Orphan Course Reference",
        "description": "Detects enrollment records in staging table referencing non-existent course IDs in courses table.",
        "rule_type": "ORPHAN",
        "target_table": "staging_enrollments",
        "target_column": "course_id",
        "parent_table": "courses",
        "parent_column": "course_id",
        "parameters_json": {
            "allow_None": False,
            "strategy": "RESTORE_PARENT"
        },
        "severity": "CRITICAL",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DUP_STAGING_ENROLLMENT",
        "name": "Duplicate Staging Enrollment Pair",
        "description": "Flags duplicate (student_id, course_id) registration attempts prior to canonical table ingestion.",
        "rule_type": "DUPLICATE",
        "target_table": "staging_enrollments",
        "target_column": "student_id,course_id",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "student_id",
                "course_id"
            ]
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DUP_STAGING_EXT_REF",
        "name": "Duplicate Staging External Reference",
        "description": "Enforces unique batch external reference identifiers (e.g., EXT-1001) in staging.",
        "rule_type": "DUPLICATE",
        "target_table": "staging_enrollments",
        "target_column": "external_ref",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "group_by": [
                "external_ref"
            ]
        },
        "severity": "MEDIUM",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_STAGING_STUDENT",
        "name": "Mandatory Staging Student Reference",
        "description": "Ensures imported staging batches have a valid student reference ID.",
        "rule_type": "NULL_CHECK",
        "target_table": "staging_enrollments",
        "target_column": "student_id",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_STAGING_COURSE",
        "name": "Mandatory Staging Course Reference",
        "description": "Ensures imported staging batches have a valid course reference ID.",
        "rule_type": "NULL_CHECK",
        "target_table": "staging_enrollments",
        "target_column": "course_id",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_NULL_STAGING_STATUS",
        "name": "Mandatory Staging Status",
        "description": "Ensures imported staging records contain a non-empty status attribute.",
        "rule_type": "NULL_CHECK",
        "target_table": "staging_enrollments",
        "target_column": "status",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "disallow_empty_string": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_MARKS_RANGE",
        "name": "Evaluation Grade Marks Range (0-100)",
        "description": "Ensures student evaluation marks in staging enrollments are within valid 0.00 to 100.00 range.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "staging_enrollments",
        "target_column": "grade_marks",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "min_value": 0.0,
            "max_value": 100.0,
            "allow_None": True
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_ENROLLMENT_STATUS",
        "name": "Valid Enrollment Status Enum",
        "description": "Ensures status matches allowed values: ENROLLED, COMPLETED, DROPPED.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "staging_enrollments",
        "target_column": "status",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "allowed_values": [
                "ENROLLED",
                "COMPLETED",
                "DROPPED"
            ],
            "allow_None": False
        },
        "severity": "MEDIUM",
        "is_enabled": True
    },
    {
        "rule_code": "RULE_DOMAIN_STAGING_EMAIL",
        "name": "Staging Contact Email Syntax",
        "description": "Ensures student_email in staging conforms to valid RFC user@domain pattern.",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "staging_enrollments",
        "target_column": "student_email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "regex_pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
        },
        "severity": "MEDIUM",
        "is_enabled": True
    }
]

def ensure_system_tables_exist(conn=None) -> bool:
    """
    Safely creates system engine tables with IF NOT EXISTS.
    Leaves user business tables completely untouched.
    Populates retail integrity rules catalog if rules table is newly initialized.
    """
    should_close = False
    if conn is None:
        try:
            conn = get_connection()
            should_close = True
        except Exception as e:
            logger.warning(f"Could not connect to database to verify system tables: {e}")
            return False

    try:
        with conn.cursor() as cur:
            # 1. Execute DDL for each table statement
            statements = [s.strip() for s in SYSTEM_TABLES_DDL.split(";") if s.strip()]
            for stmt in statements:
                cur.execute(stmt)

            # 2. Seed and sync integrity rules catalog without creating duplicates
            insert_sql = """
                INSERT INTO `integrity_rules` (
                    `rule_code`, `name`, `description`, `rule_type`,
                    `target_table`, `target_column`, `parent_table`, `parent_column`,
                    `parameters_json`, `severity`, `is_enabled`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    `name` = VALUES(`name`),
                    `description` = VALUES(`description`),
                    `parameters_json` = VALUES(`parameters_json`),
                    `severity` = VALUES(`severity`);
            """
            for r in ACADEMIC_INTEGRITY_RULES:
                cur.execute(insert_sql, (
                    r["rule_code"],
                    r["name"],
                    r["description"],
                    r["rule_type"],
                    r["target_table"],
                    r["target_column"],
                    r["parent_table"],
                    r["parent_column"],
                    json.dumps(r["parameters_json"]) if r["parameters_json"] else None,
                    r["severity"],
                    r["is_enabled"]
                ))

            # 3. Ensure metadata entry
            cur.execute("""
                INSERT INTO `database_metadata` (`meta_key`, `meta_value`)
                VALUES ('schema_type', 'ACADEMIC_SYSTEM')
                ON DUPLICATE KEY UPDATE `meta_value` = 'ACADEMIC_SYSTEM'
            """)

        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to ensure system tables: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        if should_close and conn:
            conn.close()

