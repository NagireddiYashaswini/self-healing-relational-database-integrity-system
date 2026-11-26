# -*- coding: utf-8 -*-
"""
Full Presentation Deck Builder: Self-Healing Relational Database Integrity System
Compiles: DBMS_PROJECT_PRESENTATION.pptx
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

OUTPUT_PPTX = "DBMS_PROJECT_PRESENTATION.pptx"

# Colors
C_BG            = RGBColor(248, 250, 252) # Slate 50  (#F8FAFC)
C_WHITE         = RGBColor(255, 255, 255) # White     (#FFFFFF)
C_BORDER        = RGBColor(226, 232, 240) # Slate 200 (#E2E8F0)
C_TEXT_MAIN     = RGBColor(15, 23, 42)    # Slate 900 (#0F172A)
C_TEXT_BODY     = RGBColor(51, 65, 85)    # Slate 700 (#334155)
C_TEXT_MUTED    = RGBColor(100, 116, 139) # Slate 500 (#64748B)

C_PRIMARY       = RGBColor(79, 70, 229)   # Indigo 600 (#4F46E5)
C_PRIMARY_BG    = RGBColor(238, 242, 255) # Indigo 50  (#EEF2FF)
C_PRIMARY_LIGHT = RGBColor(99, 102, 241)  # Indigo 500 (#6366F1)

C_EMERALD       = RGBColor(16, 185, 129)  # Emerald 500 (#10B981)
C_EMERALD_BG    = RGBColor(236, 253, 245) # Emerald 50  (#ECFDF5)
C_EMERALD_TEXT  = RGBColor(6, 95, 70)     # Emerald 800 (#065F46)

C_RED           = RGBColor(239, 68, 68)   # Red 500 (#EF4444)
C_RED_BG        = RGBColor(254, 242, 242) # Red 50  (#FEF2F2)
C_RED_TEXT      = RGBColor(153, 27, 27)   # Red 800 (#991B1B)

C_AMBER         = RGBColor(245, 158, 11)  # Amber 500 (#F59E0B)
C_AMBER_BG      = RGBColor(255, 251, 235) # Amber 50  (#FFFBEB)
C_AMBER_TEXT    = RGBColor(146, 64, 14)   # Amber 800 (#92400E)

C_DARK_BG       = RGBColor(15, 23, 42)    # Slate 900 (#0F172A)
C_DARK_BORDER   = RGBColor(51, 65, 85)    # Slate 700 (#334155)
C_CODE_CYAN     = RGBColor(56, 189, 248)  # Cyan 400  (#38BDF8)
C_CODE_GREEN    = RGBColor(52, 211, 153)  # Emerald 400 (#34D399)

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"
FONT_CODE    = "Consolas"

def set_shape_flat(shape, fill_color, border_color=None, border_width=1.0):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()

def add_header(slide, group_name, title_text, subtitle_text, slide_num, total_slides=14):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    set_shape_flat(bg, C_BG)

    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.48))
    set_shape_flat(top_bar, C_WHITE, C_BORDER, 0.75)

    tb_nav = slide.shapes.add_textbox(Inches(0.6), Inches(0.08), Inches(6.0), Inches(0.32))
    p = tb_nav.text_frame.paragraphs[0]
    p.text = f"SELF-HEALING DBMS  >  {group_name.upper()}"
    p.font.name = FONT_CODE
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

    pill_db = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.1), Inches(0.09), Inches(1.85), Inches(0.28))
    set_shape_flat(pill_db, C_EMERALD_BG, RGBColor(167, 243, 208), 0.75)
    p = pill_db.text_frame.paragraphs[0]
    p.text = "● MySQL Connected"
    p.font.name = FONT_HEADING
    p.font.size = Pt(8)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD_TEXT
    p.alignment = PP_ALIGN.CENTER

    pill_name = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.05), Inches(0.09), Inches(1.68), Inches(0.28))
    set_shape_flat(pill_name, RGBColor(241, 245, 249), C_BORDER, 0.75)
    p = pill_name.text_frame.paragraphs[0]
    p.text = "self_healing_test_db"
    p.font.name = FONT_CODE
    p.font.size = Pt(7.5)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_BODY
    p.alignment = PP_ALIGN.CENTER

    tb_title = slide.shapes.add_textbox(Inches(0.6), Inches(0.65), Inches(12.133), Inches(0.65))
    tf = tb_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_HEADING
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_MAIN

    p2 = tf.add_paragraph()
    p2.text = subtitle_text
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = C_TEXT_MUTED
    p2.space_before = Pt(2)

    foot_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(7.05), Inches(12.133), Inches(0.015))
    set_shape_flat(foot_line, C_BORDER)

    tb_foot = slide.shapes.add_textbox(Inches(0.6), Inches(7.1), Inches(8.0), Inches(0.3))
    p = tb_foot.text_frame.paragraphs[0]
    p.text = "Academic Group Project Demonstration & Viva Voce Guide | Department of CSE"
    p.font.name = FONT_BODY
    p.font.size = Pt(8)
    p.font.color.rgb = C_TEXT_MUTED

    tb_num = slide.shapes.add_textbox(Inches(11.0), Inches(7.1), Inches(1.733), Inches(0.3))
    p = tb_num.text_frame.paragraphs[0]
    p.text = f"Slide {slide_num} of {total_slides}"
    p.font.name = FONT_CODE
    p.font.size = Pt(8)
    p.font.color.rgb = C_TEXT_MUTED
    p.alignment = PP_ALIGN.RIGHT

def add_panel(slide, left, top, width, height, title=None, badge=None, bg_color=C_WHITE, border_color=C_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    set_shape_flat(card, bg_color, border_color, 0.75)

    if title:
        tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.12), Inches(width - 0.4), Inches(0.38))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_MAIN

        if badge:
            b_pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + width - 1.4), Inches(top + 0.15), Inches(1.2), Inches(0.24))
            set_shape_flat(b_pill, C_PRIMARY_BG, RGBColor(199, 210, 254), 0.5)
            bp = b_pill.text_frame.paragraphs[0]
            bp.text = badge
            bp.font.name = FONT_CODE
            bp.font.size = Pt(7.5)
            bp.font.bold = True
            bp.font.color.rgb = C_PRIMARY
            bp.alignment = PP_ALIGN.CENTER

        sep = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left + 0.2), Inches(top + 0.48), Inches(width - 0.4), Inches(0.01))
        set_shape_flat(sep, border_color)

def add_stat_card(slide, left, top, width, height, label, value, subtext=None, val_color=C_PRIMARY):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    set_shape_flat(card, C_WHITE, C_BORDER, 0.75)

    tb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.1), Inches(width - 0.3), Inches(height - 0.2))
    tf = tb.text_frame
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = label.upper()
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(8)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_MUTED

    p2 = tf.add_paragraph()
    p2.text = value
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(21)
    p2.font.bold = True
    p2.font.color.rgb = val_color
    p2.space_before = Pt(2)

    if subtext:
        p3 = tf.add_paragraph()
        p3.text = subtext
        p3.font.name = FONT_BODY
        p3.font.size = Pt(7.5)
        p3.font.color.rgb = C_TEXT_BODY
        p3.space_before = Pt(2)

def add_code_panel(slide, left, top, width, height, title, code_lines):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    set_shape_flat(card, C_DARK_BG, C_DARK_BORDER, 1.0)

    tb_title = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.08), Inches(width - 0.4), Inches(0.28))
    p = tb_title.text_frame.paragraphs[0]
    p.text = f"$ {title}"
    p.font.name = FONT_CODE
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = C_CODE_CYAN

    tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.35), Inches(width - 0.4), Inches(height - 0.45))
    tf = tb.text_frame
    tf.word_wrap = True

    for i, line in enumerate(code_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = FONT_CODE
        p.font.size = Pt(8)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(1)

# Initialize Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

print("Building 14 Presentation Slides...")

# -----------------------------------------------------------------------------
# SLIDE 1: TITLE SLIDE (Dark Modern Slate Theme)
# -----------------------------------------------------------------------------
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
set_shape_flat(bg1, RGBColor(15, 23, 42)) # Deep Slate 900

# Decorative top glow accent line
top_accent = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(2.5), Inches(0.06))
set_shape_flat(top_accent, C_PRIMARY_LIGHT)

# Department header
tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(11.5), Inches(0.5))
p = tb.text_frame.paragraphs[0]
p.text = "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING  |  DBMS GROUP PROJECT"
p.font.name = FONT_CODE
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = RGBColor(147, 197, 253)

# Title
tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.5), Inches(1.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Self-Healing Relational Database\nIntegrity System"
p.font.name = FONT_HEADING
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = C_WHITE

# Subtitle
tb = s1.shapes.add_textbox(Inches(0.8), Inches(3.45), Inches(11.5), Inches(0.8))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Autonomous Relational Anomaly Detection, Directed Graph Analysis, Optimistic Concurrency Control, and Transaction-Safe Self-Healing for MySQL InnoDB"
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = RGBColor(203, 213, 225)

# Badges Grid
badges = [
    "MySQL 8 / MariaDB (Port 3306)",
    "InnoDB ACID Engine",
    "FastAPI (Python 3.13)",
    "React 18 + Vite SPA",
    "NetworkX Relational DAG",
    "Optimistic Concurrency (OCC)",
    "Immutable Audit Triggers",
    "Version 2.4.0"
]
bx = 0.8
by = 4.4
for b in badges:
    bw = len(b) * 0.11 + 0.35
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(bx), Inches(by), Inches(bw), Inches(0.32))
    set_shape_flat(pill, RGBColor(30, 41, 59), RGBColor(71, 85, 105), 0.75)
    p = pill.text_frame.paragraphs[0]
    p.text = b
    p.font.name = FONT_CODE
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.alignment = PP_ALIGN.CENTER
    bx += bw + 0.15
    if bx > 11.5:
        bx = 0.8
        by += 0.42

# Meta Card Box at Bottom
card_meta = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.4), Inches(11.733), Inches(1.3))
set_shape_flat(card_meta, RGBColor(30, 41, 59), RGBColor(51, 65, 85), 1.0)

tb_m = s1.shapes.add_textbox(Inches(1.1), Inches(5.55), Inches(11.1), Inches(1.0))
tf = tb_m.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Target Database: self_healing_test_db (22 InnoDB Tables)  |  Architecture: 4-Tier Decoupled Enterprise Model"
p.font.name = FONT_CODE
p.font.size = Pt(9.5)
p.font.bold = True
p.font.color.rgb = C_PRIMARY_LIGHT

p2 = tf.add_paragraph()
p2.text = "Full-Stack Implementation: React 18 UI (http://localhost:5173)  ->  FastAPI Backend (http://127.0.0.1:8000)  ->  MySQL InnoDB"
p2.font.name = FONT_BODY
p2.font.size = Pt(9)
p2.font.color.rgb = RGBColor(203, 213, 225)
p2.space_before = Pt(3)

p3 = tf.add_paragraph()
p3.text = "Academic Evaluation: Project Viva Voce & Laboratory Demonstration Guide  |  Academic Year 2026"
p3.font.name = FONT_BODY
p3.font.size = Pt(8.5)
p3.font.color.rgb = RGBColor(148, 163, 184)
p3.space_before = Pt(3)

print("Slide 1 generated: Title")

# -----------------------------------------------------------------------------
# SLIDE 2: PROBLEM STATEMENT & MOTIVATION
# -----------------------------------------------------------------------------
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "System Overview", "The Problem: Why Traditional Databases Crash", "Relational databases in enterprise production environments face fatal disruption from unexpected data anomalies", 2)

add_panel(s2, 0.6, 1.4, 5.9, 4.2, "The Production Relational Challenge", "PROBLEM")
tb = s2.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.5), Inches(3.4))
tf = tb.text_frame
tf.word_wrap = True
bullets_p = [
    ("Silent Foreign Key Orphans", "External batch ingestion or legacy data imports frequently bypass application constraints, creating dangling child records that break JOIN queries."),
    ("Candidate Key Uniqueness Collisions", "Duplicate entity attributes (e.g. duplicate faculty emails or department codes) violate 1NF/2NF assumptions and skew analytical aggregates."),
    ("Out-of-Range Domain Violations", "Unvalidated numerical values (negative department budgets, invalid student GPAs) corrupt downstream business calculations."),
    ("Rigid ON DELETE RESTRICT Failures", "Database constraints block legitimate maintenance updates with fatal foreign key errors, requiring manual DBA intervention during peak hours.")
]
for i, (b_title, b_desc) in enumerate(bullets_p):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {b_title}: {b_desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(9)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(6)

add_panel(s2, 6.8, 1.4, 5.9, 4.2, "Our Solution: Autonomous Self-Healing", "SOLUTION")
tb = s2.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.5), Inches(3.4))
tf = tb.text_frame
tf.word_wrap = True
bullets_s = [
    ("Continuous Relational Scanning", "Proactively scans InnoDB tables using information_schema introspection to detect orphans, duplicates, and domain violations before queries crash."),
    ("Multi-Stage Staging & Quarantine", "Raw external records land in unconstrained staging buffers. Corrupted records are isolated in quarantine_records rather than aborting batch jobs."),
    ("Impact Assessment & Blast Radius", "Models schema foreign keys as a NetworkX DAG to verify cascading child dependencies before attempting any database modification."),
    ("Atomic Transactional Healing", "Executes all repairs inside explicit InnoDB transactions (SELECT ... FOR UPDATE, SAVEPOINT, COMMIT, ROLLBACK) with optimistic concurrency protection.")
]
for i, (b_title, b_desc) in enumerate(bullets_s):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {b_title}: {b_desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(9)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(6)

# 3 Stat Cards across bottom
add_stat_card(s2, 0.6, 5.8, 3.8, 1.1, "Anomaly Detection Scope", "11 Categories", "Orphans, duplicates, nulls, domains, regex bounds", C_PRIMARY)
add_stat_card(s2, 4.75, 5.8, 3.8, 1.1, "Autonomous Healing Actions", "7 Strategies", "MAP_PARENT, SET_DEFAULT, QUARANTINE, DELETE...", C_EMERALD)
add_stat_card(s2, 8.9, 5.8, 3.8, 1.1, "Transactional Safety", "100% ACID", "Pessimistic row locking & undo log rollback", C_PRIMARY)

print("Slide 2 generated: Problem Statement")

# -----------------------------------------------------------------------------
# SLIDE 3: SYSTEM ARCHITECTURE (THE 4-TIER MODEL)
# -----------------------------------------------------------------------------
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "System Architecture", "Decoupled 4-Tier Enterprise Architecture", "Strict separation of concerns ensures scanning, ingestion, and repair operations cannot corrupt production business data", 3)

tier_data = [
    ("Tier 1: Presentation Tier", "React 18 + Vite SPA", C_PRIMARY, [
        "11 Administrative Single-Page Interfaces",
        "Axios HTTP Client with unified error interceptors",
        "Vite Proxy forwarding /api to http://127.0.0.1:8000",
        "Lucide React UI icons & Tailwind CSS design system",
        "Interactive SVG Relational Dependency Canvas",
        "Real-time client-side filtering and KPI cards"
    ]),
    ("Tier 2: Application Tier", "FastAPI (Python 3.13 / Uvicorn)", C_PRIMARY, [
        "Modular REST APIs under /api (10 API routers)",
        "IntegrityScanner (dynamic rule evaluation)",
        "RepairEngine (preview generation & OCC hashing)",
        "DependencyAnalyzer (NetworkX Directed Graph)",
        "IngestionService (Staging/Quarantine ETL pipeline)",
        "TransactionManager & RecoveryManager engines"
    ]),
    ("Tier 3: Persistence Layer", "PyMySQL Connection Pool", C_EMERALD, [
        "Explicit connection factory with autocommit=False",
        "DictCursor for native dictionary result mappings",
        "validate_identifier() regex security against SQL injection",
        "Pessimistic row locking: SELECT ... FOR UPDATE",
        "Dynamic information_schema metadata introspection",
        "Health diagnostic ping and round-trip latency checks"
    ]),
    ("Tier 4: Relational Storage", "MySQL InnoDB (Port 3306)", C_TEXT_MAIN, [
        "Active database: self_healing_test_db",
        "22 InnoDB tables across 4 functional tiers",
        "Physical foreign keys (ON DELETE RESTRICT/CASCADE)",
        "Full ACID support via redo and undo logs",
        "Application-level recovery checkpoints (JSON state)",
        "Database triggers enforcing audit trail immutability"
    ])
]

tx = 0.6
tw = 2.9
for title, tech, col, items in tier_data:
    add_panel(s3, tx, 1.4, tw, 5.4, title, None)
    
    # Sub-header tech badge
    badge = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(tx + 0.15), Inches(1.95), Inches(tw - 0.3), Inches(0.28))
    set_shape_flat(badge, C_PRIMARY_BG, RGBColor(199, 210, 254), 0.5)
    p = badge.text_frame.paragraphs[0]
    p.text = tech
    p.font.name = FONT_CODE
    p.font.size = Pt(7.5)
    p.font.bold = True
    p.font.color.rgb = col
    p.alignment = PP_ALIGN.CENTER

    tb = s3.shapes.add_textbox(Inches(tx + 0.15), Inches(2.35), Inches(tw - 0.3), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, itm in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {itm}"
        p.font.name = FONT_BODY
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(5)

    tx += tw + 0.17

print("Slide 3 generated: Architecture")

# -----------------------------------------------------------------------------
# SLIDE 4: DATABASE SCHEMA: 22 TABLES ACROSS 4 TIERS
# -----------------------------------------------------------------------------
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "Relational Modeling", "Database Schema: 22 Tables Across 4 Functional Tiers", "Engine: MySQL InnoDB (Strict ACID, Physical Foreign Keys, and Audit Immutability Triggers)", 4)

schema_tiers = [
    ("Tier 1: Business Domain (6 Tables)", "Core Academic Entity Model", [
        ("departments", "dept_id (PK), dept_code, dept_name, budget, building"),
        ("instructors", "instructor_id (PK), name, email, dept_id (FK), salary"),
        ("courses", "course_id (PK), course_code, course_name, credits, dept_id (FK), instructor_id (FK)"),
        ("students", "student_id (PK), student_name, email, age, gpa, dept_id (FK)"),
        ("enrollments", "enrollment_id (PK), student_id (FK), course_id (FK), grade, status"),
        ("classrooms", "classroom_id (PK), room_number, building, capacity, dept_id (FK)")
    ]),
    ("Tier 2: Staging & Quarantine (7 Tables)", "Fault Isolation Buffers", [
        ("staging_* (6 tables)", "staging_departments, staging_instructors, staging_courses, staging_students, staging_enrollments, staging_classrooms. Contains unconstrained landing columns + validation_status, validation_error"),
        ("quarantine_records (1 table)", "quarantine_id (PK), source_table, source_pk_value, issue_type, row_data_json, quarantine_reason, quarantined_by, resolved, resolution_notes")
    ]),
    ("Tier 3: System Engine & Repairs (5 Tables)", "Integrity Engine Metadata", [
        ("integrity_rules", "rule_id (PK), rule_code (UNIQUE), rule_type, target_table, target_column, parent_table, parameters_json, severity, is_enabled"),
        ("scan_runs", "scan_id (PK), scan_type, start_time, end_time, status, total_rows_inspected, issues_found, critical_count"),
        ("integrity_issues", "issue_id (PK), scan_id, category, severity, table_name, record_id, column_name, invalid_value, description, status"),
        ("repair_recommendations", "recommendation_id (PK), issue_id, strategy, problem_description, proposed_action, risk_level, approval_status"),
        ("repair_executions", "execution_id (PK), issue_id, transaction_id, status, executed_by, before_state_json, after_state_json, sql_executed")
    ]),
    ("Tier 4: Audit Trails & Recovery (4 Tables)", "Immutable System History", [
        ("audit_logs", "event_id (PK), event_type, actor, timestamp, related_ids, target_table, result, before_json, after_json. Protected by BEFORE UPDATE/DELETE triggers"),
        ("transaction_logs", "transaction_id (PK), execution_id, start_time, end_time, status (COMMITTED/ROLLED_BACK), operations_count, duration_ms"),
        ("recovery_checkpoints", "checkpoint_id (PK), checkpoint_name, target_table, snapshot_metadata_json, snapshot_rows_json, status"),
        ("database_metadata", "meta_key (PK), meta_value, updated_at (System revision tracking)")
    ])
]

card_w = 5.9
card_h = 2.6
coords = [(0.6, 1.4), (6.8, 1.4), (0.6, 4.2), (6.8, 4.2)]

for idx, (title, sub, tbls) in enumerate(schema_tiers):
    cx, cy = coords[idx]
    add_panel(s4, cx, cy, card_w, card_h, title, sub)
    tb = s4.shapes.add_textbox(Inches(cx + 0.15), Inches(cy + 0.55), Inches(card_w - 0.3), Inches(card_h - 0.65))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, (t_name, t_cols) in enumerate(tbls):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {t_name}: {t_cols}"
        p.font.name = FONT_BODY
        p.font.size = Pt(7.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(2)

print("Slide 4 generated: Schema")

# -----------------------------------------------------------------------------
# SLIDE 5: EXECUTIVE DASHBOARD & HEALTH OBSERVABILITY
# -----------------------------------------------------------------------------
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Core Recovery Engine", "Executive Dashboard & Live Observability", "Real-time synchronization with XAMPP MySQL: Connection latency, integrity scores, table counts, and severity metrics", 5)

# 4 Stat Cards across top replicating DashboardPage.jsx
add_stat_card(s5, 0.6, 1.4, 2.85, 1.35, "MySQL Connection", "CONNECTED", "Port 3306 | 1.5ms Latency | MariaDB 10.4", C_EMERALD)
add_stat_card(s5, 3.65, 1.4, 2.85, 1.35, "Relational Integrity", "100.0%", "Healthy Records / Total Records", C_PRIMARY)
add_stat_card(s5, 6.7, 1.4, 2.85, 1.35, "Managed Tables", "22 Tables", "6 Business, 7 Staging/Quarantine, 9 System", C_TEXT_MAIN)
add_stat_card(s5, 9.75, 1.4, 2.98, 1.35, "Open Violations", "0 Pending", "All relational issues resolved & healed", C_PRIMARY_LIGHT)

# Panel 1: Violation Severity Model
add_panel(s5, 0.6, 2.95, 5.9, 3.9, "Relational Violation Severity Breakdown", "STANDARDS")
tb = s5.shapes.add_textbox(Inches(0.8), Inches(3.55), Inches(5.5), Inches(3.1))
tf = tb.text_frame
tf.word_wrap = True
items_sev = [
    ("CRITICAL SEVERITY (Red Alert)", "Assigned to orphan foreign key records in primary business entities (e.g. instructors referencing non-existent departments) and duplicate candidate keys. Left unresolved, these break JOIN queries and corrupt application logic."),
    ("HIGH SEVERITY (Orange Alert)", "Assigned to missing mandatory non-null attributes and out-of-range numerical fields (negative budgets, negative salaries). Demands prompt administrative healing before analytics run."),
    ("LOW SEVERITY (Blue Alert)", "Assigned to minor formatting discrepancies, regex pattern mismatches, and stale scan runs that crashed during prior application sessions."),
    ("INTEGRITY SCORE HEURISTIC", "Calculated dynamically: ((Total Rows - Unique Violating Keys) / Total Rows) * 100. Updates in real-time as repairs commit.")
]
for i, (title, desc) in enumerate(items_sev):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {title}: {desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(4)

# Panel 2: Live Activity & Recent Activity Feed
add_panel(s5, 6.8, 2.95, 5.933, 3.9, "Live System Observability & Quick Controls", "UI METRICS")
tb = s5.shapes.add_textbox(Inches(7.0), Inches(3.55), Inches(5.5), Inches(3.1))
tf = tb.text_frame
tf.word_wrap = True
items_dash = [
    ("Full Database Scan Trigger", "Button 'Scan Entire Database' triggers POST /api/scans with scan_type='FULL', inspecting all 6 core business tables and evaluating all active rules."),
    ("Asynchronous Multi-Resource Polling", "Dashboard load executes Promise.all across 8 endpoints: database/status, tables, rules, scans, issues, recommendations, executions, and audit logs."),
    ("Quick Navigation Cockpit", "One-click routing to Recovery Center (/recovery), Relational Explorer (/explorer), Audit Trail (/audit), and Rules Catalog (/rules)."),
    ("Real-Time Audit Feed", "Renders the last 6 chronological operations executed by either SYSTEM or ADMIN_USER with color-coded success/failure badges.")
]
for i, (title, desc) in enumerate(items_dash):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {title}: {desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(4)

print("Slide 5 generated: Dashboard")

# -----------------------------------------------------------------------------
# SLIDE 6: DATA INGESTION & MULTI-STAGE ETL PIPELINE
# -----------------------------------------------------------------------------
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Data Ingestion", "Decoupled Data Ingestion & Fault-Isolated Staging", "Prevents database crashes by landing raw external data in staging buffers prior to transactional production promotion", 6)

# 3 Stage Pipeline Cards
add_panel(s6, 0.6, 1.4, 3.8, 5.4, "Stage 1: Staging Landing Buffer", "EXTERNAL FEED")
tb = s6.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(3.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p_lines = [
    "External batches submit records via Data Ingestion page (/ingestion).",
    "Targeted to unconstrained staging tables: staging_departments, staging_students, staging_enrollments, etc.",
    "Record initially inserted with validation_status = 'PENDING'.",
    "Generates unique external tracking reference (e.g. EXT-8891) for audit traceability.",
    "Zero production foreign key constraints exist on staging tables, completely preventing fatal MySQL ingestion crashes."
]
for i, l in enumerate(p_lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {l}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(6)

add_panel(s6, 4.75, 1.4, 3.8, 5.4, "Stage 2: 5-Point Validation Pipeline", "INGESTION ENGINE")
tb = s6.shapes.add_textbox(Inches(4.95), Inches(2.0), Inches(3.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
v_lines = [
    "1. Mandatory Non-Null Check: Verifies mandatory columns are not empty or whitespace.",
    "2. Date & Timestamp Normalization: Rejects literal SQL default keywords ('CURRENT_TIMESTAMP'); verifies ISO YYYY-MM-DD.",
    "3. Foreign Key Parent Existence Probe: Queries: SELECT COUNT(*) FROM parent WHERE id = ? to ensure parents exist.",
    "4. Domain Range Bounds: Enforces GPA [0.0 - 4.0], age [16 - 65], credits [1 - 12], non-negative budgets.",
    "5. Production Uniqueness Collision: Probes production to verify candidate keys do not collide."
]
for i, l in enumerate(v_lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {l}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(5)

add_panel(s6, 8.9, 1.4, 3.833, 5.4, "Stage 3: Two-Phase Outcome", "ATOMIC ROUTING")
tb = s6.shapes.add_textbox(Inches(9.1), Inches(2.0), Inches(3.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
o_lines = [
    "IF VALID (100% Passed):",
    "  -> Begins atomic InnoDB transaction.",
    "  -> Promotes clean row: INSERT INTO production_table.",
    "  -> Updates staging: validation_status = 'VALID'.",
    "  -> Issues COMMIT & logs DATA_INGESTION_SUCCESS.",
    "",
    "IF INVALID (Violations Detected):",
    "  -> Marks staging: validation_status = 'REJECTED'.",
    "  -> Serializes full payload into quarantine_records.",
    "  -> Stores exact violation error messages.",
    "  -> Issues COMMIT & logs DATA_INGESTION_REJECTED.",
    "  -> UI displays quarantine ID and error alert!"
]
for i, l in enumerate(o_lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = l
    p.font.name = FONT_CODE if "->" in l or "IF" in l else FONT_BODY
    p.font.size = Pt(8)
    p.font.bold = True if "IF" in l else False
    p.font.color.rgb = C_EMERALD_TEXT if "VALID" in l else (C_RED_TEXT if "INVALID" in l else C_TEXT_BODY)
    p.space_before = Pt(2)

print("Slide 6 generated: Ingestion")

# -----------------------------------------------------------------------------
# SLIDE 7: PROACTIVE INTEGRITY SCANNER
# -----------------------------------------------------------------------------
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Core Recovery Engine", "Proactive Relational Integrity Scanner", "Autonomous inspection engine compiling declarative rules into high-performance MySQL anomaly detection queries", 7)

scan_cards = [
    ("1. ORPHAN Foreign Key Detection", "REFERENTIAL INTEGRITY", [
        "-- Detects child rows referencing missing parents:",
        "SELECT t.enrollment_id AS pk_val, t.student_id AS fk_val",
        "FROM `enrollments` t",
        "LEFT JOIN `students` p ON t.student_id = p.student_id",
        "WHERE p.student_id IS NULL AND t.student_id IS NOT NULL;"
    ], "Strategy: MAP_PARENT (Prompt admin to choose authoritative parent)"),

    ("2. DUPLICATE Candidate Key Check", "ENTITY INTEGRITY", [
        "-- Identifies uniqueness collisions across candidate keys:",
        "SELECT email, COUNT(*) as dup_count, ",
        "       GROUP_CONCAT(instructor_id ORDER BY instructor_id ASC) as pks",
        "FROM `instructors`",
        "WHERE email IS NOT NULL AND TRIM(email) != ''",
        "GROUP BY email HAVING COUNT(*) > 1;"
    ], "Strategy: DELETE_RECORD (Removes redundant row, retains canonical original)"),

    ("3. NULL & Mandatory Attribute Check", "DOMAIN COMPLETENESS", [
        "-- Identifies empty or null required columns:",
        "SELECT dept_id AS pk_val, dept_name AS col_val",
        "FROM `departments`",
        "WHERE dept_name IS NULL OR TRIM(dept_name) = '';"
    ], "Strategy: SET_DEFAULT (Applies verified replacement value)"),

    ("4. DOMAIN Bounds & Enum Constraints", "BUSINESS RULES", [
        "-- Flags numerical range and enum violations:",
        "SELECT dept_id AS pk_val, budget AS col_val",
        "FROM `departments`",
        "WHERE budget IS NOT NULL AND budget < 0.0;",
        "",
        "-- Validates enrollment enum: 'ENROLLED', 'COMPLETED', 'DROPPED'"
    ], "Strategy: SET_DEFAULT (Clamps to domain range / valid enum)")
]

coords_scan = [(0.6, 1.4), (6.8, 1.4), (0.6, 4.2), (6.8, 4.2)]
for idx, (title, cat, sql_lines, strat) in enumerate(scan_cards):
    cx, cy = coords_scan[idx]
    add_panel(s7, cx, cy, 5.9, 2.65, title, cat)
    add_code_panel(s7, cx + 0.15, cy + 0.55, 5.6, 1.6, "MYSQL DETECTION QUERY", sql_lines)

    # Strategy badge at bottom of card
    tb_s = s7.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 2.25), Inches(5.5), Inches(0.3))
    p = tb_s.text_frame.paragraphs[0]
    p.text = f"Recommended Healing: {strat}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY

print("Slide 7 generated: Scanner")

# -----------------------------------------------------------------------------
# SLIDE 8: SELF-HEALING & RECOVERY CENTER
# -----------------------------------------------------------------------------
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Core Recovery Engine", "Recovery Center & 7 Self-Healing Strategies", "Automated recommendation generation, blast radius calculation, transparent SQL previews, and transactional healing", 8)

add_panel(s8, 0.6, 1.4, 5.5, 5.4, "The 7 Autonomous Self-Healing Strategies", "CATALOG")
tb = s8.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.1), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
strats = [
    ("1. MAP_PARENT", "Used for orphan foreign key records in business tables. Prompts administrator to select a verified parent ID. Verifies parent existence, then updates child foreign key reference."),
    ("2. SET_DEFAULT", "Used for missing mandatory fields or domain range violations. Validates replacement value against column type, length, and uniqueness constraints before executing UPDATE."),
    ("3. QUARANTINE", "Used for corrupt staging records or unrepairable orphan entities. Copies row into quarantine_records as JSON, then deletes row from active table."),
    ("4. DELETE_RECORD", "Used for redundant duplicates. Evaluates blast radius to verify zero child records depend on the duplicate before issuing DELETE."),
    ("5. RESTORE_PARENT", "Used when an orphan child record requires its original parent restored. Re-inserts parent row from quarantine JSON and marks quarantine resolved."),
    ("6. MERGE_DUPLICATION", "Re-points child foreign key references from duplicate record to canonical parent record before deleting the duplicate."),
    ("7. MANUAL_INTERVENTION", "Used for complex multi-table relational anomalies. Generates zero automatic database changes, flagging row for human administrative review.")
]
for i, (st, desc) in enumerate(strats):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {st}: {desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(3)

add_panel(s8, 6.4, 1.4, 6.333, 5.4, "Transparent Repair Preview Modal Workflow", "PREVIEW COCKPIT")

# Before vs After Comparison Panels
add_panel(s8, 6.6, 2.05, 2.8, 1.6, "BEFORE STATE (Live Row)", "VIOLATION", RGBColor(254, 242, 242), RGBColor(254, 202, 202))
tb = s8.shapes.add_textbox(Inches(6.75), Inches(2.5), Inches(2.5), Inches(1.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = '{\n  "dept_id": 905,\n  "dept_code": "DEFICIT",\n  "budget": -50000.00\n}'
p.font.name = FONT_CODE
p.font.size = Pt(8)
p.font.color.rgb = C_RED_TEXT

add_panel(s8, 9.7, 2.05, 2.8, 1.6, "PROPOSED AFTER STATE", "HEALED", RGBColor(236, 253, 245), RGBColor(167, 243, 208))
tb = s8.shapes.add_textbox(Inches(9.85), Inches(2.5), Inches(2.5), Inches(1.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = '{\n  "dept_id": 905,\n  "dept_code": "DEFICIT",\n  "budget": 100000.00\n}'
p.font.name = FONT_CODE
p.font.size = Pt(8)
p.font.color.rgb = C_EMERALD_TEXT

# Blast Radius Panel
add_panel(s8, 6.6, 3.8, 5.9, 1.25, "Relational Blast Radius & Cascade Assessment", "NETWORKX")
tb = s8.shapes.add_textbox(Inches(6.8), Inches(4.25), Inches(5.5), Inches(0.75))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "• Direct Child Tables: instructors (0 rows), courses (0 rows), students (0 rows)\n• Downstream Descendants: enrollments (0 rows)  |  Matching Child Dependencies: 0\n• Concurrency Token: SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
p.font.name = FONT_CODE
p.font.size = Pt(7.5)
p.font.color.rgb = C_TEXT_BODY

# SQL Preview Block
add_code_panel(s8, 6.6, 5.2, 5.9, 1.45, "ATOMIC INNODB EXECUTION PLAN", [
    "START TRANSACTION; SAVEPOINT pre_repair_step;",
    "UPDATE `departments` SET `budget` = '100000.00' WHERE `dept_id` = 905;",
    "SELECT * FROM `departments` WHERE `dept_id` = 905; -- Verification check",
    "UPDATE `integrity_issues` SET status = 'REPAIRED' WHERE issue_id = 'ISSUE-DOM-12';",
    "COMMIT;"
])

print("Slide 8 generated: Recovery Center")

# -----------------------------------------------------------------------------
# SLIDE 9: OPTIMISTIC CONCURRENCY CONTROL (OCC)
# -----------------------------------------------------------------------------
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Concurrency Control", "Optimistic Concurrency Control (OCC) & Stale Preview Defense", "Prevents the Lost Update Problem when multiple database administrators review and execute repairs concurrently", 9)

add_panel(s9, 0.6, 1.4, 5.8, 5.4, "The Lost Update Problem in Admin Consoles", "RACE CONDITION")
tb = s9.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
occ_points = [
    ("The Classic Multi-User Race Condition", "In enterprise database systems, two administrators (Admin A and Admin B) may open the same integrity issue simultaneously. Both see budget = -50,000.00."),
    ("Unsynchronized Writes Cause Data Loss", "Admin A modifies budget to 100,000.00 and commits. A few seconds later, Admin B modifies budget to 75,000.00 based on the obsolete stale preview. Admin B silently overwrites Admin A's changes!"),
    ("Why Long-Lived Database Locks Fail", "Holding a physical row lock (FOR UPDATE) while the administrator reads the screen would freeze database tables, blocking all concurrent transactions."),
    ("The Cryptographic OCC Solution", "Instead of long-lived locks, RepairEngine computes a deterministic cryptographic SHA-256 hash token (row_version_token) over the row's JSON dictionary representation."),
    ("Atomic Execution-Time Verification", "During execution, RepairEngine acquires a momentary FOR UPDATE lock and re-computes the hash. If the hashes differ, a StalePreviewError is raised, rolling back the transaction!")
]
for i, (title, desc) in enumerate(occ_points):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {title}: {desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(5)

add_panel(s9, 6.7, 1.4, 6.033, 5.4, "Source Code Implementation in repair_engine.py", "PYTHON + INNODB")

# Code snippet for compute_row_hash
add_code_panel(s9, 6.9, 2.05, 5.633, 2.3, "PYTHON SHA-256 STATE HASH GENERATOR", [
    "def compute_row_hash(row_dict: Optional[Dict[str, Any]]) -> str:",
    "    if not row_dict:",
    "        return ''",
    "    clean_row = {}",
    "    for k, v in row_dict.items():",
    "        clean_row[k] = v.isoformat() if isinstance(v, datetime) else str(v)",
    "    s = json.dumps(clean_row, sort_keys=True)",
    "    return hashlib.sha256(s.encode('utf-8')).hexdigest()"
])

# Code snippet for OCC check
add_code_panel(s9, 6.9, 4.5, 5.633, 2.15, "STALE PREVIEW DETECTION & ROLLBACK", [
    "# Inside execute_repair() transaction block:",
    "cur.execute('SELECT * FROM `{table}` WHERE id = %s FOR UPDATE', (pk,))",
    "current_row = cur.fetchone()",
    "current_token = compute_row_hash(current_row)",
    "if row_version_token and row_version_token != current_token:",
    "    conn.rollback()",
    "    raise StalePreviewError('Record modified since preview generation!')"
])

print("Slide 9 generated: OCC")

# -----------------------------------------------------------------------------
# SLIDE 10: RELATIONAL DEPENDENCY & TOPOLOGY ANALYZER (DAG)
# -----------------------------------------------------------------------------
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Graph Theory & Topology", "Relational Dependency & Topology Analyzer (DAG)", "Models schema foreign key constraints as a Directed Acyclic Graph using NetworkX to determine safe operation sequences", 10)

add_panel(s10, 0.6, 1.4, 5.8, 5.4, "NetworkX Directed Acyclic Graph (DAG)", "MATHEMATICAL MODEL")
tb = s10.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
dag_points = [
    ("Mathematical Graph Modeling", "Tables represent vertices (V) and foreign key constraints represent directed edges (E): Parent Table -> Child Table. (Data in Parent must exist before Child can reference it)."),
    ("Automated Cycle Detection", "Evaluates nx.is_directed_acyclic_graph(G). If cycles exist (e.g. Table A references B and B references A), it detects cyclic deadlock risks that would freeze relational operations."),
    ("Topological Sorting (Safe Execution Order)", "Computes nx.topological_sort(G) to determine linear insertion and deletion orders:"),
    ("  • Safe Bulk Loading Sequence:", "departments -> instructors -> courses -> students -> enrollments"),
    ("  • Safe Bulk Deletion Sequence:", "enrollments -> courses -> instructors -> students -> departments"),
    ("Blast Radius Calculation", "Uses nx.descendants(G, target_table) to evaluate all downstream child tables impacted before executing a repair or deletion.")
]
for i, l in enumerate(dag_points):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    if isinstance(l, tuple):
        p.text = f"{l[0]} {l[1]}"
        p.font.bold = True if "•" in l[0] else False
    else:
        p.text = l
    p.font.name = FONT_CODE if "->" in p.text else FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_PRIMARY if "->" in p.text else C_TEXT_BODY
    p.space_before = Pt(4)

add_panel(s10, 6.7, 1.4, 6.033, 5.4, "Dependency Graph Neighborhood & Impact Cockpit", "FRONTEND UI")

# Topology Status Card
add_stat_card(s10, 6.9, 2.05, 2.7, 1.2, "Topology Status", "DAG VERIFIED", "has_cycles: false | Acyclic", C_EMERALD)
add_stat_card(s10, 9.8, 2.05, 2.7, 1.2, "Topological Order", "5 Levels", "departments -> enrollments", C_PRIMARY)

add_panel(s10, 6.9, 3.4, 5.633, 3.25, "Neighborhood Inspector for Table: departments", "BLAST RADIUS")
tb = s10.shapes.add_textbox(Inches(7.1), Inches(3.95), Inches(5.2), Inches(2.5))
tf = tb.text_frame
tf.word_wrap = True
insp_lines = [
    "• Direct Parents: None (Root reference entity)",
    "• Direct Children: instructors, courses, students, classrooms",
    "• Indirect Descendants: enrollments (depends on courses & students)",
    "• Total Descendant Blast Radius: 5 Tables",
    "• Safety Constraint: Deleting a department requires cascading or remapping child instructors and courses before deletion."
]
for i, l in enumerate(insp_lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = l
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(4)

print("Slide 10 generated: DAG")

# -----------------------------------------------------------------------------
# SLIDE 11: TRANSACTION MANAGEMENT & ACID SIMULATOR
# -----------------------------------------------------------------------------
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Database Utilities", "Real-Time MySQL InnoDB ACID Transaction Simulator", "Interactive real-time demonstration of atomicity, dirty read isolation, rollbacks, and savepoints", 11)

scenarios = [
    ("Scenario 1: Failure Simulation & Rollback", "ATOMIC ROLLBACK", C_RED, [
        "1. START TRANSACTION (Disables autocommit)",
        "2. SELECT COUNT(*) AS c -> Count = 10",
        "3. INSERT test row into staging_enrollments",
        "4. SELECT COUNT(*) AS c -> Count = 11 (Dirty buffer)",
        "5. Simulated Exception Triggers!",
        "6. ROLLBACK executes atomically",
        "7. SELECT COUNT(*) AS c -> Count = 10 (Restored!)",
        "Verdict: Demonstrates Atomicity ('All-or-Nothing')."
    ]),
    ("Scenario 2: Multi-Step Atomic Commit", "DURABLE COMMIT", C_EMERALD, [
        "1. START TRANSACTION (Disables autocommit)",
        "2. Validates business constraints and foreign keys",
        "3. Inserts valid row into staging_enrollments",
        "4. Updates related staging table status",
        "5. COMMIT executes permanently",
        "6. Row durably written to InnoDB redo logs",
        "7. Verified: Changes survive server restart!",
        "Verdict: Demonstrates Durability & Consistency."
    ]),
    ("Scenario 3: Savepoint Partial Rollback", "NESTED SAVEPOINTS", C_PRIMARY, [
        "1. START TRANSACTION",
        "2. INSERT Record A into table (Step 1)",
        "3. SAVEPOINT sp1; (Declares rollback boundary)",
        "4. INSERT invalid Record B into table (Step 2)",
        "5. Error occurs on Record B!",
        "6. ROLLBACK TO SAVEPOINT sp1; (Undoes only B)",
        "7. COMMIT; (Persists Record A permanently!)",
        "Verdict: Demonstrates Nested Partial Rollback."
    ])
]

sx = 0.6
sw = 3.8
for title, badge, col, steps in scenarios:
    add_panel(s11, sx, 1.4, sw, 5.4, title, badge)
    tb = s11.shapes.add_textbox(Inches(sx + 0.15), Inches(2.0), Inches(sw - 0.3), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, stp in enumerate(steps):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = stp
        p.font.name = FONT_CODE if "->" in stp or "1." in stp else FONT_BODY
        p.font.size = Pt(8)
        p.font.bold = True if "Verdict" in stp else False
        p.font.color.rgb = col if "Verdict" in stp else C_TEXT_BODY
        p.space_before = Pt(4)
    sx += sw + 0.35

print("Slide 11 generated: Transactions")

# -----------------------------------------------------------------------------
# SLIDE 12: QUERY HISTORY & IMMUTABLE AUDIT TRAILS
# -----------------------------------------------------------------------------
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Audit & Compliance", "Regulatory Audit Traceability & Database Immutability", "Enforces regulatory compliance through immutable audit trails protected by database-level security triggers", 12)

add_panel(s12, 0.6, 1.4, 5.8, 5.4, "Immutable Audit Trail Architecture", "AUDIT LEDGER")
tb = s12.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
audit_points = [
    ("Chronological Traceability", "Every administrative action—scans, repairs, rollbacks, data ingestion, and rule modifications—is captured in audit_logs with exact timestamps and actors."),
    ("Sanitized Before/After State JSON", "Captures complete row state snapshots before and after modification, automatically redacting sensitive keywords (passwords, tokens, hashes)."),
    ("Correlation Identifiers", "Links each audit event to related_scan_id, related_issue_id, and related_transaction_id for end-to-end non-repudiation."),
    ("Transaction Monitoring (transaction_logs)", "Records transaction durations (ms), operation counts, and rollback failure reasons for latency analysis."),
    ("Point-in-Time Checkpoints (recovery_checkpoints)", "Stores table structure DDL and JSON rows snapshots for instant reversible rollbacks.")
]
for i, (title, desc) in enumerate(audit_points):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {title}: {desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(5)

add_panel(s12, 6.7, 1.4, 6.033, 5.4, "Database-Level Security Triggers (02_create_tables.sql)", "SQL IMMUTABILITY")

add_code_panel(s12, 6.9, 2.05, 5.633, 2.3, "TRIGGER 1: PREVENTS AUDIT RECORD UPDATES", [
    "CREATE TRIGGER `trg_audit_logs_no_update`",
    "BEFORE UPDATE ON `audit_logs` FOR EACH ROW",
    "BEGIN",
    "    SIGNAL SQLSTATE '45000'",
    "    SET MESSAGE_TEXT = 'Security Policy Violation: ",
    "        Audit log records are immutable and cannot be modified.';",
    "END;"
])

add_code_panel(s12, 6.9, 4.5, 5.633, 2.15, "TRIGGER 2: PREVENTS AUDIT RECORD DELETIONS", [
    "CREATE TRIGGER `trg_audit_logs_no_delete`",
    "BEFORE DELETE ON `audit_logs` FOR EACH ROW",
    "BEGIN",
    "    SIGNAL SQLSTATE '45000'",
    "    SET MESSAGE_TEXT = 'Security Policy Violation: ",
    "        Audit log records are immutable and cannot be deleted.';",
    "END;"
])

print("Slide 12 generated: Audit")

# -----------------------------------------------------------------------------
# SLIDE 13: END-TO-END EXECUTION WALKTHROUGH
# -----------------------------------------------------------------------------
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "System Demonstration", "Complete End-to-End System Walkthrough", "Live demonstration lifecycle: Ingesting an invalid record, isolating to quarantine, scanning, and executing an atomic repair", 13)

flow_steps = [
    ("Step 1: External Submission", "DATA INGESTION", C_PRIMARY, [
        "User opens /ingestion.",
        "Submits enrollment with student_id = 9999 (non-existent parent student).",
        "Generates batch tracking ref EXT-8891."
    ]),
    ("Step 2: Staging & Quarantine", "FAULT ISOLATION", C_RED, [
        "IngestionService probes parent: SELECT COUNT(*) FROM students...",
        "Count = 0 (Orphan detected!).",
        "Row isolated to quarantine_records.",
        "Staging marked REJECTED."
    ]),
    ("Step 3: Scanner Detection", "INTEGRITY SCANNER", C_AMBER, [
        "Admin executes scan on /scanner.",
        "Scanner runs LEFT JOIN query.",
        "Flags production orphan enrollment_id = 203.",
        "Inserts CRITICAL issue into integrity_issues."
    ]),
    ("Step 4: Preview & Mapping", "RECOVERY COCKPIT", C_PRIMARY, [
        "Admin opens /recovery preview modal.",
        "Calculates SHA-256 state token.",
        "Evaluates blast radius: 0 dependencies.",
        "Admin selects verified parent: student_id = 101."
    ]),
    ("Step 5: Atomic Healing", "INNODB COMMIT", C_EMERALD, [
        "START TRANSACTION;",
        "Locks row FOR UPDATE, checks OCC token.",
        "Executes UPDATE enrollments SET student_id=101.",
        "Verifies state, updates issue, COMMIT;",
        "Audit log written; 100% integrity restored!"
    ])
]

fx = 0.6
fw = 2.25
for title, badge, col, lines in flow_steps:
    add_panel(s13, fx, 1.4, fw, 5.4, title, badge)
    tb = s13.shapes.add_textbox(Inches(fx + 0.1), Inches(2.0), Inches(fw - 0.2), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, l in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {l}"
        p.font.name = FONT_BODY
        p.font.size = Pt(8)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(5)
    fx += fw + 0.2

print("Slide 13 generated: Walkthrough")

# -----------------------------------------------------------------------------
# SLIDE 14: CONCLUSION & EVALUATOR VIVA VOCE DEFENSE
# -----------------------------------------------------------------------------
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Viva Voce Defense", "Examiner Q&A Defense & Project Summary", "Core theoretical DBMS principles implemented in the codebase ready for examination defense", 14)

viva_cards = [
    ("1. Referential & Entity Integrity", "PHYSICAL ENFORCEMENT", [
        "Q: How does your system enforce foreign keys without breaking?",
        "A: Physical foreign keys enforce integrity at the engine level.",
        "When batch imports introduce anomalies, the scanner detects orphans via LEFT JOIN and heals them using MAP_PARENT or QUARANTINE without disabling database constraints."
    ]),
    ("2. True ACID Atomicity", "TRANSACTION SAFETY", [
        "Q: Where is Atomicity implemented in your Python code?",
        "A: In repair_engine.py:execute_repair(). It initiates an explicit transaction (conn.begin()), executes the SQL, and commits (conn.commit()).",
        "If any constraint or verification fails, conn.rollback() restores the exact pre-repair image."
    ]),
    ("3. Optimistic Concurrency (OCC)", "LOST UPDATE DEFENSE", [
        "Q: Why use SHA-256 hashing instead of long-lived locks?",
        "A: Long-lived row locks freeze database tables during human inspection.",
        "We compute a deterministic SHA-256 row-version hash during preview. At execution, we re-verify the hash under a brief lock; any discrepancy aborts stale writes."
    ]),
    ("4. Zero Data Loss Architecture", "STAGING & QUARANTINE", [
        "Q: Why use separate staging and quarantine tables?",
        "A: Staging buffers absorb unverified external data feeds without crashing.",
        "Quarantine tables preserve corrupt records as JSON snapshots for administrative review rather than terminating batch pipelines."
    ])
]

coords_viva = [(0.6, 1.4), (6.8, 1.4), (0.6, 4.2), (6.8, 4.2)]
for idx, (title, badge, qa_lines) in enumerate(viva_cards):
    cx, cy = coords_viva[idx]
    add_panel(s14, cx, cy, 5.9, 2.65, title, badge)
    tb = s14.shapes.add_textbox(Inches(cx + 0.15), Inches(cy + 0.55), Inches(5.6), Inches(1.95))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, l in enumerate(qa_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = l
        p.font.name = FONT_BODY
        p.font.size = Pt(8)
        p.font.bold = True if "Q:" in l else False
        p.font.color.rgb = C_PRIMARY if "Q:" in l else C_TEXT_BODY
        p.space_before = Pt(2)

print("Slide 14 generated: Viva Voce")

# Save Presentation
final_pptx_path = os.path.abspath(OUTPUT_PPTX)
prs.save(final_pptx_path)
print(f"\n[SUCCESS] Master presentation saved to: {final_pptx_path}")
print(f"File Size: {os.path.getsize(final_pptx_path):,} bytes ({round(os.path.getsize(final_pptx_path)/1024, 1)} KB)")
print("Total Slides: 14")
