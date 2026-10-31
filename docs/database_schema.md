# Database Schema & Relational Model Specification

## 1. Relational Entity Summary
The database `self_healing_db` utilizes the **MySQL InnoDB** storage engine for full ACID transaction compliance and declarative foreign key constraints.

---

## 2. Business Tables

### `departments`
- `dept_id` INT AUTO_INCREMENT PRIMARY KEY
- `dept_code` VARCHAR(20) NOT NULL UNIQUE
- `dept_name` VARCHAR(100) NOT NULL
- `building` VARCHAR(100)
- `budget` DECIMAL(12, 2) NOT NULL DEFAULT 100000.00
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### `instructors`
- `instructor_id` INT AUTO_INCREMENT PRIMARY KEY
- `instructor_name` VARCHAR(100) NOT NULL
- `email` VARCHAR(150) NOT NULL UNIQUE
- `dept_id` INT NULL (FK -> `departments.dept_id` ON DELETE RESTRICT ON UPDATE CASCADE)
- `salary` DECIMAL(10, 2) NOT NULL DEFAULT 50000.00
- `hire_date` DATE NULL

### `courses`
- `course_id` INT AUTO_INCREMENT PRIMARY KEY
- `course_code` VARCHAR(20) NOT NULL
- `course_name` VARCHAR(150) NOT NULL
- `credits` INT NOT NULL DEFAULT 3
- `dept_id` INT NULL (FK -> `departments.dept_id` ON DELETE SET NULL ON UPDATE CASCADE)
- `instructor_id` INT NULL (FK -> `instructors.instructor_id` ON DELETE SET NULL ON UPDATE CASCADE)

### `students`
- `student_id` INT AUTO_INCREMENT PRIMARY KEY
- `student_name` VARCHAR(100) NOT NULL
- `email` VARCHAR(150) NOT NULL
- `age` INT NULL
- `gpa` DECIMAL(3, 2) NULL
- `dept_id` INT NULL (FK -> `departments.dept_id` ON DELETE SET NULL ON UPDATE CASCADE)
- `enrollment_year` INT NULL

### `enrollments`
- `enrollment_id` INT AUTO_INCREMENT PRIMARY KEY
- `student_id` INT NOT NULL (FK -> `students.student_id` ON DELETE RESTRICT ON UPDATE CASCADE)
- `course_id` INT NOT NULL (FK -> `courses.course_id` ON DELETE RESTRICT ON UPDATE CASCADE)
- `enrolled_on` DATE NOT NULL
- `grade_marks` DECIMAL(5, 2) NULL
- `status` ENUM('ENROLLED', 'COMPLETED', 'DROPPED') NOT NULL DEFAULT 'ENROLLED'
- UNIQUE KEY `uq_student_course` (`student_id`, `course_id`)

### `staging_enrollments`
*Unconstrained staging table for ingestion demonstration without globally disabling foreign keys:*
- `staging_id` INT AUTO_INCREMENT PRIMARY KEY
- `external_ref` VARCHAR(50)
- `student_id` INT NULL (Targeted by logical rule)
- `course_id` INT NULL (Targeted by logical rule)
- `student_email` VARCHAR(150) NULL
- `enrolled_on` DATE NULL
- `grade_marks` DECIMAL(5, 2) NULL
- `status` VARCHAR(50) NULL
- `notes` VARCHAR(255) NULL
- `imported_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### `quarantine_records`
*Isolated staging area for corrupted records moved during self-healing:*
- `quarantine_id` INT AUTO_INCREMENT PRIMARY KEY
- `source_table` VARCHAR(100) NOT NULL
- `source_pk_value` VARCHAR(100) NOT NULL
- `issue_type` VARCHAR(50) NOT NULL
- `row_data_json` LONGTEXT NOT NULL
- `quarantine_reason` TEXT NOT NULL
- `quarantined_by` VARCHAR(100) DEFAULT 'SYSTEM'
- `quarantined_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `resolved` BOOLEAN DEFAULT FALSE
- `resolution_notes` TEXT NULL

---

## 3. System Engine Tables

| Table | Purpose |
|---|---|
| `integrity_rules` | Catalog of configured validation rules (type, target column, parameters, severity). |
| `scan_runs` | Historical log of every executed integrity scan with counters and timing. |
| `integrity_issues` | Individual detected violations with status lifecycle (`OPEN` -> `REVIEWED` -> `APPROVED` -> `REPAIRED` / `IGNORED`). |
| `repair_recommendations` | Healing recommendations linked to issues with risk level and approval flag. |
| `repair_executions` | Atomic execution record with transaction ID, timing, and before/after states. |
| `audit_logs` | Immutable audit trail with sensitive key redaction. |
| `transaction_logs` | Low-level transaction lifecycle recording commits, rollbacks, and savepoints. |
| `recovery_checkpoints` | Application-level table snapshots capturing schema DDL and row states. |
| `database_metadata` | Key-value store tracking system initialized state, version, and schema revisions. |
