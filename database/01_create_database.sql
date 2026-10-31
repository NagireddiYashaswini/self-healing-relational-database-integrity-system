-- =============================================================================
-- Self-Healing Relational Database Integrity System
-- Script 01: Database Creation
-- DBMS: MySQL 8.0+ / MariaDB 10.4+ (XAMPP compatible)
-- Engine: InnoDB (Full ACID & Foreign Key Support)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `self_healing_test_db`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `self_healing_test_db`;
