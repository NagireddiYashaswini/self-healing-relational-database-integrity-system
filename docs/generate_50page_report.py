#!/usr/bin/env python3
"""
Comprehensive 50-Page Academic & Technical Project Report Generator
Generates both:
  1. docs/SELF_HEALING_DBMS_COMPLETE_PROJECT_REPORT.docx (Microsoft Word)
  2. docs/SELF_HEALING_DBMS_COMPLETE_PROJECT_REPORT.pdf  (Print-ready PDF)

Covers all 20 chapters from kid-friendly analogies to deep relational algebra,
NetworkX graph theory, ACID engine internals, SQL queries, and complete schema dictionaries.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ReportLab Imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# python-docx Imports
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_DIR = Path(__file__).resolve().parent
DOCX_PATH = OUTPUT_DIR / "SELF_HEALING_DBMS_COMPLETE_PROJECT_REPORT.docx"
PDF_PATH = OUTPUT_DIR / "SELF_HEALING_DBMS_COMPLETE_PROJECT_REPORT.pdf"

print("Starting generation of comprehensive 50-page report...")
print(f"Destination DOCX: {DOCX_PATH}")
print(f"Destination PDF : {PDF_PATH}")

# -----------------------------------------------------------------------------
# Numbered Canvas for Two-Pass Dynamic Page Numbering in ReportLab
# -----------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:  # Skip headers/footers on title/cover page
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            # Running Header
            self.drawString(54, 755, "SELF-HEALING RELATIONAL DATABASE INTEGRITY SYSTEM")
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 755, "Comprehensive Engineering Project Report (v2.4.0)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(54, 748, 558, 748)
            
            # Running Footer
            self.line(54, 45, 558, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(54, 32, "Confidential — DBMS Group Final Submission | MySQL InnoDB + FastAPI + React")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_text)
            self.restoreState()

# Include full chapters definition module
import report_content

print("Building PDF with ReportLab...")
report_content.build_pdf(PDF_PATH, NumberedCanvas)

print("Building DOCX with python-docx...")
report_content.build_docx(DOCX_PATH)

import fitz
doc_pdf = fitz.open(PDF_PATH)
print("=" * 60)
print(f"[SUCCESS] PDF generated successfully! Page count: {len(doc_pdf)} pages")
print(f"[SUCCESS] DOCX generated successfully! Size: {os.path.getsize(DOCX_PATH) / 1024:.1f} KB")
print("=" * 60)
