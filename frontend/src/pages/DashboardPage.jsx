import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Database,
  ScanSearch,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Wrench,
  Clock,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  RefreshCw,
  Server,
  Activity,
  Layers,
  FileText
} from 'lucide-react';
import { databaseApi, scansApi, issuesApi, repairsApi, rulesApi, auditApi } from '../services/api';
import { StatCard } from '../components/common/StatCard';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dbStatus, setDbStatus] = useState(null);
  const [tables, setTables] = useState([]);
  const [rulesCount, setRulesCount] = useState(0);
  const [recentScans, setRecentScans] = useState([]);
  const [issuesData, setIssuesData] = useState({ total: 0, items: [] });
  const [pendingRecsCount, setPendingRecsCount] = useState(0);
  const [executions, setExecutions] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [isScanning, setIsScanning] = useState(false);

  const loadDashboardData = async () => {
    try {
      const [statusRes, tablesRes, rulesRes, scansRes, issuesRes, recsRes, execRes, auditRes] = await Promise.all([
        databaseApi.getStatus().catch(() => ({ data: null })),
        databaseApi.getTables().catch(() => ({ data: [] })),
        rulesApi.getRules().catch(() => ({ data: [] })),
        scansApi.getScans(5).catch(() => ({ data: [] })),
        issuesApi.getIssues({ limit: 100 }).catch(() => ({ data: { total: 0, items: [] } })),
        repairsApi.getRecommendations('PENDING').catch(() => ({ data: [] })),
        repairsApi.getExecutions(5).catch(() => ({ data: [] })),
        auditApi.getLogs({ limit: 6 }).catch(() => ({ data: { items: [] } })),
      ]);

      setDbStatus(statusRes.data);
      setTables(tablesRes.data || []);
      setRulesCount((rulesRes.data || []).length);
      setRecentScans(scansRes.data || []);
      setIssuesData(issuesRes.data || { total: 0, items: [] });
      setPendingRecsCount((recsRes.data || []).length);
      setExecutions(execRes.data || []);
      setAuditLogs(auditRes.data?.items || []);
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleScanNow = async () => {
    try {
      setIsScanning(true);
      await scansApi.triggerScan({ scan_type: 'FULL' });
      await loadDashboardData();
      navigate('/scanner');
    } catch (err) {
      console.error('Scan trigger error:', err);
    } finally {
      setIsScanning(false);
    }
  };

  if (loading) {
    return <LoadingSpinner label="Connecting to MySQL database and calculating metrics..." size="lg" />;
  }

  // Derive counts from live issues
  const allIssues = issuesData.items || [];
  const openCount = allIssues.filter(i => i.status === 'OPEN' || i.status === 'REVIEWED' || i.status === 'APPROVED').length;
  const repairedCount = allIssues.filter(i => i.status === 'REPAIRED').length;

  // Severity counts
  const criticalCount = allIssues.filter(i => i.severity === 'CRITICAL').length;
  const highCount = allIssues.filter(i => i.severity === 'HIGH').length;
  const mediumCount = allIssues.filter(i => i.severity === 'MEDIUM').length;
  const lowCount = allIssues.filter(i => i.severity === 'LOW').length;

  // Derive counts from tables
  const totalRecords = tables.reduce((acc, t) => acc + (t.row_count || 0), 0);
  const businessTables = tables.filter(t => t.table_type === 'BUSINESS');
  const businessRecords = businessTables.reduce((acc, t) => acc + (t.row_count || 0), 0);

  // Integrity Analysis calculations
  const uniqueViolationsCount = new Set(allIssues.map(i => `${i.table_name}-${i.record_id}`)).size;
  const healthyRecords = Math.max(0, totalRecords - uniqueViolationsCount);
  const integrityScore = totalRecords > 0 
    ? ((healthyRecords / totalRecords) * 100).toFixed(1) 
    : '100.0';

  const lastScan = recentScans[0];

  return (
    <div className="space-y-5 max-w-[1600px] mx-auto">
      {/* Page Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Database Integrity Monitoring
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time status of MySQL InnoDB relational constraints, active scans, and autonomous repair actions.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Button
            variant="secondary"
            size="sm"
            icon={RefreshCw}
            loading={refreshing}
            onClick={() => { setRefreshing(true); loadDashboardData(); }}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={ScanSearch}
            loading={isScanning}
            onClick={handleScanNow}
          >
            Execute Scan
          </Button>
        </div>
      </div>

      {/* TOP KPI SECTION - 6 Equal Height, Compact Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard
          title="Connection"
          value={dbStatus?.connected ? 'CONNECTED' : 'OFFLINE'}
          subtitle={dbStatus?.database_name || 'self_healing_test_db'}
          icon={Server}
          variant={dbStatus?.connected ? 'emerald' : 'rose'}
        />

        <StatCard
          title="Tables"
          value={tables.length}
          subtitle={`${businessTables.length} Business · ${tables.length - businessTables.length} System`}
          icon={Database}
          variant="sky"
        />

        <StatCard
          title="Total Records"
          value={totalRecords}
          subtitle={`${businessRecords} in retail tables`}
          icon={Layers}
          variant="emerald"
        />

        <StatCard
          title="Active Rules"
          value={rulesCount}
          subtitle="Enforced integrity rules"
          icon={ShieldCheck}
          variant="purple"
        />

        <StatCard
          title="Issues Found"
          value={issuesData.total}
          subtitle={`${openCount} open · ${repairedCount} healed`}
          icon={AlertTriangle}
          variant={openCount > 0 ? 'amber' : 'emerald'}
        />

        <StatCard
          title="Pending Actions"
          value={pendingRecsCount}
          subtitle={lastScan ? `Last scan: ${lastScan.issues_found} issues` : 'No scans executed'}
          icon={Clock}
          variant={pendingRecsCount > 0 ? 'rose' : 'emerald'}
        />
      </div>

      {/* SECTION A & B: Health Overview & Integrity Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Section A: Database Health Overview */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Server className="w-3.5 h-3.5 text-slate-500" /> Database Health Overview
            </h3>
            {dbStatus?.connected ? (
              <Badge variant="SUCCESS">Live Connection</Badge>
            ) : (
              <Badge variant="FAILED">Connection Failed</Badge>
            )}
          </div>

          <div className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-500 uppercase font-medium block">Database Name</span>
              <span className="font-mono font-semibold text-slate-900 truncate block mt-0.5">
                {dbStatus?.database_name || 'self_healing_test_db'}
              </span>
            </div>

            <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-500 uppercase font-medium block">Storage Engine</span>
              <span className="font-semibold text-slate-900 block mt-0.5">
                {dbStatus?.engine || 'InnoDB (ACID)'}
              </span>
            </div>

            <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-500 uppercase font-medium block">Server Version</span>
              <span className="font-mono text-slate-900 block mt-0.5 truncate">
                {dbStatus?.server_version || '10.4.x-MariaDB'}
              </span>
            </div>

            <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-500 uppercase font-medium block">Discovered Tables</span>
              <span className="font-mono font-bold text-slate-900 block mt-0.5">
                {tables.length} Total
              </span>
            </div>

            <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-500 uppercase font-medium block">Business Rows</span>
              <span className="font-mono font-bold text-slate-900 block mt-0.5">
                {businessRecords} Rows
              </span>
            </div>

            <div className="p-2.5 rounded bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-500 uppercase font-medium block">Last Scan Status</span>
              <span className="font-semibold text-slate-900 block mt-0.5">
                {lastScan ? `${lastScan.status} (${lastScan.duration_ms}ms)` : 'Never run'}
              </span>
            </div>
          </div>
        </div>

        {/* Section B: Integrity Analysis */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-slate-500" /> Relational Integrity Analysis
            </h3>
            <span className="text-xs font-mono font-bold text-slate-700">
              Score: <span className={Number(integrityScore) > 90 ? 'text-emerald-600' : 'text-amber-600'}>{integrityScore}%</span>
            </span>
          </div>

          <div className="p-4 space-y-3.5">
            {/* Progress Bar */}
            <div>
              <div className="flex justify-between text-xs text-slate-600 mb-1">
                <span>Healthy Records: <strong className="font-mono text-slate-900">{healthyRecords}</strong> / {totalRecords}</span>
                <span>Violations: <strong className="font-mono text-rose-600">{uniqueViolationsCount}</strong></span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden flex">
                <div 
                  className="bg-emerald-500 h-full transition-all duration-300" 
                  style={{ width: `${integrityScore}%` }} 
                />
                <div 
                  className="bg-rose-500 h-full transition-all duration-300" 
                  style={{ width: `${100 - Number(integrityScore)}%` }} 
                />
              </div>
            </div>

            {/* Severity Breakdown Pills */}
            <div className="grid grid-cols-4 gap-2 pt-1 text-center">
              <div className="p-2 rounded bg-rose-50 border border-rose-200">
                <span className="text-[10px] uppercase font-bold text-rose-800 block">Critical</span>
                <span className="text-sm font-bold font-mono text-rose-900">{criticalCount}</span>
              </div>
              <div className="p-2 rounded bg-amber-50 border border-amber-200">
                <span className="text-[10px] uppercase font-bold text-amber-800 block">High</span>
                <span className="text-sm font-bold font-mono text-amber-900">{highCount}</span>
              </div>
              <div className="p-2 rounded bg-sky-50 border border-sky-200">
                <span className="text-[10px] uppercase font-bold text-sky-800 block">Medium</span>
                <span className="text-sm font-bold font-mono text-sky-900">{mediumCount}</span>
              </div>
              <div className="p-2 rounded bg-slate-100 border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-700 block">Low</span>
                <span className="text-sm font-bold font-mono text-slate-800">{lowCount}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION C: Recent Integrity Issues Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> Recent Integrity Issues ({allIssues.length})
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/recovery')}
            className="text-xs text-indigo-600 font-medium"
          >
            View in Recovery Center <ArrowRight className="w-3 h-3 ml-1" />
          </Button>
        </div>

        {allIssues.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Issue ID</th>
                  <th className="py-2.5 px-3">Table</th>
                  <th className="py-2.5 px-3">Record ID</th>
                  <th className="py-2.5 px-3">Violation Type</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {allIssues.slice(0, 5).map((issue) => (
                  <tr key={issue.issue_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2 px-3 text-slate-900 font-bold">{issue.issue_id}</td>
                    <td className="py-2 px-3 text-slate-700">{issue.table_name}</td>
                    <td className="py-2 px-3 text-slate-600">#{issue.record_id}</td>
                    <td className="py-2 px-3 font-sans text-slate-700 truncate max-w-xs" title={issue.description}>
                      {issue.category}
                    </td>
                    <td className="py-2 px-3"><Badge variant={issue.severity} /></td>
                    <td className="py-2 px-3"><Badge variant={issue.status} /></td>
                    <td className="py-2 px-3 text-right">
                      {issue.status === 'REPAIRED' ? (
                        <span className="text-[11px] text-emerald-600 font-sans font-medium">Repaired</span>
                      ) : (
                        <button
                          onClick={() => navigate(`/repairs?issue=${issue.issue_id}`)}
                          className="text-xs text-indigo-600 hover:text-indigo-800 font-sans font-medium hover:underline"
                        >
                          Heal
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-slate-500">
            No active integrity violations detected.
          </div>
        )}
      </div>

      {/* SECTION D & E: Recent Repair Activity & Database Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Section D: Recent Repair Activity */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Wrench className="w-3.5 h-3.5 text-slate-500" /> Recent Repair Activity
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/repairs')}
              className="text-xs text-indigo-600 font-medium"
            >
              Repair Center <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </div>

          {executions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <tr>
                    <th className="py-2 px-3">Execution ID</th>
                    <th className="py-2 px-3">Table</th>
                    <th className="py-2 px-3">Strategy</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {executions.map((e) => (
                    <tr key={e.execution_id} className="hover:bg-slate-50/70">
                      <td className="py-2 px-3 text-slate-900 font-bold">{e.execution_id}</td>
                      <td className="py-2 px-3 text-slate-700">{e.table_name || 'N/A'}</td>
                      <td className="py-2 px-3 font-sans text-slate-600">{e.strategy || 'AUTOMATIC'}</td>
                      <td className="py-2 px-3"><Badge variant={e.status} /></td>
                      <td className="py-2 px-3 text-slate-500 text-[11px]">
                        {e.executed_at ? new Date(e.executed_at).toLocaleTimeString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6 text-center text-xs text-slate-500">
              No repairs executed yet. Open issues can be previewed and executed in the Repair Center.
            </div>
          )}
        </div>

        {/* Section E: Database Activity Log */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <FileText className="w-3.5 h-3.5 text-slate-500" /> Database Activity Log
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/audit')}
              className="text-xs text-indigo-600 font-medium"
            >
              Full Audit <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </div>

          {auditLogs.length > 0 ? (
            <div className="divide-y divide-slate-100 text-xs">
              {auditLogs.map((log) => (
                <div key={log.event_id} className="px-4 py-2.5 flex items-center justify-between gap-3 hover:bg-slate-50/70">
                  <div className="min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-mono font-bold text-slate-800 text-[11px]">{log.event_type}</span>
                      <Badge variant={log.result} />
                    </div>
                    <p className="text-slate-500 text-[11px] truncate mt-0.5" title={log.action_description}>
                      {log.action_description}
                    </p>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 flex-shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 text-center text-xs text-slate-500">
              No audit activities logged yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
