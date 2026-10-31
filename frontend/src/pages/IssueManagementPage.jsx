import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Search,
  Filter,
  CheckCircle,
  CheckCircle2,
  Eye,
  Wrench,
  Ban,
  Clock,
  RefreshCw,
  FileCode,
  ShieldAlert,
  Play,
  Network
} from 'lucide-react';
import { issuesApi, repairsApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
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

  // Self-Healing Execution States
  const [executingIssueId, setExecutingIssueId] = useState(null);
  const [activeIssue, setActiveIssue] = useState(null);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [overrideParentId, setOverrideParentId] = useState('');
  const [overrideValue, setOverrideValue] = useState('');
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [statusNotification, setStatusNotification] = useState(null);

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

  const handleHealClick = async (issue) => {
    if (issue.status === 'REPAIRED' || issue.status === 'IGNORED' || executingIssueId) return;

    setExecutingIssueId(issue.issue_id);
    setActiveIssue(issue);
    setPreviewData(null);
    setOverrideParentId('');
    setOverrideValue('');
    setStatusNotification(null);

    try {
      const payload = {
        issue_id: issue.issue_id,
        strategy: issue.strategy,
      };
      const res = await repairsApi.previewRepair(payload);
      setPreviewData(res.data);
      setPreviewModalOpen(true);
    } catch (err) {
      if (err.status === 409 || err.message?.toLowerCase().includes('already repaired') || err.message?.toLowerCase().includes('already been repaired')) {
        setStatusNotification({
          type: 'error',
          message: 'This integrity issue has already been repaired. Duplicate execution is not allowed.'
        });
        setIssues(prev => prev.map(i => i.issue_id === issue.issue_id ? { ...i, status: 'REPAIRED' } : i));
        await fetchIssues();
      } else {
        setStatusNotification({
          type: 'error',
          message: err.message || 'Failed to prepare repair preview.'
        });
      }
      setExecutingIssueId(null);
    }
  };

  const handleClosePreview = () => {
    setPreviewModalOpen(false);
    setExecutingIssueId(null);
    setPreviewData(null);
  };

  const handleUpdatePreviewInput = async (val, parentId) => {
    if (!activeIssue) return;
    try {
      const params = {};
      const pId = parentId !== undefined ? parentId : overrideParentId;
      const v = val !== undefined ? val : overrideValue;
      if (pId) params.parent_id = pId;
      if (v !== undefined && v !== '') params.value = v;

      const res = await repairsApi.previewRepair({
        issue_id: activeIssue.issue_id,
        strategy: activeIssue.strategy || previewData?.strategy,
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

  const handleExecuteRepair = async () => {
    if (!activeIssue || executing) return;
    setExecuting(true);
    setStatusNotification(null);

    try {
      const params = {};
      if (overrideParentId) params.parent_id = overrideParentId;
      if (overrideValue) params.value = overrideValue;

      const payload = {
        issue_id: activeIssue.issue_id,
        strategy: activeIssue.strategy || previewData?.strategy,
        repair_parameters: Object.keys(params).length > 0 ? params : undefined,
        admin_provided_value: overrideValue || undefined,
        row_version_token: previewData?.row_version_token,
        confirmed: true,
        operator: 'ADMIN_USER',
      };

      const res = await repairsApi.executeRepair(payload);
      setConfirmDialogOpen(false);
      setPreviewModalOpen(false);

      // Update state locally immediately
      setIssues(prev => prev.map(i => i.issue_id === activeIssue.issue_id ? { ...i, status: 'REPAIRED' } : i));
      if (selectedIssueId === activeIssue.issue_id) {
        setIssueDetail(prev => prev ? { ...prev, issue: { ...prev.issue, status: 'REPAIRED' } } : prev);
      }

      setStatusNotification({
        type: 'success',
        message: res.data?.message || `Successfully repaired issue ${activeIssue.issue_id}.`
      });

      await fetchIssues();
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
          setIssues(prev => prev.map(i => i.issue_id === activeIssue.issue_id ? { ...i, status: 'REPAIRED' } : i));
          if (selectedIssueId === activeIssue.issue_id) {
            setIssueDetail(prev => prev ? { ...prev, issue: { ...prev.issue, status: 'REPAIRED' } } : prev);
          }
          setStatusNotification({
            type: 'error',
            message: 'This integrity issue has already been repaired. Duplicate execution is not allowed.'
          });
          await fetchIssues();
        }
      } else {
        setStatusNotification({
          type: 'error',
          message: `Repair execution failed: ${err.message}`
        });
      }
    } finally {
      setExecuting(false);
      setExecutingIssueId(null);
    }
  };

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Integrity Issues Management
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Active catalog of detected referential anomalies, duplicate records, and constraint violations awaiting resolution.
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          loading={loading}
          onClick={fetchIssues}
        >
          Refresh List
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
              onKeyDown={(e) => e.key === 'Enter' && fetchIssues()}
              placeholder="Search description, table, or ID..."
              className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Severity Dropdown */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 focus:outline-none focus:border-indigo-500 font-medium"
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
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 focus:outline-none focus:border-indigo-500 font-medium"
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
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 focus:outline-none focus:border-indigo-500 font-medium"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="APPROVED">Approved</option>
            <option value="REPAIRED">Repaired</option>
            <option value="IGNORED">Ignored</option>
          </select>

          <Button variant="secondary" size="sm" onClick={fetchIssues}>
            Filter
          </Button>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-100">
          <span>Found {total} recorded issues</span>
          {(statusFilter || severityFilter || categoryFilter || searchTerm) && (
            <button
              onClick={() => {
                setStatusFilter('');
                setSeverityFilter('');
                setCategoryFilter('');
                setSearchTerm('');
              }}
              className="text-indigo-600 font-medium hover:underline"
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
        <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Issue ID</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Table & Row</th>
                  <th className="py-2.5 px-3">Problem Description</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {issues.map((issue) => (
                  <tr key={issue.issue_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-3 text-slate-900 font-bold">{issue.issue_id}</td>
                    <td className="py-2.5 px-3"><Badge variant={issue.severity} /></td>
                    <td className="py-2.5 px-3 text-slate-700">{issue.category}</td>
                    <td className="py-2.5 px-3 text-slate-800">
                      <span className="text-indigo-600 font-bold">`{issue.table_name}`</span>.id={issue.record_id}
                    </td>
                    <td className="py-2.5 px-3 font-sans text-slate-600 max-w-sm truncate" title={issue.description}>
                      {issue.description}
                    </td>
                    <td className="py-2.5 px-3"><Badge variant={issue.status} /></td>
                    <td className="py-2.5 px-3 text-right font-sans">
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="secondary"
                          size="sm"
                          icon={Eye}
                          onClick={() => handleOpenDetail(issue.issue_id)}
                          title="Inspect Details"
                        />
                        {issue.status === 'REPAIRED' ? (
                          <span className="text-[11px] text-emerald-600 font-medium px-2 py-0.5">Repaired</span>
                        ) : issue.status === 'IGNORED' ? (
                          <span className="text-[11px] text-slate-400 font-medium px-2 py-0.5">Ignored</span>
                        ) : executingIssueId === issue.issue_id ? (
                          <Button disabled variant="primary" size="sm" loading={true}>
                            Working...
                          </Button>
                        ) : (
                          <Button
                            variant="primary"
                            size="sm"
                            icon={Wrench}
                            disabled={!!executingIssueId}
                            onClick={() => handleHealClick(issue)}
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
        <div className="p-8 text-center bg-white border border-slate-200 rounded-lg text-slate-500 text-xs">
          No integrity issues match the selected filters.
        </div>
      )}

      {/* Issue Detail & Raw Row Modal */}
      <Modal
        isOpen={!!selectedIssueId}
        onClose={() => setSelectedIssueId(null)}
        title={`Integrity Violation: ${selectedIssueId}`}
        subtitle={issueDetail ? `${issueDetail.issue.category} · Table: ${issueDetail.issue.table_name}` : ''}
        maxWidth="max-w-3xl"
      >
        {detailLoading ? (
          <LoadingSpinner label="Fetching issue record details..." />
        ) : issueDetail ? (
          <div className="space-y-4">
            {/* Metadata Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3 rounded bg-slate-50 border border-slate-200 text-xs font-mono">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold font-sans">Severity</span>
                <Badge variant={issueDetail.issue.severity} className="mt-1" />
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold font-sans">Status</span>
                <Badge variant={issueDetail.issue.status} className="mt-1" />
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold font-sans">Target Record</span>
                <span className="text-slate-900 font-bold mt-1 block">ID: {issueDetail.issue.record_id}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold font-sans">Detected On</span>
                <span className="text-slate-600 mt-1 block">
                  {new Date(issueDetail.issue.detected_at).toLocaleDateString()}
                </span>
              </div>
            </div>

            {/* Problem Description */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">Issue Description</h4>
              <p className="p-3 rounded bg-slate-50 border border-slate-200 text-xs text-slate-800 leading-relaxed">
                {issueDetail.issue.description}
              </p>
            </div>

            {/* Recommended Action */}
            {issueDetail.recommendation && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">Recommended Healing Strategy</h4>
                <div className="p-3 rounded bg-indigo-50/60 border border-indigo-100 space-y-1 text-xs">
                  <div className="flex items-center justify-between font-mono">
                    <span className="font-bold text-indigo-900">Strategy: {issueDetail.recommendation.strategy}</span>
                    <Badge variant={issueDetail.recommendation.risk_level}>Risk: {issueDetail.recommendation.risk_level}</Badge>
                  </div>
                  <p className="text-slate-700 font-sans">{issueDetail.recommendation.proposed_action}</p>
                  <p className="text-slate-500 text-[11px] font-sans pt-1">
                    <strong className="text-slate-700">Rationale:</strong> {issueDetail.recommendation.reason}
                  </p>
                </div>
              </div>
            )}

            {/* Raw Live Database Row Data */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Live Record State ({issueDetail.issue.table_name})
              </h4>
              {issueDetail.live_record_data ? (
                <div className="p-3 rounded bg-slate-900 border border-slate-800 overflow-x-auto max-h-40 font-mono text-xs">
                  <pre className="text-indigo-200">{JSON.stringify(issueDetail.live_record_data, null, 2)}</pre>
                </div>
              ) : (
                <div className="p-3 rounded bg-rose-50 border border-rose-200 text-xs text-rose-700">
                  Record does not exist in active table (may have already been deleted or quarantined).
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="flex flex-wrap items-center justify-between gap-2.5 pt-3 border-t border-slate-200">
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
                    className="text-slate-500 hover:text-rose-600"
                  >
                    Ignore Issue
                  </Button>
                )}
              </div>

              {issueDetail.issue.status === 'REPAIRED' ? (
                <span className="text-xs text-emerald-600 font-medium font-sans">Repaired</span>
              ) : issueDetail.issue.status === 'IGNORED' ? (
                <span className="text-xs text-slate-400 font-medium font-sans">Ignored</span>
              ) : executingIssueId === issueDetail.issue.issue_id ? (
                <Button disabled variant="primary" size="sm" loading={true}>
                  Processing...
                </Button>
              ) : (
                <Button
                  variant="primary"
                  size="sm"
                  icon={Wrench}
                  disabled={!!executingIssueId}
                  onClick={() => {
                    const targetIssue = issueDetail.issue;
                    setSelectedIssueId(null);
                    handleHealClick(targetIssue);
                  }}
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
        <div className="space-y-3">
          <p className="text-xs text-slate-600 leading-relaxed">
            Please record a justified reason for ignoring this integrity issue. This reason will be permanently recorded in the audit log.
          </p>
          <textarea
            value={ignoreReason}
            onChange={(e) => setIgnoreReason(e.target.value)}
            placeholder="e.g., Verified legacy data exception; exempt from current rule..."
            rows={3}
            className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500"
          />
          <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
            <Button variant="secondary" size="sm" onClick={() => setIgnoreDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" onClick={handleConfirmIgnore}>
              Confirm Ignore
            </Button>
          </div>
        </div>
      </Modal>

      {/* Self-Healing Transaction Preview Modal */}
      <Modal
        isOpen={previewModalOpen}
        onClose={handleClosePreview}
        title="Self-Healing Transaction Preview"
        subtitle={previewData ? `Target: ${previewData.table_name} (Row ID: ${previewData.record_id})` : ''}
        maxWidth="max-w-3xl"
      >
        {previewData ? (
          <div className="space-y-4">
            {/* Risk & Strategy Badge */}
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
                <p className="text-[11px] text-slate-600 leading-relaxed font-sans">
                  Original business data is missing. Automated insertion of placeholder strings is strictly prohibited. Enter a verified replacement value:
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

            {/* Custom Parameter Inputs for MAP_PARENT */}
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
                    placeholder="e.g., 1"
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
                  <span>Administrator input required. No automatic execution available.</span>
                </div>
              ) : previewData.requires_admin_input && (
                (previewData.strategy === 'SET_DEFAULT' && (!overrideValue || previewData.validation_error)) ||
                (previewData.strategy === 'MAP_PARENT' && (!overrideParentId || previewData.validation_error))
              ) ? (
                <div className="flex items-center gap-1.5 text-xs text-amber-800 bg-amber-50 px-2.5 py-1 rounded border border-amber-200">
                  <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 text-amber-600" />
                  <span>Input required before execution.</span>
                </div>
              ) : (
                <div />
              )}

              <div className="flex items-center gap-2">
                <Button variant="secondary" size="sm" onClick={handleClosePreview}>
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
                        handleExecuteRepair();
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
        onConfirm={handleExecuteRepair}
        loading={executing}
        title="Confirm Repair Execution"
        message={`You are about to execute '${activeIssue?.strategy || previewData?.strategy}' on table '${previewData?.table_name}'. An application recovery checkpoint will be taken before execution, and the transaction will automatically rollback if integrity verification fails.`}
        confirmText="Confirm & Commit Repair"
      />
    </div>
  );
};

export default IssueManagementPage;
