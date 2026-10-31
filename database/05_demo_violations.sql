-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 05: Demonstration Violations Injection
-- Introduces controlled, isolated integrity anomalies for scanning & self-healing
-- WITHOUT corrupting or disabling InnoDB foreign keys globally.
-- =============================================================================

USE `self_healing_db`;

-- 1. STAGING TABLE ANOMALIES (Orphan records, duplicates, domain range, invalid enums)
TRUNCATE TABLE `staging_enrollments`;

INSERT INTO `staging_enrollments` 
    (`staging_id`, `external_ref`, `student_id`, `course_id`, `student_email`, `enrolled_on`, `grade_marks`, `status`, `notes`)
VALUES 
    -- Normal valid staging records
    (1, 'EXT-1001', 101, 3, 'ravi.kumar@univ.edu', '2026-09-01', 89.00, 'ENROLLED', 'Valid transfer record'),
    (2, 'EXT-1002', 102, 2, 'priya.sharma@univ.edu', '2026-09-01', 94.50, 'ENROLLED', 'Valid elective registration'),

    -- Violation 1: Orphan Student Reference (Student ID 999 does not exist in students)
    (3, 'EXT-1003', 999, 1, 'ghost.student@univ.edu', '2026-09-01', 75.00, 'ENROLLED', 'Orphan: Missing parent student record'),

    -- Violation 2: Orphan Course Reference (Course ID 888 does not exist in courses)
    (4, 'EXT-1004', 103, 888, 'arun.patel@univ.edu', '2026-09-01', 82.00, 'ENROLLED', 'Orphan: Missing parent course record'),

    -- Violation 3 & 4: Duplicate Enrollment Pair (Both records register student 104 for course 1)
    (5, 'EXT-1005', 104, 1, 'sneha.reddy@univ.edu', '2026-09-01', 88.00, 'ENROLLED', 'Original registration entry'),
    (6, 'EXT-1006', 104, 1, 'sneha.reddy@univ.edu', '2026-09-01', 88.00, 'ENROLLED', 'Duplicate submission anomaly'),

    -- Violation 5: Domain Range Violation (Marks = 145.00, exceeds max limit 100.00)
    (7, 'EXT-1007', 105, 1, 'vikram.malhotra@univ.edu', '2026-09-01', 145.00, 'ENROLLED', 'Domain violation: Grade marks out of 0-100 range'),

    -- Violation 6: Domain Enum Violation (Status = 'SUSPENDED', not in allowed set)
    (8, 'EXT-1008', 106, 3, 'ananya.roy@univ.edu', '2026-09-01', 85.00, 'SUSPENDED', 'Domain violation: Invalid status code');

-- 2. STUDENT PROFILE ANOMALIES (Duplicate email, domain age, invalid GPA, malformed email)
-- Remove any previous demo violation records (IDs 200+)
DELETE FROM `students` WHERE `student_id` >= 200;

INSERT INTO `students` (`student_id`, `student_name`, `email`, `age`, `gpa`, `dept_id`, `enrollment_year`)
VALUES 
    -- Violation 7: Domain Age Out of Range (Age 140, exceeds 65 maximum)
    (201, 'Walter Elder', 'walter.elder@univ.edu', 140, 3.20, 1, 2024),

    -- Violation 8: Domain GPA Out of Range (GPA 4.95, exceeds 4.00 maximum)
    (202, 'Luna Genius', 'luna.genius@univ.edu', 20, 4.95, 1, 2025),

    -- Violation 9: Malformed Email Domain Pattern (No domain extension)
    (203, 'Alex Malformed', 'alex.malformed@no-tld', 22, 3.10, 2, 2023),

    -- Violation 10: Mandatory Name Missing / Empty
    (204, '', 'ghost.name@univ.edu', 21, 2.90, 3, 2024);
