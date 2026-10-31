-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 04: Integrity Rules Definition
-- Seed standard database integrity rules across all 5 categories:
-- ORPHAN, DUPLICATE, NULL_CHECK, DOMAIN_CHECK, RELATIONAL_CONSISTENCY
-- =============================================================================

USE `self_healing_db`;

INSERT INTO `integrity_rules` (
    `rule_code`, `name`, `description`, `rule_type`, 
    `target_table`, `target_column`, `parent_table`, `parent_column`, 
    `parameters_json`, `severity`, `is_enabled`
) VALUES 
    -- 1. Orphan Checks
    (
        'RULE_ORPHAN_STAGING_STUDENT',
        'Staging Enrollment Orphan Student Reference',
        'Detects enrollment records in staging table referencing non-existent student IDs in the students parent table.',
        'ORPHAN',
        'staging_enrollments', 'student_id', 'students', 'student_id',
        JSON_OBJECT('allow_null', false, 'strategy', 'RESTORE_PARENT'),
        'CRITICAL', TRUE
    ),
    (
        'RULE_ORPHAN_STAGING_COURSE',
        'Staging Enrollment Orphan Course Reference',
        'Detects enrollment records in staging table referencing non-existent course IDs in the courses parent table.',
        'ORPHAN',
        'staging_enrollments', 'course_id', 'courses', 'course_id',
        JSON_OBJECT('allow_null', false, 'strategy', 'RESTORE_PARENT'),
        'CRITICAL', TRUE
    ),
    (
        'RULE_ORPHAN_STUDENT_DEPT',
        'Student Missing Department Reference',
        'Verifies that foreign key dept_id in students table correctly resolves to a registered department.',
        'ORPHAN',
        'students', 'dept_id', 'departments', 'dept_id',
        JSON_OBJECT('allow_null', true, 'strategy', 'MAP_PARENT'),
        'HIGH', TRUE
    ),
    (
        'RULE_ORPHAN_COURSE_INSTRUCTOR',
        'Course Missing Assigned Instructor',
        'Verifies that foreign key instructor_id in courses points to a valid active instructor.',
        'ORPHAN',
        'courses', 'instructor_id', 'instructors', 'instructor_id',
        JSON_OBJECT('allow_null', true, 'strategy', 'MAP_PARENT'),
        'HIGH', TRUE
    ),

    -- 2. Duplicate Checks
    (
        'RULE_DUP_STUDENT_EMAIL',
        'Duplicate Student Email Address',
        'Enforces logical uniqueness for student contact emails to prevent profile fragmentation and collision.',
        'DUPLICATE',
        'students', 'email', NULL, NULL,
        JSON_OBJECT('group_by', JSON_ARRAY('email'), 'case_sensitive', false),
        'CRITICAL', TRUE
    ),
    (
        'RULE_DUP_STAGING_ENROLLMENT',
        'Duplicate Staging Enrollment Pair',
        'Flags duplicate (student_id, course_id) registration attempts prior to canonical table ingestion.',
        'DUPLICATE',
        'staging_enrollments', 'student_id,course_id', NULL, NULL,
        JSON_OBJECT('group_by', JSON_ARRAY('student_id', 'course_id')),
        'HIGH', TRUE
    ),
    (
        'RULE_DUP_DEPT_NAME',
        'Duplicate Department Name',
        'Detects redundant department records having identical human-readable department names.',
        'DUPLICATE',
        'departments', 'dept_name', NULL, NULL,
        JSON_OBJECT('group_by', JSON_ARRAY('dept_name')),
        'MEDIUM', TRUE
    ),

    -- 3. NULL / Required Value Checks
    (
        'RULE_NULL_STUDENT_NAME',
        'Mandatory Student Name',
        'Ensures that student records do not contain empty or NULL student names.',
        'NULL_CHECK',
        'students', 'student_name', NULL, NULL,
        JSON_OBJECT('disallow_empty_string', true),
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_STUDENT_EMAIL',
        'Mandatory Student Email',
        'Ensures that student identity records have a non-empty contact email.',
        'NULL_CHECK',
        'students', 'email', NULL, NULL,
        JSON_OBJECT('disallow_empty_string', true),
        'CRITICAL', TRUE
    ),
    (
        'RULE_NULL_COURSE_NAME',
        'Mandatory Course Name',
        'Validates that all courses possess a descriptive title and not NULL.',
        'NULL_CHECK',
        'courses', 'course_name', NULL, NULL,
        JSON_OBJECT('disallow_empty_string', true),
        'HIGH', TRUE
    ),

    -- 4. Domain & Range Checks
    (
        'RULE_DOMAIN_STUDENT_AGE',
        'Student Age Range (16-65)',
        'Validates that student ages fall within the standard collegiate admission range between 16 and 65.',
        'DOMAIN_CHECK',
        'students', 'age', NULL, NULL,
        JSON_OBJECT('min_value', 16, 'max_value', 65, 'allow_null', true),
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_STUDENT_GPA',
        'Student GPA Scale (0.00 - 4.00)',
        'Validates that academic GPA records strictly conform to the 4.00 maximum point scale.',
        'DOMAIN_CHECK',
        'students', 'gpa', NULL, NULL,
        JSON_OBJECT('min_value', 0.00, 'max_value', 4.00, 'allow_null', true),
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_MARKS_RANGE',
        'Evaluation Grade Marks (0 - 100)',
        'Ensures student evaluation marks in staging enrollments are within the valid 0.00 to 100.00 grade range.',
        'DOMAIN_CHECK',
        'staging_enrollments', 'grade_marks', NULL, NULL,
        JSON_OBJECT('min_value', 0.00, 'max_value', 100.00, 'allow_null', true),
        'HIGH', TRUE
    ),
    (
        'RULE_DOMAIN_ENROLLMENT_STATUS',
        'Valid Enrollment Status Enum',
        'Ensures status matches allowed values: ENROLLED, COMPLETED, DROPPED.',
        'DOMAIN_CHECK',
        'staging_enrollments', 'status', NULL, NULL,
        JSON_OBJECT('allowed_values', JSON_ARRAY('ENROLLED', 'COMPLETED', 'DROPPED'), 'allow_null', false),
        'MEDIUM', TRUE
    ),
    (
        'RULE_DOMAIN_EMAIL_FORMAT',
        'Valid Email Syntax Pattern',
        'Ensures email values conform to a standard user@domain format.',
        'DOMAIN_CHECK',
        'students', 'email', NULL, NULL,
        JSON_OBJECT('regex_pattern', '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
        'MEDIUM', TRUE
    )
ON DUPLICATE KEY UPDATE 
    `name` = VALUES(`name`),
    `description` = VALUES(`description`),
    `rule_type` = VALUES(`rule_type`),
    `parameters_json` = VALUES(`parameters_json`),
    `severity` = VALUES(`severity`),
    `is_enabled` = VALUES(`is_enabled`);
