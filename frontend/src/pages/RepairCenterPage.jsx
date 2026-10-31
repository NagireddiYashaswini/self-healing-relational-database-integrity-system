import React, { useState, useEffect } from 'react';
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
  Shuffle
} from 'lucide-react';
import { repairsApi, issuesApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const RepairCenterPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [executions, setExecutions] = useState([]);

  // Preview & Execution Modal
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [activeRec, setActiveRec] = useState(null);

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
    setActiveRec(rec);
    setPreviewModalOpen(true);
    setPreviewLoading(true);
    setExecutionResult(null);
    setStatusNotification(null);
    try {
      const payload = {
        issue_id: rec.issue_id,
        strategy: rec.strategy,
        repair_parameters: overrideParentId ? { parent_id: overrideParentId } : undefined,
      };
      const res = await repairsApi.previewRepair(payload);
      setPreviewData(res.data);
    } catch (err) {
      setPreviewModalOpen(false);
      setStatusNotification({ type: 'error', message: err.message || 'Failed to load preview.' });
      await fetchRepairsData();
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!activeRec) return;
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
        confirmed: true,
        operator: 'ADMIN_USER',
      };

      const res = await repairsApi.executeRepair(payload);
      setExecutionResult(res.data);
      setConfirmDialogOpen(false);
      setStatusNotification({ type: 'success', message: res.data?.message || 'Repair successfully executed.' });
      // Refresh list
      await fetchRepairsData();
    } catch (err) {
      setConfirmDialogOpen(false);
      setStatusNotification({ type: 'error', message: `Repair execution failed: ${err.message}` });
      await fetchRepairsData();
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Self-Healing & Repair Center
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Transaction-safe integrity restoration, impact previews, quarantine isolation, and rollback protection.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          onClick={fetchRepairsData}
        >
          Refresh Actions
        </Button>
      </div>

      {/* Global Status / Error Notification */}
      {statusNotification && (
        <div className={`p-4 rounded-xl flex items-center justify-between text-xs border ${
          statusNotification.type === 'error' 
            ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' 
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
        }`}>
          <div className="flex items-center gap-2">
            {statusNotification.type === 'error' ? (
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-400" />
            ) : (
              <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-400" />
            )}
            <span>{statusNotification.message}</span>
          </div>
          <button 
            onClick={() => setStatusNotification(null)}
            className="text-slate-400 hover:text-white transition-colors text-xs font-bold px-2 py-1"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Grid: Pending Recommendations + Past Executions */}
      <div className="space-y-6">
        {/* Section 1: Pending Recommendations */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
              <Wrench className="w-4 h-4 text-emerald-400" /> Pending Self-Healing Recommendations ({recommendations.filter(r => r.issue_status !== 'REPAIRED').length})
            </h3>
            <Badge variant="PENDING">Awaiting Execution</Badge>
          </div>

          {loading ? (
            <LoadingSpinner label="Loading proposed repair strategies..." />
          ) : recommendations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-3">Issue & Record</th>
                    <th className="py-3 px-3">Strategy</th>
                    <th className="py-3 px-3">Risk Level</th>
                    <th className="py-3 px-4">Proposed Action</th>
                    <th className="py-3 px-3">Approval</th>
                    <th className="py-3 px-4 text-right">Self-Heal Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {recommendations.map((rec) => {
                    const isRepaired = rec.issue_status === 'REPAIRED';
                    return (
                      <tr key={rec.recommendation_id} className={`hover:bg-slate-800/30 transition-colors ${isRepaired ? 'opacity-50' : ''}`}>
                        <td className="py-3.5 px-3">
                          <div className="font-bold text-slate-200">{rec.issue_id}</div>
                          <div className="text-[11px] text-emerald-400 font-mono mt-0.5">
                            `{rec.table_name}`.id={rec.record_id}
                          </div>
                        </td>
                        <td className="py-3.5 px-3">
                          <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-bold">
                            {rec.strategy}
                          </span>
                        </td>
                        <td className="py-3.5 px-3"><Badge variant={rec.risk_level} /></td>
                        <td className="py-3.5 px-4 font-sans text-slate-300 max-w-sm">
                          {rec.proposed_action}
                        </td>
                        <td className="py-3.5 px-3"><Badge variant={rec.approval_status} /></td>
                        <td className="py-3.5 px-4 text-right">
                          {isRepaired ? (
                            <span className="text-emerald-400 text-xs font-sans font-semibold flex items-center justify-end gap-1">
                              <CheckCircle2 className="w-4 h-4" /> Repaired
                            </span>
                          ) : (
                            <Button
                              variant="primary"
                              size="sm"
                              icon={Eye}
                              onClick={() => handleOpenPreview(rec)}
                              className="text-xs"
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
            <div className="text-center py-10 text-slate-500 text-xs">
              No pending recommendations. Run an integrity scan to detect violations.
            </div>
          )}
        </div>

        {/* Section 2: Recent Repair Executions History */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-purple-400" /> Durably Executed Transactions Log
            </h3>
            <span className="text-xs text-slate-400 font-mono">{executions.length} logged events</span>
          </div>

          {executions.length > 0 ? (
            <div className="overflow-x-auto max-h-80">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-900 sticky top-0 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Execution ID</th>
                    <th className="py-2.5 px-3">Transaction ID</th>
                    <th className="py-2.5 px-3">Target Table</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Latency</th>
                    <th className="py-2.5 px-4">SQL Executed</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {executions.map((e) => (
                    <tr key={e.execution_id} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-3 text-slate-200 font-bold">{e.execution_id}</td>
                      <td className="py-2.5 px-3 text-emerald-400">{e.transaction_id}</td>
                      <td className="py-2.5 px-3 text-slate-300">`{e.table_name}`.id={e.record_id}</td>
                      <td className="py-2.5 px-3"><Badge variant={e.status} /></td>
                      <td className="py-2.5 px-3 text-slate-400">{e.execution_time_ms} ms</td>
                      <td className="py-2.5 px-4 text-slate-400 max-w-xs truncate" title={e.sql_executed}>
                        {e.sql_executed}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-6 text-center">No repair executions logged yet.</p>
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
          <div className="space-y-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-center">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
            <h4 className="text-base font-bold text-white">Self-Healing Execution Succeeded!</h4>
            <p className="text-xs text-slate-300 font-mono">{executionResult.message}</p>
            <div className="flex justify-center gap-4 text-xs font-mono text-slate-400 pt-2 border-t border-emerald-500/20">
              <span>Tx: {executionResult.transaction_id}</span>
              <span>Time: {executionResult.execution_time_ms} ms</span>
              <span className="text-emerald-400 font-bold">InnoDB Verified: YES</span>
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
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Chosen Strategy:</span>
                <span className="font-bold text-emerald-400 font-mono">{previewData.strategy}</span>
              </div>
              <Badge variant={previewData.risk_level}>Risk: {previewData.risk_level}</Badge>
            </div>

            {previewData.warning && (
              <div className="p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{previewData.warning}</span>
              </div>
            )}

            {/* Custom Parameter Inputs for Strategies */}
            {previewData.strategy === 'MAP_PARENT' && (
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-700 space-y-2">
                <label className="text-xs font-bold text-slate-200 block">
                  Authoritative Parent ID to Map:
                </label>
                <input
                  type="text"
                  value={overrideParentId}
                  onChange={(e) => setOverrideParentId(e.target.value)}
                  placeholder="e.g., 101"
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-xs text-slate-100 font-mono"
                />
              </div>
            )}

            {/* Before vs After State Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Current Before State
                </span>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono max-h-40 overflow-y-auto">
                  <pre className="text-rose-300">{JSON.stringify(previewData.before_state, null, 2)}</pre>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Simulated After State
                </span>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono max-h-40 overflow-y-auto">
                  <pre className="text-emerald-300">{JSON.stringify(previewData.after_state, null, 2)}</pre>
                </div>
              </div>
            </div>

            {/* SQL Preview */}
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                Generated Parameterized SQL Statements
              </span>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-amber-300 max-h-32 overflow-y-auto space-y-1">
                {previewData.sql_preview.map((sql, idx) => (
                  <div key={idx} className="line-clamp-2">{sql}</div>
                ))}
              </div>
            </div>

            {/* Downstream Affected Tables */}
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <span>Dependent Child Tables Checked:</span>
              {previewData.dependent_tables.length > 0 ? (
                previewData.dependent_tables.map(t => (
                  <span key={t} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-200">{t}</span>
                ))
              ) : (
                <span className="text-emerald-400">None (Isolated)</span>
              )}
            </div>

            {/* Modal Execution Trigger */}
            <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
              <Button variant="outline" size="sm" onClick={() => setPreviewModalOpen(false)}>
                Cancel
              </Button>
              <Button
                variant={previewData.is_destructive ? 'danger' : 'primary'}
                size="md"
                icon={Play}
                loading={executing}
                onClick={() => {
                  if (previewData.is_destructive || previewData.requires_confirmation) {
                    setConfirmDialogOpen(true);
                  } else {
                    handleExecute();
                  }
                }}
              >
                Execute Transaction Safe Repair
              </Button>
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
