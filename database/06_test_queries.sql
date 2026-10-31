-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 06: Test & Inspection Queries
-- Verifies manual SQL equivalents of the automated Integrity Scanner engine.
-- =============================================================================

USE `self_healing_db`;

-- 1. Detect Orphan Records in staging_enrollments referencing missing students
SELECT 
    se.staging_id,
    se.student_id AS invalid_student_fk,
    se.course_id,
    se.student_email,
    'MISSING_STUDENT_PARENT' AS violation_type
FROM `staging_enrollments` se
LEFT JOIN `students` s ON se.student_id = s.student_id
WHERE se.student_id IS NOT NULL AND s.student_id IS NULL;

-- 2. Detect Orphan Records in staging_enrollments referencing missing courses
SELECT 
    se.staging_id,
    se.student_id,
    se.course_id AS invalid_course_fk,
    'MISSING_COURSE_PARENT' AS violation_type
FROM `staging_enrollments` se
LEFT JOIN `courses` c ON se.course_id = c.course_id
WHERE se.course_id IS NOT NULL AND c.course_id IS NULL;

-- 3. Detect Duplicate Enrollment Pairs (student_id, course_id)
SELECT 
    student_id, 
    course_id, 
    COUNT(*) AS occurrence_count,
    GROUP_CONCAT(staging_id) AS conflicting_ids
FROM `staging_enrollments`
GROUP BY student_id, course_id
HAVING COUNT(*) > 1;

-- 4. Detect Domain Range Violations (Marks > 100 or < 0)
SELECT 
    staging_id, 
    student_id, 
    course_id, 
    grade_marks,
    'MARKS_OUT_OF_RANGE' AS violation_type
FROM `staging_enrollments`
WHERE grade_marks < 0.00 OR grade_marks > 100.00;

-- 5. Detect Invalid Status Enums
SELECT 
    staging_id, 
    status,
    'INVALID_ENUM_VALUE' AS violation_type
FROM `staging_enrollments`
WHERE status NOT IN ('ENROLLED', 'COMPLETED', 'DROPPED');

-- 6. Detect Student Age Domain Violations (Age < 16 or Age > 65)
SELECT 
    student_id, 
    student_name, 
    age,
    'AGE_OUT_OF_RANGE' AS violation_type
FROM `students`
WHERE age < 16 OR age > 65;

-- 7. Detect Missing / Empty Student Names
SELECT 
    student_id, 
    email, 
    student_name,
    'MISSING_NAME' AS violation_type
FROM `students`
WHERE student_name IS NULL OR TRIM(student_name) = '';

-- 8. Verify System Status Overview
SELECT 'Departments' AS entity, COUNT(*) AS count FROM `departments`
UNION ALL
SELECT 'Instructors', COUNT(*) FROM `instructors`
UNION ALL
SELECT 'Courses', COUNT(*) FROM `courses`
UNION ALL
SELECT 'Students', COUNT(*) FROM `students`
UNION ALL
SELECT 'Clean Enrollments', COUNT(*) FROM `enrollments`
UNION ALL
SELECT 'Staging Records', COUNT(*) FROM `staging_enrollments`
UNION ALL
SELECT 'Integrity Rules', COUNT(*) FROM `integrity_rules`
UNION ALL
SELECT 'Quarantined Records', COUNT(*) FROM `quarantine_records`
UNION ALL
SELECT 'Audit Log Events', COUNT(*) FROM `audit_logs`;
