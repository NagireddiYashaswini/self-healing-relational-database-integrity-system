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
  RefreshCw
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { databaseApi, scansApi, issuesApi, repairsApi } from '../services/api';
import { StatCard } from '../components/common/StatCard';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const SEVERITY_COLORS = {
  CRITICAL: '#f43f5e',
  HIGH: '#f59e0b',
  MEDIUM: '#38bdf8',
  LOW: '#94a3b8',
};

const CATEGORY_COLORS = {
  ORPHAN: '#f43f5e',
  DUPLICATE: '#f59e0b',
  NULL_VIOLATION: '#818cf8',
  DOMAIN_VIOLATION: '#38bdf8',
  RELATIONAL_VIOLATION: '#c084fc',
};

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dbStatus, setDbStatus] = useState(null);
  const [recentScans, setRecentScans] = useState([]);
  const [issuesData, setIssuesData] = useState({ total: 0, items: [] });
  const [executions, setExecutions] = useState([]);
  const [isScanning, setIsScanning] = useState(false);

  const loadDashboardData = async () => {
    try {
      const [statusRes, scansRes, issuesRes, execRes] = await Promise.all([
        databaseApi.getStatus(),
        scansApi.getScans(5),
        issuesApi.getIssues({ limit: 100 }),
        repairsApi.getExecutions(5),
      ]);

      setDbStatus(statusRes.data);
      setRecentScans(scansRes.data || []);
      setIssuesData(issuesRes.data || { total: 0, items: [] });
      setExecutions(execRes.data || []);
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
  const failedCount = allIssues.filter(i => i.status === 'FAILED').length;

  // Severity Chart Data
  const severityMap = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  allIssues.forEach(i => {
    if (severityMap[i.severity] !== undefined) severityMap[i.severity]++;
  });
  const severityChartData = Object.entries(severityMap).map(([name, value]) => ({ name, value }));

  // Category Chart Data
  const categoryMap = {};
  allIssues.forEach(i => {
    const cat = i.category;
    categoryMap[cat] = (categoryMap[cat] || 0) + 1;
  });
  const categoryChartData = Object.entries(categoryMap).map(([name, count]) => ({
    name: name.replace('_', ' '),
    count,
  }));

  const lastScan = recentScans[0];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            System Overview & Health
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time monitoring of relational integrity, active scans, and transaction-safe self-healing operations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            loading={refreshing}
            onClick={() => { setRefreshing(true); loadDashboardData(); }}
          >
            Refresh Metrics
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={ScanSearch}
            loading={isScanning}
            onClick={handleScanNow}
          >
            Execute Full Scan
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Database State"
          value={dbStatus?.connected ? 'CONNECTED' : 'OFFLINE'}
          subtitle={`${dbStatus?.database_name || 'self_healing_db'} • ${dbStatus?.tables?.length || 0} Tables`}
          icon={Database}
          variant={dbStatus?.connected ? 'emerald' : 'rose'}
        />

        <StatCard
          title="Total Issues Detected"
          value={issuesData.total}
          subtitle={`Across ${recentScans.length} recorded scan run(s)`}
          icon={AlertTriangle}
          variant="amber"
        />

        <StatCard
          title="Pending / Open Issues"
          value={openCount}
          subtitle="Require administrator review or approval"
          icon={Clock}
          variant="rose"
        />

        <StatCard
          title="Successfully Healed"
          value={repairedCount}
          subtitle={`${failedCount} failed attempts recorded`}
          icon={Wrench}
          variant="purple"
        />
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution Pie Chart */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">Issue Severity Breakdown</h3>
              <p className="text-xs text-slate-400 mt-0.5">Classification by integrity failure severity</p>
            </div>
            <Badge variant="HIGH">{allIssues.length} Total</Badge>
          </div>

          <div className="h-64 flex items-center justify-center">
            {allIssues.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {severityChartData.map((entry) => (
                      <Cell key={`cell-${entry.name}`} fill={SEVERITY_COLORS[entry.name] || '#94a3b8'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-slate-500 text-xs">
                No active integrity issues detected. Database is completely healthy.
              </div>
            )}
          </div>
        </div>

        {/* Category Breakdown Bar Chart */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">Violation Categories</h3>
              <p className="text-xs text-slate-400 mt-0.5">Distribution across relational check categories</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => navigate('/issues')} className="text-xs text-emerald-400">
              View All <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>

          <div className="h-64">
            {categoryChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} interval={0} angle={-15} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                No categorized violations present.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Activity: Scans & Repairs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Scans Table */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <ScanSearch className="w-4 h-4 text-emerald-400" /> Recent Integrity Scans
            </h3>
            <Button variant="ghost" size="sm" onClick={() => navigate('/scanner')} className="text-xs text-emerald-400">
              View History <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>

          {recentScans.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2.5">Scan ID</th>
                    <th className="pb-2.5">Status</th>
                    <th className="pb-2.5">Rows Inspected</th>
                    <th className="pb-2.5">Issues</th>
                    <th className="pb-2.5">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {recentScans.map((s) => (
                    <tr key={s.scan_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-2.5 font-mono text-slate-200">{s.scan_id}</td>
                      <td className="py-2.5"><Badge variant={s.status} /></td>
                      <td className="py-2.5 font-mono text-slate-400">{s.total_rows_inspected}</td>
                      <td className="py-2.5">
                        <span className={`font-mono font-bold ${s.issues_found > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                          {s.issues_found}
                        </span>
                      </td>
                      <td className="py-2.5 font-mono text-slate-400">{s.duration_ms ? `${s.duration_ms} ms` : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-xs text-slate-500">
              No scans performed yet. Click "Execute Full Scan" to inspect database.
            </div>
          )}
        </div>

        {/* Recent Repair Executions Table */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <Wrench className="w-4 h-4 text-purple-400" /> Recent Self-Healing Executions
            </h3>
            <Button variant="ghost" size="sm" onClick={() => navigate('/repairs')} className="text-xs text-purple-400">
              Repair Center <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>

          {executions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2.5">Execution ID</th>
                    <th className="pb-2.5">Table</th>
                    <th className="pb-2.5">Status</th>
                    <th className="pb-2.5">Executed At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {executions.map((e) => (
                    <tr key={e.execution_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-2.5 font-mono text-slate-200">{e.execution_id}</td>
                      <td className="py-2.5 font-mono text-slate-300">{e.table_name || 'N/A'}</td>
                      <td className="py-2.5"><Badge variant={e.status} /></td>
                      <td className="py-2.5 font-mono text-slate-400">
                        {e.executed_at ? new Date(e.executed_at).toLocaleTimeString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-xs text-slate-500">
              No self-healing operations executed yet. Open issues can be repaired in the Repair Center.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
