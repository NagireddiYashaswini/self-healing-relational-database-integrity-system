# -*- coding: utf-8 -*-
"""Vector SVG Illustrations for Academic DBMS Project PDF"""

SVG_SYSTEM_ARCHITECTURE = """
<svg width="100%" height="280" viewBox="0 0 900 280" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; font-family: 'Segoe UI', Arial, sans-serif;">
  <defs>
    <linearGradient id="gradClient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1d4ed8;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="gradServer" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d9488;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f766e;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="gradDB" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3730a3;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="0" dy="2" />
      <feComponentTransfer><feFuncA type="linear" slope="0.15"/></feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#475569" />
    </marker>
  </defs>

  <!-- Background frame -->
  <rect x="5" y="5" width="890" height="270" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>

  <!-- Tier 1: Presentation (React + Vite) -->
  <g filter="url(#shadow)">
    <rect x="25" y="30" width="220" height="220" rx="6" fill="#ffffff" stroke="#93c5fd" stroke-width="1.5"/>
    <rect x="25" y="30" width="220" height="34" rx="6" fill="url(#gradClient)"/>
    <text x="135" y="52" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">PRESENTATION TIER</text>
    
    <text x="35" y="82" fill="#1e293b" font-size="10" font-weight="bold">React 18 Single-Page App</text>
    <text x="35" y="98" fill="#64748b" font-size="8.5">• 11 Functional Pages</text>
    <text x="35" y="112" fill="#64748b" font-size="8.5">• Lucide UI Icons & Tailwind</text>
    <text x="35" y="126" fill="#64748b" font-size="8.5">• NetworkX Interactive Graph</text>
    <text x="35" y="140" fill="#64748b" font-size="8.5">• Recharts Metrics Visualization</text>
    
    <rect x="35" y="160" width="200" height="42" rx="4" fill="#eff6ff" stroke="#bfdbfe"/>
    <text x="135" y="177" fill="#1e40af" font-size="9" font-weight="bold" text-anchor="middle">Axios HTTP Client</text>
    <text x="135" y="192" fill="#3b82f6" font-size="8" text-anchor="middle">Vite Proxy: /api -> :8000</text>
    <text x="135" y="235" fill="#64748b" font-size="8" text-anchor="middle">Client Port: 5173</text>
  </g>

  <!-- Arrow: Tier 1 to Tier 2 -->
  <line x1="245" y1="140" x2="285" y2="140" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="265" y="132" fill="#475569" font-size="7.5" font-weight="bold" text-anchor="middle">JSON/REST</text>

  <!-- Tier 2: Application (FastAPI Services) -->
  <g filter="url(#shadow)">
    <rect x="290" y="30" width="290" height="220" rx="6" fill="#ffffff" stroke="#99f6e4" stroke-width="1.5"/>
    <rect x="290" y="30" width="290" height="34" rx="6" fill="url(#gradServer)"/>
    <text x="435" y="52" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">APPLICATION / ENGINE TIER</text>
    
    <text x="300" y="80" fill="#0f766e" font-size="10" font-weight="bold">FastAPI 0.110+ (Python 3.13 / Uvicorn)</text>
    
    <!-- Service Blocks -->
    <rect x="300" y="92" width="130" height="32" rx="3" fill="#f0fdfa" stroke="#ccfbf1"/>
    <text x="365" y="105" fill="#0f766e" font-size="8" font-weight="bold" text-anchor="middle">Integrity Scanner</text>
    <text x="365" y="117" fill="#64748b" font-size="7" text-anchor="middle">Rule & Anomaly Engine</text>

    <rect x="440" y="92" width="130" height="32" rx="3" fill="#f0fdfa" stroke="#ccfbf1"/>
    <text x="505" y="105" fill="#0f766e" font-size="8" font-weight="bold" text-anchor="middle">Repair Engine</text>
    <text x="505" y="117" fill="#64748b" font-size="7" text-anchor="middle">OCC & 7 Healing Strategies</text>

    <rect x="300" y="130" width="130" height="32" rx="3" fill="#f0fdfa" stroke="#ccfbf1"/>
    <text x="365" y="143" fill="#0f766e" font-size="8" font-weight="bold" text-anchor="middle">Dependency Analyzer</text>
    <text x="365" y="155" fill="#64748b" font-size="7" text-anchor="middle">NetworkX DAG & Blast Radius</text>

    <rect x="440" y="130" width="130" height="32" rx="3" fill="#f0fdfa" stroke="#ccfbf1"/>
    <text x="505" y="143" fill="#0f766e" font-size="8" font-weight="bold" text-anchor="middle">Ingestion Service</text>
    <text x="505" y="155" fill="#64748b" font-size="7" text-anchor="middle">Staging & Quarantine ETL</text>

    <rect x="300" y="168" width="130" height="32" rx="3" fill="#f0fdfa" stroke="#ccfbf1"/>
    <text x="365" y="181" fill="#0f766e" font-size="8" font-weight="bold" text-anchor="middle">Transaction Manager</text>
    <text x="365" y="193" fill="#64748b" font-size="7" text-anchor="middle">ACID Simulations & Savepoints</text>

    <rect x="440" y="168" width="130" height="32" rx="3" fill="#f0fdfa" stroke="#ccfbf1"/>
    <text x="505" y="181" fill="#0f766e" font-size="8" font-weight="bold" text-anchor="middle">Recovery Manager</text>
    <text x="505" y="193" fill="#64748b" font-size="7" text-anchor="middle">Snapshot Checkpoints</text>

    <rect x="300" y="208" width="270" height="32" rx="3" fill="#e0f2fe" stroke="#bae6fd"/>
    <text x="435" y="222" fill="#0369a1" font-size="8.5" font-weight="bold" text-anchor="middle">PyMySQL Connection Layer (autocommit=False)</text>
    <text x="435" y="234" fill="#0284c7" font-size="7.5" text-anchor="middle">Strict Identifier Regex Validation & DictCursor</text>
  </g>

  <!-- Arrow: Tier 2 to Tier 3 -->
  <line x1="580" y1="140" x2="620" y2="140" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="600" y="132" fill="#475569" font-size="7.5" font-weight="bold" text-anchor="middle">TCP:3306</text>

  <!-- Tier 3: Database (MySQL InnoDB) -->
  <g filter="url(#shadow)">
    <rect x="625" y="30" width="250" height="220" rx="6" fill="#ffffff" stroke="#c7d2fe" stroke-width="1.5"/>
    <rect x="625" y="30" width="250" height="34" rx="6" fill="url(#gradDB)"/>
    <text x="750" y="52" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">DATABASE TIER (MySQL InnoDB)</text>
    
    <text x="635" y="78" fill="#312e81" font-size="9" font-weight="bold">self_healing_test_db (22 Tables)</text>
    
    <rect x="635" y="86" width="230" height="34" rx="3" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="642" y="99" fill="#3730a3" font-size="8" font-weight="bold">Tier 1: Business Domain (6)</text>
    <text x="642" y="112" fill="#64748b" font-size="7.5">departments, instructors, courses, students, enrollments, classrooms</text>

    <rect x="635" y="124" width="230" height="34" rx="3" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="642" y="137" fill="#3730a3" font-size="8" font-weight="bold">Tier 2: Staging & Quarantine (7)</text>
    <text x="642" y="150" fill="#64748b" font-size="7.5">staging_* (6 buffers), quarantine_records</text>

    <rect x="635" y="162" width="230" height="34" rx="3" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="642" y="175" fill="#3730a3" font-size="8" font-weight="bold">Tier 3: Integrity Engine & Repairs (5)</text>
    <text x="642" y="188" fill="#64748b" font-size="7.5">integrity_rules, scan_runs, integrity_issues, repair_*</text>

    <rect x="635" y="200" width="230" height="42" rx="3" fill="#eef2ff" stroke="#c7d2fe"/>
    <text x="642" y="213" fill="#3730a3" font-size="8" font-weight="bold">Tier 4: Audit Trails & Recovery (4)</text>
    <text x="642" y="225" fill="#64748b" font-size="7.5">audit_logs, transaction_logs, recovery_checkpoints, metadata</text>
    <text x="642" y="236" fill="#b91c1c" font-size="7" font-weight="bold">Protected by Immutable SQL Triggers</text>
  </g>
</svg>
"""

SVG_SEQUENCE_FLOW = """
<svg width="100%" height="240" viewBox="0 0 880 240" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; font-family: 'Segoe UI', Arial, sans-serif;">
  <defs>
    <marker id="seqArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563eb" />
    </marker>
    <marker id="seqReturn" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#10b981" />
    </marker>
  </defs>

  <!-- Lifeline Columns -->
  <!-- 1. Administrator -->
  <rect x="20" y="15" width="100" height="28" rx="4" fill="#1e293b"/>
  <text x="70" y="33" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">Administrator</text>
  <line x1="70" y1="43" x2="70" y2="225" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- 2. React UI -->
  <rect x="180" y="15" width="100" height="28" rx="4" fill="#2563eb"/>
  <text x="230" y="33" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">React Page / UI</text>
  <line x1="230" y1="43" x2="230" y2="225" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- 3. Axios Client -->
  <rect x="340" y="15" width="100" height="28" rx="4" fill="#0284c7"/>
  <text x="390" y="33" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">Axios api.js</text>
  <line x1="390" y1="43" x2="390" y2="225" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- 4. FastAPI Router -->
  <rect x="500" y="15" width="100" height="28" rx="4" fill="#0d9488"/>
  <text x="550" y="33" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">FastAPI Router</text>
  <line x1="550" y1="43" x2="550" y2="225" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- 5. Engine Service -->
  <rect x="660" y="15" width="100" height="28" rx="4" fill="#4f46e5"/>
  <text x="710" y="33" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">Engine Service</text>
  <line x1="710" y1="43" x2="710" y2="225" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- 6. MySQL InnoDB -->
  <rect x="800" y="15" width="70" height="28" rx="4" fill="#7c3aed"/>
  <text x="835" y="33" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">MySQL</text>
  <line x1="835" y1="43" x2="835" y2="225" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- Messages -->
  <!-- Step 1 -->
  <line x1="70" y1="65" x2="230" y2="65" stroke="#2563eb" stroke-width="1.5" marker-end="url(#seqArrow)"/>
  <text x="150" y="58" fill="#1e293b" font-size="8" text-anchor="middle">1. Clicks Button (e.g. Execute Repair)</text>

  <!-- Step 2 -->
  <line x1="230" y1="90" x2="390" y2="90" stroke="#2563eb" stroke-width="1.5" marker-end="url(#seqArrow)"/>
  <text x="310" y="83" fill="#1e293b" font-size="8" text-anchor="middle">2. Dispatches repairsApi.executeRepair()</text>

  <!-- Step 3 -->
  <line x1="390" y1="115" x2="550" y2="115" stroke="#2563eb" stroke-width="1.5" marker-end="url(#seqArrow)"/>
  <text x="470" y="108" fill="#1e293b" font-size="8" text-anchor="middle">3. POST /api/repairs/execute (JSON)</text>

  <!-- Step 4 -->
  <line x1="550" y1="140" x2="710" y2="140" stroke="#2563eb" stroke-width="1.5" marker-end="url(#seqArrow)"/>
  <text x="630" y="133" fill="#1e293b" font-size="8" text-anchor="middle">4. RepairEngine.execute_repair()</text>

  <!-- Step 5 -->
  <line x1="710" y1="165" x2="835" y2="165" stroke="#2563eb" stroke-width="1.5" marker-end="url(#seqArrow)"/>
  <text x="772" y="158" fill="#1e293b" font-size="8" text-anchor="middle">5. START TX; UPDATE/DELETE; COMMIT</text>

  <!-- Step 6: Return -->
  <line x1="835" y1="185" x2="710" y2="185" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,3" marker-end="url(#seqReturn)"/>
  <text x="772" y="180" fill="#047857" font-size="7.5" text-anchor="middle">6. DictCursor / Rows</text>

  <line x1="710" y1="198" x2="390" y2="198" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,3" marker-end="url(#seqReturn)"/>
  <text x="550" y="193" fill="#047857" font-size="7.5" text-anchor="middle">7. ApiResponse (success=True, data={...})</text>

  <line x1="390" y1="212" x2="230" y2="212" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,3" marker-end="url(#seqReturn)"/>
  <text x="310" y="207" fill="#047857" font-size="7.5" text-anchor="middle">8. setState() -> Re-renders Component</text>
</svg>
"""

SVG_RELATIONAL_ER = """
<svg width="100%" height="300" viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; font-family: 'Segoe UI', Arial, sans-serif;">
  <defs>
    <marker id="erArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748b" />
    </marker>
  </defs>

  <rect x="5" y="5" width="890" height="290" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>

  <!-- Entity: departments -->
  <g>
    <rect x="25" y="25" width="160" height="110" rx="4" fill="#ffffff" stroke="#3b82f6" stroke-width="1.5"/>
    <rect x="25" y="25" width="160" height="22" rx="4" fill="#3b82f6"/>
    <text x="105" y="40" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">departments</text>
    <text x="32" y="60" fill="#1e293b" font-size="8"><b>PK:</b> dept_id (INT)</text>
    <text x="32" y="74" fill="#64748b" font-size="8">dept_code (VARCHAR 20)</text>
    <text x="32" y="88" fill="#64748b" font-size="8">dept_name (VARCHAR 100)</text>
    <text x="32" y="102" fill="#64748b" font-size="8">budget (DECIMAL 12,2)</text>
    <text x="32" y="116" fill="#64748b" font-size="8">building (VARCHAR 100)</text>
  </g>

  <!-- Entity: instructors -->
  <g>
    <rect x="270" y="25" width="160" height="110" rx="4" fill="#ffffff" stroke="#0d9488" stroke-width="1.5"/>
    <rect x="270" y="25" width="160" height="22" rx="4" fill="#0d9488"/>
    <text x="350" y="40" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">instructors</text>
    <text x="277" y="60" fill="#1e293b" font-size="8"><b>PK:</b> instructor_id (INT)</text>
    <text x="277" y="74" fill="#64748b" font-size="8">instructor_name (VARCHAR)</text>
    <text x="277" y="88" fill="#64748b" font-size="8">email (VARCHAR 150)</text>
    <text x="277" y="102" fill="#0f766e" font-size="8"><b>FK:</b> dept_id -> departments</text>
    <text x="277" y="116" fill="#64748b" font-size="8">salary (DECIMAL 10,2)</text>
  </g>

  <!-- Entity: courses -->
  <g>
    <rect x="520" y="25" width="160" height="110" rx="4" fill="#ffffff" stroke="#8b5cf6" stroke-width="1.5"/>
    <rect x="520" y="25" width="160" height="22" rx="4" fill="#8b5cf6"/>
    <text x="600" y="40" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">courses</text>
    <text x="527" y="60" fill="#1e293b" font-size="8"><b>PK:</b> course_id (INT)</text>
    <text x="527" y="74" fill="#64748b" font-size="8">course_code (VARCHAR 20)</text>
    <text x="527" y="88" fill="#64748b" font-size="8">course_name (VARCHAR 150)</text>
    <text x="527" y="102" fill="#6d28d9" font-size="8"><b>FK:</b> dept_id -> departments</text>
    <text x="527" y="116" fill="#6d28d9" font-size="8"><b>FK:</b> instructor_id -> inst</text>
  </g>

  <!-- Entity: classrooms -->
  <g>
    <rect x="25" y="170" width="160" height="100" rx="4" fill="#ffffff" stroke="#ec4899" stroke-width="1.5"/>
    <rect x="25" y="170" width="160" height="22" rx="4" fill="#ec4899"/>
    <text x="105" y="185" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">classrooms</text>
    <text x="32" y="205" fill="#1e293b" font-size="8"><b>PK:</b> classroom_id (INT)</text>
    <text x="32" y="219" fill="#64748b" font-size="8">room_number (VARCHAR 50)</text>
    <text x="32" y="233" fill="#64748b" font-size="8">capacity (INT DEFAULT 30)</text>
    <text x="32" y="247" fill="#be185d" font-size="8"><b>FK:</b> dept_id -> departments</text>
  </g>

  <!-- Entity: students -->
  <g>
    <rect x="270" y="170" width="160" height="105" rx="4" fill="#ffffff" stroke="#f59e0b" stroke-width="1.5"/>
    <rect x="270" y="170" width="160" height="22" rx="4" fill="#f59e0b"/>
    <text x="350" y="185" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">students</text>
    <text x="277" y="205" fill="#1e293b" font-size="8"><b>PK:</b> student_id (INT)</text>
    <text x="277" y="219" fill="#64748b" font-size="8">student_name (VARCHAR 100)</text>
    <text x="277" y="233" fill="#64748b" font-size="8">email, age, gpa</text>
    <text x="277" y="247" fill="#b45309" font-size="8"><b>FK:</b> dept_id -> departments</text>
  </g>

  <!-- Entity: enrollments -->
  <g>
    <rect x="520" y="170" width="160" height="110" rx="4" fill="#ffffff" stroke="#ef4444" stroke-width="1.5"/>
    <rect x="520" y="170" width="160" height="22" rx="4" fill="#ef4444"/>
    <text x="600" y="185" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">enrollments (Junction)</text>
    <text x="527" y="205" fill="#1e293b" font-size="8"><b>PK:</b> enrollment_id (INT)</text>
    <text x="527" y="219" fill="#b91c1c" font-size="8"><b>FK:</b> student_id -> students</text>
    <text x="527" y="233" fill="#b91c1c" font-size="8"><b>FK:</b> course_id -> courses</text>
    <text x="527" y="247" fill="#64748b" font-size="8">grade_marks (DECIMAL 5,2)</text>
    <text x="527" y="261" fill="#64748b" font-size="8">status ENUM(ENROLLED...)</text>
  </g>

  <!-- System Tables Box -->
  <g>
    <rect x="710" y="25" width="165" height="255" rx="4" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>
    <rect x="710" y="25" width="165" height="22" rx="4" fill="#475569"/>
    <text x="792" y="40" fill="#ffffff" font-size="9" font-weight="bold" text-anchor="middle">SYSTEM & AUDIT TIERS</text>
    <text x="718" y="60" fill="#1e293b" font-size="7.5"><b>Staging Tier (6 tables):</b></text>
    <text x="718" y="73" fill="#64748b" font-size="7">• staging_departments ...</text>
    <text x="718" y="86" fill="#1e293b" font-size="7.5"><b>Quarantine (1 table):</b></text>
    <text x="718" y="99" fill="#64748b" font-size="7">• quarantine_records</text>
    <text x="718" y="114" fill="#1e293b" font-size="7.5"><b>Integrity Engine (5 tables):</b></text>
    <text x="718" y="127" fill="#64748b" font-size="7">• integrity_rules</text>
    <text x="718" y="139" fill="#64748b" font-size="7">• scan_runs</text>
    <text x="718" y="151" fill="#64748b" font-size="7">• integrity_issues</text>
    <text x="718" y="163" fill="#64748b" font-size="7">• repair_recommendations</text>
    <text x="718" y="175" fill="#64748b" font-size="7">• repair_executions</text>
    <text x="718" y="190" fill="#1e293b" font-size="7.5"><b>Audit & Recovery (4 tables):</b></text>
    <text x="718" y="203" fill="#64748b" font-size="7">• audit_logs (Immutable)</text>
    <text x="718" y="215" fill="#64748b" font-size="7">• transaction_logs (Immutable)</text>
    <text x="718" y="227" fill="#64748b" font-size="7">• recovery_checkpoints</text>
    <text x="718" y="239" fill="#64748b" font-size="7">• database_metadata</text>
    <text x="718" y="260" fill="#0f766e" font-size="7.5" font-weight="bold">Total Tables: 22 InnoDB</text>
  </g>

  <!-- FK Lines -->
  <!-- departments -> instructors -->
  <line x1="185" y1="80" x2="270" y2="80" stroke="#64748b" stroke-width="1.5" marker-end="url(#erArrow)"/>
  <!-- instructors -> courses -->
  <line x1="430" y1="80" x2="520" y2="80" stroke="#64748b" stroke-width="1.5" marker-end="url(#erArrow)"/>
  <!-- departments -> classrooms -->
  <line x1="105" y1="135" x2="105" y2="170" stroke="#64748b" stroke-width="1.5" marker-end="url(#erArrow)"/>
  <!-- departments -> students -->
  <path d="M 105 135 L 105 150 L 270 190" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#erArrow)"/>
  <!-- students -> enrollments -->
  <line x1="430" y1="225" x2="520" y2="225" stroke="#64748b" stroke-width="1.5" marker-end="url(#erArrow)"/>
  <!-- courses -> enrollments -->
  <line x1="600" y1="135" x2="600" y2="170" stroke="#64748b" stroke-width="1.5" marker-end="url(#erArrow)"/>
</svg>
"""

SVG_INGESTION_FLOW = """
<svg width="100%" height="220" viewBox="0 0 880 220" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; font-family: 'Segoe UI', Arial, sans-serif;">
  <defs>
    <marker id="ingArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#334155" />
    </marker>
  </defs>

  <rect x="5" y="5" width="870" height="210" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>

  <!-- Step 1 -->
  <rect x="25" y="85" width="130" height="50" rx="4" fill="#3b82f6"/>
  <text x="90" y="106" fill="#ffffff" font-size="8.5" font-weight="bold" text-anchor="middle">1. Raw Input</text>
  <text x="90" y="122" fill="#bfdbfe" font-size="7.5" text-anchor="middle">External Batch Record</text>

  <line x1="155" y1="110" x2="195" y2="110" stroke="#334155" stroke-width="1.5" marker-end="url(#ingArrow)"/>

  <!-- Step 2 -->
  <rect x="195" y="85" width="140" height="50" rx="4" fill="#0284c7"/>
  <text x="265" y="106" fill="#ffffff" font-size="8.5" font-weight="bold" text-anchor="middle">2. Staging Landing</text>
  <text x="265" y="122" fill="#bae6fd" font-size="7.5" text-anchor="middle">INSERT staging_* (PENDING)</text>

  <line x1="335" y1="110" x2="375" y2="110" stroke="#334155" stroke-width="1.5" marker-end="url(#ingArrow)"/>

  <!-- Step 3: Validation Pipeline -->
  <rect x="375" y="65" width="160" height="90" rx="4" fill="#ffffff" stroke="#0d9488" stroke-width="1.5"/>
  <rect x="375" y="65" width="160" height="20" rx="4" fill="#0d9488"/>
  <text x="455" y="79" fill="#ffffff" font-size="8" font-weight="bold" text-anchor="middle">3. Validation Pipeline</text>
  <text x="385" y="97" fill="#0f766e" font-size="7.5">• Mandatory Non-Null</text>
  <text x="385" y="110" fill="#0f766e" font-size="7.5">• Foreign Key Parent Exists</text>
  <text x="385" y="123" fill="#0f766e" font-size="7.5">• Numerical / Domain Range</text>
  <text x="385" y="136" fill="#0f766e" font-size="7.5">• Candidate Key Uniqueness</text>

  <!-- Decision Fork -->
  <line x1="535" y1="95" x2="600" y2="55" stroke="#059669" stroke-width="1.5" marker-end="url(#ingArrow)"/>
  <text x="560" y="70" fill="#059669" font-size="8" font-weight="bold">PASS (Valid)</text>

  <line x1="535" y1="125" x2="600" y2="165" stroke="#dc2626" stroke-width="1.5" marker-end="url(#ingArrow)"/>
  <text x="560" y="155" fill="#dc2626" font-size="8" font-weight="bold">FAIL (Violation)</text>

  <!-- Outcome Valid -->
  <rect x="600" y="30" width="250" height="60" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="725" y="48" fill="#065f46" font-size="8.5" font-weight="bold" text-anchor="middle">COMMITTED TO PRODUCTION</text>
  <text x="610" y="64" fill="#047857" font-size="7.5">• INSERT INTO {production_table} (Atomic TX)</text>
  <text x="610" y="78" fill="#047857" font-size="7.5">• UPDATE staging_* SET validation_status = 'VALID'</text>

  <!-- Outcome Invalid -->
  <rect x="600" y="135" width="250" height="65" rx="4" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="725" y="153" fill="#991b1b" font-size="8.5" font-weight="bold" text-anchor="middle">REJECTED & QUARANTINED</text>
  <text x="610" y="169" fill="#b91c1c" font-size="7.5">• INSERT INTO quarantine_records (Row JSON)</text>
  <text x="610" y="182" fill="#b91c1c" font-size="7.5">• UPDATE staging_* SET validation_status = 'REJECTED'</text>
  <text x="610" y="195" fill="#b91c1c" font-size="7.5">• Log DATA_INGESTION_REJECTED to audit_logs</text>
</svg>
"""
