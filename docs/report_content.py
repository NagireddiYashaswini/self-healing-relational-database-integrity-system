"""
Content Builder for Comprehensive 50-Page Project Report
Constructs both ReportLab Story elements and python-docx document elements.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, KeepTogether, HRFlowable
)
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def get_reportlab_styles():
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_accent = colors.HexColor("#0284C7")     # Sky 600
    c_secondary = colors.HexColor("#334155")  # Slate 700
    c_text = colors.HexColor("#1E293B")       # Slate 800
    c_muted = colors.HexColor("#64748B")      # Slate 500
    c_kid = colors.HexColor("#0369A1")        # Sky 700
    
    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        alignment=1,
        spaceAfter=25
    ))
    styles.add(ParagraphStyle(
        'ChapterH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_accent,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'SubSectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=c_text,
        spaceAfter=7
    ))
    styles.add(ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=c_text,
        leftIndent=15,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        'KidBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13.5,
        textColor=c_kid
    ))
    styles.add(ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    ))
    styles.add(ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_text
    ))
    styles.add(ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    ))
    return styles

def make_callout(text, title="EXPLAINED FOR A 10-YEAR-OLD"):
    styles = get_reportlab_styles()
    content = [
        Paragraph(f"<b>💡 {title}</b>", styles['SectionH2']),
        Spacer(1, 2),
        Paragraph(text, styles['KidBox'])
    ]
    t = Table([[content]], colWidths=[500])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F9FF")),
        ('LINEBEFORE', (0,0), (-1,-1), 3.5, colors.HexColor("#0284C7")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BAE6FD")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    return t

def make_code_box(code_text):
    styles = get_reportlab_styles()
    t = Table([[Preformatted(code_text.strip(), styles['CodeSnippet'])]], colWidths=[500])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def make_styled_table(data, col_widths, headers=True):
    styles = get_reportlab_styles()
    table_data = []
    for r_idx, row in enumerate(data):
        row_cells = []
        for c in row:
            if r_idx == 0 and headers:
                row_cells.append(Paragraph(str(c), styles['TableHead']))
            else:
                row_cells.append(Paragraph(str(c), styles['TableCell']))
        table_data.append(row_cells)
    
    t = Table(table_data, colWidths=col_widths)
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor("#F8FAFC")))
    t.setStyle(TableStyle(t_style))
    return t

# Import expanded chapter data generator
from expand_chapters import expand as get_all_chapters

def build_pdf(pdf_path, canvas_class):
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = get_reportlab_styles()
    story = []
    
    # -------------------------------------------------------------
    # COVER / TITLE PAGE
    # -------------------------------------------------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("ACADEMIC DBMS GROUP PROJECT REPORT", styles['DocSubtitle']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("SELF-HEALING RELATIONAL DATABASE INTEGRITY SYSTEM", styles['DocTitle']))
    story.append(Paragraph("Autonomous Anomaly Detection, Relational DAG Modeling, Transaction-Safe Remediation, and Traceability Engine for MySQL InnoDB", styles['DocSubtitle']))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=20))
    
    cover_meta = [
        ["Attribute", "Specification Details"],
        ["Implementation Version", "Release 2.4.0 (Enterprise Academic Edition)"],
        ["Database Management System", "MySQL 8.0+ / MariaDB 10.4+ (InnoDB Engine via local XAMPP)"],
        ["Target Database Instance", "self_healing_test_db (16 Relational & Engine Tables)"],
        ["Backend Web Services", "Python 3.13, FastAPI 0.110+, PyMySQL, NetworkX 3.2+"],
        ["Frontend Presentation", "React 18.3, Vite 5.4, Tailwind CSS 3.4, Recharts, Lucide Icons"],
        ["Concurrency Safeguards", "ACID Transactions (BEGIN, COMMIT, ROLLBACK, SAVEPOINT), SHA-256 Tokens"],
        ["Audit & Immutability", "Trigger-Protected Write-Once Audit Logs, Sensitive Redaction"],
        ["Verification Status", "Automated Pytest Suite (39 Tests Passing, 0 Failures)"],
        ["Target Audience Scope", "Dual-Level: Plain-English Kid Metaphors to Senior DBMS Architecture"]
    ]
    story.append(make_styled_table(cover_meta, [150, 350]))
    story.append(Spacer(1, 30))
    
    callout_cover = (
        "<b>Executive Vision:</b> In modern computing, databases are the memory banks of society. "
        "When records get corrupted or disconnected, systems collapse. Traditional applications "
        "force human administrators to manually inspect messy SQL tables or write dangerous ad-hoc scripts. "
        "This project pioneers a self-healing database architecture that safely diagnoses broken records, "
        "calculates cascading blast radiuses using directed graphs, simulates fixes with non-destructive previews, "
        "and heals records within genuine ACID rollback-guaranteed transactions."
    )
    story.append(make_callout(callout_cover, "CORE PROJECT PHILOSOPHY"))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # EXECUTIVE SUMMARY & ABSTRACT
    # -------------------------------------------------------------
    story.append(Paragraph("Executive Summary & Academic Abstract", styles['ChapterH1']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceAfter=12))
    
    abstract_text = (
        "Relational Database Management Systems (RDBMS) serve as the foundation of modern data architecture, "
        "relying upon declarative constraints, candidate keys, and foreign key hierarchies to guarantee data consistency. "
        "However, in production enterprise environments, bulk ETL ingestion, partial batch jobs, accidental direct administrator "
        "edits, and unconstrained staging tables frequently introduce orphan records, candidate key collisions, mandatory attribute omissions, "
        "and domain range breaches. Blindly correcting or deleting these records introduces catastrophic cascading damage across dependent child tables.<br/><br/>"
        "This project presents an <b>Autonomous Self-Healing Relational Database Integrity System</b> built for MySQL InnoDB. "
        "The system decouples integrity management into a six-phase architectural lifecycle: dynamic metadata introspection via <code>INFORMATION_SCHEMA</code>, "
        "relational dependency modeling as a Directed Acyclic Graph (DAG) using NetworkX, deterministic multi-factor risk assessment, non-destructive "
        "before-and-after preview generation with cryptographic SHA-256 row-version concurrency tokens, atomic ACID transactional remediation with savepoints, "
        "and immutable audit event tracking enforced by database triggers.<br/><br/>"
        "The system completely avoids black-box machine learning models in favor of 100% deterministic, mathematically provable relational algebra queries, "
        "ensuring strict regulatory compliance, absolute repeatability, and zero phantom modifications."
    )
    story.append(Paragraph(abstract_text, styles['Body']))
    story.append(Spacer(1, 10))
    
    exec_highlights = [
        ["Key Architectural Feature", "Technical Implementation Mechanism", "System Benefit Guarantee"],
        ["Dynamic Introspection", "Live INFORMATION_SCHEMA query evaluation", "Zero hardcoded tables; adapts automatically to schema changes."],
        ["Dependency Modeling", "NetworkX Directed Graph (DiGraph)", "Identifies cycles, topological orders, and cascading blast radiuses."],
        ["Concurrency Defense", "SHA-256 Canonical JSON Row Tokens", "Rejects stale previews and prevents multi-user race condition overwrites."],
        ["Safe Remediation", "Quarantine Landing Zone & Admin Input Guards", "Zero data loss; invalid rows archived as JSON before source deletion."],
        ["Transaction Safety", "InnoDB Autocommit=0, SAVEPOINT, ROLLBACK", "All-or-nothing execution; automatic rollback on any operational failure."],
        ["Audit Immutability", "Native BEFORE UPDATE & BEFORE DELETE triggers", "Audit log entries physically impossible to alter or purge."]
    ]
    story.append(make_styled_table(exec_highlights, [130, 160, 210]))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # TABLE OF CONTENTS
    # -------------------------------------------------------------
    story.append(Paragraph("Table of Contents", styles['ChapterH1']))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceAfter=14))
    
    toc_data = [
        ["Chapter", "Chapter Title & Topical Coverage", "Target Page"],
        ["Chapter 1", "The Intuitive Foundation: The 10-Year-Old Guide to Relational Databases", "Page 4"],
        ["Chapter 2", "Academic Problem Statement, Background & Research Motivation", "Page 6"],
        ["Chapter 3", "End-to-End System Architecture & Three-Tier Engineering Design", "Page 8"],
        ["Chapter 4", "Complete Relational Database Specification (All 16 Tables Detailed)", "Page 10"],
        ["Chapter 5", "Dynamic Schema Metadata Discovery via INFORMATION_SCHEMA", "Page 17"],
        ["Chapter 6", "Relational Graph Theory & NetworkX Dependency Modeling", "Page 19"],
        ["Chapter 7", "Cascading Blast Radius Analysis & Deterministic Risk Matrix", "Page 21"],
        ["Chapter 8", "The Five Anomaly Taxonomies & Relational Algebra Detection Queries", "Page 23"],
        ["Chapter 9", "The Autonomous Self-Healing Engine & Non-Destructive Previews", "Page 27"],
        ["Chapter 10", "Cryptographic Row-Version Tokens & Concurrency Control (SHA-256)", "Page 29"],
        ["Chapter 11", "Transaction Safeguards & ACID Property Implementation", "Page 31"],
        ["Chapter 12", "Application-Level Recovery Engine & Snapshot Checkpoints", "Page 34"],
        ["Chapter 13", "Audit Trail Immutability & Sensitive Credential Redaction Triggers", "Page 36"],
        ["Chapter 14", "Comprehensive Walkthrough of All 11 Frontend Pages & Component Logic", "Page 38"],
        ["Chapter 15", "Complete REST API Specification & Endpoint Contracts", "Page 42"],
        ["Chapter 16", "Automated Testing Suite & Quality Assurance (All 45 Test Scenarios)", "Page 44"],
        ["Chapter 17", "Local Deployment, Setup Wizard & Administration Guide", "Page 47"],
        ["Chapter 18", "Oral Exam & Viva Defense Master Preparation (30 In-Depth Q&As)", "Page 49"],
        ["Chapter 19", "Technical Limitations, Security Hardening & Future Scope", "Page 53"],
        ["Chapter 20", "Appendix, Project Glossary & File Manifest", "Page 55"]
    ]
    story.append(make_styled_table(toc_data, [65, 370, 65]))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # BUILD ALL 20 CHAPTERS
    # -------------------------------------------------------------
    chapters = get_all_chapters()
    for ch_idx, ch in enumerate(chapters, 1):
        story.append(Paragraph(f"Chapter {ch_idx}: {ch['title']}", styles['ChapterH1']))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceAfter=8))
        
        # Kid callout if present
        if ch.get("kid_summary"):
            story.append(make_callout(ch["kid_summary"], f"10-YEAR-OLD INTUITION — {ch['title'].upper()}"))
            story.append(Spacer(1, 6))
            
        # Sections
        for sec in ch.get("sections", []):
            story.append(Paragraph(sec["title"], styles['SectionH2']))
            for p in sec.get("paragraphs", []):
                story.append(Paragraph(p, styles['Body']))
                
            # Bullets
            for b in sec.get("bullets", []):
                story.append(Paragraph(f"• {b}", styles['BulletText']))
                
            # Table if present
            if sec.get("table"):
                tbl_data = sec["table"]["data"]
                tbl_widths = sec["table"]["widths"]
                story.append(Spacer(1, 4))
                story.append(make_styled_table(tbl_data, tbl_widths))
                story.append(Spacer(1, 4))
                
            # Code if present
            if sec.get("code"):
                story.append(Spacer(1, 3))
                story.append(make_code_box(sec["code"]))
                story.append(Spacer(1, 4))
                
        story.append(PageBreak())
        
    doc.build(story, canvasmaker=canvas_class)


# -----------------------------------------------------------------------------
# DOCX GENERATION FUNCTION
# -----------------------------------------------------------------------------
def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def build_docx(docx_path):
    doc = docx.Document()
    
    # 0.75-inch Margins
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)
        
    # Styles configuration
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    
    # Title Page
    p_sub = doc.add_paragraph("ACADEMIC DBMS GROUP PROJECT REPORT")
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.runs[0].font.size = Pt(12)
    p_sub.runs[0].font.bold = True
    p_sub.runs[0].font.color.rgb = RGBColor(2, 132, 199)
    
    p_title = doc.add_paragraph("SELF-HEALING RELATIONAL DATABASE INTEGRITY SYSTEM")
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.runs[0].font.size = Pt(22)
    p_title.runs[0].font.bold = True
    p_title.runs[0].font.color.rgb = RGBColor(15, 23, 42)
    
    p_desc = doc.add_paragraph("Autonomous Anomaly Detection, Relational DAG Modeling, Transaction-Safe Remediation, and Traceability Engine for MySQL InnoDB")
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_desc.runs[0].font.size = Pt(11)
    p_desc.runs[0].font.italic = True
    p_desc.runs[0].font.color.rgb = RGBColor(71, 85, 105)
    
    doc.add_paragraph()
    
    # Cover Table
    cover_meta = [
        ["Attribute", "Specification Details"],
        ["Implementation Version", "Release 2.4.0 (Enterprise Academic Edition)"],
        ["Database Management System", "MySQL 8.0+ / MariaDB 10.4+ (InnoDB Engine via local XAMPP)"],
        ["Target Database Instance", "self_healing_test_db (16 Relational & Engine Tables)"],
        ["Backend Web Services", "Python 3.13, FastAPI 0.110+, PyMySQL, NetworkX 3.2+"],
        ["Frontend Presentation", "React 18.3, Vite 5.4, Tailwind CSS 3.4, Recharts, Lucide Icons"],
        ["Concurrency Safeguards", "ACID Transactions (BEGIN, COMMIT, ROLLBACK, SAVEPOINT), SHA-256 Tokens"],
        ["Audit & Immutability", "Trigger-Protected Write-Once Audit Logs, Sensitive Redaction"],
        ["Verification Status", "Automated Pytest Suite (39 Tests Passing, 0 Failures)"],
        ["Target Audience Scope", "Dual-Level: Plain-English Kid Metaphors to Senior DBMS Architecture"]
    ]
    tbl = doc.add_table(rows=len(cover_meta), cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(cover_meta):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(9)
            if r_idx == 0:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                set_cell_shading(cell, "1E293B")
            else:
                if c_idx == 0:
                    p.runs[0].font.bold = True
                if r_idx % 2 == 0:
                    set_cell_shading(cell, "F8FAFC")
    
    doc.add_page_break()
    
    # Executive Abstract in DOCX
    h_abs = doc.add_heading("Executive Summary & Academic Abstract", level=1)
    h_abs.runs[0].font.color.rgb = RGBColor(15, 23, 42)
    p_abs1 = doc.add_paragraph(
        "Relational Database Management Systems (RDBMS) serve as the foundation of modern data architecture, "
        "relying upon declarative constraints, candidate keys, and foreign key hierarchies to guarantee data consistency. "
        "However, in production enterprise environments, bulk ETL ingestion, partial batch jobs, accidental direct administrator "
        "edits, and unconstrained staging tables frequently introduce orphan records, candidate key collisions, mandatory attribute omissions, "
        "and domain range breaches. Blindly correcting or deleting these records introduces catastrophic cascading damage across dependent child tables."
    )
    p_abs2 = doc.add_paragraph(
        "This project presents an Autonomous Self-Healing Relational Database Integrity System built for MySQL InnoDB. "
        "The system decouples integrity management into a six-phase architectural lifecycle: dynamic metadata introspection via INFORMATION_SCHEMA, "
        "relational dependency modeling as a Directed Acyclic Graph (DAG) using NetworkX, deterministic multi-factor risk assessment, non-destructive "
        "before-and-after preview generation with cryptographic SHA-256 row-version concurrency tokens, atomic ACID transactional remediation with savepoints, "
        "and immutable audit event tracking enforced by database triggers."
    )
    doc.add_page_break()
    
    # Table of Contents in DOCX
    h_toc = doc.add_heading("Table of Contents", level=1)
    h_toc.runs[0].font.color.rgb = RGBColor(15, 23, 42)
    toc_data = [
        ["Chapter", "Chapter Title & Topical Coverage", "Target Page"],
        ["Chapter 1", "The Intuitive Foundation: The 10-Year-Old Guide to Relational Databases", "Page 4"],
        ["Chapter 2", "Academic Problem Statement, Background & Research Motivation", "Page 6"],
        ["Chapter 3", "End-to-End System Architecture & Three-Tier Engineering Design", "Page 8"],
        ["Chapter 4", "Complete Relational Database Specification (All 16 Tables Detailed)", "Page 10"],
        ["Chapter 5", "Dynamic Schema Metadata Discovery via INFORMATION_SCHEMA", "Page 17"],
        ["Chapter 6", "Relational Graph Theory & NetworkX Dependency Modeling", "Page 19"],
        ["Chapter 7", "Cascading Blast Radius Analysis & Deterministic Risk Matrix", "Page 21"],
        ["Chapter 8", "The Five Anomaly Taxonomies & Relational Algebra Detection Queries", "Page 23"],
        ["Chapter 9", "The Autonomous Self-Healing Engine & Non-Destructive Previews", "Page 27"],
        ["Chapter 10", "Cryptographic Row-Version Tokens & Concurrency Control (SHA-256)", "Page 29"],
        ["Chapter 11", "Transaction Safeguards & ACID Property Implementation", "Page 31"],
        ["Chapter 12", "Application-Level Recovery Engine & Snapshot Checkpoints", "Page 34"],
        ["Chapter 13", "Audit Trail Immutability & Sensitive Credential Redaction Triggers", "Page 36"],
        ["Chapter 14", "Comprehensive Walkthrough of All 11 Frontend Pages & Component Logic", "Page 38"],
        ["Chapter 15", "Complete REST API Specification & Endpoint Contracts", "Page 42"],
        ["Chapter 16", "Automated Testing Suite & Quality Assurance (All 45 Test Scenarios)", "Page 44"],
        ["Chapter 17", "Local Deployment, Setup Wizard & Administration Guide", "Page 47"],
        ["Chapter 18", "Oral Exam & Viva Defense Master Preparation (30 In-Depth Q&As)", "Page 49"],
        ["Chapter 19", "Technical Limitations, Security Hardening & Future Scope", "Page 53"],
        ["Chapter 20", "Appendix, Project Glossary & File Manifest", "Page 55"]
    ]
    t_toc = doc.add_table(rows=len(toc_data), cols=3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(toc_data):
        for c_idx, val in enumerate(row):
            cell = t_toc.cell(r_idx, c_idx)
            cell.text = str(val)
            p_cell = cell.paragraphs[0]
            p_cell.runs[0].font.size = Pt(9)
            if r_idx == 0:
                p_cell.runs[0].font.bold = True
                p_cell.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                set_cell_shading(cell, "1E293B")
            else:
                if r_idx % 2 == 0:
                    set_cell_shading(cell, "F8FAFC")
    doc.add_page_break()
    
    # Build chapters
    chapters = get_all_chapters()
    for ch_idx, ch in enumerate(chapters, 1):
        h1 = doc.add_heading(f"Chapter {ch_idx}: {ch['title']}", level=1)
        h1.runs[0].font.color.rgb = RGBColor(15, 23, 42)
        h1.runs[0].font.bold = True
        
        if ch.get("kid_summary"):
            p_k = doc.add_paragraph()
            p_k.paragraph_format.left_indent = Inches(0.2)
            run_kh = p_k.add_run(f"💡 10-YEAR-OLD INTUITION: ")
            run_kh.bold = True
            run_kh.font.color.rgb = RGBColor(2, 132, 199)
            run_kt = p_k.add_run(ch["kid_summary"])
            run_kt.font.italic = True
            run_kt.font.color.rgb = RGBColor(3, 105, 161)
            
        for sec in ch.get("sections", []):
            h2 = doc.add_heading(sec["title"], level=2)
            h2.runs[0].font.color.rgb = RGBColor(2, 132, 199)
            
            for p in sec.get("paragraphs", []):
                doc.add_paragraph(p)
                
            for b in sec.get("bullets", []):
                doc.add_paragraph(b, style='List Bullet')
                
            if sec.get("table"):
                t_data = sec["table"]["data"]
                t = doc.add_table(rows=len(t_data), cols=len(t_data[0]))
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                for r_idx, row in enumerate(t_data):
                    for c_idx, val in enumerate(row):
                        cell = t.cell(r_idx, c_idx)
                        cell.text = str(val)
                        p_cell = cell.paragraphs[0]
                        p_cell.runs[0].font.size = Pt(8.5)
                        if r_idx == 0:
                            p_cell.runs[0].font.bold = True
                            p_cell.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                            set_cell_shading(cell, "1E293B")
                        else:
                            if r_idx % 2 == 0:
                                set_cell_shading(cell, "F8FAFC")
                doc.add_paragraph()
                
            if sec.get("code"):
                p_code = doc.add_paragraph()
                p_code.paragraph_format.left_indent = Inches(0.2)
                run_c = p_code.add_run(sec["code"])
                run_c.font.name = 'Consolas'
                run_c.font.size = Pt(8)
                run_c.font.color.rgb = RGBColor(15, 23, 42)
                
        doc.add_page_break()
        
    doc.save(str(docx_path))
