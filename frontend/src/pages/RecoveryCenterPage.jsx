import React, { useState, useEffect } from 'react';
import {
  History,
  ShieldCheck,
  RotateCcw,
  Plus,
  AlertTriangle,
  Archive,
  RefreshCw,
  Clock,
  Info
} from 'lucide-react';
import { recoveryApi, databaseApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const RecoveryCenterPage = () => {
  const [loading, setLoading] = useState(true);
  const [checkpoints, setCheckpoints] = useState([]);
  const [recoveryHistory, setRecoveryHistory] = useState([]);
  const [availableTables, setAvailableTables] = useState([]);

  // Create Checkpoint Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [targetTable, setTargetTable] = useState('');
  const [checkpointName, setCheckpointName] = useState('');
  const [creating, setCreating] = useState(false);

  // Restore Checkpoint Confirm
  const [restoreConfirmOpen, setRestoreConfirmOpen] = useState(false);
  const [selectedCheckpoint, setSelectedCheckpoint] = useState(null);
  const [restoring, setRestoring] = useState(false);

  const fetchRecoveryData = async () => {
    try {
      setLoading(true);
      const [ckptsRes, histRes, tablesRes] = await Promise.all([
        recoveryApi.getCheckpoints(),
        recoveryApi.getHistory(),
        databaseApi.getTables(),
      ]);
      setCheckpoints(ckptsRes.data || []);
      setRecoveryHistory(histRes.data || []);
      const tbls = tablesRes.data || [];
      setAvailableTables(tbls);
      if (tbls.length > 0 && !targetTable) {
        setTargetTable(tbls[0].table_name);
      }
    } catch (err) {
      console.error('Failed to fetch recovery data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecoveryData();
  }, []);

  const handleCreateCheckpoint = async () => {
    if (!targetTable || !checkpointName) return;
    setCreating(true);
    try {
      await recoveryApi.createCheckpoint({
        target_table: targetTable,
        checkpoint_name: checkpointName,
      });
      setCreateModalOpen(false);
      setCheckpointName('');
      await fetchRecoveryData();
    } catch (err) {
      alert(`Checkpoint creation failed: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const handleRestoreCheckpoint = async () => {
    if (!selectedCheckpoint) return;
    setRestoring(true);
    try {
      await recoveryApi.rollback({
        checkpoint_id: selectedCheckpoint.checkpoint_id,
        confirmed: true,
      });
      setRestoreConfirmOpen(false);
      setSelectedCheckpoint(null);
      await fetchRecoveryData();
    } catch (err) {
      alert(`Restoration failed: ${err.message}`);
    } finally {
      setRestoring(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Database Recovery Center
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Application-level recovery checkpoints, pre-repair table snapshots, and safe point-in-time state restoration.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={fetchRecoveryData}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setCreateModalOpen(true)}
          >
            Create Checkpoint
          </Button>
        </div>
      </div>

      {/* Technical Distinction Banner */}
      <div className="p-4 rounded-2xl glass-panel border border-sky-500/30 bg-sky-950/10 flex items-start gap-3">
        <Info className="w-5 h-5 text-sky-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 leading-relaxed">
          <strong className="text-sky-300 font-semibold block mb-0.5">Academic System Limitation Note:</strong>
          Application recovery checkpoints capture consistent table state snapshots inside atomic InnoDB transactions. They provide safe, immediate reversal for application self-healing operations without replacing native physical MySQL binary log (`mysqlbinlog`) crash recovery or operating-system disk dumps.
        </div>
      </div>

      {/* Main Grid: Checkpoints + Rollback Audit History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Active Recovery Checkpoints */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
              <Archive className="w-4 h-4 text-emerald-400" /> Available Recovery Checkpoints ({checkpoints.length})
            </h3>
            <Badge variant="ACTIVE">Snapshot Catalog</Badge>
          </div>

          {loading ? (
            <LoadingSpinner label="Loading snapshot checkpoints..." />
          ) : checkpoints.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Checkpoint ID</th>
                    <th className="py-2.5 px-3">Target Table</th>
                    <th className="py-2.5 px-3">Captured Rows</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {checkpoints.map((c) => (
                    <tr key={c.checkpoint_id} className="hover:bg-slate-800/30">
                      <td className="py-3 px-3 text-slate-200 font-bold">
                        <div>{c.checkpoint_name}</div>
                        <span className="text-[10px] text-slate-400 font-normal">{c.checkpoint_id}</span>
                      </td>
                      <td className="py-3 px-3 text-emerald-400">`{c.target_table}`</td>
                      <td className="py-3 px-3 text-slate-300">{c.rows_captured}</td>
                      <td className="py-3 px-3"><Badge variant="MEDIUM">{c.checkpoint_type}</Badge></td>
                      <td className="py-3 px-3"><Badge variant={c.status} /></td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          icon={RotateCcw}
                          onClick={() => {
                            setSelectedCheckpoint(c);
                            setRestoreConfirmOpen(true);
                          }}
                          className="text-xs text-amber-400"
                        >
                          Restore State
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-500 text-xs">
              No recovery checkpoints created yet. Checkpoints are automatically generated before every self-healing operation or can be created manually.
            </div>
          )}
        </div>

        {/* Right Col: Rollback & Recovery Audit Timeline */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <History className="w-4 h-4 text-purple-400" /> Recovery History Log
          </h3>

          {recoveryHistory.length > 0 ? (
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
              {recoveryHistory.map((h) => (
                <div key={h.event_id} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-emerald-400 font-bold">{h.event_type}</span>
                    <span className="text-[10px] text-slate-400">
                      {new Date(h.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">{h.action_description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-6 text-center">No recovery actions recorded in log.</p>
          )}
        </div>
      </div>

      {/* Create Checkpoint Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create Table Recovery Checkpoint"
        subtitle="Captures an atomic before-state snapshot of table rows and schema metadata"
        maxWidth="max-w-md"
      >
        <div className="space-y-4">
          <div>
            <label className="text-xs font-bold text-slate-300 block mb-1">Target Table:</label>
            <select
              value={targetTable}
              onChange={(e) => setTargetTable(e.target.value)}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-slate-100"
            >
              {availableTables.map((t) => (
                <option key={t.table_name} value={t.table_name}>
                  {t.table_name} ({t.row_count} rows)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-300 block mb-1">Checkpoint Label:</label>
            <input
              type="text"
              value={checkpointName}
              onChange={(e) => setCheckpointName(e.target.value)}
              placeholder="e.g., Pre-Migration Backup"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-100 placeholder:text-slate-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
            <Button variant="outline" size="sm" onClick={() => setCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              loading={creating}
              onClick={handleCreateCheckpoint}
            >
              Capture Snapshot
            </Button>
          </div>
        </div>
      </Modal>

      {/* Confirm Restore Dialog */}
      <ConfirmDialog
        isOpen={restoreConfirmOpen}
        onClose={() => setRestoreConfirmOpen(false)}
        onConfirm={handleRestoreCheckpoint}
        loading={restoring}
        title="Restore Table State from Checkpoint"
        message={`Are you sure you want to restore table '${selectedCheckpoint?.target_table}' from checkpoint '${selectedCheckpoint?.checkpoint_name}'? Rows will be re-applied using an atomic upsert transaction.`}
        confirmText="Confirm & Restore"
      />
    </div>
  );
};

export default RecoveryCenterPage;
