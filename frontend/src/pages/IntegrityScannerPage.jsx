import React, { useState, useEffect } from 'react';
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
  Layers
} from 'lucide-react';
import { scansApi, databaseApi, rulesApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

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

  useEffect(() => {
    const tableParam = searchParams.get('table');
    if (tableParam) {
      setScanType('TABLE');
      setSelectedTables([tableParam]);
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
          // Select default business and staging tables
          setSelectedTables(tbls.filter(t => t.table_type === 'BUSINESS' || t.table_type === 'STAGING').map(t => t.table_name));
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

  return (
    <div className="space-y-5 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Database Integrity Scanner
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Autonomous multi-rule relational verification engine checking foreign keys, duplicate keys, NOT NULL constraints, and domain ranges.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          icon={Play}
          loading={isScanning}
          onClick={handleExecuteScan}
        >
          {isScanning ? 'Scanning...' : 'Run Integrity Scan'}
        </Button>
      </div>

      {/* SCAN CONFIGURATION 3-PANEL GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Panel 1: Target Tables */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between">
          <div>
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">1. Target Scope</span>
              <div className="flex items-center bg-slate-100 p-0.5 rounded text-xs">
                <button
                  onClick={() => setScanType('FULL')}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    scanType === 'FULL' ? 'bg-white text-slate-900 font-semibold shadow-xs' : 'text-slate-600'
                  }`}
                >
                  Full DB
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

            <div className="p-3 space-y-1 max-h-56 overflow-y-auto">
              {availableTables.map((t) => {
                const isSelected = selectedTables.includes(t.table_name);
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
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">{t.row_count} rows</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
            <span>{selectedTables.length} tables selected</span>
            <button
              onClick={() => setSelectedTables(availableTables.map(t => t.table_name))}
              className="text-indigo-600 hover:underline font-medium"
            >
              Select All
            </button>
          </div>
        </div>

        {/* Panel 2: Integrity Rules Set */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between">
          <div>
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">2. Active Rule Set</span>
              <span className="text-xs font-mono font-bold text-slate-700">{selectedRules.length} / {rules.length} Active</span>
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
                      <span className="font-semibold text-slate-900 truncate">{r.name}</span>
                      <Badge variant={r.severity} />
                    </div>
                    <div className="text-[11px] text-slate-500 truncate mt-0.5">{r.description}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
            <span>{rules.length} defined rules</span>
            <button
              onClick={() => setSelectedRules(rules.map(r => r.rule_code))}
              className="text-indigo-600 hover:underline font-medium"
            >
              Enable All
            </button>
          </div>
        </div>

        {/* Panel 3: Execution Diagnostics & Trigger */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs p-4 flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
              3. Execution Summary
            </span>
            <p className="text-xs text-slate-500 leading-relaxed">
              Executes parameterized SQL checks against active MySQL tables inside the active schema catalog.
            </p>

            {scanResult ? (
              <div className="mt-3 p-3 rounded bg-slate-50 border border-slate-200 text-xs font-mono space-y-1.5">
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
                  <span className="text-rose-600 font-bold">{scanResult.issues_found}</span>
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
              {isScanning ? 'Scanning Database...' : 'Run Full Scan Now'}
            </Button>
          </div>
        </div>
      </div>

      {/* SCAN RESULTS & DETAILED VIOLATIONS TABLE */}
      {scanResult && (
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                Detected Integrity Violations ({scanResult.issues.length})
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Recorded violations waiting in the issue catalog for autonomous self-healing preview and execution.
              </p>
            </div>
            <Button
              variant="secondary"
              size="sm"
              icon={ArrowRight}
              onClick={() => navigate('/issues')}
            >
              Open in Issue Manager
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Issue ID</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Table & Record</th>
                  <th className="py-2.5 px-3">Violation Details</th>
                  <th className="py-2.5 px-3 text-right">Self-Heal Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {scanResult.issues.map((issue) => (
                  <tr key={issue.issue_id} className="hover:bg-slate-50/70">
                    <td className="py-2.5 px-3 text-slate-900 font-bold">{issue.issue_id}</td>
                    <td className="py-2.5 px-3"><Badge variant={issue.severity} /></td>
                    <td className="py-2.5 px-3 text-slate-700">{issue.category}</td>
                    <td className="py-2.5 px-3 text-slate-800 font-semibold">
                      `{issue.table_name}`.id={issue.record_id}
                    </td>
                    <td className="py-2.5 px-3 font-sans text-slate-600 max-w-md truncate" title={issue.description}>
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
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrityScannerPage;
