-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 02: Table Schema Definition
-- Engine: InnoDB (Full ACID & Foreign Key Enforcement)
-- Database: self_healing_test_db
-- =============================================================================

USE `self_healing_test_db`;

-- -----------------------------------------------------------------------------
-- 1. BUSINESS DOMAIN SCHEMA: Academic Management System
-- -----------------------------------------------------------------------------

-- 1. Departments Table
CREATE TABLE IF NOT EXISTS `departments` (
    `dept_id` INT AUTO_INCREMENT PRIMARY KEY,
    `dept_code` VARCHAR(20) NOT NULL UNIQUE,
    `dept_name` VARCHAR(100) NOT NULL UNIQUE,
    `building` VARCHAR(100) NULL,
    `budget` DECIMAL(12, 2) NOT NULL DEFAULT 100000.00,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `chk_dept_budget` CHECK (`budget` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Instructors Table
CREATE TABLE IF NOT EXISTS `instructors` (
    `instructor_id` INT AUTO_INCREMENT PRIMARY KEY,
    `instructor_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `dept_id` INT NULL,
    `salary` DECIMAL(10, 2) NOT NULL DEFAULT 50000.00,
    `hire_date` DATE NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_instructors_dept` FOREIGN KEY (`dept_id`) 
        REFERENCES `departments`(`dept_id`) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `chk_instructor_salary` CHECK (`salary` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Courses Table
CREATE TABLE IF NOT EXISTS `courses` (
    `course_id` INT AUTO_INCREMENT PRIMARY KEY,
    `course_code` VARCHAR(20) NOT NULL UNIQUE,
    `course_name` VARCHAR(150) NOT NULL,
    `credits` INT NOT NULL DEFAULT 3,
    `dept_id` INT NULL,
    `instructor_id` INT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_courses_dept` FOREIGN KEY (`dept_id`) 
        REFERENCES `departments`(`dept_id`) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_courses_instructor` FOREIGN KEY (`instructor_id`) 
        REFERENCES `instructors`(`instructor_id`) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `chk_course_credits` CHECK (`credits` > 0 AND `credits` <= 12)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Students Table
CREATE TABLE IF NOT EXISTS `students` (
    `student_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL,
    `age` INT NULL,
    `gpa` DECIMAL(3, 2) NULL,
    `dept_id` INT NULL,
    `enrollment_year` INT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_students_dept` FOREIGN KEY (`dept_id`) 
        REFERENCES `departments`(`dept_id`) 
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Enrollments Table
CREATE TABLE IF NOT EXISTS `enrollments` (
    `enrollment_id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `course_id` INT NOT NULL,
    `enrolled_on` DATE NOT NULL,
    `grade_marks` DECIMAL(5, 2) NULL,
    `status` ENUM('ENROLLED', 'COMPLETED', 'DROPPED') NOT NULL DEFAULT 'ENROLLED',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_enrollments_student` FOREIGN KEY (`student_id`) 
        REFERENCES `students`(`student_id`) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_enrollments_course` FOREIGN KEY (`course_id`) 
        REFERENCES `courses`(`course_id`) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `uq_student_course` UNIQUE (`student_id`, `course_id`),
    CONSTRAINT `chk_grade_marks` CHECK (`grade_marks` IS NULL OR (`grade_marks` >= 0.00 AND `grade_marks` <= 100.00))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. STAGING & QUARANTINE SCHEMA
-- -----------------------------------------------------------------------------

-- Staging Enrollments Table (Unconstrained to allow staging ingestion testing & violation detection)
CREATE TABLE IF NOT EXISTS `staging_enrollments` (
    `staging_id` INT AUTO_INCREMENT PRIMARY KEY,
    `external_ref` VARCHAR(50) NULL,
    `student_id` INT NULL,
    `course_id` INT NULL,
    `student_email` VARCHAR(150) NULL,
    `enrolled_on` DATE NULL,
    `grade_marks` DECIMAL(5, 2) NULL,
    `status` VARCHAR(50) NULL,
    `notes` VARCHAR(255) NULL,
    `imported_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Quarantine Records Table (Safe landing zone for corrupted/orphan records during healing)
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

-- -----------------------------------------------------------------------------
-- 3. SYSTEM ENGINE SCHEMA: Integrity Rules, Scans, Repairs & Audits
-- -----------------------------------------------------------------------------

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
    `category` ENUM('ORPHAN', 'DUPLICATE', 'NULL_VIOLATION', 'DOMAIN_VIOLATION', 'RELATIONAL_VIOLATION') NOT NULL,
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

-- Set Database Metadata initialization
INSERT INTO `database_metadata` (`meta_key`, `meta_value`) 
VALUES 
    ('system_name', 'Self-Healing Relational Database Integrity System'),
    ('version', '2.4.0'),
    ('database_name', 'self_healing_test_db'),
    ('schema_revision', '2026.10'),
    ('initialized_at', NOW())
ON DUPLICATE KEY UPDATE `meta_value` = VALUES(`meta_value`);

-- -----------------------------------------------------------------------------
-- 4. DATABASE-LEVEL AUDIT LOG IMMUTABILITY TRIGGERS
-- Protects audit trail and transaction logs from unauthorized alteration/deletion
-- -----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS `trg_audit_logs_no_update`;
DROP TRIGGER IF EXISTS `trg_audit_logs_no_delete`;
DROP TRIGGER IF EXISTS `trg_transaction_logs_no_update`;
DROP TRIGGER IF EXISTS `trg_transaction_logs_no_delete`;

DELIMITER $$

CREATE TRIGGER `trg_audit_logs_no_update`
BEFORE UPDATE ON `audit_logs`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Security Policy Violation: Audit log records are immutable and cannot be modified.';
END$$

CREATE TRIGGER `trg_audit_logs_no_delete`
BEFORE DELETE ON `audit_logs`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Security Policy Violation: Audit log records are immutable and cannot be deleted.';
END$$

CREATE TRIGGER `trg_transaction_logs_no_update`
BEFORE UPDATE ON `transaction_logs`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Security Policy Violation: Transaction log records are immutable and cannot be modified.';
END$$

CREATE TRIGGER `trg_transaction_logs_no_delete`
BEFORE DELETE ON `transaction_logs`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Security Policy Violation: Transaction log records are immutable and cannot be deleted.';
END$$

DELIMITER ;
