import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  ScanSearch,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  ArrowRight,
  Filter,
  Check,
  Table as TableIcon,
  ShieldCheck,
  Clock,
  Layers,
  Search,
  Database,
  ShieldAlert,
  GitFork,
  Copy,
  FileQuestion,
  Gauge
} from 'lucide-react';
import { scansApi, databaseApi, rulesApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const CORE_SIX_TABLES = [
  { name: 'departments', role: 'Reference Entity', description: 'Academic departments, budget allocations, leadership' },
  { name: 'instructors', role: 'Child of departments', description: 'Faculty members, salaries, department assignments' },
  { name: 'courses', role: 'Child of depts & instructors', description: 'Academic courses, credit limits, assigned faculty' },
  { name: 'students', role: 'Child of departments', description: 'Enrolled students, GPA, age domain, enrollment year' },
  { name: 'enrollments', role: 'Junction (student x course)', description: 'Course enrollments, grade marks, academic standing' },
  { name: 'staging_enrollments', role: 'Staging Intake Entity', description: 'External unvalidated batch records pending migration' },
];

export const IntegrityScannerPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [scanType, setScanType] = useState('FULL'); // 'FULL' or 'TABLE'
  const [availableTables, setAvailableTables] = useState([]);
  const [selectedTables, setSelectedTables] = useState([]);
  const [rules, setRules] = useState([]);
  const [selectedRules, setSelectedRules] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [recentScans, setRecentScans] = useState([]);

  // Results filtering states
  const [tableFilter, setTableFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const tableParam = searchParams.get('table');
    if (tableParam) {
      setScanType('TABLE');
      setSelectedTables([tableParam]);
      setTableFilter(tableParam);
    }

    const initData = async () => {
      try {
        const [tablesRes, rulesRes, scansRes] = await Promise.all([
          databaseApi.getTables(),
          rulesApi.getRules(),
          scansApi.getScans(5),
        ]);
        const tbls = tablesRes.data || [];
        setAvailableTables(tbls);
        if (!tableParam) {
          // Default select all 6 core business and staging tables
          const defaultNames = CORE_SIX_TABLES.map(t => t.name);
          const foundDefaults = tbls.filter(t => defaultNames.includes(t.table_name)).map(t => t.table_name);
          setSelectedTables(foundDefaults.length > 0 ? foundDefaults : tbls.map(t => t.table_name));
        }

        const rls = rulesRes.data || [];
        setRules(rls);
        setSelectedRules(rls.filter(r => r.is_enabled).map(r => r.rule_code));
        setRecentScans(scansRes.data || []);
      } catch (err) {
        console.error('Initialization error:', err);
      }
    };
    initData();
  }, [searchParams]);

  const handleExecuteScan = async () => {
    setIsScanning(true);
    setScanResult(null);
    try {
      const payload = {
        scan_type: scanType,
        target_tables: scanType === 'TABLE' ? selectedTables : null,
        rule_codes: selectedRules.length > 0 ? selectedRules : null,
      };
      const res = await scansApi.triggerScan(payload);
      setScanResult(res.data);
      // Refresh scan history
      const updatedScans = await scansApi.getScans(5);
      setRecentScans(updatedScans.data || []);
    } catch (err) {
      console.error('Scan failed:', err);
    } finally {
      setIsScanning(false);
    }
  };

  const toggleTable = (tableName) => {
    setSelectedTables((prev) =>
      prev.includes(tableName) ? prev.filter((t) => t !== tableName) : [...prev, tableName]
    );
  };

  const toggleRule = (ruleCode) => {
    setSelectedRules((prev) =>
      prev.includes(ruleCode) ? prev.filter((r) => r !== ruleCode) : [...prev, ruleCode]
    );
  };

  // Precomputed rule counts per table
  const rulesCountByTable = useMemo(() => {
    const counts = {};
    CORE_SIX_TABLES.forEach(t => { counts[t.name] = 0; });
    rules.forEach(r => {
      if (r.target_table) {
        counts[r.target_table] = (counts[r.target_table] || 0) + 1;
      }
    });
    return counts;
  }, [rules]);

  // Filtered issues list
  const filteredIssues = useMemo(() => {
    if (!scanResult || !scanResult.issues) return [];
    return scanResult.issues.filter((issue) => {
      if (tableFilter !== 'ALL' && issue.table_name !== tableFilter) return false;
      if (categoryFilter !== 'ALL' && issue.category !== categoryFilter) return false;
      if (severityFilter !== 'ALL' && issue.severity !== severityFilter) return false;
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const matchesId = issue.issue_id.toLowerCase().includes(q);
        const matchesDesc = (issue.description || '').toLowerCase().includes(q);
        const matchesCol = (issue.column_name || '').toLowerCase().includes(q);
        const matchesVal = String(issue.invalid_value || '').toLowerCase().includes(q);
        const matchesTable = issue.table_name.toLowerCase().includes(q);
        if (!matchesId && !matchesDesc && !matchesCol && !matchesVal && !matchesTable) {
          return false;
        }
      }
      return true;
    });
  }, [scanResult, tableFilter, categoryFilter, severityFilter, searchQuery]);

  return (
    <div className="space-y-5 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <ScanSearch className="w-5 h-5 text-indigo-600" />
            Database Integrity Scanner
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Autonomous multi-rule relational verification engine checking foreign keys, duplicate keys, NOT NULL constraints, and domain ranges across all six database tables.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="md"
            icon={Play}
            loading={isScanning}
            onClick={handleExecuteScan}
          >
            {isScanning ? 'Scanning All Tables...' : 'Run Full Integrity Scan'}
          </Button>
        </div>
      </div>

      {/* SCAN CONFIGURATION 3-PANEL GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Panel 1: Target Scope (All 6 Tables) */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between">
          <div>
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-indigo-600" /> 1. Target Scope (All 6 Tables)
              </span>
              <div className="flex items-center bg-slate-100 p-0.5 rounded text-xs">
                <button
                  onClick={() => {
                    setScanType('FULL');
                    setSelectedTables(availableTables.map(t => t.table_name));
                  }}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    scanType === 'FULL' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Full DB (6)
                </button>
                <button
                  onClick={() => setScanType('TABLE')}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    scanType === 'TABLE' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Selected
                </button>
              </div>
            </div>

            <div className="p-3 space-y-1.5 max-h-56 overflow-y-auto">
              {availableTables.map((t) => {
                const isSelected = selectedTables.includes(t.table_name);
                const isCore = CORE_SIX_TABLES.some(c => c.name === t.table_name);
                return (
                  <div
                    key={t.table_name}
                    onClick={() => toggleTable(t.table_name)}
                    className={`flex items-center justify-between px-2.5 py-1.5 rounded border text-xs cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-indigo-50 border-indigo-200 text-indigo-900 font-semibold'
                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center gap-2 font-mono">
                      <div className={`w-3.5 h-3.5 rounded flex items-center justify-center border text-[9px] ${
                        isSelected ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-slate-300 bg-white'
                      }`}>
                        {isSelected && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                      </div>
                      <span className="truncate">{t.table_name}</span>
                      {isCore && (
                        <span className="px-1 py-0.2 text-[9px] rounded bg-indigo-100 text-indigo-800 font-sans font-medium">Core</span>
                      )}
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">{t.row_count ?? t.TABLE_ROWS ?? 0} rows</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
            <span>{selectedTables.length} tables selected</span>
            <button
              onClick={() => setSelectedTables(availableTables.map(t => t.table_name))}
              className="text-indigo-600 hover:underline font-medium text-xs"
            >
              Select All 6 Tables
            </button>
          </div>
        </div>

        {/* Panel 2: Integrity Rules Set */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between">
          <div>
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" /> 2. Active Rule Set
              </span>
              <span className="text-xs font-mono font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                {selectedRules.length} / {rules.length} Active Rules
              </span>
            </div>

            <div className="p-3 space-y-1.5 max-h-56 overflow-y-auto">
              {rules.map((r) => {
                const isSelected = selectedRules.includes(r.rule_code);
                return (
                  <div
                    key={r.rule_code}
                    onClick={() => toggleRule(r.rule_code)}
                    className={`p-2 rounded border text-xs cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-slate-50 border-slate-300 text-slate-900'
                        : 'bg-white border-slate-200 text-slate-400 opacity-60'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <div className="flex items-center gap-1.5 truncate">
                        <span className="font-semibold text-slate-900 truncate">{r.rule_code}</span>
                        <span className="text-[10px] text-slate-500 font-mono">({r.target_table})</span>
                      </div>
                      <Badge variant={r.severity} />
                    </div>
                    <div className="text-[11px] text-slate-500 truncate mt-0.5">{r.description || r.name}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
            <span>{rules.length} defined integrity rules</span>
            <button
              onClick={() => setSelectedRules(rules.map(r => r.rule_code))}
              className="text-indigo-600 hover:underline font-medium text-xs"
            >
              Enable All Rules
            </button>
          </div>
        </div>

        {/* Panel 3: Execution Diagnostics & Trigger */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs p-4 flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
              3. Execution Telemetry
            </span>
            <p className="text-xs text-slate-500 leading-relaxed">
              Executes parameterized SQL validation checks against all six database tables inside the active MySQL schema catalog.
            </p>

            {scanResult ? (
              <div className="mt-3 p-3 rounded bg-slate-50 border border-slate-200 text-xs font-mono space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Status:</span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[11px] flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" /> {scanResult.status || 'COMPLETED'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Scan ID:</span>
                  <span className="font-bold text-slate-900">{scanResult.scan_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Rows Inspected:</span>
                  <span className="text-slate-900 font-bold">{scanResult.total_rows_inspected}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Duration:</span>
                  <span className="text-slate-900">{scanResult.duration_ms} ms</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-slate-200">
                  <span className="text-slate-600 font-bold font-sans">Violations Found:</span>
                  <span className="text-rose-600 font-bold font-mono">{scanResult.issues_found}</span>
                </div>
              </div>
            ) : (
              <div className="mt-3 p-4 rounded border border-dashed border-slate-200 text-center text-xs text-slate-400">
                Ready to execute. Click button below to inspect database.
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-200">
            <Button
              variant="primary"
              size="md"
              icon={Play}
              loading={isScanning}
              onClick={handleExecuteScan}
              className="w-full"
            >
              {isScanning ? 'Scanning All 6 Tables...' : 'Run Full Integrity Scan'}
            </Button>
          </div>
        </div>
      </div>

      {/* SCAN RESULTS DASHBOARD (VISIBLE POST-SCAN) */}
      {scanResult && (
        <div className="space-y-4">
          {/* 1. CATEGORY BREAKDOWN CARDS (ORPHAN, DUPLICATE, NULL, DOMAIN) */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-indigo-600" /> Integrity Category Breakdown
              </h3>
              <span className="text-xs text-slate-500 font-mono">
                {scanResult.issues_found} total violations across 4 categories
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* ORPHAN */}
              <div className="bg-white border border-rose-200 rounded-lg p-3.5 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-rose-800 flex items-center gap-1.5">
                    <GitFork className="w-4 h-4 text-rose-600" /> ORPHAN Checks
                  </span>
                  <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-mono font-bold text-xs">
                    {scanResult.issues_by_category?.['ORPHAN'] ?? scanResult.issues.filter(i => i.category === 'ORPHAN').length}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Foreign key referential integrity: records referencing missing parent keys across all 6 tables.
                </p>
                <button
                  onClick={() => setCategoryFilter(categoryFilter === 'ORPHAN' ? 'ALL' : 'ORPHAN')}
                  className={`mt-2 text-[11px] font-semibold flex items-center gap-1 transition-colors ${
                    categoryFilter === 'ORPHAN' ? 'text-rose-700 underline' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {categoryFilter === 'ORPHAN' ? 'Active Filter (Clear)' : 'Filter by Orphan →'}
                </button>
              </div>

              {/* DUPLICATE */}
              <div className="bg-white border border-amber-200 rounded-lg p-3.5 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-amber-800 flex items-center gap-1.5">
                    <Copy className="w-4 h-4 text-amber-600" /> DUPLICATE Checks
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-mono font-bold text-xs">
                    {scanResult.issues_by_category?.['DUPLICATE'] ?? scanResult.issues.filter(i => i.category === 'DUPLICATE').length}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Candidate key & unique constraints: duplicate emails, codes, and composite pairs.
                </p>
                <button
                  onClick={() => setCategoryFilter(categoryFilter === 'DUPLICATE' ? 'ALL' : 'DUPLICATE')}
                  className={`mt-2 text-[11px] font-semibold flex items-center gap-1 transition-colors ${
                    categoryFilter === 'DUPLICATE' ? 'text-amber-700 underline' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {categoryFilter === 'DUPLICATE' ? 'Active Filter (Clear)' : 'Filter by Duplicate →'}
                </button>
              </div>

              {/* NULL */}
              <div className="bg-white border border-indigo-200 rounded-lg p-3.5 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-800 flex items-center gap-1.5">
                    <FileQuestion className="w-4 h-4 text-indigo-600" /> NULL Checks
                  </span>
                  <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-mono font-bold text-xs">
                    {scanResult.issues_by_category?.['NULL_VIOLATION'] ?? scanResult.issues.filter(i => i.category === 'NULL_VIOLATION').length}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Completeness checks: missing mandatory attributes, empty strings, and whitespace-only TRIM fields.
                </p>
                <button
                  onClick={() => setCategoryFilter(categoryFilter === 'NULL_VIOLATION' ? 'ALL' : 'NULL_VIOLATION')}
                  className={`mt-2 text-[11px] font-semibold flex items-center gap-1 transition-colors ${
                    categoryFilter === 'NULL_VIOLATION' ? 'text-indigo-700 underline' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {categoryFilter === 'NULL_VIOLATION' ? 'Active Filter (Clear)' : 'Filter by Null →'}
                </button>
              </div>

              {/* DOMAIN */}
              <div className="bg-white border border-teal-200 rounded-lg p-3.5 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-teal-800 flex items-center gap-1.5">
                    <Gauge className="w-4 h-4 text-teal-600" /> DOMAIN Checks
                  </span>
                  <span className="px-2 py-0.5 rounded bg-teal-100 text-teal-800 font-mono font-bold text-xs">
                    {scanResult.issues_by_category?.['DOMAIN_VIOLATION'] ?? scanResult.issues.filter(i => i.category === 'DOMAIN_VIOLATION').length}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Value domain checks: numeric ranges (budget, salary, credits, GPA, age, marks), status enums, regex patterns.
                </p>
                <button
                  onClick={() => setCategoryFilter(categoryFilter === 'DOMAIN_VIOLATION' ? 'ALL' : 'DOMAIN_VIOLATION')}
                  className={`mt-2 text-[11px] font-semibold flex items-center gap-1 transition-colors ${
                    categoryFilter === 'DOMAIN_VIOLATION' ? 'text-teal-700 underline' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {categoryFilter === 'DOMAIN_VIOLATION' ? 'Active Filter (Clear)' : 'Filter by Domain →'}
                </button>
              </div>
            </div>
          </div>

          {/* 2. SEVERITY DISTRIBUTION BAR */}
          <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Severity Distribution
              </span>
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-rose-600"></span> CRITICAL: <strong className="text-slate-900">{scanResult.critical_count}</strong>
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-amber-500"></span> HIGH: <strong className="text-slate-900">{scanResult.high_count}</strong>
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-yellow-500"></span> MEDIUM: <strong className="text-slate-900">{scanResult.medium_count}</strong>
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-sky-500"></span> LOW: <strong className="text-slate-900">{scanResult.low_count}</strong>
                </span>
              </div>
            </div>

            <div className="flex h-2.5 rounded-full overflow-hidden bg-slate-100">
              {scanResult.issues_found > 0 ? (
                <>
                  <div style={{ width: `${(scanResult.critical_count / scanResult.issues_found) * 100}%` }} className="bg-rose-600" title={`Critical: ${scanResult.critical_count}`}></div>
                  <div style={{ width: `${(scanResult.high_count / scanResult.issues_found) * 100}%` }} className="bg-amber-500" title={`High: ${scanResult.high_count}`}></div>
                  <div style={{ width: `${(scanResult.medium_count / scanResult.issues_found) * 100}%` }} className="bg-yellow-500" title={`Medium: ${scanResult.medium_count}`}></div>
                  <div style={{ width: `${(scanResult.low_count / scanResult.issues_found) * 100}%` }} className="bg-sky-500" title={`Low: ${scanResult.low_count}`}></div>
                </>
              ) : (
                <div className="w-full bg-emerald-500" title="100% Clean"></div>
              )}
            </div>
          </div>

          {/* 3. SIX-TABLE INTEGRITY COVERAGE MATRIX */}
          <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
                <TableIcon className="w-3.5 h-3.5 text-indigo-600" />
                Six-Table Integrity Coverage Matrix
              </h3>
              <span className="text-xs text-slate-500 font-mono">
                {scanResult.total_rules || rules.length} Total Rules Active
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Table Name</th>
                    <th className="py-2.5 px-3">Relational Role</th>
                    <th className="py-2.5 px-3 text-center">Active Rules</th>
                    <th className="py-2.5 px-3 text-center">Issues Detected</th>
                    <th className="py-2.5 px-3">Category Breakdown</th>
                    <th className="py-2.5 px-3">Health Status</th>
                    <th className="py-2.5 px-3 text-right">Table Filter</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {CORE_SIX_TABLES.map((t) => {
                    const issuesCount = scanResult.issues_by_table?.[t.name] ?? scanResult.issues.filter(i => i.table_name === t.name).length;
                    const tableRulesCount = scanResult.rules_by_table?.[t.name] ?? rulesCountByTable[t.name] ?? 0;
                    const tableIssues = scanResult.issues.filter(i => i.table_name === t.name);
                    const orphCnt = tableIssues.filter(i => i.category === 'ORPHAN').length;
                    const dupCnt = tableIssues.filter(i => i.category === 'DUPLICATE').length;
                    const nullCnt = tableIssues.filter(i => i.category === 'NULL_VIOLATION').length;
                    const domCnt = tableIssues.filter(i => i.category === 'DOMAIN_VIOLATION').length;

                    return (
                      <tr key={t.name} className="hover:bg-slate-50/70">
                        <td className="py-2.5 px-3 text-slate-900 font-bold">
                          `{t.name}`
                        </td>
                        <td className="py-2.5 px-3 font-sans text-slate-600">
                          <span className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-[11px] text-slate-700">
                            {t.role}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-center font-bold text-slate-800">
                          {tableRulesCount}
                        </td>
                        <td className="py-2.5 px-3 text-center font-bold">
                          {issuesCount > 0 ? (
                            <span className="text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                              {issuesCount}
                            </span>
                          ) : (
                            <span className="text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              0 Clean
                            </span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 font-mono text-[10px]">
                          <div className="flex items-center gap-1 flex-wrap">
                            {orphCnt > 0 && <span className="px-1 rounded bg-rose-100 text-rose-800">ORPH:{orphCnt}</span>}
                            {dupCnt > 0 && <span className="px-1 rounded bg-amber-100 text-amber-800">DUP:{dupCnt}</span>}
                            {nullCnt > 0 && <span className="px-1 rounded bg-indigo-100 text-indigo-800">NULL:{nullCnt}</span>}
                            {domCnt > 0 && <span className="px-1 rounded bg-teal-100 text-teal-800">DOM:{domCnt}</span>}
                            {issuesCount === 0 && <span className="text-slate-400">None</span>}
                          </div>
                        </td>
                        <td className="py-2.5 px-3 font-sans">
                          {issuesCount > 0 ? (
                            <Badge variant="HIGH">Action Needed</Badge>
                          ) : (
                            <Badge variant="REPAIRED">All Clean</Badge>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-right font-sans">
                          <button
                            onClick={() => setTableFilter(tableFilter === t.name ? 'ALL' : t.name)}
                            className={`px-2 py-1 rounded text-[11px] font-semibold border transition-colors ${
                              tableFilter === t.name
                                ? 'bg-indigo-600 text-white border-indigo-600'
                                : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                            }`}
                          >
                            {tableFilter === t.name ? 'Selected' : 'View Issues'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* 4. DETECTED VIOLATIONS TABLE WITH ADVANCED MULTI-TABLE FILTERING */}
          <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-200 space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                    Detected Violations ({filteredIssues.length} of {scanResult.issues.length})
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Click "Self-Heal" on any violation to open transaction preview and approve repairs in the Repair Center.
                  </p>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={ArrowRight}
                  onClick={() => navigate('/repairs')}
                >
                  Open Repair Center
                </Button>
              </div>

              {/* Filter Pills Bar */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
                {/* Table Filter Selector */}
                <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded text-[11px]">
                  <span className="px-1 text-slate-500 font-bold uppercase text-[9px]">Table:</span>
                  <button
                    onClick={() => setTableFilter('ALL')}
                    className={`px-1.5 py-0.5 rounded ${tableFilter === 'ALL' ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                  >
                    All (6)
                  </button>
                  {CORE_SIX_TABLES.map(t => (
                    <button
                      key={t.name}
                      onClick={() => setTableFilter(t.name)}
                      className={`px-1.5 py-0.5 rounded ${tableFilter === t.name ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                    >
                      {t.name}
                    </button>
                  ))}
                </div>

                {/* Category Filter Selector */}
                <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded text-[11px]">
                  <span className="px-1 text-slate-500 font-bold uppercase text-[9px]">Category:</span>
                  {['ALL', 'ORPHAN', 'DUPLICATE', 'NULL_VIOLATION', 'DOMAIN_VIOLATION'].map(c => (
                    <button
                      key={c}
                      onClick={() => setCategoryFilter(c)}
                      className={`px-1.5 py-0.5 rounded ${categoryFilter === c ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                    >
                      {c === 'NULL_VIOLATION' ? 'NULL' : c === 'DOMAIN_VIOLATION' ? 'DOMAIN' : c}
                    </button>
                  ))}
                </div>

                {/* Severity Filter Selector */}
                <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded text-[11px]">
                  <span className="px-1 text-slate-500 font-bold uppercase text-[9px]">Severity:</span>
                  {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(s => (
                    <button
                      key={s}
                      onClick={() => setSeverityFilter(s)}
                      className={`px-1.5 py-0.5 rounded ${severityFilter === s ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                    >
                      {s}
                    </button>
                  ))}
                </div>

                {/* Search Box */}
                <div className="relative flex-1 min-w-[180px]">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2 top-2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by ID, table, column, value..."
                    className="w-full pl-7 pr-2 py-1 bg-white border border-slate-200 rounded text-xs text-slate-800 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Issue ID</th>
                    <th className="py-2.5 px-3">Severity</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Table & Record</th>
                    <th className="py-2.5 px-3">Column & Invalid Value</th>
                    <th className="py-2.5 px-3">Violation Details</th>
                    <th className="py-2.5 px-3 text-right">Self-Heal Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {filteredIssues.map((issue) => (
                    <tr key={issue.issue_id} className="hover:bg-slate-50/70">
                      <td className="py-2.5 px-3 text-slate-900 font-bold">{issue.issue_id}</td>
                      <td className="py-2.5 px-3"><Badge variant={issue.severity} /></td>
                      <td className="py-2.5 px-3 text-slate-700">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          issue.category === 'ORPHAN' ? 'bg-rose-100 text-rose-800' :
                          issue.category === 'DUPLICATE' ? 'bg-amber-100 text-amber-800' :
                          issue.category === 'NULL_VIOLATION' ? 'bg-indigo-100 text-indigo-800' :
                          'bg-teal-100 text-teal-800'
                        }`}>
                          {issue.category}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-800 font-semibold">
                        `{issue.table_name}`.id={issue.record_id}
                      </td>
                      <td className="py-2.5 px-3 text-slate-600 text-[11px]">
                        {issue.column_name ? (
                          <>
                            <strong className="text-slate-900">{issue.column_name}</strong>:
                            <span className="text-rose-600 ml-1">"{String(issue.invalid_value ?? '')}"</span>
                          </>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 font-sans text-slate-600 max-w-sm truncate" title={issue.description}>
                        {issue.description}
                      </td>
                      <td className="py-2.5 px-3 text-right font-sans">
                        {issue.status === 'REPAIRED' ? (
                          <span className="text-[11px] text-emerald-600 font-medium">Repaired</span>
                        ) : (
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => navigate(`/repairs?issue=${issue.issue_id}`)}
                          >
                            Self-Heal
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {filteredIssues.length === 0 && (
                    <tr>
                      <td colSpan="7" className="py-6 text-center text-slate-400 font-sans text-xs">
                        No violations matching the active filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrityScannerPage;
