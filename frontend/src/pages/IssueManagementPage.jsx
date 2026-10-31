import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Search,
  Filter,
  CheckCircle,
  Eye,
  Wrench,
  Ban,
  Clock,
  RefreshCw,
  FileCode,
  ShieldAlert
} from 'lucide-react';
import { issuesApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const IssueManagementPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [issues, setIssues] = useState([]);
  const [total, setTotal] = useState(0);

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Selected Issue Modal
  const [selectedIssueId, setSelectedIssueId] = useState(null);
  const [issueDetail, setIssueDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Status Change Dialog
  const [ignoreDialogOpen, setIgnoreDialogOpen] = useState(false);
  const [ignoreReason, setIgnoreReason] = useState('');

  const fetchIssues = async () => {
    try {
      setLoading(true);
      const params = {
        limit: 100,
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
        category: categoryFilter || undefined,
        search: searchTerm || undefined,
      };
      const res = await issuesApi.getIssues(params);
      setIssues(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (err) {
      console.error('Failed to fetch issues:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, [statusFilter, severityFilter, categoryFilter]);

  const handleOpenDetail = async (issueId) => {
    setSelectedIssueId(issueId);
    setDetailLoading(true);
    try {
      const res = await issuesApi.getIssue(issueId);
      setIssueDetail(res.data);
    } catch (err) {
      console.error('Failed to load issue detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleMarkReviewed = async (issueId) => {
    try {
      await issuesApi.updateStatus(issueId, { status: 'REVIEWED' });
      await fetchIssues();
      if (selectedIssueId === issueId) {
        handleOpenDetail(issueId);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleConfirmIgnore = async () => {
    if (!selectedIssueId) return;
    try {
      await issuesApi.updateStatus(selectedIssueId, {
        status: 'IGNORED',
        reason: ignoreReason || 'Administrator ignored issue after manual assessment.',
      });
      setIgnoreDialogOpen(false);
      setIgnoreReason('');
      await fetchIssues();
      handleOpenDetail(selectedIssueId);
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Integrity Issues Management
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Catalog of detected referential anomalies, duplicate records, and constraint breaches awaiting resolution.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={fetchIssues}
        >
          Refresh List
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
              onKeyDown={(e) => e.key === 'Enter' && fetchIssues()}
              placeholder="Search by description, table, or ID..."
              className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Severity Dropdown */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Category Dropdown */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none"
          >
            <option value="">All Categories</option>
            <option value="ORPHAN">Orphan Record</option>
            <option value="DUPLICATE">Duplicate Record</option>
            <option value="NULL_VIOLATION">NULL Violation</option>
            <option value="DOMAIN_VIOLATION">Domain Violation</option>
          </select>

          {/* Status Dropdown */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="APPROVED">Approved</option>
            <option value="REPAIRED">Repaired</option>
            <option value="IGNORED">Ignored</option>
          </select>

          <Button variant="secondary" size="sm" onClick={fetchIssues} className="text-xs">
            Apply Filters
          </Button>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1">
          <span>Found {total} recorded issues</span>
          {(statusFilter || severityFilter || categoryFilter || searchTerm) && (
            <button
              onClick={() => {
                setStatusFilter('');
                setSeverityFilter('');
                setCategoryFilter('');
                setSearchTerm('');
              }}
              className="text-emerald-400 hover:underline"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Issues Table */}
      {loading ? (
        <LoadingSpinner label="Fetching registered integrity issues..." />
      ) : issues.length > 0 ? (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Issue ID</th>
                  <th className="py-3 px-3">Severity</th>
                  <th className="py-3 px-3">Category</th>
                  <th className="py-3 px-3">Table & Row</th>
                  <th className="py-3 px-4">Problem Description</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {issues.map((issue) => (
                  <tr key={issue.issue_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 text-slate-200 font-bold">{issue.issue_id}</td>
                    <td className="py-3 px-3"><Badge variant={issue.severity} /></td>
                    <td className="py-3 px-3 text-slate-300">{issue.category}</td>
                    <td className="py-3 px-3 text-slate-300">
                      <span className="text-emerald-400 font-bold">`{issue.table_name}`</span>.id={issue.record_id}
                    </td>
                    <td className="py-3 px-4 font-sans text-slate-300 max-w-sm line-clamp-1">
                      {issue.description}
                    </td>
                    <td className="py-3 px-3"><Badge variant={issue.status} /></td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="outline"
                          size="sm"
                          icon={Eye}
                          onClick={() => handleOpenDetail(issue.issue_id)}
                          className="text-xs"
                          title="Inspect Details"
                        />
                        {issue.status !== 'REPAIRED' && (
                          <Button
                            variant="primary"
                            size="sm"
                            icon={Wrench}
                            onClick={() => navigate(`/repairs?issue=${issue.issue_id}`)}
                            className="text-xs"
                          >
                            Heal
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 text-slate-400 text-sm">
          No integrity issues match the selected filters.
        </div>
      )}

      {/* Issue Detail & Raw Row Modal */}
      <Modal
        isOpen={!!selectedIssueId}
        onClose={() => setSelectedIssueId(null)}
        title={`Integrity Violation: ${selectedIssueId}`}
        subtitle={issueDetail ? `${issueDetail.issue.category} • Table: ${issueDetail.issue.table_name}` : ''}
        maxWidth="max-w-3xl"
      >
        {detailLoading ? (
          <LoadingSpinner label="Fetching issue record details..." />
        ) : issueDetail ? (
          <div className="space-y-5">
            {/* Metadata Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Severity</span>
                <Badge variant={issueDetail.issue.severity} className="mt-1" />
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Status</span>
                <Badge variant={issueDetail.issue.status} className="mt-1" />
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Target Record</span>
                <span className="text-slate-200 mt-1 block">ID: {issueDetail.issue.record_id}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase">Detected On</span>
                <span className="text-slate-400 mt-1 block">
                  {new Date(issueDetail.issue.detected_at).toLocaleDateString()}
                </span>
              </div>
            </div>

            {/* Problem Description */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Issue Description</h4>
              <p className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-sm text-slate-200 leading-relaxed">
                {issueDetail.issue.description}
              </p>
            </div>

            {/* Recommended Action */}
            {issueDetail.recommendation && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Recommended Healing Strategy</h4>
                <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-1.5 text-xs">
                  <div className="flex items-center justify-between font-mono">
                    <span className="font-bold text-emerald-300">Strategy: {issueDetail.recommendation.strategy}</span>
                    <Badge variant={issueDetail.recommendation.risk_level}>Risk: {issueDetail.recommendation.risk_level}</Badge>
                  </div>
                  <p className="text-slate-300">{issueDetail.recommendation.proposed_action}</p>
                  <p className="text-slate-400 text-[11px] pt-1">
                    <strong className="text-slate-300">Rationale:</strong> {issueDetail.recommendation.reason}
                  </p>
                </div>
              </div>
            )}

            {/* Raw Live Database Row Data */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                Live Record State ({issueDetail.issue.table_name})
              </h4>
              {issueDetail.live_record_data ? (
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 overflow-x-auto max-h-48 font-mono text-xs">
                  <pre className="text-emerald-400">{JSON.stringify(issueDetail.live_record_data, null, 2)}</pre>
                </div>
              ) : (
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-rose-400">
                  Record does not exist in active table (may have already been deleted or quarantined).
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800">
              <div className="flex items-center gap-2">
                {issueDetail.issue.status === 'OPEN' && (
                  <Button
                    variant="outline"
                    size="sm"
                    icon={CheckCircle}
                    onClick={() => handleMarkReviewed(issueDetail.issue.issue_id)}
                  >
                    Mark Reviewed
                  </Button>
                )}
                {issueDetail.issue.status !== 'IGNORED' && issueDetail.issue.status !== 'REPAIRED' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={Ban}
                    onClick={() => setIgnoreDialogOpen(true)}
                    className="text-slate-400 hover:text-rose-400"
                  >
                    Ignore Issue
                  </Button>
                )}
              </div>

              {issueDetail.issue.status !== 'REPAIRED' && (
                <Button
                  variant="primary"
                  size="sm"
                  icon={Wrench}
                  onClick={() => navigate(`/repairs?issue=${issueDetail.issue.issue_id}`)}
                >
                  Proceed to Self-Healing
                </Button>
              )}
            </div>
          </div>
        ) : null}
      </Modal>

      {/* Ignore Reason Dialog */}
      <Modal
        isOpen={ignoreDialogOpen}
        onClose={() => setIgnoreDialogOpen(false)}
        title="Ignore Integrity Issue"
        maxWidth="max-w-md"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-400">
            Please record a justified reason for ignoring this integrity issue. This reason will be permanently written to the audit log.
          </p>
          <textarea
            value={ignoreReason}
            onChange={(e) => setIgnoreReason(e.target.value)}
            placeholder="e.g., Verified legacy data exception; exempt from current rule..."
            rows={3}
            className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
          />
          <div className="flex justify-end gap-2">
            <Button variant="outline" size="sm" onClick={() => setIgnoreDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" onClick={handleConfirmIgnore}>
              Confirm Ignore
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default IssueManagementPage;
