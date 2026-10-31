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
    <div className="space-y-4 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Query History & System Audit Logs
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable chronological trace of scanning operations, repair executions, ACID transactions, rollbacks, and recovery checkpoints.
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={fetchLogs}
        >
          Refresh Logs
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 bg-white border border-slate-200 rounded-lg shadow-xs space-y-2.5">
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Search */}
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchLogs()}
              placeholder="Search description, table, actor, or ID..."
              className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Event Type Filter */}
          <select
            value={eventTypeFilter}
            onChange={(e) => setEventTypeFilter(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 focus:outline-none focus:border-indigo-500 font-medium"
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
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 focus:outline-none focus:border-indigo-500 font-medium"
          >
            <option value="">All Results</option>
            <option value="SUCCESS">Success</option>
            <option value="FAILURE">Failure</option>
            <option value="WARNING">Warning</option>
            <option value="INFO">Info</option>
          </select>

          <Button variant="secondary" size="sm" onClick={fetchLogs}>
            Filter
          </Button>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-100">
          <span>Found {total} audit records</span>
          {(eventTypeFilter || resultFilter || searchTerm) && (
            <button
              onClick={() => {
                setEventTypeFilter('');
                setResultFilter('');
                setSearchTerm('');
              }}
              className="text-indigo-600 font-medium hover:underline"
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
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Event ID</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Actor</th>
                  <th className="py-2.5 px-3">Action Description</th>
                  <th className="py-2.5 px-3">Result</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {logs.map((log) => (
                  <tr key={log.event_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-3 text-slate-900 font-bold">#{log.event_id}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-800 font-bold text-[11px]">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-600">{log.actor}</td>
                    <td className="py-2.5 px-3 font-sans text-slate-700 max-w-sm truncate" title={log.action_description}>
                      {log.action_description}
                    </td>
                    <td className="py-2.5 px-3"><Badge variant={log.result} /></td>
                    <td className="py-2.5 px-3 text-slate-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right font-sans">
                      <Button
                        variant="ghost"
                        size="sm"
                        icon={Eye}
                        onClick={() => setInspectEvent(log)}
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
        <div className="p-8 text-center bg-white border border-slate-200 rounded-lg text-slate-500 text-xs">
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
          <div className="space-y-3.5 text-xs font-mono">
            <div className="p-3 rounded bg-slate-50 border border-slate-200 space-y-1 font-sans">
              <span className="text-[10px] uppercase font-bold text-slate-500 block font-mono">
                Action Description:
              </span>
              <p className="text-slate-900 text-xs leading-relaxed">{inspectEvent.action_description}</p>
            </div>

            <div className="grid grid-cols-2 gap-2.5 p-3 rounded bg-slate-50 border border-slate-200">
              <div>
                <span className="text-slate-400 block text-[10px]">Actor:</span>
                <span className="text-slate-900 font-bold">{inspectEvent.actor}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Result:</span>
                <Badge variant={inspectEvent.result}>{inspectEvent.result}</Badge>
              </div>
              {inspectEvent.related_scan_id && (
                <div>
                  <span className="text-slate-400 block text-[10px]">Related Scan:</span>
                  <span className="text-indigo-600 font-semibold">{inspectEvent.related_scan_id}</span>
                </div>
              )}
              {inspectEvent.related_transaction_id && (
                <div>
                  <span className="text-slate-400 block text-[10px]">Related Transaction:</span>
                  <span className="text-indigo-600 font-semibold">{inspectEvent.related_transaction_id}</span>
                </div>
              )}
            </div>

            {/* Before / After JSON States if applicable */}
            {inspectEvent.before_values_json && (
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Before State (Sanitized):
                </span>
                <div className="p-3 rounded bg-rose-50 border border-rose-200 max-h-32 overflow-y-auto">
                  <pre className="text-rose-950 font-semibold">{inspectEvent.before_values_json}</pre>
                </div>
              </div>
            )}

            {inspectEvent.after_values_json && (
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  After State (Sanitized):
                </span>
                <div className="p-3 rounded bg-emerald-50 border border-emerald-200 max-h-32 overflow-y-auto">
                  <pre className="text-emerald-950 font-semibold">{inspectEvent.after_values_json}</pre>
                </div>
              </div>
            )}

            {inspectEvent.error_message && (
              <div className="p-3 rounded bg-rose-50 border border-rose-200 text-rose-800">
                <span className="font-bold block mb-1 text-[10px] uppercase">Error Recorded:</span>
                {inspectEvent.error_message}
              </div>
            )}

            <div className="flex justify-end pt-2 border-t border-slate-200">
              <Button variant="secondary" size="sm" onClick={() => setInspectEvent(null)}>
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
