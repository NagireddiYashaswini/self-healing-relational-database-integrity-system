import React, { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Filter,
  Eye,
  RefreshCw,
  Clock,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import { auditApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const AuditLogsPage = () => {
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);

  // Filters
  const [eventTypeFilter, setEventTypeFilter] = useState('');
  const [resultFilter, setResultFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Inspect Event Modal
  const [inspectEvent, setInspectEvent] = useState(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = {
        limit: 100,
        event_type: eventTypeFilter || undefined,
        result: resultFilter || undefined,
        search: searchTerm || undefined,
      };
      const res = await auditApi.getLogs(params);
      setLogs(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [eventTypeFilter, resultFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            System Audit Logs & Traceability
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Immutable chronological record of scans, approvals, transaction executions, rollbacks, and recovery checkpoints.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={fetchLogs}
        >
          Refresh Logs
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800 space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search */}
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchLogs()}
              placeholder="Search description, table, actor, or ID..."
              className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Event Type Filter */}
          <select
            value={eventTypeFilter}
            onChange={(e) => setEventTypeFilter(e.target.value)}
            className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none"
          >
            <option value="">All Event Types</option>
            <option value="SCAN_STARTED">Scan Started</option>
            <option value="SCAN_COMPLETED">Scan Completed</option>
            <option value="REPAIR_EXECUTED">Repair Executed</option>
            <option value="REPAIR_FAILED">Repair Failed</option>
            <option value="CHECKPOINT_CREATED">Checkpoint Created</option>
            <option value="CHECKPOINT_RESTORED">Checkpoint Restored</option>
            <option value="TRANSACTION_DEMO_ROLLBACK">Rollback Demo</option>
            <option value="DATABASE_RESET">Database Reset</option>
          </select>

          {/* Result Filter */}
          <select
            value={resultFilter}
            onChange={(e) => setResultFilter(e.target.value)}
            className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none"
          >
            <option value="">All Results</option>
            <option value="SUCCESS">Success</option>
            <option value="FAILURE">Failure</option>
            <option value="WARNING">Warning</option>
            <option value="INFO">Info</option>
          </select>

          <Button variant="secondary" size="sm" onClick={fetchLogs} className="text-xs">
            Filter
          </Button>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1">
          <span>Found {total} audit records</span>
          {(eventTypeFilter || resultFilter || searchTerm) && (
            <button
              onClick={() => {
                setEventTypeFilter('');
                setResultFilter('');
                setSearchTerm('');
              }}
              className="text-emerald-400 hover:underline"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Logs Table */}
      {loading ? (
        <LoadingSpinner label="Fetching audit log events..." />
      ) : logs.length > 0 ? (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Event ID</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Actor</th>
                  <th className="py-3 px-4">Action Description</th>
                  <th className="py-3 px-3">Result</th>
                  <th className="py-3 px-3">Timestamp</th>
                  <th className="py-3 px-4 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {logs.map((log) => (
                  <tr key={log.event_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 text-slate-200 font-bold">#{log.event_id}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-bold text-[11px]">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-300">{log.actor}</td>
                    <td className="py-3 px-4 font-sans text-slate-300 max-w-sm line-clamp-1">
                      {log.action_description}
                    </td>
                    <td className="py-3 px-3"><Badge variant={log.result} /></td>
                    <td className="py-3 px-3 text-slate-400">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        icon={Eye}
                        onClick={() => setInspectEvent(log)}
                        className="text-xs text-emerald-400 hover:text-emerald-300"
                        title="View Full Payload"
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 text-slate-400 text-sm">
          No audit records found matching your filters.
        </div>
      )}

      {/* Inspect Event Modal */}
      <Modal
        isOpen={!!inspectEvent}
        onClose={() => setInspectEvent(null)}
        title={`Audit Event #${inspectEvent?.event_id}: ${inspectEvent?.event_type}`}
        subtitle={`Recorded: ${inspectEvent ? new Date(inspectEvent.timestamp).toLocaleString() : ''}`}
        maxWidth="max-w-2xl"
      >
        {inspectEvent && (
          <div className="space-y-4 text-xs font-mono">
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5 font-sans">
              <span className="text-[10px] uppercase font-bold text-slate-400 block font-mono">
                Description:
              </span>
              <p className="text-slate-200 text-sm leading-relaxed">{inspectEvent.action_description}</p>
            </div>

            <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div>
                <span className="text-slate-400 block text-[10px]">Actor:</span>
                <span className="text-slate-200 font-bold">{inspectEvent.actor}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Result:</span>
                <Badge variant={inspectEvent.result}>{inspectEvent.result}</Badge>
              </div>
              {inspectEvent.related_scan_id && (
                <div>
                  <span className="text-slate-400 block text-[10px]">Related Scan:</span>
                  <span className="text-emerald-400">{inspectEvent.related_scan_id}</span>
                </div>
              )}
              {inspectEvent.related_transaction_id && (
                <div>
                  <span className="text-slate-400 block text-[10px]">Related Transaction:</span>
                  <span className="text-emerald-400">{inspectEvent.related_transaction_id}</span>
                </div>
              )}
            </div>

            {/* Before / After JSON States if applicable */}
            {inspectEvent.before_values_json && (
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Before State (Sanitized):
                </span>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 max-h-36 overflow-y-auto">
                  <pre className="text-rose-300">{inspectEvent.before_values_json}</pre>
                </div>
              </div>
            )}

            {inspectEvent.after_values_json && (
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  After State (Sanitized):
                </span>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 max-h-36 overflow-y-auto">
                  <pre className="text-emerald-300">{inspectEvent.after_values_json}</pre>
                </div>
              </div>
            )}

            {inspectEvent.error_message && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300">
                <span className="font-bold block mb-1 text-[10px] uppercase">Error Recorded:</span>
                {inspectEvent.error_message}
              </div>
            )}

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <Button variant="outline" size="sm" onClick={() => setInspectEvent(null)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AuditLogsPage;
