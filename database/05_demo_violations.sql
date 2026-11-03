-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 05: Demonstration Violations Injection
-- Introduces controlled, isolated integrity anomalies across all six tables:
-- 1. departments
-- 2. instructors
-- 3. courses
-- 4. students
-- 5. enrollments
-- 6. staging_enrollments
-- Database: self_healing_test_db
-- =============================================================================

USE `self_healing_test_db`;

SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------------------
-- 1. DEPARTMENTS ANOMALIES (Duplicate code, duplicate name, empty fields, negative budget)
-- -----------------------------------------------------------------------------
DELETE FROM `departments` WHERE `dept_id` >= 900;

INSERT INTO `departments` (`dept_id`, `dept_code`, `dept_name`, `building`, `budget`)
VALUES 
    -- Anomaly 1: Duplicate Department Code (Collides with Dept 1 'CS')
    (901, 'CS', 'Computer Science Clashing Unit', 'Turing North Annex', 250000.00),

    -- Anomaly 2: Duplicate Department Name (Collides with Dept 4 'Department of Mechanical Engineering')
    (902, 'MECH_DUP', 'Department of Mechanical Engineering', 'Carnot West Wing', 300000.00),

    -- Anomaly 3: Mandatory Department Code Missing / Empty
    (903, '', 'Anonymous Interdisciplinary Center', 'Babbage Pavilion', 150000.00),

    -- Anomaly 4: Mandatory Department Name Missing / Empty
    (904, 'NONAME', '', 'Lovelace Science Tower', 120000.00),

    -- Anomaly 5: Domain Operating Budget Negative
    (905, 'DEFICIT', 'Deficit Research Laboratory', 'Kelvin Underground Vault', -50000.00);


-- -----------------------------------------------------------------------------
-- 2. INSTRUCTORS ANOMALIES (Orphan dept, duplicate email, empty fields, negative salary, malformed email)
-- -----------------------------------------------------------------------------
DELETE FROM `instructors` WHERE `instructor_id` >= 900;

INSERT INTO `instructors` (`instructor_id`, `instructor_name`, `email`, `dept_id`, `salary`, `hire_date`)
VALUES 
    -- Anomaly 6: Orphan Department Reference (Department ID 9999 does not exist)
    (901, 'Dr. Ghost Professor', 'ghost.prof@univ.edu', 9999, 85000.00, '2024-01-15'),

    -- Anomaly 7: Duplicate Instructor Email (Collides with Instructor 1 alan.turing@univ.edu)
    (902, 'Dr. Alan Clone', 'alan.turing@univ.edu', 1, 90000.00, '2023-08-01'),

    -- Anomaly 8: Mandatory Instructor Name Missing / Empty
    (903, '', 'empty.instructor.name@univ.edu', 1, 75000.00, '2022-09-01'),

    -- Anomaly 9: Mandatory Instructor Email Missing / Empty
    (904, 'Dr. Nameless Email', '', 2, 70000.00, '2021-04-10'),

    -- Anomaly 10: Domain Salary Negative
    (905, 'Dr. Insolvent Scholar', 'negative.salary@univ.edu', 1, -15000.00, '2025-01-10'),

    -- Anomaly 11: Domain Email Syntax Pattern Malformed
    (906, 'Dr. Broken Syntax', 'broken-email-no-at-sign', 2, 65000.00, '2024-06-15');


-- -----------------------------------------------------------------------------
-- 3. COURSES ANOMALIES (Orphan dept, orphan instructor, duplicate code, empty name, credits range)
-- -----------------------------------------------------------------------------
DELETE FROM `courses` WHERE `course_id` >= 900;

INSERT INTO `courses` (`course_id`, `course_code`, `course_name`, `credits`, `dept_id`, `instructor_id`)
VALUES 
    -- Anomaly 12: Orphan Department Reference (Department ID 9999 does not exist)
    (901, 'GHOST101', 'Ghost Department Course', 3, 9999, 1),

    -- Anomaly 13: Orphan Instructor Reference (Instructor ID 9999 does not exist)
    (902, 'GHOST201', 'Ghost Instructor Seminar', 4, 1, 9999),

    -- Anomaly 14: Duplicate Course Code (Collides with Course 1 'CS101')
    (903, 'CS101', 'Advanced Relational Database Topics', 3, 1, 1),

    -- Anomaly 15: Mandatory Course Code Missing / Empty
    (904, '', 'Empty Course Code Workshop', 3, 1, 1),

    -- Anomaly 16: Mandatory Course Name Missing / Empty
    (905, 'NONAME101', '', 3, 1, 1),

    -- Anomaly 17: Domain Credits Range Out of Bounds (Credits 24, exceeds maximum 12)
    (906, 'EXTREME101', 'Super Intensive Dissertation Study', 24, 1, 1);


-- -----------------------------------------------------------------------------
-- 4. STUDENTS ANOMALIES (Orphan dept, duplicate email, age range, GPA range, email syntax, empty name)
-- -----------------------------------------------------------------------------
DELETE FROM `students` WHERE `student_id` >= 200;

INSERT INTO `students` (`student_id`, `student_name`, `email`, `age`, `gpa`, `dept_id`, `enrollment_year`)
VALUES 
    -- Anomaly 18: Orphan Department Reference (Department ID 9999 does not exist)
    (200, 'Lost Student', 'lost.student@univ.edu', 20, 3.50, 9999, 2024),

    -- Anomaly 19: Domain Age Out of Range (Age 140, exceeds 65 maximum)
    (201, 'Walter Elder', 'walter.elder@univ.edu', 140, 3.20, 1, 2024),

    -- Anomaly 20: Domain GPA Out of Range (GPA 4.95, exceeds 4.00 maximum)
    (202, 'Luna Genius', 'luna.genius@univ.edu', 20, 4.95, 1, 2025),

    -- Anomaly 21: Malformed Email Domain Pattern (No valid top-level domain)
    (203, 'Alex Malformed', 'alex.malformed@no-tld', 22, 3.10, 2, 2023),

    -- Anomaly 22: Mandatory Student Name Missing / Empty
    (204, '', 'ghost.name@univ.edu', 21, 2.90, 3, 2024),

    -- Anomaly 23: Duplicate Candidate Key Email (Collides with Student 101 ravi.kumar@univ.edu)
    (205, 'Ravi Duplicate', 'ravi.kumar@univ.edu', 22, 3.50, 1, 2024),

    -- Anomaly 24: Mandatory Student Email Missing / Empty
    (206, 'Nameless Email Scholar', '', 21, 3.15, 1, 2024);


-- -----------------------------------------------------------------------------
-- 5. ENROLLMENTS ANOMALIES (Orphan student, orphan course, duplicate pair, empty status, grade range, invalid enum)
-- -----------------------------------------------------------------------------
DELETE FROM `enrollments` WHERE `enrollment_id` >= 9000;

INSERT INTO `enrollments` (`enrollment_id`, `student_id`, `course_id`, `enrolled_on`, `grade_marks`, `status`)
VALUES 
    -- Anomaly 25: Orphan Student Reference (Student ID 9999 does not exist)
    (9001, 9999, 1, '2026-09-01', 85.00, 'ENROLLED'),

    -- Anomaly 26: Orphan Course Reference (Course ID 9999 does not exist)
    (9002, 101, 9999, '2026-09-01', 80.00, 'ENROLLED'),

    -- Anomaly 27: Duplicate Student-Course Pair (Collides with Enrollment 1001: student 101, course 1)
    (9003, 101, 1, '2026-09-01', 92.00, 'ENROLLED'),

    -- Anomaly 28: Mandatory Status Missing / Empty
    (9004, 102, 2, '2026-09-01', 75.00, ''),

    -- Anomaly 29: Domain Grade Marks Out of Bounds (Grade 180.00, exceeds 100.00 maximum)
    (9005, 103, 1, '2026-09-01', 180.00, 'ENROLLED'),

    -- Anomaly 30: Domain Status Invalid Enum Value ('EXPELLED' not in ENROLLED, COMPLETED, DROPPED)
    (9006, 104, 2, '2026-09-01', 88.00, 'EXPELLED');


-- -----------------------------------------------------------------------------
-- 6. STAGING ENROLLMENTS ANOMALIES (Unconstrained staging ingestion violations)
-- -----------------------------------------------------------------------------
TRUNCATE TABLE `staging_enrollments`;

INSERT INTO `staging_enrollments` 
    (`staging_id`, `external_ref`, `student_id`, `course_id`, `student_email`, `enrolled_on`, `grade_marks`, `status`, `notes`)
VALUES 
    -- Normal valid staging records
    (1, 'EXT-1001', 101, 3, 'ravi.kumar@univ.edu', '2026-09-01', 89.00, 'ENROLLED', 'Valid transfer record'),
    (2, 'EXT-1002', 102, 2, 'priya.sharma@univ.edu', '2026-09-01', 94.50, 'ENROLLED', 'Valid elective registration'),

    -- Anomaly 31: Orphan Student Reference (Student ID 999 does not exist in students)
    (3, 'EXT-1003', 999, 1, 'ghost.student@univ.edu', '2026-09-01', 75.00, 'ENROLLED', 'Orphan: Missing parent student record'),

    -- Anomaly 32: Orphan Course Reference (Course ID 888 does not exist in courses)
    (4, 'EXT-1004', 103, 888, 'arun.patel@univ.edu', '2026-09-01', 82.00, 'ENROLLED', 'Orphan: Missing parent course record'),

    -- Anomaly 33 & 34: Duplicate Enrollment Pair (Both records register student 104 for course 1)
    (5, 'EXT-1005', 104, 1, 'sneha.reddy@univ.edu', '2026-09-01', 88.00, 'ENROLLED', 'Original registration entry'),
    (6, 'EXT-1006', 104, 1, 'sneha.reddy@univ.edu', '2026-09-01', 88.00, 'ENROLLED', 'Duplicate submission anomaly'),

    -- Anomaly 35: Domain Range Violation (Marks = 145.00, exceeds max limit 100.00)
    (7, 'EXT-1007', 105, 1, 'vikram.malhotra@univ.edu', '2026-09-01', 145.00, 'ENROLLED', 'Domain violation: Grade marks out of 0-100 range'),

    -- Anomaly 36: Domain Enum Violation (Status = 'SUSPENDED', not in allowed set)
    (8, 'EXT-1008', 106, 3, 'ananya.roy@univ.edu', '2026-09-01', 85.00, 'SUSPENDED', 'Domain violation: Invalid status code'),

    -- Anomaly 37: Duplicate External Reference Identifier (EXT-1001 collides with record 1)
    (9, 'EXT-1001', 107, 4, 'devendra.joshi@univ.edu', '2026-09-01', 90.00, 'ENROLLED', 'Duplicate batch external reference'),

    -- Anomaly 38: Mandatory Fields Missing (Both student_id and course_id are NULL)
    (10, 'EXT-1010', NULL, NULL, 'unassigned@univ.edu', '2026-09-01', 50.00, 'ENROLLED', 'Mandatory foreign keys missing');

SET FOREIGN_KEY_CHECKS = 1;
