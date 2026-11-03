-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 04: Integrity Rules Definition
-- Comprehensive rule catalog covering all 6 tables across all 4 categories:
-- ORPHAN, DUPLICATE, NULL_CHECK, DOMAIN_CHECK
-- Database: self_healing_test_db
-- =============================================================================

USE `self_healing_test_db`;

INSERT INTO `integrity_rules` (
    `rule_code`, `name`, `description`, `rule_type`, 
    `target_table`, `target_column`, `parent_table`, `parent_column`, 
    `parameters_json`, `severity`, `is_enabled`
) VALUES 
    (
        'RULE_DUP_DEPT_CODE',
        'Duplicate Department Code',
        'Enforces logical uniqueness for department code identifiers (e.g., CS, EE).',
        'DUPLICATE',
        'departments', 'dept_code', NULL, NULL,
        '{"group_by": ["dept_code"], "case_sensitive": false}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_DUP_DEPT_NAME',
        'Duplicate Department Name',
        'Detects redundant department records having identical human-readable department names.',
        'DUPLICATE',
        'departments', 'dept_name', NULL, NULL,
        '{"group_by": ["dept_name"]}',
        'HIGH', TRUE
    ),
    (
        'RULE_NULL_DEPT_CODE',
        'Mandatory Department Code',
        'Ensures department records possess a non-empty departmental acronym.',
        'NULL_CHECK',
        'departments', 'dept_code', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_DEPT_NAME',
        'Mandatory Department Name',
        'Ensures that all academic departments possess an official non-empty title.',
        'NULL_CHECK',
        'departments', 'dept_name', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_DOMAIN_DEPT_BUDGET',
        'Department Operating Budget Non-Negative',
        'Validates that departmental operating budgets are non-negative values.',
        'DOMAIN_CHECK',
        'departments', 'budget', NULL, NULL,
        '{"min_value": 0.0, "allow_null": false}',
        'HIGH', TRUE
    ),
    (
        'RULE_ORPHAN_INSTRUCTOR_DEPT',
        'Instructor Missing Department Reference',
        'Verifies that foreign key dept_id in instructors resolves to a registered department.',
        'ORPHAN',
        'instructors', 'dept_id', 'departments', 'dept_id',
        '{"allow_null": true, "strategy": "MAP_PARENT"}',
        'HIGH', TRUE
    ),
    (
        'RULE_DUP_INSTRUCTOR_EMAIL',
        'Duplicate Instructor Email',
        'Enforces unique contact email addresses across faculty instructor profiles.',
        'DUPLICATE',
        'instructors', 'email', NULL, NULL,
        '{"group_by": ["email"]}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_INSTRUCTOR_NAME',
        'Mandatory Instructor Name',
        'Ensures that faculty instructor records do not contain empty or NULL names.',
        'NULL_CHECK',
        'instructors', 'instructor_name', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_INSTRUCTOR_EMAIL',
        'Mandatory Instructor Email',
        'Ensures that all faculty members have a primary contact email specified.',
        'NULL_CHECK',
        'instructors', 'email', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_DOMAIN_INSTRUCTOR_SALARY',
        'Faculty Salary Non-Negative',
        'Ensures faculty compensation is greater than or equal to zero.',
        'DOMAIN_CHECK',
        'instructors', 'salary', NULL, NULL,
        '{"min_value": 0.0, "allow_null": false}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_INSTRUCTOR_EMAIL',
        'Instructor Email Syntax Validation',
        'Ensures instructor email addresses conform to valid RFC-compliant user@domain syntax.',
        'DOMAIN_CHECK',
        'instructors', 'email', NULL, NULL,
        '{"regex_pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"}',
        'MEDIUM', TRUE
    ),
    (
        'RULE_ORPHAN_COURSE_DEPT',
        'Course Department Reference Check',
        'Ensures that dept_id in courses correctly points to an existing academic department.',
        'ORPHAN',
        'courses', 'dept_id', 'departments', 'dept_id',
        '{"allow_null": true, "strategy": "MAP_PARENT"}',
        'HIGH', TRUE
    ),
    (
        'RULE_ORPHAN_COURSE_INSTRUCTOR',
        'Course Missing Assigned Instructor',
        'Verifies that foreign key instructor_id in courses points to a valid active instructor.',
        'ORPHAN',
        'courses', 'instructor_id', 'instructors', 'instructor_id',
        '{"allow_null": true, "strategy": "MAP_PARENT"}',
        'HIGH', TRUE
    ),
    (
        'RULE_DUP_COURSE_CODE',
        'Duplicate Course Code',
        'Ensures catalog course codes (e.g. CS101, EE101) are strictly unique.',
        'DUPLICATE',
        'courses', 'course_code', NULL, NULL,
        '{"group_by": ["course_code"]}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_COURSE_CODE',
        'Mandatory Course Code',
        'Ensures all courses possess a non-empty curricular course code.',
        'NULL_CHECK',
        'courses', 'course_code', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_COURSE_NAME',
        'Mandatory Course Name',
        'Validates that all courses possess a descriptive title and not NULL.',
        'NULL_CHECK',
        'courses', 'course_name', NULL, NULL,
        '{"disallow_empty_string": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_NULL_COURSE_CREDITS',
        'Mandatory Course Credits',
        'Validates that courses have an explicit credit value assigned.',
        'NULL_CHECK',
        'courses', 'credits', NULL, NULL,
        '{"disallow_empty_string": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_COURSE_CREDITS',
        'Permitted Course Credits Range (1-12)',
        'Ensures academic credit weightings fall between 1 and 12 credits.',
        'DOMAIN_CHECK',
        'courses', 'credits', NULL, NULL,
        '{"min_value": 1, "max_value": 12, "allow_null": false}',
        'HIGH', TRUE
    ),
    (
        'RULE_ORPHAN_STUDENT_DEPT',
        'Student Missing Department Reference',
        'Verifies that foreign key dept_id in students table correctly resolves to a registered department.',
        'ORPHAN',
        'students', 'dept_id', 'departments', 'dept_id',
        '{"allow_null": true, "strategy": "MAP_PARENT"}',
        'HIGH', TRUE
    ),
    (
        'RULE_DUP_STUDENT_EMAIL',
        'Duplicate Student Email Address',
        'Enforces logical uniqueness for student contact emails to prevent profile collision.',
        'DUPLICATE',
        'students', 'email', NULL, NULL,
        '{"group_by": ["email"], "case_sensitive": false}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_STUDENT_NAME',
        'Mandatory Student Name',
        'Ensures that student records do not contain empty or NULL student names.',
        'NULL_CHECK',
        'students', 'student_name', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_STUDENT_EMAIL',
        'Mandatory Student Email',
        'Ensures that student identity records have a non-empty contact email.',
        'NULL_CHECK',
        'students', 'email', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_DOMAIN_STUDENT_AGE',
        'Student Age Range (16-65)',
        'Validates that student ages fall within collegiate admission range between 16 and 65.',
        'DOMAIN_CHECK',
        'students', 'age', NULL, NULL,
        '{"min_value": 16, "max_value": 65, "allow_null": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_STUDENT_GPA',
        'Student GPA Scale (0.00 - 4.00)',
        'Validates that academic GPA records strictly conform to the 4.00 maximum point scale.',
        'DOMAIN_CHECK',
        'students', 'gpa', NULL, NULL,
        '{"min_value": 0.0, "max_value": 4.0, "allow_null": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_EMAIL_FORMAT',
        'Valid Email Syntax Pattern',
        'Ensures email values conform to a standard user@domain format.',
        'DOMAIN_CHECK',
        'students', 'email', NULL, NULL,
        '{"regex_pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"}',
        'MEDIUM', TRUE
    ),
    (
        'RULE_DOMAIN_STUDENT_ENROLL_YEAR',
        'Student Matriculation Year Range',
        'Validates that enrollment year falls within legitimate bounds (1950 to 2030).',
        'DOMAIN_CHECK',
        'students', 'enrollment_year', NULL, NULL,
        '{"min_value": 1950, "max_value": 2030, "allow_null": true}',
        'MEDIUM', TRUE
    ),
    (
        'RULE_ORPHAN_ENROLLMENT_STUDENT',
        'Enrollment Orphan Student Reference',
        'Verifies that student_id in enrollments resolves to an existing registered student.',
        'ORPHAN',
        'enrollments', 'student_id', 'students', 'student_id',
        '{"allow_null": false, "strategy": "MAP_PARENT"}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_ORPHAN_ENROLLMENT_COURSE',
        'Enrollment Orphan Course Reference',
        'Verifies that course_id in enrollments resolves to an active course in the catalog.',
        'ORPHAN',
        'enrollments', 'course_id', 'courses', 'course_id',
        '{"allow_null": false, "strategy": "MAP_PARENT"}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_DUP_ENROLLMENT_PAIR',
        'Duplicate Student Course Enrollment',
        'Prevents duplicate enrollment pairs of the same student in the same course.',
        'DUPLICATE',
        'enrollments', 'student_id,course_id', NULL, NULL,
        '{"group_by": ["student_id", "course_id"]}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_ENROLLMENT_STUDENT',
        'Mandatory Enrollment Student ID',
        'Ensures student_id foreign key in enrollments is NOT NULL.',
        'NULL_CHECK',
        'enrollments', 'student_id', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_ENROLLMENT_COURSE',
        'Mandatory Enrollment Course ID',
        'Ensures course_id foreign key in enrollments is NOT NULL.',
        'NULL_CHECK',
        'enrollments', 'course_id', NULL, NULL,
        '{"disallow_empty_string": true}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_ENROLLMENT_STATUS',
        'Mandatory Enrollment Status',
        'Ensures that enrollment records contain a valid non-empty enrollment status.',
        'NULL_CHECK',
        'enrollments', 'status', NULL, NULL,
        '{"disallow_empty_string": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_NULL_ENROLLMENT_DATE',
        'Mandatory Enrollment Date',
        'Ensures that the date of enrollment is recorded and not NULL.',
        'NULL_CHECK',
        'enrollments', 'enrolled_on', NULL, NULL,
        '{"disallow_empty_string": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_ENROLLMENT_GRADE',
        'Enrollment Grade Marks Range (0-100)',
        'Ensures final evaluation grade marks are within 0.00 and 100.00.',
        'DOMAIN_CHECK',
        'enrollments', 'grade_marks', NULL, NULL,
        '{"min_value": 0.0, "max_value": 100.0, "allow_null": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_ENROLLMENT_STATUS_ENUM',
        'Allowed Enrollment Status Values',
        'Restricts enrollment status to allowed enum values: ENROLLED, COMPLETED, DROPPED.',
        'DOMAIN_CHECK',
        'enrollments', 'status', NULL, NULL,
        '{"allowed_values": ["ENROLLED", "COMPLETED", "DROPPED"], "allow_null": false}',
        'HIGH', TRUE
    ),
    (
        'RULE_ORPHAN_STAGING_STUDENT',
        'Staging Enrollment Orphan Student Reference',
        'Detects enrollment records in staging table referencing non-existent student IDs in students table.',
        'ORPHAN',
        'staging_enrollments', 'student_id', 'students', 'student_id',
        '{"allow_null": false, "strategy": "RESTORE_PARENT"}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_ORPHAN_STAGING_COURSE',
        'Staging Enrollment Orphan Course Reference',
        'Detects enrollment records in staging table referencing non-existent course IDs in courses table.',
        'ORPHAN',
        'staging_enrollments', 'course_id', 'courses', 'course_id',
        '{"allow_null": false, "strategy": "RESTORE_PARENT"}',
        'CRITICAL', TRUE
    ),
    (
        'RULE_DUP_STAGING_ENROLLMENT',
        'Duplicate Staging Enrollment Pair',
        'Flags duplicate (student_id, course_id) registration attempts prior to canonical table ingestion.',
        'DUPLICATE',
        'staging_enrollments', 'student_id,course_id', NULL, NULL,
        '{"group_by": ["student_id", "course_id"]}',
        'HIGH', TRUE
    ),
    (
        'RULE_DUP_STAGING_EXT_REF',
        'Duplicate Staging External Reference',
        'Enforces unique batch external reference identifiers (e.g., EXT-1001) in staging.',
        'DUPLICATE',
        'staging_enrollments', 'external_ref', NULL, NULL,
        '{"group_by": ["external_ref"]}',
        'MEDIUM', TRUE
    ),
    (
        'RULE_NULL_STAGING_STUDENT',
        'Mandatory Staging Student Reference',
        'Ensures imported staging batches have a valid student reference ID.',
        'NULL_CHECK',
        'staging_enrollments', 'student_id', NULL, NULL,
        '{"disallow_empty_string": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_NULL_STAGING_COURSE',
        'Mandatory Staging Course Reference',
        'Ensures imported staging batches have a valid course reference ID.',
        'NULL_CHECK',
        'staging_enrollments', 'course_id', NULL, NULL,
        '{"disallow_empty_string": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_NULL_STAGING_STATUS',
        'Mandatory Staging Status',
        'Ensures imported staging records contain a non-empty status attribute.',
        'NULL_CHECK',
        'staging_enrollments', 'status', NULL, NULL,
        '{"disallow_empty_string": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_MARKS_RANGE',
        'Evaluation Grade Marks Range (0-100)',
        'Ensures student evaluation marks in staging enrollments are within valid 0.00 to 100.00 range.',
        'DOMAIN_CHECK',
        'staging_enrollments', 'grade_marks', NULL, NULL,
        '{"min_value": 0.0, "max_value": 100.0, "allow_null": true}',
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_ENROLLMENT_STATUS',
        'Valid Enrollment Status Enum',
        'Ensures status matches allowed values: ENROLLED, COMPLETED, DROPPED.',
        'DOMAIN_CHECK',
        'staging_enrollments', 'status', NULL, NULL,
        '{"allowed_values": ["ENROLLED", "COMPLETED", "DROPPED"], "allow_null": false}',
        'MEDIUM', TRUE
    ),
    (
        'RULE_DOMAIN_STAGING_EMAIL',
        'Staging Contact Email Syntax',
        'Ensures student_email in staging conforms to valid RFC user@domain pattern.',
        'DOMAIN_CHECK',
        'staging_enrollments', 'student_email', NULL, NULL,
        '{"regex_pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"}',
        'MEDIUM', TRUE
    )
ON DUPLICATE KEY UPDATE 
    `name` = VALUES(`name`),
    `description` = VALUES(`description`),
    `rule_type` = VALUES(`rule_type`),
    `target_table` = VALUES(`target_table`),
    `target_column` = VALUES(`target_column`),
    `parent_table` = VALUES(`parent_table`),
    `parent_column` = VALUES(`parent_column`),
    `parameters_json` = VALUES(`parameters_json`),
    `severity` = VALUES(`severity`),
    `is_enabled` = VALUES(`is_enabled`);
