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
  Database
} from 'lucide-react';
import { repairsApi, issuesApi } from '../services/api';
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
  'staging_enrollments',
];

export const RepairCenterPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [executions, setExecutions] = useState([]);

  // Filtering states across all six tables
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

  // Confirmation Dialog
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [statusNotification, setStatusNotification] = useState(null);

  const fetchRepairsData = async () => {
    try {
      setLoading(true);
      const [recsRes, execsRes] = await Promise.all([
        repairsApi.getRecommendations(),
        repairsApi.getExecutions(20),
      ]);
      setRecommendations(recsRes.data || []);
      setExecutions(execsRes.data || []);
    } catch (err) {
      console.error('Failed to fetch repairs data:', err);
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
      setStatusNotification({ type: 'error', message: 'This integrity issue has already been repaired. Duplicate execution is not allowed.' });
      return;
    }
    setActiveRec(rec);
    setProcessingRecId(rec.recommendation_id);
    setOverrideParentId('');
    setOverrideValue('');
    setPreviewModalOpen(true);
    setPreviewLoading(true);
    setExecutionResult(null);
    setStatusNotification(null);
    try {
      const payload = {
        issue_id: rec.issue_id,
        strategy: rec.strategy,
      };
      const res = await repairsApi.previewRepair(payload);
      setPreviewData(res.data);
    } catch (err) {
      setPreviewModalOpen(false);
      if (err.status === 409 || err.message?.toLowerCase().includes('already repaired') || err.message?.toLowerCase().includes('already been repaired')) {
        setStatusNotification({ type: 'error', message: 'This integrity issue has already been repaired. Duplicate execution is not allowed.' });
      } else {
        setStatusNotification({ type: 'error', message: err.message || 'Failed to load preview.' });
      }
      await fetchRepairsData();
    } finally {
      setPreviewLoading(false);
      setProcessingRecId(null);
    }
  };

  const handleUpdatePreviewInput = async (val, parentId) => {
    if (!activeRec) return;
    try {
      const params = {};
      const pId = parentId !== undefined ? parentId : overrideParentId;
      const v = val !== undefined ? val : overrideValue;
      if (pId) params.parent_id = pId;
      if (v !== undefined && v !== '') params.value = v;

      const res = await repairsApi.previewRepair({
        issue_id: activeRec.issue_id,
        strategy: activeRec.strategy || previewData?.strategy,
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
          setStatusNotification({ type: 'error', message: 'This integrity issue has already been repaired. Duplicate execution is not allowed.' });
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

  // Filtered recommendations across all six tables
  const filteredRecommendations = useMemo(() => {
    return recommendations.filter((rec) => {
      if (tableFilter !== 'ALL' && rec.table_name !== tableFilter) return false;
      if (strategyFilter !== 'ALL' && rec.strategy !== strategyFilter) return false;
      if (statusFilter === 'PENDING' && rec.issue_status === 'REPAIRED') return false;
      if (statusFilter === 'REPAIRED' && rec.issue_status !== 'REPAIRED') return false;
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const matchesId = rec.issue_id.toLowerCase().includes(q);
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

  // Unique strategies present in recommendations
  const availableStrategies = useMemo(() => {
    const set = new Set();
    recommendations.forEach(r => { if (r.strategy) set.add(r.strategy); });
    return Array.from(set);
  }, [recommendations]);

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Wrench className="w-5 h-5 text-indigo-600" />
            Self-Healing Operations & Repair Center
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            ACID transaction-safe repair actions across all six schema tables: preview before/after diffs, blast radius calculation, state rollback protection, and durability logs.
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          onClick={fetchRepairsData}
        >
          Refresh Actions
        </Button>
      </div>

      {/* Global Status / Error Notification */}
      {statusNotification && (
        <div className={`p-3 rounded-md flex items-center justify-between text-xs border ${
          statusNotification.type === 'error' 
            ? 'bg-rose-50 border-rose-200 text-rose-800' 
            : 'bg-emerald-50 border-emerald-200 text-emerald-800'
        }`}>
          <div className="flex items-center gap-2 font-medium">
            {statusNotification.type === 'error' ? (
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-600" />
            ) : (
              <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
            )}
            <span>{statusNotification.message}</span>
          </div>
          <button 
            onClick={() => setStatusNotification(null)}
            className="text-slate-500 hover:text-slate-800 font-bold px-2 py-0.5 rounded hover:bg-black/5"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Sections: Pending Recommendations + Past Executions */}
      <div className="space-y-4">
        {/* Section 1: Pending Recommendations Table */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
                <Wrench className="w-3.5 h-3.5 text-indigo-600" />
                Healing Recommendations ({filteredRecommendations.length} of {recommendations.length})
              </h3>
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 font-bold">
                  Pending: {recommendations.filter(r => r.issue_status !== 'REPAIRED').length}
                </span>
                <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold">
                  Repaired: {recommendations.filter(r => r.issue_status === 'REPAIRED').length}
                </span>
              </div>
            </div>

            {/* Filter Pills Bar Covering All Six Tables */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
              {/* Table Selector */}
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded text-[11px]">
                <span className="px-1 text-slate-500 font-bold uppercase text-[9px]">Table:</span>
                <button
                  onClick={() => setTableFilter('ALL')}
                  className={`px-1.5 py-0.5 rounded ${tableFilter === 'ALL' ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                >
                  All (6)
                </button>
                {CORE_SIX_TABLES.map(tbl => (
                  <button
                    key={tbl}
                    onClick={() => setTableFilter(tbl)}
                    className={`px-1.5 py-0.5 rounded ${tableFilter === tbl ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                  >
                    {tbl}
                  </button>
                ))}
              </div>

              {/* Strategy Selector */}
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded text-[11px]">
                <span className="px-1 text-slate-500 font-bold uppercase text-[9px]">Strategy:</span>
                <button
                  onClick={() => setStrategyFilter('ALL')}
                  className={`px-1.5 py-0.5 rounded ${strategyFilter === 'ALL' ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                >
                  All
                </button>
                {availableStrategies.map(st => (
                  <button
                    key={st}
                    onClick={() => setStrategyFilter(st)}
                    className={`px-1.5 py-0.5 rounded ${strategyFilter === st ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                  >
                    {st}
                  </button>
                ))}
              </div>

              {/* Status Selector */}
              <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded text-[11px]">
                <span className="px-1 text-slate-500 font-bold uppercase text-[9px]">Status:</span>
                {[
                  { id: 'ALL', label: 'All' },
                  { id: 'PENDING', label: 'Pending' },
                  { id: 'REPAIRED', label: 'Repaired' }
                ].map(s => (
                  <button
                    key={s.id}
                    onClick={() => setStatusFilter(s.id)}
                    className={`px-1.5 py-0.5 rounded ${statusFilter === s.id ? 'bg-white text-slate-900 font-bold shadow-xs' : 'text-slate-600'}`}
                  >
                    {s.label}
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
                  placeholder="Search issues, tables, actions..."
                  className="w-full pl-7 pr-2 py-1 bg-white border border-slate-200 rounded text-xs text-slate-800 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {loading ? (
            <LoadingSpinner label="Loading proposed repair strategies..." />
          ) : filteredRecommendations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Issue & Record</th>
                    <th className="py-2.5 px-3">Strategy</th>
                    <th className="py-2.5 px-3">Risk Level</th>
                    <th className="py-2.5 px-4">Proposed Action</th>
                    <th className="py-2.5 px-3">Approval</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {filteredRecommendations.map((rec) => {
                    const isRepaired = rec.issue_status === 'REPAIRED';
                    return (
                      <tr key={rec.recommendation_id} className={`hover:bg-slate-50/70 transition-colors ${isRepaired ? 'opacity-50' : ''}`}>
                        <td className="py-2.5 px-3">
                          <div className="font-bold text-slate-900">{rec.issue_id}</div>
                          <div className="text-[11px] text-slate-500 font-mono mt-0.5">
                            `{rec.table_name}`.id={rec.record_id}
                          </div>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded border font-bold text-[11px] ${
                            rec.strategy === 'QUARANTINE' ? 'bg-purple-50 text-purple-800 border-purple-200' :
                            rec.strategy === 'MAP_PARENT' ? 'bg-sky-50 text-sky-800 border-sky-200' :
                            rec.strategy === 'RESTORE_PARENT' || rec.strategy === 'RESTORE' ? 'bg-blue-50 text-blue-800 border-blue-200' :
                            rec.strategy === 'SET_DEFAULT' ? 'bg-amber-50 text-amber-800 border-amber-200' :
                            rec.strategy === 'MERGE_DUPLICATE' || rec.strategy === 'MERGE' ? 'bg-orange-50 text-orange-800 border-orange-200' :
                            'bg-slate-100 text-slate-800 border-slate-200'
                          }`}>
                            {rec.strategy}
                          </span>
                        </td>
                        <td className="py-2.5 px-3"><Badge variant={rec.risk_level} /></td>
                        <td className="py-2.5 px-4 font-sans text-slate-600 max-w-sm truncate" title={rec.proposed_action}>
                          {rec.proposed_action}
                        </td>
                        <td className="py-2.5 px-3"><Badge variant={rec.approval_status} /></td>
                        <td className="py-2.5 px-3 text-right font-sans">
                          {isRepaired ? (
                            <span className="text-[11px] text-emerald-600 font-medium">Repaired</span>
                          ) : processingRecId === rec.recommendation_id && previewLoading ? (
                            <Button disabled variant="primary" size="sm" loading={true}>
                              Working...
                            </Button>
                          ) : (
                            <Button
                              variant="primary"
                              size="sm"
                              icon={Eye}
                              disabled={executing || (previewLoading && processingRecId === rec.recommendation_id)}
                              onClick={() => handleOpenPreview(rec)}
                            >
                              Preview & Execute
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
            <div className="p-8 text-center text-slate-500 text-xs font-sans">
              No recommendations matching the active filters. Run an integrity scan or select 'All'.
            </div>
          )}
        </div>

        {/* Section 2: Recent Repair Executions History */}
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Durably Executed Transactions Log
            </h3>
            <span className="text-xs text-slate-500 font-mono">{executions.length} logged events</span>
          </div>

          {executions.length > 0 ? (
            <div className="overflow-x-auto max-h-72">
              <table className="w-full text-left text-xs font-mono border-collapse">
                <thead className="bg-slate-50 sticky top-0 text-slate-600 border-b border-slate-200 font-semibold">
                  <tr>
                    <th className="py-2 px-3">Execution ID</th>
                    <th className="py-2 px-3">Transaction ID</th>
                    <th className="py-2 px-3">Target Entity</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3">Latency</th>
                    <th className="py-2 px-3">SQL Executed</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {executions.map((e) => (
                    <tr key={e.execution_id} className="hover:bg-slate-50/70">
                      <td className="py-2 px-3 text-slate-900 font-bold">{e.execution_id}</td>
                      <td className="py-2 px-3 text-indigo-600">{e.transaction_id}</td>
                      <td className="py-2 px-3 text-slate-700">`{e.table_name}`.id={e.record_id}</td>
                      <td className="py-2 px-3"><Badge variant={e.status} /></td>
                      <td className="py-2 px-3 text-slate-500">{e.execution_time_ms} ms</td>
                      <td className="py-2 px-3 text-slate-600 max-w-xs truncate" title={e.sql_executed}>
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

      {/* Repair Preview & Transaction Execution Modal */}
      <Modal
        isOpen={previewModalOpen}
        onClose={() => setPreviewModalOpen(false)}
        title="Self-Healing Transaction Preview"
        subtitle={previewData ? `Target: ${previewData.table_name} (Row ID: ${previewData.record_id})` : ''}
        maxWidth="max-w-3xl"
      >
        {previewLoading ? (
          <LoadingSpinner label="Calculating transaction impact, before/after diffs, and SQL preview..." />
        ) : executionResult ? (
          /* Execution Success Card */
          <div className="space-y-3 p-4 rounded bg-emerald-50 border border-emerald-200 text-center">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
            <h4 className="text-sm font-bold text-emerald-900">Self-Healing Execution Succeeded!</h4>
            <p className="text-xs text-emerald-800 font-mono">{executionResult.message}</p>
            <div className="flex justify-center gap-4 text-xs font-mono text-slate-600 pt-2 border-t border-emerald-200">
              <span>Tx: {executionResult.transaction_id}</span>
              <span>Time: {executionResult.execution_time_ms} ms</span>
              <span className="text-emerald-700 font-bold">InnoDB Verified: YES</span>
            </div>
            <div className="pt-2">
              <Button variant="primary" size="sm" onClick={() => setPreviewModalOpen(false)}>
                Done & Return to Center
              </Button>
            </div>
          </div>
        ) : previewData ? (
          <div className="space-y-4">
            {/* Risk & Safety Warning Banner */}
            <div className="p-3 rounded bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="text-slate-500">Chosen Strategy:</span>
                <span className="font-bold text-slate-900 font-mono">{previewData.strategy}</span>
              </div>
              <Badge variant={previewData.risk_level}>Risk: {previewData.risk_level}</Badge>
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
                <p className="text-[11px] text-purple-800 leading-relaxed font-sans">
                  1. The complete original row from table <strong className="font-mono">`{previewData.table_name}`</strong> will be serialized to JSON.
                  <br />
                  2. Row is inserted into <strong className="font-mono">`quarantine_records`</strong> with audit timestamp, source table, and reason.
                  <br />
                  3. The invalid row is deleted from <strong className="font-mono">`{previewData.table_name}`</strong> only after successful quarantine storage within the same ACID transaction.
                </p>
              </div>
            )}

            {/* RESTORE_PARENT Strategy Notice */}
            {(previewData.strategy === 'RESTORE_PARENT' || previewData.strategy === 'RESTORE') && (
              <div className="p-3 rounded bg-sky-50 border border-sky-200 text-xs space-y-1">
                <div className="font-bold text-sky-900 flex items-center gap-1.5">
                  <RotateCcw className="w-3.5 h-3.5 text-sky-700" />
                  Parent Entity Restoration
                </div>
                <p className="text-[11px] text-sky-800 leading-relaxed font-sans">
                  Restores or recreates the missing parent entity in the referenced master table, ensuring referential integrity without orphan records.
                </p>
              </div>
            )}

            {/* MERGE_DUPLICATE Strategy Notice */}
            {(previewData.strategy === 'MERGE_DUPLICATE' || previewData.strategy === 'MERGE') && (
              <div className="p-3 rounded bg-amber-50 border border-amber-200 text-xs space-y-1">
                <div className="font-bold text-amber-900 flex items-center gap-1.5">
                  <Shuffle className="w-3.5 h-3.5 text-amber-700" />
                  Duplicate Record Consolidation & Merge
                </div>
                <p className="text-[11px] text-amber-800 leading-relaxed font-sans">
                  Consolidates duplicate records into the canonical master row. Reassigns any dependent child foreign keys before removing the redundant row.
                </p>
              </div>
            )}

            {/* Administrator Input Section for SET_DEFAULT */}
            {previewData.strategy === 'SET_DEFAULT' && (previewData.requires_admin_input || previewData.input_field_name) && (
              <div className="p-3.5 rounded bg-amber-50/70 border border-amber-200 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    Administrator Replacement Value Required:
                  </label>
                  <span className="text-[10px] font-mono text-slate-500">
                    Column: <strong className="text-slate-900 font-bold">{previewData.input_field_name}</strong> ({previewData.input_field_type})
                    {previewData.input_field_max_length ? ` [Max: ${previewData.input_field_max_length}]` : ''}
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Original business data is missing or invalid. Automated insertion of arbitrary placeholder strings is prohibited. Enter a verified replacement value:
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={overrideValue}
                    onChange={handleValueChange}
                    placeholder={`Enter verified ${previewData.input_field_name || 'value'}...`}
                    className="flex-1 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs text-slate-900 font-mono focus:outline-none focus:border-indigo-600"
                  />
                </div>
                {previewData.validation_error && (
                  <p className="text-[11px] text-rose-600 flex items-center gap-1 font-mono font-bold">
                    <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                    {previewData.validation_error}
                  </p>
                )}
              </div>
            )}

            {/* Custom Parameter Inputs for Strategies */}
            {previewData.strategy === 'MAP_PARENT' && (
              <div className="p-3.5 rounded bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-800 block">
                    Authoritative Parent ID to Map:
                  </label>
                  <span className="text-[10px] font-mono text-slate-500">
                    Target: <strong className="text-slate-900 font-bold">{previewData.input_field_name || 'parent_id'}</strong>
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Enter an existing parent entity ID to restore referential linkage.
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={overrideParentId}
                    onChange={handleParentIdChange}
                    placeholder="e.g., 101"
                    className="w-full px-3 py-1.5 bg-white border border-slate-300 rounded text-xs text-slate-900 font-mono focus:outline-none focus:border-indigo-600"
                  />
                </div>
                {previewData.validation_error && (
                  <p className="text-[11px] text-rose-600 flex items-center gap-1 font-mono font-bold">
                    <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                    {previewData.validation_error}
                  </p>
                )}
              </div>
            )}

            {/* Before vs After State Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Current Before State
                </span>
                <div className="p-3 rounded bg-rose-50 border border-rose-200 text-xs font-mono max-h-36 overflow-y-auto">
                  <pre className="text-rose-950 font-semibold">{JSON.stringify(previewData.before_state, null, 2)}</pre>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Simulated After State
                </span>
                <div className="p-3 rounded bg-emerald-50 border border-emerald-200 text-xs font-mono max-h-36 overflow-y-auto">
                  <pre className="text-emerald-950 font-semibold">{JSON.stringify(previewData.after_state, null, 2)}</pre>
                </div>
              </div>
            </div>

            {/* Foreign Key Dependency Impact Section */}
            <div className="p-3 rounded bg-slate-50 border border-slate-200 space-y-1.5 text-xs">
              <div className="font-bold text-slate-800 flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <Network className="w-3.5 h-3.5 text-indigo-600" /> Dependency Impact & Blast Radius
                </span>
                <span className="font-mono text-[11px] text-slate-500">
                  Child Rows: <strong className={previewData.matching_child_records_count > 0 ? "text-amber-600 font-bold" : "text-emerald-600 font-bold"}>{previewData.matching_child_records_count || 0}</strong>
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono pt-1">
                <div>
                  <span className="text-slate-500 block mb-0.5">Direct Child Tables:</span>
                  {previewData.direct_children && previewData.direct_children.length > 0 ? (
                    <div className="flex flex-wrap gap-1">
                      {previewData.direct_children.map(t => (
                        <span key={t} className="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-800 border border-indigo-200 font-semibold">{t}</span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-slate-400">None</span>
                  )}
                </div>

                <div>
                  <span className="text-slate-500 block mb-0.5">Downstream Affected:</span>
                  {previewData.downstream_tables && previewData.downstream_tables.length > 0 ? (
                    <div className="flex flex-wrap gap-1">
                      {previewData.downstream_tables.map(t => (
                        <span key={t} className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200 font-semibold">{t}</span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-slate-400">None</span>
                  )}
                </div>
              </div>
            </div>

            {/* SQL Preview */}
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                Generated Parameterized SQL Statements
              </span>
              <div className="p-3 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-indigo-200 max-h-28 overflow-y-auto space-y-1">
                {(Array.isArray(previewData.sql_preview) ? previewData.sql_preview : (previewData.sql_preview || '').split('\n')).map((sql, idx) => (
                  <div key={idx} className="line-clamp-2">{sql}</div>
                ))}
              </div>
            </div>

            {/* Modal Execution Trigger */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-slate-200">
              {previewData.strategy === 'MANUAL_INTERVENTION' ? (
                <div className="flex items-center gap-1.5 text-xs text-amber-800 bg-amber-50 px-2.5 py-1 rounded border border-amber-200">
                  <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 text-amber-600" />
                  <span>Administrator input required. No automatic SQL execution available.</span>
                </div>
              ) : previewData.requires_admin_input && (
                (previewData.strategy === 'SET_DEFAULT' && (!overrideValue || previewData.validation_error)) ||
                (previewData.strategy === 'MAP_PARENT' && (!overrideParentId || previewData.validation_error))
              ) ? (
                <div className="flex items-center gap-1.5 text-xs text-amber-800 bg-amber-50 px-2.5 py-1 rounded border border-amber-200">
                  <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 text-amber-600" />
                  <span>Administrator input required before execution can proceed.</span>
                </div>
              ) : (
                <div />
              )}

              <div className="flex items-center gap-2">
                <Button variant="secondary" size="sm" onClick={() => setPreviewModalOpen(false)}>
                  {previewData.strategy === 'MANUAL_INTERVENTION' ? 'Close' : 'Cancel'}
                </Button>
                {previewData.strategy !== 'MANUAL_INTERVENTION' && (
                  <Button
                    variant={previewData.is_destructive ? 'danger' : 'primary'}
                    size="md"
                    icon={Play}
                    loading={executing}
                    disabled={
                      executing ||
                      Boolean(
                        previewData.requires_admin_input && (
                          (previewData.strategy === 'SET_DEFAULT' && (!overrideValue || previewData.validation_error)) ||
                          (previewData.strategy === 'MAP_PARENT' && (!overrideParentId || previewData.validation_error))
                        )
                      )
                    }
                    onClick={() => {
                      if (previewData.is_destructive || previewData.requires_confirmation) {
                        setConfirmDialogOpen(true);
                      } else {
                        handleExecute();
                      }
                    }}
                  >
                    {executing ? 'Executing Repair...' : 'Execute Transaction Safe Repair'}
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
        title="Confirm Repair Execution"
        message={`You are about to execute '${activeRec?.strategy}' on table '${previewData?.table_name}'. An application recovery checkpoint will be taken before execution, and the transaction will automatically rollback if integrity verification fails.`}
        confirmText="Confirm & Commit Repair"
      />
    </div>
  );
};

export default RepairCenterPage;
