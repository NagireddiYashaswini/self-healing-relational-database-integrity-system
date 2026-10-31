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
  Table as TableIcon
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
      // Refresh scan list
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Database Integrity Scanner
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous multi-rule engine detecting orphans, duplicate keys, NOT NULL infractions, and domain violations.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          icon={Play}
          loading={isScanning}
          onClick={handleExecuteScan}
        >
          Run Integrity Scan
        </Button>
      </div>

      {/* Configuration Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Scan Scope & Tables */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">1. Target Scope</h3>
            <div className="flex items-center bg-slate-900 rounded-lg p-0.5 border border-slate-800 text-xs">
              <button
                onClick={() => setScanType('FULL')}
                className={`px-2.5 py-1 rounded font-medium ${scanType === 'FULL' ? 'bg-emerald-600 text-white' : 'text-slate-400'}`}
              >
                Full Database
              </button>
              <button
                onClick={() => setScanType('TABLE')}
                className={`px-2.5 py-1 rounded font-medium ${scanType === 'TABLE' ? 'bg-emerald-600 text-white' : 'text-slate-400'}`}
              >
                Selected Tables
              </button>
            </div>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {availableTables.map((t) => {
              const isSelected = selectedTables.includes(t.table_name);
              return (
                <div
                  key={t.table_name}
                  onClick={() => toggleTable(t.table_name)}
                  className={`flex items-center justify-between p-2.5 rounded-lg border text-xs cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300 font-semibold'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2 font-mono">
                    <div className={`w-4 h-4 rounded flex items-center justify-center border ${isSelected ? 'bg-emerald-500 border-emerald-400 text-white' : 'border-slate-700'}`}>
                      {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                    </div>
                    <span>{t.table_name}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">{t.row_count} rows</span>
                </div>
              );
            })}
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800">
            <span>{selectedTables.length} tables selected</span>
            <button
              onClick={() => setSelectedTables(availableTables.map(t => t.table_name))}
              className="text-emerald-400 hover:underline"
            >
              Select All
            </button>
          </div>
        </div>

        {/* Center: Rules Selection */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">2. Active Rule Set</h3>
            <Badge variant="MEDIUM">{selectedRules.length} Active</Badge>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {rules.map((r) => {
              const isSelected = selectedRules.includes(r.rule_code);
              return (
                <div
                  key={r.rule_code}
                  onClick={() => toggleRule(r.rule_code)}
                  className={`p-2.5 rounded-lg border text-xs cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-slate-900/90 border-slate-700 text-slate-200'
                      : 'bg-slate-950/40 border-slate-850 text-slate-500 opacity-60'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-100">{r.name}</span>
                    <Badge variant={r.severity} />
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1 line-clamp-1">{r.description}</div>
                </div>
              );
            })}
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between pt-2 border-t border-slate-800">
            <span>{rules.length} total defined rules</span>
            <button
              onClick={() => setSelectedRules(rules.map(r => r.rule_code))}
              className="text-emerald-400 hover:underline"
            >
              Enable All
            </button>
          </div>
        </div>

        {/* Right: Scan Execution Summary Card */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 mb-2">3. Engine Execution</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              When triggered, the scanner connects to the XAMPP MySQL InnoDB tablespace, validates metadata against INFORMATION_SCHEMA, and executes parameterized relational checks.
            </p>

            {scanResult ? (
              <div className="mt-4 p-3.5 rounded-xl bg-slate-900 border border-slate-700 space-y-2 text-xs">
                <div className="flex justify-between font-mono">
                  <span className="text-slate-400">Scan ID:</span>
                  <span className="text-emerald-400 font-bold">{scanResult.scan_id}</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-slate-400">Rows Inspected:</span>
                  <span className="text-slate-200">{scanResult.total_rows_inspected}</span>
                </div>
                <div className="flex justify-between font-mono">
                  <span className="text-slate-400">Duration:</span>
                  <span className="text-slate-200">{scanResult.duration_ms} ms</span>
                </div>
                <div className="flex justify-between font-mono pt-2 border-t border-slate-800">
                  <span className="text-slate-400">Total Violations:</span>
                  <span className="text-rose-400 font-extrabold text-sm">{scanResult.issues_found}</span>
                </div>
              </div>
            ) : (
              <div className="mt-4 p-6 rounded-xl border border-dashed border-slate-800 text-center text-xs text-slate-500">
                Ready to execute. Click button below to start scanner.
              </div>
            )}
          </div>

          <div className="mt-6">
            <Button
              variant="primary"
              size="lg"
              icon={Play}
              loading={isScanning}
              onClick={handleExecuteScan}
              className="w-full font-bold"
            >
              {isScanning ? 'Inspecting Database...' : 'Run Scan Now'}
            </Button>
          </div>
        </div>
      </div>

      {/* Scan Results View */}
      {scanResult && (
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-rose-400" />
                Detected Integrity Violations ({scanResult.issues.length})
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Issues registered in catalog. Recommendations automatically generated for self-healing.
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
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Issue ID</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Table & Record</th>
                  <th className="py-2.5 px-3">Violation Details</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {scanResult.issues.map((issue) => (
                  <tr key={issue.issue_id} className="hover:bg-slate-800/30">
                    <td className="py-3 px-3 text-slate-300 font-bold">{issue.issue_id}</td>
                    <td className="py-3 px-3"><Badge variant={issue.severity} /></td>
                    <td className="py-3 px-3 text-slate-300">{issue.category}</td>
                    <td className="py-3 px-3 text-slate-200">
                      `{issue.table_name}`.id={issue.record_id}
                    </td>
                    <td className="py-3 px-3 font-sans text-slate-300 max-w-md">
                      {issue.description}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/repairs?issue=${issue.issue_id}`)}
                        className="text-xs text-emerald-400"
                      >
                        Self-Heal
                      </Button>
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
