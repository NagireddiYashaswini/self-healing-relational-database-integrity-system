# -*- coding: utf-8 -*-
"""
Master Academic PDF Document Builder
Self-Healing Relational Database Integrity System
Compiles all 14 chapters, styles, and SVG diagrams into DBMS_COMPLETE_PROJECT_EXPLANATION_AND_VIVA_GUIDE.pdf
"""

import os
import sys
import subprocess
import fitz  # PyMuPDF

from pdf_styles import CSS_STYLES
from pdf_ch1_to_4 import CH1_HTML, CH2_HTML, CH3_HTML, CH4_HTML
from pdf_ch5_to_9 import CH5_HTML, CH6_HTML, CH7_HTML, CH8_HTML, CH9_HTML
from pdf_ch10_to_14 import CH10_HTML, CH11_HTML, CH12_HTML, CH13_HTML, CH14_HTML

EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_PDF = "DBMS_COMPLETE_PROJECT_EXPLANATION_AND_VIVA_GUIDE.pdf"
TEMP_HTML = "temp_doc_render.html"
TEMP_RAW_PDF = "temp_raw_render.pdf"

COVER_PAGE_HTML = """
<div class="cover-page">
  <div class="cover-header">
    <div class="cover-institution">Department of Computer Science & Engineering</div>
    <div class="cover-department">Database Management Systems Laboratory & Group Project Evaluation</div>
  </div>

  <div class="cover-body">
    <div class="cover-title">SELF-HEALING RELATIONAL DATABASE INTEGRITY SYSTEM</div>
    <div class="cover-subtitle">
      Comprehensive System Architecture, Page-by-Page Frontend Diagnostics, Backend Service Engineering, Transactional Self-Healing Mechanics, and Evaluator Viva Voce Preparation Guide
    </div>

    <div class="cover-badges">
      <span class="cover-badge">MySQL / MariaDB (XAMPP :3306)</span>
      <span class="cover-badge">InnoDB ACID Engine</span>
      <span class="cover-badge">FastAPI (Python 3.13)</span>
      <span class="cover-badge">React 18 + Vite SPA</span>
      <span class="cover-badge">NetworkX Relational DAG</span>
      <span class="cover-badge">Optimistic Concurrency Control (OCC)</span>
      <span class="cover-badge">Immutable Audit Triggers</span>
      <span class="cover-badge">Version 2.4.0</span>
    </div>
  </div>

  <div class="cover-meta">
    <div class="cover-meta-grid">
      <div class="cover-meta-label">Project Type:</div>
      <div class="cover-meta-val">Academic DBMS Group Project Demonstration & Viva</div>

      <div class="cover-meta-label">Target Database:</div>
      <div class="cover-meta-val">self_healing_test_db (22 Managed InnoDB Tables)</div>

      <div class="cover-meta-label">Relational Scope:</div>
      <div class="cover-meta-val">Business Domain, Staging Buffers, Quarantine Zone, Audit Trails</div>

      <div class="cover-meta-label">Documentation Date:</div>
      <div class="cover-meta-val">Academic Year 2026 - Comprehensive Master Edition</div>

      <div class="cover-meta-label">Execution Status:</div>
      <div class="cover-meta-val">Fully Operational on http://localhost:5173 / API :8000</div>
    </div>
  </div>
</div>
"""

TOC_HTML = """
<div class="page-break">
  <h1>Table of Contents</h1>
  <ul class="toc-list">
    <li class="toc-item"><span class="toc-title">Chapter 1: System Overview & Complete Architecture</span><span>3</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">1.1 Four-Tier Architecture Model</span><span>3</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">1.2 End-to-End Request-Response Execution Lifecycle</span><span>4</span></li>
    
    <li class="toc-item"><span class="toc-title">Chapter 2: Database Schema & Relational Modeling (22 Tables)</span><span>5</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">2.1 Tier 1: Business Domain Schema (6 InnoDB Tables)</span><span>5</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">2.2 Tier 2: Staging & Quarantine Schema (7 InnoDB Tables)</span><span>6</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">2.3 Tier 3: System Engine & Repair Schema (5 InnoDB Tables)</span><span>6</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">2.4 Tier 4: Audit Trails & Immutable Logs (4 InnoDB Tables)</span><span>6</span></li>

    <li class="toc-item"><span class="toc-title">Chapter 3: Page-by-Page Source-Code Deep Dive (All 11 Pages)</span><span>7</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.1 Dashboard (DashboardPage.jsx)</span><span>7</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.2 Database Schema & Object Explorer (DatabaseExplorerPage.jsx)</span><span>8</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.3 Integrity Scanner (IntegrityScannerPage.jsx)</span><span>8</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.4 Recovery & Self-Healing Center (RecoveryCenterPage.jsx)</span><span>9</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.5 Relational Dependency & Topology Analyzer (DependencyVisualizerPage.jsx)</span><span>10</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.6 Data Ingestion & Staging Pipeline (DataIngestionPage.jsx)</span><span>11</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.7 Transaction & Rollback Simulator (TransactionSimulatorPage.jsx)</span><span>11</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.8 Query History & Audit Logs (AuditLogsPage.jsx)</span><span>12</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.9 Rules Configuration Catalog (RulesConfigurationPage.jsx)</span><span>12</span></li>
    <li class="toc-item toc-sub"><span class="toc-title">3.10 System Configuration & Maintenance (SettingsPage.jsx)</span><span>13</span></li>

    <li class="toc-item"><span class="toc-title">Chapter 4: Button-by-Button Master Execution Flow</span><span>13</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 5: Backend Architecture & Service Layer Breakdown</span><span>14</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 6: Data Ingestion & Multi-Stage ETL Pipeline</span><span>15</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 7: Integrity Scanner & Rule Configuration Catalog</span><span>16</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 8: Recovery Center, Repair Engine & Optimistic Concurrency</span><span>17</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 9: Transaction Management & ACID Concurrency Control</span><span>18</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 10: Query History, Audit Logs & Immutability Triggers</span><span>19</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 11: Consolidated SQL Execution Layer</span><span>20</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 12: End-to-End System Workflow Walkthrough</span><span>21</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 13: Comprehensive DBMS Viva Voce Preparation (Evaluator Q&A)</span><span>22</span></li>
    <li class="toc-item"><span class="toc-title">Chapter 14: System Mapping & Verification Tables</span><span>24</span></li>
  </ul>
</div>
"""

def generate_pdf():
    print("[1/4] Assembling full HTML document...")
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DBMS Complete Project Explanation & Viva Guide</title>
  <style>
    {CSS_STYLES}
  </style>
</head>
<body>
  {COVER_PAGE_HTML}
  {TOC_HTML}
  {CH1_HTML}
  {CH2_HTML}
  {CH3_HTML}
  {CH4_HTML}
  {CH5_HTML}
  {CH6_HTML}
  {CH7_HTML}
  {CH8_HTML}
  {CH9_HTML}
  {CH10_HTML}
  {CH11_HTML}
  {CH12_HTML}
  {CH13_HTML}
  {CH14_HTML}
</body>
</html>
"""

    html_path = os.path.abspath(TEMP_HTML)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"      Written {len(full_html):,} bytes to {TEMP_HTML}")

    print("[2/4] Rendering HTML to raw PDF via Headless Edge...")
    raw_pdf_path = os.path.abspath(TEMP_RAW_PDF)
    cmd = [
        EDGE_EXE,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={raw_pdf_path}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(raw_pdf_path):
        print(f"Error rendering PDF: Return code {res.returncode}")
        print("Stderr:", res.stderr)
        sys.exit(1)
    print(f"      Raw PDF generated: {os.path.getsize(raw_pdf_path):,} bytes")

    print("[3/4] Post-processing PDF with PyMuPDF (Headers, Footers, Bookmarks)...")
    doc = fitz.open(raw_pdf_path)
    total_pages = len(doc)
    print(f"      Total document pages: {total_pages}")

    # Add Running Header and Footer on all pages after Cover Page (page index 0)
    for p_idx in range(1, total_pages):
        page = doc[p_idx]
        w = page.rect.width
        h = page.rect.height

        # Running Top Header
        page.insert_text(
            (45, 30),
            "Self-Healing Relational Database Integrity System | Project Documentation & Viva Guide",
            fontsize=7.5,
            color=(0.4, 0.45, 0.5)
        )
        page.draw_line((45, 36), (w - 45, 36), color=(0.8, 0.85, 0.9), width=0.5)

        # Running Bottom Footer
        page.draw_line((45, h - 34), (w - 45, h - 34), color=(0.8, 0.85, 0.9), width=0.5)
        page.insert_text(
            (45, h - 22),
            "Academic Group Project - DBMS Laboratory Evaluation",
            fontsize=7.5,
            color=(0.4, 0.45, 0.5)
        )
        page_str = f"Page {p_idx + 1} of {total_pages}"
        page.insert_text(
            (w - 45 - (len(page_str) * 4.5), h - 22),
            page_str,
            fontsize=7.5,
            color=(0.3, 0.35, 0.4)
        )

    # Dynamic Bookmark Discovery
    # Find exact page for each section based on text search in doc
    def find_page_for_text(query, default_page):
        for i, page in enumerate(doc):
            if query.lower() in page.get_text().lower():
                return i + 1
        return default_page

    p_cov = 1
    p_toc = find_page_for_text("Table of Contents", 2)
    p_ch1 = find_page_for_text("Chapter 1: System Overview", 3)
    p_ch2 = find_page_for_text("Chapter 2: Database Schema", 5)
    p_ch3 = find_page_for_text("Chapter 3: Page-by-Page", 7)
    p_ch4 = find_page_for_text("Chapter 4: Button-by-Button", 13)
    p_ch5 = find_page_for_text("Chapter 5: Backend Architecture", 14)
    p_ch6 = find_page_for_text("Chapter 6: Data Ingestion", 15)
    p_ch7 = find_page_for_text("Chapter 7: Integrity Scanner", 16)
    p_ch8 = find_page_for_text("Chapter 8: Recovery Center", 17)
    p_ch9 = find_page_for_text("Chapter 9: Transaction Management", 18)
    p_ch10 = find_page_for_text("Chapter 10: Query History", 19)
    p_ch11 = find_page_for_text("Chapter 11: Consolidated SQL", 20)
    p_ch12 = find_page_for_text("Chapter 12: End-to-End System", 21)
    p_ch13 = find_page_for_text("Chapter 13: Comprehensive DBMS", 22)
    p_ch14 = find_page_for_text("Chapter 14: System Mapping", 24)

    # Set PDF Table of Contents (Hierarchical PDF Outline Bookmarks)
    toc = [
        [1, "Title & Cover Page", p_cov],
        [1, "Table of Contents", p_toc],
        [1, "Chapter 1: System Overview & Complete Architecture", p_ch1],
        [1, "Chapter 2: Database Schema & Relational Modeling (22 Tables)", p_ch2],
        [1, "Chapter 3: Page-by-Page Source-Code Deep Dive (All 11 Pages)", p_ch3],
        [1, "Chapter 4: Button-by-Button Master Execution Flow", p_ch4],
        [1, "Chapter 5: Backend Architecture & Service Layer Breakdown", p_ch5],
        [1, "Chapter 6: Data Ingestion & Multi-Stage ETL Pipeline", p_ch6],
        [1, "Chapter 7: Integrity Scanner & Rule Configuration Catalog", p_ch7],
        [1, "Chapter 8: Recovery Center, Repair Engine & Optimistic Concurrency", p_ch8],
        [1, "Chapter 9: Transaction Management & ACID Concurrency Control", p_ch9],
        [1, "Chapter 10: Query History, Audit Logs & Immutability Triggers", p_ch10],
        [1, "Chapter 11: Consolidated SQL Execution Layer", p_ch11],
        [1, "Chapter 12: End-to-End System Workflow Walkthrough", p_ch12],
        [1, "Chapter 13: Comprehensive DBMS Viva Voce Preparation (Evaluator Q&A)", p_ch13],
        [1, "Chapter 14: System Mapping & Verification Tables", p_ch14]
    ]

    doc.set_toc(toc)

    final_pdf_path = os.path.abspath(OUTPUT_PDF)
    doc.save(final_pdf_path, garbage=4, deflate=True)
    doc.close()

    # Clean up temp files
    if os.path.exists(TEMP_HTML): os.remove(TEMP_HTML)
    if os.path.exists(TEMP_RAW_PDF): os.remove(TEMP_RAW_PDF)

    print("[4/4] SUCCESS! Master PDF compiled successfully.")
    print(f"      Final PDF Output: {final_pdf_path}")
    print(f"      File Size: {os.path.getsize(final_pdf_path):,} bytes ({round(os.path.getsize(final_pdf_path)/1024/1024, 2)} MB)")
    print(f"      Total Pages: {total_pages}")

if __name__ == "__main__":
    generate_pdf()
