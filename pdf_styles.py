# -*- coding: utf-8 -*-
"""CSS Styling and Layout Configuration for Academic DBMS Project PDF"""

CSS_STYLES = """
@page {
    size: A4 portrait;
    margin: 20mm 16mm 22mm 16mm;
}

@page :first {
    margin: 0;
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
}

/* Page Break Management */
.page-break {
    page-break-before: always;
}

.avoid-break {
    page-break-inside: avoid;
}

h1, h2, h3, h4, h5 {
    color: #0f172a;
    page-break-after: avoid;
    font-weight: 700;
}

h1 {
    font-size: 20pt;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 6px;
    margin-top: 24pt;
    margin-bottom: 14pt;
    color: #1e3a8a;
}

h2 {
    font-size: 14pt;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 18pt;
    margin-bottom: 10pt;
    color: #1e40af;
}

h3 {
    font-size: 11.5pt;
    margin-top: 14pt;
    margin-bottom: 6pt;
    color: #334155;
}

h4 {
    font-size: 10.5pt;
    margin-top: 10pt;
    margin-bottom: 4pt;
    color: #475569;
}

p {
    margin-top: 0;
    margin-bottom: 8pt;
    text-align: justify;
}

/* Cover Page */
.cover-page {
    width: 100vw;
    height: 100vh;
    padding: 60px 50px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #172554 100%);
    color: #ffffff;
    page-break-after: always;
}

.cover-header {
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 20px;
}

.cover-institution {
    font-size: 12pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #93c5fd;
    margin-bottom: 6px;
}

.cover-department {
    font-size: 10pt;
    color: #cbd5e1;
}

.cover-body {
    margin-top: 40px;
    margin-bottom: 40px;
}

.cover-title {
    font-size: 26pt;
    font-weight: 800;
    line-height: 1.2;
    color: #ffffff;
    margin-bottom: 16px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.4);
}

.cover-subtitle {
    font-size: 13pt;
    font-weight: 400;
    color: #93c5fd;
    line-height: 1.5;
    margin-bottom: 24px;
}

.cover-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 20px;
}

.cover-badge {
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 8.5pt;
    font-family: 'Cascadia Code', Consolas, monospace;
    color: #e2e8f0;
}

.cover-meta {
    background-color: rgba(15, 23, 42, 0.6);
    border-left: 4px solid #3b82f6;
    padding: 16px 20px;
    border-radius: 0 6px 6px 0;
}

.cover-meta-grid {
    display: grid;
    grid-template-columns: 140px 1fr;
    gap: 8px;
    font-size: 9.5pt;
}

.cover-meta-label {
    color: #94a3b8;
    font-weight: 600;
}

.cover-meta-val {
    color: #f8fafc;
    font-weight: 500;
}

/* Callout Boxes */
.callout {
    border-left: 4px solid #3b82f6;
    background-color: #f8fafc;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    margin: 12pt 0;
    border: 1px solid #e2e8f0;
    border-left-width: 4px;
}

.callout-info { border-left-color: #3b82f6; background-color: #eff6ff; }
.callout-success { border-left-color: #10b981; background-color: #f0fdf4; }
.callout-warning { border-left-color: #f59e0b; background-color: #fffbeb; }
.callout-danger { border-left-color: #ef4444; background-color: #fef2f2; }

.callout-title {
    font-weight: 700;
    font-size: 9.5pt;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.callout-info .callout-title { color: #1e40af; }
.callout-success .callout-title { color: #065f46; }
.callout-warning .callout-title { color: #92400e; }
.callout-danger .callout-title { color: #991b1b; }

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 8.5pt;
}

th, td {
    padding: 6px 8px;
    text-align: left;
    border: 1px solid #cbd5e1;
    vertical-align: top;
}

th {
    background-color: #1e293b;
    color: #ffffff;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 8pt;
    letter-spacing: 0.5px;
}

tr:nth-child(even) {
    background-color: #f8fafc;
}

/* Code Blocks */
pre, code {
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
}

code {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 8.5pt;
    border: 1px solid #e2e8f0;
}

pre {
    background-color: #0f172a;
    color: #e2e8f0;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 8.5pt;
    line-height: 1.45;
    overflow-x: auto;
    margin: 10pt 0;
    border: 1px solid #334155;
    page-break-inside: avoid;
}

pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
}

/* Syntax Highlighting Tokens in Pre */
.kw { color: #38bdf8; font-weight: bold; }       /* Keywords (SELECT, FROM, etc.) */
.fn { color: #818cf8; font-weight: 600; }        /* Functions */
.str { color: #34d399; }                         /* Strings */
.num { color: #fbbf24; }                         /* Numbers */
.cmt { color: #64748b; font-style: italic; }     /* Comments */
.tbl { color: #f472b6; font-weight: 600; }       /* Table Names */

/* Badges */
.badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.badge-critical { background-color: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
.badge-high { background-color: #ffedd5; color: #9a3412; border: 1px solid #fb923c; }
.badge-medium { background-color: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.badge-low { background-color: #e0f2fe; color: #075985; border: 1px solid #7dd3fc; }
.badge-success { background-color: #dcfce7; color: #166534; border: 1px solid #86efac; }
.badge-neutral { background-color: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }

/* Table of Contents */
.toc-list {
    list-style: none;
    padding: 0;
    margin: 16pt 0;
}

.toc-item {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 9.5pt;
}

.toc-title {
    font-weight: 600;
    color: #1e3a8a;
}

.toc-sub {
    padding-left: 20px;
    font-size: 9pt;
}

.toc-sub .toc-title {
    font-weight: normal;
    color: #334155;
}

/* Diagram Container */
.diagram-box {
    margin: 14pt 0;
    padding: 12pt;
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    text-align: center;
    page-break-inside: avoid;
}

.diagram-caption {
    font-size: 8.5pt;
    font-weight: 600;
    color: #475569;
    margin-top: 8px;
    text-align: center;
}
"""
