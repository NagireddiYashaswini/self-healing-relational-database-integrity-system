-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 03: Baseline Clean Sample Data Insertion
-- All data inserted here satisfies 100% referential integrity and constraints.
-- =============================================================================

USE `self_healing_db`;

-- 1. Departments
INSERT INTO `departments` (`dept_id`, `dept_code`, `dept_name`, `building`, `budget`)
VALUES 
    (1, 'CS', 'Computer Science and Engineering', 'Turing Science Center', 850000.00),
    (2, 'EE', 'Electrical & Electronics Engineering', 'Faraday Engineering Complex', 650000.00),
    (3, 'MATH', 'Department of Applied Mathematics', 'Euler Mathematical Sciences', 450000.00),
    (4, 'MECH', 'Department of Mechanical Engineering', 'Carnot Technology Hall', 550000.00)
ON DUPLICATE KEY UPDATE 
    `dept_code` = VALUES(`dept_code`),
    `dept_name` = VALUES(`dept_name`),
    `building` = VALUES(`building`),
    `budget` = VALUES(`budget`);

-- 2. Instructors
INSERT INTO `instructors` (`instructor_id`, `instructor_name`, `email`, `dept_id`, `salary`, `hire_date`)
VALUES 
    (1, 'Dr. Alan Turing', 'alan.turing@univ.edu', 1, 95000.00, '2018-08-15'),
    (2, 'Dr. Ada Lovelace', 'ada.lovelace@univ.edu', 1, 98000.00, '2017-01-10'),
    (3, 'Dr. Claude Shannon', 'claude.shannon@univ.edu', 2, 92000.00, '2019-06-01'),
    (4, 'Dr. John von Neumann', 'john.neumann@univ.edu', 3, 96000.00, '2016-03-20')
ON DUPLICATE KEY UPDATE 
    `instructor_name` = VALUES(`instructor_name`),
    `email` = VALUES(`email`),
    `dept_id` = VALUES(`dept_id`),
    `salary` = VALUES(`salary`),
    `hire_date` = VALUES(`hire_date`);

-- 3. Courses
INSERT INTO `courses` (`course_id`, `course_code`, `course_name`, `credits`, `dept_id`, `instructor_id`)
VALUES 
    (1, 'CS101', 'Relational Database Management Systems', 4, 1, 1),
    (2, 'CS201', 'Computer Networks and Protocols', 3, 1, 2),
    (3, 'CS301', 'Modern Operating Systems Design', 4, 1, 2),
    (4, 'EE101', 'Digital Systems and Logic Circuitry', 3, 2, 3),
    (5, 'MATH201', 'Discrete Mathematics & Graph Theory', 3, 3, 4)
ON DUPLICATE KEY UPDATE 
    `course_code` = VALUES(`course_code`),
    `course_name` = VALUES(`course_name`),
    `credits` = VALUES(`credits`),
    `dept_id` = VALUES(`dept_id`),
    `instructor_id` = VALUES(`instructor_id`);

-- 4. Students
INSERT INTO `students` (`student_id`, `student_name`, `email`, `age`, `gpa`, `dept_id`, `enrollment_year`)
VALUES 
    (101, 'Ravi Kumar', 'ravi.kumar@univ.edu', 21, 3.85, 1, 2023),
    (102, 'Priya Sharma', 'priya.sharma@univ.edu', 20, 3.92, 1, 2024),
    (103, 'Arun Patel', 'arun.patel@univ.edu', 22, 3.65, 2, 2022),
    (104, 'Sneha Reddy', 'sneha.reddy@univ.edu', 21, 3.78, 1, 2023),
    (105, 'Vikram Malhotra', 'vikram.malhotra@univ.edu', 23, 3.40, 3, 2022),
    (106, 'Ananya Roy', 'ananya.roy@univ.edu', 19, 3.90, 1, 2025),
    (107, 'Devendra Joshi', 'devendra.joshi@univ.edu', 22, 3.52, 4, 2023)
ON DUPLICATE KEY UPDATE 
    `student_name` = VALUES(`student_name`),
    `email` = VALUES(`email`),
    `age` = VALUES(`age`),
    `gpa` = VALUES(`gpa`),
    `dept_id` = VALUES(`dept_id`),
    `enrollment_year` = VALUES(`enrollment_year`);

-- 5. Enrollments (Clean core relational table)
INSERT INTO `enrollments` (`enrollment_id`, `student_id`, `course_id`, `enrolled_on`, `grade_marks`, `status`)
VALUES 
    (1001, 101, 1, '2026-01-15', 88.50, 'COMPLETED'),
    (1002, 101, 2, '2026-08-20', 92.00, 'ENROLLED'),
    (1003, 102, 1, '2026-01-15', 94.00, 'COMPLETED'),
    (1004, 102, 3, '2026-08-20', 89.50, 'ENROLLED'),
    (1005, 103, 4, '2026-01-15', 85.00, 'COMPLETED'),
    (1006, 104, 1, '2026-01-15', 78.00, 'COMPLETED'),
    (1007, 104, 5, '2026-08-20', 82.50, 'ENROLLED'),
    (1008, 105, 5, '2026-01-15', 91.00, 'COMPLETED'),
    (1009, 106, 1, '2026-08-20', 87.00, 'ENROLLED'),
    (1010, 106, 2, '2026-08-20', 90.00, 'ENROLLED')
ON DUPLICATE KEY UPDATE 
    `student_id` = VALUES(`student_id`),
    `course_id` = VALUES(`course_id`),
    `enrolled_on` = VALUES(`enrolled_on`),
    `grade_marks` = VALUES(`grade_marks`),
    `status` = VALUES(`status`);
