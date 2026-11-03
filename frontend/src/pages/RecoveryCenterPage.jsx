import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Wrench,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Play,
  RotateCcw,
  Eye,
  FileCode,
  ShieldCheck,
  RefreshCw,
  Archive,
  Trash2,
  Shuffle,
  Network,
  Filter,
  Search,
  Database,
  History,
  Layers,
  Clock,
  ArrowRight
} from 'lucide-react';
import { repairsApi, recoveryApi, databaseApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const CORE_SIX_TABLES = [
  'departments',
  'instructors',
  'courses',
  'students',
  'enrollments',
  'classrooms',
];

const SEVEN_REPAIR_STRATEGIES = [
  'QUARANTINE',
  'MAP_PARENT',
  'DELETE_RECORD',
  'SET_DEFAULT',
  'RESTORE_PARENT',
  'MERGE_DUPLICATION',
  'MANUAL_INTERVENTION',
];

export const RecoveryCenterPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('self_healing'); // 'self_healing' | 'checkpoints'
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [executions, setExecutions] = useState([]);

  // Checkpoints & Recovery
  const [checkpoints, setCheckpoints] = useState([]);
  const [recoveryHistory, setRecoveryHistory] = useState([]);
  const [createCkptModalOpen, setCreateCkptModalOpen] = useState(false);
  const [ckptTargetTable, setCkptTargetTable] = useState('students');
  const [ckptName, setCkptName] = useState('');
  const [creatingCkpt, setCreatingCkpt] = useState(false);
  const [selectedCkpt, setSelectedCkpt] = useState(null);
  const [rollbackConfirmOpen, setRollbackConfirmOpen] = useState(false);
  const [rollingBack, setRollingBack] = useState(false);

  // Filtering states across the six business tables
  const [tableFilter, setTableFilter] = useState('ALL');
  const [strategyFilter, setStrategyFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Preview & Execution Modal
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [activeRec, setActiveRec] = useState(null);
  const [processingRecId, setProcessingRecId] = useState(null);

  // Custom repair parameters
  const [overrideParentId, setOverrideParentId] = useState('');
  const [overrideValue, setOverrideValue] = useState('');
  const [manualNotes, setManualNotes] = useState('');

  // Confirmation Dialog
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [statusNotification, setStatusNotification] = useState(null);

  const fetchRepairsData = async () => {
    try {
      setLoading(true);
      const [recsRes, execsRes, ckptsRes, histRes] = await Promise.all([
        repairsApi.getRecommendations().catch(() => ({ data: [] })),
        repairsApi.getExecutions(30).catch(() => ({ data: [] })),
        recoveryApi.getCheckpoints(20).catch(() => ({ data: [] })),
        recoveryApi.getHistory().catch(() => ({ data: [] })),
      ]);
      setRecommendations(recsRes.data || []);
      setExecutions(execsRes.data || []);
      setCheckpoints(ckptsRes.data || []);
      setRecoveryHistory(histRes.data || []);
    } catch (err) {
      console.error('Failed to fetch recovery data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRepairsData();
  }, []);

  // If issue param is passed in URL, automatically trigger preview
  useEffect(() => {
    const issueId = searchParams.get('issue');
    if (issueId && recommendations.length > 0) {
      const match = recommendations.find(r => r.issue_id === issueId);
      if (match) {
        handleOpenPreview(match);
      }
    }
  }, [searchParams, recommendations]);

  const handleOpenPreview = async (rec) => {
    if (rec.issue_status === 'REPAIRED') {
      setStatusNotification({ type: 'info', message: 'This integrity issue has already been repaired.' });
      return;
    }
    setActiveRec(rec);
    setProcessingRecId(rec.recommendation_id);
    setOverrideParentId('');
    setOverrideValue('');
    setManualNotes('');
    setPreviewData(null);
    setExecutionResult(null);
    setStatusNotification(null);
    setPreviewModalOpen(true);
    setPreviewLoading(true);

    try {
      const payload = {
        issue_id: rec.issue_id,
        strategy: rec.strategy,
      };
      const res = await repairsApi.previewRepair(payload);
      setPreviewData(res.data);
      if (res.data?.status === 'ALREADY_REPAIRED') {
        setStatusNotification({
          type: 'info',
          message: 'Target record is already absent/quarantined. Issue has been auto-marked as REPAIRED.'
        });
      }
    } catch (err) {
      setPreviewModalOpen(false);
      if (err.status === 409 || err.message?.toLowerCase().includes('already repaired')) {
        setStatusNotification({ type: 'info', message: 'This integrity issue has already been repaired.' });
      } else {
        setStatusNotification({ type: 'error', message: err.message || 'Failed to load preview.' });
      }
      await fetchRepairsData();
    } finally {
      setPreviewLoading(false);
      setProcessingRecId(null);
    }
  };

  const handleUpdatePreviewInput = async (val, parentId, strategyOverride) => {
    if (!activeRec) return;
    try {
      const params = {};
      const pId = parentId !== undefined ? parentId : overrideParentId;
      const v = val !== undefined ? val : overrideValue;
      if (pId) params.parent_id = pId;
      if (v !== undefined && v !== '') params.value = v;

      const res = await repairsApi.previewRepair({
        issue_id: activeRec.issue_id,
        strategy: strategyOverride || activeRec.strategy || previewData?.strategy,
        repair_parameters: Object.keys(params).length > 0 ? params : undefined,
      });
      setPreviewData(res.data);
    } catch (err) {
      console.error("Preview update error:", err);
    }
  };

  const handleValueChange = (e) => {
    const val = e.target.value;
    setOverrideValue(val);
    handleUpdatePreviewInput(val, undefined);
  };

  const handleParentIdChange = (e) => {
    const pId = e.target.value;
    setOverrideParentId(pId);
    handleUpdatePreviewInput(undefined, pId);
  };

  const handleExecute = async () => {
    if (!activeRec || executing) return;
    setExecuting(true);
    setStatusNotification(null);
    try {
      const params = {};
      if (overrideParentId) params.parent_id = overrideParentId;
      if (overrideValue) params.value = overrideValue;
      if (manualNotes) params.notes = manualNotes;

      const payload = {
        issue_id: activeRec.issue_id,
        strategy: activeRec.strategy,
        repair_parameters: Object.keys(params).length > 0 ? params : undefined,
        admin_provided_value: overrideValue || undefined,
        row_version_token: previewData?.row_version_token,
        confirmed: true,
        operator: 'ADMIN_USER',
      };

      const res = await repairsApi.executeRepair(payload);
      setExecutionResult(res.data);
      setConfirmDialogOpen(false);
      setPreviewModalOpen(false);
      setStatusNotification({ type: 'success', message: res.data?.message || 'Repair successfully executed.' });
      await fetchRepairsData();
    } catch (err) {
      setConfirmDialogOpen(false);
      if (err.status === 409) {
        if (err.message?.toLowerCase().includes('modified') || err.message?.toLowerCase().includes('stale') || err.message?.toLowerCase().includes('refresh the preview')) {
          setStatusNotification({
            type: 'error',
            message: 'Database record has changed since preview was generated. Please refresh the preview before executing.'
          });
          handleUpdatePreviewInput(overrideValue, overrideParentId);
        } else {
          setPreviewModalOpen(false);
          setStatusNotification({ type: 'info', message: 'This integrity issue has already been repaired.' });
          await fetchRepairsData();
        }
      } else {
        setStatusNotification({ type: 'error', message: `Repair execution failed: ${err.message}` });
        await fetchRepairsData();
      }
    } finally {
      setExecuting(false);
    }
  };

  const handleCreateCheckpoint = async () => {
    if (!ckptName.trim()) return;
    try {
      setCreatingCkpt(true);
      await recoveryApi.createCheckpoint({
        target_table: ckptTargetTable,
        checkpoint_name: ckptName,
        checkpoint_type: 'MANUAL',
      });
      setCreateCkptModalOpen(false);
      setCkptName('');
      setStatusNotification({ type: 'success', message: `Recovery checkpoint created for table '${ckptTargetTable}'.` });
      await fetchRepairsData();
    } catch (err) {
      setStatusNotification({ type: 'error', message: `Checkpoint creation failed: ${err.message}` });
    } finally {
      setCreatingCkpt(false);
    }
  };

  const handleRollback = async () => {
    if (!selectedCkpt) return;
    try {
      setRollingBack(true);
      await recoveryApi.rollback({
        checkpoint_id: selectedCkpt.checkpoint_id,
        operator: 'ADMIN_USER',
        reason: 'Operator-initiated table state rollback from Recovery Center.'
      });
      setRollbackConfirmOpen(false);
      setSelectedCkpt(null);
      setStatusNotification({ type: 'success', message: `Successfully restored table state to checkpoint '${selectedCkpt.checkpoint_name}'.` });
      await fetchRepairsData();
    } catch (err) {
      setStatusNotification({ type: 'error', message: `Rollback failed: ${err.message}` });
    } finally {
      setRollingBack(false);
    }
  };

  // Filtered recommendations across the six business tables
  const filteredRecommendations = useMemo(() => {
    return recommendations.filter((rec) => {
      if (tableFilter !== 'ALL' && rec.table_name !== tableFilter) return false;
      if (strategyFilter !== 'ALL' && rec.strategy !== strategyFilter) return false;
      if (statusFilter === 'PENDING' && rec.issue_status === 'REPAIRED') return false;
      if (statusFilter === 'REPAIRED' && rec.issue_status !== 'REPAIRED') return false;
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const matchesId = (rec.issue_id || '').toLowerCase().includes(q);
        const matchesTable = (rec.table_name || '').toLowerCase().includes(q);
        const matchesRecId = String(rec.record_id || '').toLowerCase().includes(q);
        const matchesAction = (rec.proposed_action || '').toLowerCase().includes(q);
        const matchesStrategy = (rec.strategy || '').toLowerCase().includes(q);
        if (!matchesId && !matchesTable && !matchesRecId && !matchesAction && !matchesStrategy) {
          return false;
        }
      }
      return true;
    });
  }, [recommendations, tableFilter, strategyFilter, statusFilter, searchQuery]);

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Wrench className="w-5 h-5 text-indigo-600" />
            Recovery Center & Autonomous Healing Hub
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Unified control center for detected relational violations, idempotent repair previews, and table snapshot rollbacks.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Tab Switcher */}
          <div className="flex bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <button
              onClick={() => setActiveTab('self_healing')}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === 'self_healing' ? 'bg-white text-indigo-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Self-Healing Issues ({recommendations.filter(r => r.issue_status !== 'REPAIRED').length})
            </button>
            <button
              onClick={() => setActiveTab('checkpoints')}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === 'checkpoints' ? 'bg-white text-indigo-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Recovery Checkpoints ({checkpoints.length})
            </button>
          </div>

          <Button variant="secondary" size="sm" onClick={fetchRepairsData} disabled={loading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          {activeTab === 'checkpoints' && (
            <Button variant="primary" size="sm" onClick={() => setCreateCkptModalOpen(true)} className="bg-indigo-600 text-white">
              <History className="w-3.5 h-3.5 mr-1" />
              New Checkpoint
            </Button>
          )}
        </div>
      </div>

      {/* Global Status Notification */}
      {statusNotification && (
        <div
          className={`p-3 rounded-lg border text-xs flex items-center justify-between ${
            statusNotification.type === 'error'
              ? 'bg-rose-50 border-rose-200 text-rose-800'
              : statusNotification.type === 'info'
              ? 'bg-indigo-50 border-indigo-200 text-indigo-800'
              : 'bg-emerald-50 border-emerald-200 text-emerald-800'
          }`}
        >
          <div className="flex items-center gap-2">
            {statusNotification.type === 'error' ? (
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-600" />
            ) : statusNotification.type === 'info' ? (
              <ShieldCheck className="w-4 h-4 flex-shrink-0 text-indigo-600" />
            ) : (
              <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
            )}
            <span className="font-medium">{statusNotification.message}</span>
          </div>
          <button
            onClick={() => setStatusNotification(null)}
            className="text-xs font-bold px-2 py-0.5 rounded hover:bg-black/5"
          >
            &times;
          </button>
        </div>
      )}

      {/* TAB 1: SELF-HEALING RECOMMENDATIONS */}
      {activeTab === 'self_healing' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="bg-white p-3.5 rounded-lg border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs shadow-xs">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-slate-400 font-semibold flex items-center gap-1">
                <Filter className="w-3.5 h-3.5" /> Filter:
              </span>

              {/* Table Filter */}
              <select
                value={tableFilter}
                onChange={(e) => setTableFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded border border-slate-300 bg-white font-medium text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="ALL">All Six Tables</option>
                {CORE_SIX_TABLES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>

              {/* Strategy Filter (7 Strategies) */}
              <select
                value={strategyFilter}
                onChange={(e) => setStrategyFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded border border-slate-300 bg-white font-medium text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="ALL">All 7 Strategies</option>
                {SEVEN_REPAIR_STRATEGIES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded border border-slate-300 bg-white font-medium text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="ALL">All Statuses</option>
                <option value="PENDING">Pending Action</option>
                <option value="REPAIRED">Repaired / Resolved</option>
              </select>
            </div>

            {/* Search Input */}
            <div className="relative min-w-[220px]">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search issues, rows, rules..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 rounded border border-slate-300 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
              </input>
            </div>
          </div>

          {/* Recommendations Table */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Active Relational Issues & Applicable Strategies ({filteredRecommendations.length})
              </span>
              <span className="text-xs text-slate-500">
                Scope: Six Target Tables (Departments, Instructors, Courses, Students, Enrollments, Classrooms)
              </span>
            </div>

            {loading ? (
              <div className="py-12">
                <LoadingSpinner label="Loading self-healing recommendations..." />
              </div>
            ) : filteredRecommendations.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-semibold">
                    <tr>
                      <th className="py-2.5 px-3">Issue ID</th>
                      <th className="py-2.5 px-3">Target Table & PK</th>
                      <th className="py-2.5 px-3">Severity</th>
                      <th className="py-2.5 px-3">Applicable Strategy</th>
                      <th className="py-2.5 px-3">Proposed Self-Healing Action</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredRecommendations.map((rec) => {
                      const isRepaired = rec.issue_status === 'REPAIRED';
                      // Strict 3-level severity normalization
                      const sev = (rec.risk_level || 'HIGH').toUpperCase();
                      const cleanSev = sev === 'MEDIUM' ? 'HIGH' : (['CRITICAL', 'HIGH', 'LOW'].includes(sev) ? sev : 'HIGH');

                      return (
                        <tr key={rec.recommendation_id} className={`hover:bg-slate-50/80 transition-colors ${isRepaired ? 'opacity-60 bg-slate-50/40' : ''}`}>
                          <td className="py-2.5 px-3 font-mono font-medium text-slate-900 whitespace-nowrap">
                            {rec.issue_id}
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap">
                            <span className="font-semibold text-slate-900">{rec.table_name}</span>
                            <span className="text-slate-400 font-mono ml-1.5">(PK: {rec.record_id})</span>
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap">
                            <Badge variant={cleanSev}>{cleanSev}</Badge>
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap font-mono">
                            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-800 border border-slate-200">
                              {rec.strategy}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-slate-600 max-w-md truncate" title={rec.proposed_action}>
                            {rec.proposed_action}
                          </td>
                          <td className="py-2.5 px-3 whitespace-nowrap">
                            {isRepaired ? (
                              <Badge variant="LOW">REPAIRED</Badge>
                            ) : (
                              <Badge variant="HIGH">PENDING</Badge>
                            )}
                          </td>
                          <td className="py-2.5 px-3 text-right whitespace-nowrap">
                            {isRepaired ? (
                              <span className="text-xs text-slate-400 font-medium">Auto-Resolved</span>
                            ) : (
                              <Button
                                variant="primary"
                                size="sm"
                                disabled={processingRecId === rec.recommendation_id}
                                onClick={() => handleOpenPreview(rec)}
                                className="bg-indigo-600 text-white hover:bg-indigo-700"
                              >
                                <Play className="w-3 h-3 mr-1" />
                                Review & Heal
                              </Button>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-400">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
                <p className="font-semibold text-slate-700">No active integrity violations found matching your filter.</p>
                <p className="text-slate-500 mt-0.5">Run a scan in the Integrity Scanner or inject data via Data Ingestion to simulate anomalies.</p>
              </div>
            )}
          </div>

          {/* Execution History Card */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Recent Repair Executions & ACID Verifications ({executions.length})
              </span>
              <span className="text-xs font-mono text-slate-400">InnoDB Savepoint Audited</span>
            </div>
            {executions.length > 0 ? (
              <div className="overflow-x-auto max-h-72">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-semibold sticky top-0">
                    <tr>
                      <th className="py-2 px-3">Execution ID</th>
                      <th className="py-2 px-3">Tx ID</th>
                      <th className="py-2 px-3">Strategy</th>
                      <th className="py-2 px-3">Status</th>
                      <th className="py-2 px-3">Time</th>
                      <th className="py-2 px-3">SQL Log</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {executions.map((e) => (
                      <tr key={e.execution_id} className="hover:bg-slate-50">
                        <td className="py-1.5 px-3 text-indigo-600 font-bold">{e.execution_id}</td>
                        <td className="py-1.5 px-3 text-slate-600">{e.transaction_id}</td>
                        <td className="py-1.5 px-3 font-sans font-semibold text-slate-800">{e.strategy}</td>
                        <td className="py-1.5 px-3">
                          <span className="text-emerald-700 font-bold">SUCCESS</span>
                        </td>
                        <td className="py-1.5 px-3 text-slate-500">{e.execution_time_ms} ms</td>
                        <td className="py-1.5 px-3 text-slate-600 max-w-sm truncate" title={e.sql_executed}>
                          {e.sql_executed}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-xs text-slate-400 py-6 text-center">No repair executions logged yet.</p>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: RECOVERY CHECKPOINTS & ROLLBACK */}
      {activeTab === 'checkpoints' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-indigo-50/60 border border-indigo-200">
              <span className="text-xs text-indigo-800 font-semibold block mb-1">Pre-Repair Snapshot Isolation</span>
              <p className="text-xs text-slate-600">
                Every destructive repair automatically captures a serialized JSON checkpoint row in <code className="text-indigo-700 font-bold">recovery_checkpoints</code> before SQL execution.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-emerald-50/60 border border-emerald-200">
              <span className="text-xs text-emerald-800 font-semibold block mb-1">Point-In-Time Restoration</span>
              <p className="text-xs text-slate-600">
                1-click rollback transactionally restores original record states back to the master production table and purges quarantine entries.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-800 font-semibold block mb-1">Immutable Audit Traceability</span>
              <p className="text-xs text-slate-600">
                All checkpoint creations and rollback restorations are logged into <code className="text-slate-700 font-bold">audit_logs</code> with operator ID and timestamps.
              </p>
            </div>
          </div>

          {/* Checkpoints Table */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-xs">
            <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Available Table State Checkpoints ({checkpoints.length})
              </span>
              <span className="text-xs text-slate-500">Stored in recovery_checkpoints</span>
            </div>

            {checkpoints.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-semibold">
                    <tr>
                      <th className="py-2.5 px-3">Checkpoint ID</th>
                      <th className="py-2.5 px-3">Name</th>
                      <th className="py-2.5 px-3">Target Table</th>
                      <th className="py-2.5 px-3">Type</th>
                      <th className="py-2.5 px-3">Row Filter</th>
                      <th className="py-2.5 px-3">Created At</th>
                      <th className="py-2.5 px-3 text-right">Rollback Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {checkpoints.map((c) => (
                      <tr key={c.checkpoint_id} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-mono font-medium text-slate-900">{c.checkpoint_id}</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-800">{c.checkpoint_name}</td>
                        <td className="py-2.5 px-3 font-mono text-indigo-600">{c.target_table}</td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                            {c.checkpoint_type}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-mono text-slate-500">{c.row_id_filter || 'Full Table'}</td>
                        <td className="py-2.5 px-3 text-slate-500 whitespace-nowrap">{new Date(c.created_at).toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-right">
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => {
                              setSelectedCkpt(c);
                              setRollbackConfirmOpen(true);
                            }}
                            className="text-amber-700 hover:bg-amber-50 border-amber-200"
                          >
                            <RotateCcw className="w-3 h-3 mr-1 text-amber-600" />
                            Rollback Table
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-xs text-slate-400 py-8 text-center">No checkpoints available yet.</p>
            )}
          </div>
        </div>
      )}

      {/* Repair Preview & Transaction Execution Modal */}
      <Modal
        isOpen={previewModalOpen}
        onClose={() => setPreviewModalOpen(false)}
        title="Self-Healing Transaction Preview & Safety Check"
        subtitle={previewData ? `Target: ${previewData.table_name} (Row ID: ${previewData.record_id})` : ''}
        maxWidth="max-w-3xl"
      >
        {previewLoading ? (
          <div className="py-8">
            <LoadingSpinner label="Calculating transaction impact, before/after diffs, and SQL preview..." />
          </div>
        ) : previewData ? (
          <div className="space-y-4">
            {/* Risk & Safety Warning Banner */}
            <div className="p-3 rounded bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="text-slate-500 font-medium">Chosen Strategy:</span>
                <span className="font-bold text-slate-900 font-mono px-2 py-0.5 rounded bg-white border border-slate-200">
                  {previewData.strategy}
                </span>
              </div>
              <Badge variant={previewData.risk_level === 'MEDIUM' ? 'HIGH' : previewData.risk_level}>
                Risk: {previewData.risk_level === 'MEDIUM' ? 'HIGH' : previewData.risk_level}
              </Badge>
            </div>

            {previewData.warning && (
              <div className="p-2.5 rounded bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-600" />
                <span>{previewData.warning}</span>
              </div>
            )}

            {/* QUARANTINE Strategy Notice */}
            {previewData.strategy === 'QUARANTINE' && (
              <div className="p-3 rounded bg-purple-50 border border-purple-200 text-xs space-y-1">
                <div className="font-bold text-purple-900 flex items-center gap-1.5">
                  <Archive className="w-3.5 h-3.5 text-purple-700" />
                  Quarantine Archival Operation (Zero Data Loss)
                </div>
                <p className="text-[11px] text-purple-800 leading-relaxed">
                  1. The original row from <strong className="font-mono">`{previewData.table_name}`</strong> will be serialized to JSON.
                  <br />
                  2. Row is inserted into <strong className="font-mono">`quarantine_records`</strong> with audit timestamp and issue reason.
                  <br />
                  3. Deleted from <strong className="font-mono">`{previewData.table_name}`</strong> only after successful quarantine storage inside the same transaction.
                </p>
              </div>
            )}

            {/* MAP_PARENT Strategy Notice */}
            {previewData.strategy === 'MAP_PARENT' && (
              <div className="p-3.5 rounded bg-slate-50 border border-slate-200 space-y-2">
                <label className="text-xs font-bold text-slate-800 block">
                  Authoritative Parent ID to Map:
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={overrideParentId}
                    onChange={handleParentIdChange}
                    placeholder="Enter verified parent ID (e.g., 1)..."
                    className="w-full px-3 py-1.5 bg-white border border-slate-300 rounded text-xs text-slate-900 font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                {previewData.validation_error && (
                  <p className="text-[11px] text-rose-600 font-mono font-bold">{previewData.validation_error}</p>
                )}
              </div>
            )}

            {/* SET_DEFAULT Strategy Notice */}
            {previewData.strategy === 'SET_DEFAULT' && (
              <div className="p-3.5 rounded bg-amber-50/70 border border-amber-200 space-y-2">
                <label className="text-xs font-bold text-amber-900 block">
                  Administrator Replacement Value for Column:
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={overrideValue}
                    onChange={handleValueChange}
                    placeholder={`Enter sanitized replacement value...`}
                    className="flex-1 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs text-slate-900 font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                {previewData.validation_error && (
                  <p className="text-[11px] text-rose-600 font-mono font-bold">{previewData.validation_error}</p>
                )}
              </div>
            )}

            {/* RESTORE_PARENT Notice */}
            {previewData.strategy === 'RESTORE_PARENT' && (
              <div className="p-3 rounded bg-sky-50 border border-sky-200 text-xs space-y-1">
                <span className="font-bold text-sky-950 flex items-center gap-1">
                  <RotateCcw className="w-3.5 h-3.5 text-sky-700" />
                  Parent Entity Baseline Restoration
                </span>
                <p className="text-[11px] text-sky-800">
                  Recreates missing parent stub or restores parent from quarantine vault to resolve orphan foreign key constraint.
                </p>
              </div>
            )}

            {/* MERGE_DUPLICATION Notice */}
            {(previewData.strategy === 'MERGE_DUPLICATION' || previewData.strategy === 'MERGE_DUPLICATE') && (
              <div className="p-3 rounded bg-amber-50 border border-amber-200 text-xs space-y-1">
                <span className="font-bold text-amber-950 flex items-center gap-1">
                  <Shuffle className="w-3.5 h-3.5 text-amber-700" />
                  Duplicate Record Consolidation & Merge
                </span>
                <p className="text-[11px] text-amber-800">
                  Archives redundant duplicate row into quarantine and reassigns child foreign keys to the primary canonical record.
                </p>
              </div>
            )}

            {/* MANUAL_INTERVENTION Notice */}
            {previewData.strategy === 'MANUAL_INTERVENTION' && (
              <div className="p-3.5 rounded bg-slate-100 border border-slate-300 text-xs space-y-2">
                <span className="font-bold text-slate-900 block">Manual Operator Verification Notes:</span>
                <textarea
                  rows={2}
                  value={manualNotes}
                  onChange={(e) => setManualNotes(e.target.value)}
                  placeholder="Document administrator review steps or justification..."
                  className="w-full text-xs p-2 rounded border border-slate-300 bg-white"
                />
              </div>
            )}

            {/* Before vs After State Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Current Before State
                </label>
                <pre className="p-2.5 rounded bg-slate-900 text-slate-200 font-mono text-[11px] max-h-40 overflow-auto border border-slate-800">
                  {JSON.stringify(previewData.before_state, null, 2)}
                </pre>
              </div>
              <div>
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Simulated After State
                </label>
                <pre className="p-2.5 rounded bg-slate-900 text-emerald-400 font-mono text-[11px] max-h-40 overflow-auto border border-slate-800">
                  {JSON.stringify(previewData.after_state, null, 2)}
                </pre>
              </div>
            </div>

            {/* SQL Preview */}
            <div>
              <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1 flex items-center gap-1">
                <FileCode className="w-3.5 h-3.5" />
                Atomic SQL Statements to Execute
              </label>
              <pre className="p-2.5 rounded bg-slate-900 text-indigo-300 font-mono text-[11px] overflow-x-auto border border-slate-800">
                {previewData.sql_preview?.join('\n') || '-- No SQL statements required'}
              </pre>
            </div>

            {/* Modal Actions */}
            <div className="pt-3 border-t border-slate-200 flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-mono">
                {previewData.status === 'ALREADY_REPAIRED' ? 'Status: ALREADY_REPAIRED' : 'ACID Transaction Ready'}
              </span>

              <div className="flex items-center gap-2">
                <Button variant="secondary" size="sm" onClick={() => setPreviewModalOpen(false)}>
                  Close
                </Button>

                {previewData.status !== 'ALREADY_REPAIRED' && (
                  <Button
                    variant={previewData.is_destructive ? 'danger' : 'primary'}
                    size="sm"
                    loading={executing}
                    onClick={() => {
                      if (previewData.is_destructive) {
                        setConfirmDialogOpen(true);
                      } else {
                        handleExecute();
                      }
                    }}
                    className={previewData.is_destructive ? '' : 'bg-indigo-600 text-white hover:bg-indigo-700'}
                  >
                    <Play className="w-3 h-3 mr-1" />
                    {executing ? 'Executing...' : 'Execute Transaction Safe Repair'}
                  </Button>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </Modal>

      {/* Confirmation Dialog for Destructive Repair */}
      <ConfirmDialog
        isOpen={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        onConfirm={handleExecute}
        loading={executing}
        title="Confirm Self-Healing Repair Execution"
        message={`You are about to execute '${activeRec?.strategy}' on table '${previewData?.table_name}'. An application recovery checkpoint will be taken before execution, and the transaction will automatically rollback if integrity verification fails.`}
        confirmText="Confirm & Commit Repair"
      />

      {/* Create Manual Checkpoint Modal */}
      <Modal
        isOpen={createCkptModalOpen}
        onClose={() => setCreateCkptModalOpen(false)}
        title="Create Table State Recovery Checkpoint"
        maxWidth="max-w-md"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Target Business Table:</label>
            <select
              value={ckptTargetTable}
              onChange={(e) => setCkptTargetTable(e.target.value)}
              className="w-full p-2 border border-slate-300 rounded bg-white text-xs font-mono"
            >
              {CORE_SIX_TABLES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Checkpoint Label:</label>
            <input
              type="text"
              value={ckptName}
              onChange={(e) => setCkptName(e.target.value)}
              placeholder="e.g. Pre-Exam Grade Audit Snapshot"
              className="w-full p-2 border border-slate-300 rounded text-xs"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
            <Button variant="secondary" size="sm" onClick={() => setCreateCkptModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleCreateCheckpoint} loading={creatingCkpt} className="bg-indigo-600 text-white">
              Save Checkpoint
            </Button>
          </div>
        </div>
      </Modal>

      {/* Rollback Confirmation Dialog */}
      <ConfirmDialog
        isOpen={rollbackConfirmOpen}
        onClose={() => setRollbackConfirmOpen(false)}
        onConfirm={handleRollback}
        loading={rollingBack}
        title="Confirm Table State Rollback"
        message={`Are you sure you want to rollback table '${selectedCkpt?.target_table}' to checkpoint '${selectedCkpt?.checkpoint_name}'? Original snapshot data will be restored transactionally.`}
        confirmText="Execute Rollback"
      />
    </div>
  );
};

export default RecoveryCenterPage;
