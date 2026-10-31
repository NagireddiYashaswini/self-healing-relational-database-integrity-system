-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 07: Reset Database to Clean Baseline State
-- Resets staging tables, clears active demo anomalies, retains structural data.
-- =============================================================================

USE `self_healing_db`;

-- 1. Remove temporary demo anomaly students (ID >= 200)
DELETE FROM `students` WHERE `student_id` >= 200;

-- 2. Clear staging enrollments
TRUNCATE TABLE `staging_enrollments`;

-- 3. Repopulate clean staging enrollments
INSERT INTO `staging_enrollments` 
    (`staging_id`, `external_ref`, `student_id`, `course_id`, `student_email`, `enrolled_on`, `grade_marks`, `status`, `notes`)
VALUES 
    (1, 'EXT-1001', 101, 3, 'ravi.kumar@univ.edu', '2026-09-01', 89.00, 'ENROLLED', 'Valid transfer record'),
    (2, 'EXT-1002', 102, 2, 'priya.sharma@univ.edu', '2026-09-01', 94.50, 'ENROLLED', 'Valid elective registration'),
    (3, 'EXT-1003', 103, 1, 'arun.patel@univ.edu', '2026-09-01', 85.00, 'ENROLLED', 'Valid regular registration');

-- 4. Reset or Archive Quarantined Records
TRUNCATE TABLE `quarantine_records`;

-- 5. Record Reset Event in Audit Log
INSERT INTO `audit_logs` (
    `event_type`, `actor`, `action_description`, `target_table`, `result`
) VALUES (
    'DATABASE_RESET',
    'ADMIN_USER',
    'Reset staging and active tables to clean baseline state for demonstration.',
    'ALL_TABLES',
    'SUCCESS'
);
