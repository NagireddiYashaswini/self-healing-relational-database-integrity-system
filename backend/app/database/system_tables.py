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

RETAIL_RULES = [
    # 1. Candidate Key Duplicate Email
    {
        "rule_code": "RULE_RETAIL_DUP_CUSTOMER_EMAIL",
        "name": "Duplicate Customer Email Address",
        "description": "Enforces uniqueness for customer email addresses to prevent profile fragmentation and collision.",
        "rule_type": "DUPLICATE",
        "target_table": "customers",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {"group_by": ["email"], "case_sensitive": False},
        "severity": "HIGH",
        "is_enabled": True
    },
    # 2. Mandatory Customer Name (NULL / Empty string)
    {
        "rule_code": "RULE_RETAIL_NULL_CUSTOMER_NAME",
        "name": "Mandatory Customer Name",
        "description": "Ensures customer records possess a non-null, non-empty customer name.",
        "rule_type": "NULL_CHECK",
        "target_table": "customers",
        "target_column": "customer_name",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {"disallow_empty_string": True},
        "severity": "CRITICAL",
        "is_enabled": True
    },
    # 3. Mandatory Customer Email (NULL / Empty string)
    {
        "rule_code": "RULE_RETAIL_NULL_CUSTOMER_EMAIL",
        "name": "Mandatory Customer Email",
        "description": "Ensures customer records possess a valid non-null contact email address.",
        "rule_type": "NULL_CHECK",
        "target_table": "customers",
        "target_column": "email",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {"disallow_empty_string": True},
        "severity": "CRITICAL",
        "is_enabled": True
    },
    # 4. Product Positive Price Check (Domain violation)
    {
        "rule_code": "RULE_RETAIL_DOMAIN_PRODUCT_PRICE",
        "name": "Product Positive Price Requirement",
        "description": "Ensures catalog product prices are strictly positive values (> 0.00).",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "products",
        "target_column": "price",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {"min_value": 0.01},
        "severity": "CRITICAL",
        "is_enabled": True
    },
    # 5. Non-Negative Stock Quantity (Domain violation)
    {
        "rule_code": "RULE_RETAIL_DOMAIN_PRODUCT_STOCK",
        "name": "Non-Negative Product Stock Quantity",
        "description": "Ensures catalog product inventory stock cannot be negative (>= 0).",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "products",
        "target_column": "stock_quantity",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {"min_value": 0},
        "severity": "HIGH",
        "is_enabled": True
    },
    # 6. Valid Order Status (Domain Enum violation)
    {
        "rule_code": "RULE_RETAIL_DOMAIN_ORDER_STATUS",
        "name": "Valid Order Status Enum",
        "description": "Ensures order status conforms to recognized domain states (COMPLETED, PENDING, SHIPPED).",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "orders",
        "target_column": "order_status",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "allowed_values": ["COMPLETED", "PENDING", "SHIPPED"],
            "allow_null": False
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    # 7. Valid Payment Status (Domain Enum violation)
    {
        "rule_code": "RULE_RETAIL_DOMAIN_PAYMENT_STATUS",
        "name": "Valid Payment Status Enum",
        "description": "Ensures payment records have valid transaction statuses (PAID, PENDING).",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "payments",
        "target_column": "payment_status",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {
            "allowed_values": ["PAID", "PENDING"],
            "allow_null": False
        },
        "severity": "HIGH",
        "is_enabled": True
    },
    # 8. Positive Payment Amount (Domain range violation)
    {
        "rule_code": "RULE_RETAIL_DOMAIN_PAYMENT_AMOUNT",
        "name": "Positive Payment Amount Requirement",
        "description": "Ensures transaction payment amounts are strictly positive values (> 0.00).",
        "rule_type": "DOMAIN_CHECK",
        "target_table": "payments",
        "target_column": "amount",
        "parent_table": None,
        "parent_column": None,
        "parameters_json": {"min_value": 0.01},
        "severity": "CRITICAL",
        "is_enabled": True
    },
    # 9. Orphan Order Customer Reference
    {
        "rule_code": "RULE_RETAIL_ORPHAN_ORDER_CUSTOMER",
        "name": "Order Customer Reference Check",
        "description": "Ensures foreign key customer_id in orders resolves to an existing customer record.",
        "rule_type": "ORPHAN",
        "target_table": "orders",
        "target_column": "customer_id",
        "parent_table": "customers",
        "parent_column": "customer_id",
        "parameters_json": {"allow_null": False, "strategy": "MAP_PARENT"},
        "severity": "CRITICAL",
        "is_enabled": True
    },
    # 10. Orphan Order Item Product Reference
    {
        "rule_code": "RULE_RETAIL_ORPHAN_ITEM_PRODUCT",
        "name": "Order Item Product Reference Check",
        "description": "Ensures foreign key product_id in order_items resolves to an existing catalog product.",
        "rule_type": "ORPHAN",
        "target_table": "order_items",
        "target_column": "product_id",
        "parent_table": "products",
        "parent_column": "product_id",
        "parameters_json": {"allow_null": False, "strategy": "MAP_PARENT"},
        "severity": "CRITICAL",
        "is_enabled": True
    },
    # 11. Orphan Inventory Product Reference
    {
        "rule_code": "RULE_RETAIL_ORPHAN_INVENTORY_PRODUCT",
        "name": "Inventory Product Reference Check",
        "description": "Ensures foreign key product_id in inventory resolves to an existing product.",
        "rule_type": "ORPHAN",
        "target_table": "inventory",
        "target_column": "product_id",
        "parent_table": "products",
        "parent_column": "product_id",
        "parameters_json": {"allow_null": False, "strategy": "MAP_PARENT"},
        "severity": "CRITICAL",
        "is_enabled": True
    },
    # 12. Orphan Inventory Supplier Reference
    {
        "rule_code": "RULE_RETAIL_ORPHAN_INVENTORY_SUPPLIER",
        "name": "Inventory Supplier Reference Check",
        "description": "Ensures foreign key supplier_id in inventory resolves to an existing supplier.",
        "rule_type": "ORPHAN",
        "target_table": "inventory",
        "target_column": "supplier_id",
        "parent_table": "suppliers",
        "parent_column": "supplier_id",
        "parameters_json": {"allow_null": False, "strategy": "MAP_PARENT"},
        "severity": "CRITICAL",
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

            # 2. Check if integrity_rules needs seed rules
            cur.execute("SELECT COUNT(*) AS c FROM `integrity_rules`")
            rule_count = cur.fetchone()["c"]

            if rule_count == 0:
                logger.info("Seeding Retail Database integrity rules catalog...")
                insert_sql = """
                    INSERT INTO `integrity_rules` (
                        `rule_code`, `name`, `description`, `rule_type`,
                        `target_table`, `target_column`, `parent_table`, `parent_column`,
                        `parameters_json`, `severity`, `is_enabled`
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);
                """
                for r in RETAIL_RULES:
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
                VALUES ('schema_type', 'RETAIL_MANAGEMENT')
                ON DUPLICATE KEY UPDATE `meta_value` = 'RETAIL_MANAGEMENT'
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

