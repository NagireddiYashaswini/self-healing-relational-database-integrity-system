import React, { useState, useEffect, useMemo } from 'react';
import {
  Sliders,
  Plus,
  Play,
  CheckCircle2,
  XCircle,
  ToggleLeft,
  ToggleRight,
  AlertTriangle,
  RefreshCw,
  Trash2,
  Search,
  Filter,
  ShieldCheck,
  Table,
  Check
} from 'lucide-react';
import { rulesApi, databaseApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const RulesConfigurationPage = () => {
  const [loading, setLoading] = useState(true);
  const [rules, setRules] = useState([]);
  const [availableTables, setAvailableTables] = useState([]);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('ALL');
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');

  // Create Rule Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [ruleCode, setRuleCode] = useState('');
  const [ruleName, setRuleName] = useState('');
  const [description, setDescription] = useState('');
  const [ruleType, setRuleType] = useState('DOMAIN_CHECK');
  const [targetTable, setTargetTable] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [parentTable, setParentTable] = useState('');
  const [parentColumn, setParentColumn] = useState('');
  const [severity, setSeverity] = useState('HIGH');
  const [parametersJson, setParametersJson] = useState('{\n  "min_value": 0,\n  "max_value": 100\n}');
  const [creating, setCreating] = useState(false);

  // Test Rule State
  const [testingRuleId, setTestingRuleId] = useState(null);
  const [testResult, setTestResult] = useState(null);

  const fetchRulesAndTables = async () => {
    try {
      setLoading(true);
      const [rulesRes, tablesRes] = await Promise.all([
        rulesApi.getRules(),
        databaseApi.getTables(),
      ]);
      setRules(rulesRes.data || []);
      const tbls = tablesRes.data || [];
      setAvailableTables(tbls);
      if (tbls.length > 0 && !targetTable) {
        setTargetTable(tbls[0].table_name);
      }
    } catch (err) {
      console.error('Failed to load rules:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRulesAndTables();
  }, []);

  const handleToggleRule = async (rule) => {
    try {
      await rulesApi.updateRule(rule.rule_id, {
        is_enabled: !rule.is_enabled,
      });
      setRules(rules.map(r => r.rule_id === rule.rule_id ? { ...r, is_enabled: !r.is_enabled } : r));
    } catch (err) {
      alert(`Failed to update rule status: ${err.message}`);
    }
  };

  const handleTestRule = async (ruleId) => {
    setTestingRuleId(ruleId);
    setTestResult(null);
    try {
      const res = await rulesApi.testRule(ruleId);
      setTestResult(res.data);
    } catch (err) {
      alert(`Rule testing error: ${err.message}`);
    } finally {
      setTestingRuleId(null);
    }
  };

  const handleCreateRule = async () => {
    if (!ruleCode || !ruleName || !targetTable || !targetColumn) {
      alert('Please fill all mandatory fields (Code, Name, Target Table, Target Column).');
      return;
    }
    setCreating(true);
    try {
      let parsedParams = null;
      if (parametersJson.trim()) {
        parsedParams = JSON.parse(parametersJson);
      }

      await rulesApi.createRule({
        rule_code: ruleCode,
        name: ruleName,
        description: description || ruleName,
        rule_type: ruleType,
        target_table: targetTable,
        target_column: targetColumn,
        parent_table: parentTable || null,
        parent_column: parentColumn || null,
        parameters_json: parsedParams,
        severity: severity,
        is_enabled: true,
      });

      setCreateModalOpen(false);
      setRuleCode('');
      setRuleName('');
      setDescription('');
      await fetchRulesAndTables();
    } catch (err) {
      alert(`Failed to create rule: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteRule = async (ruleId) => {
    if (!window.confirm('Are you sure you want to delete this integrity rule?')) return;
    try {
      await rulesApi.deleteRule(ruleId);
      setRules(rules.filter(r => r.rule_id !== ruleId));
    } catch (err) {
      alert(`Failed to delete rule: ${err.message}`);
    }
  };

  // Filtered Rules
  const filteredRules = useMemo(() => {
    return rules.filter((r) => {
      const matchesSearch =
        !searchQuery ||
        r.rule_code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.target_table?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.target_column?.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesType = filterType === 'ALL' || r.rule_type === filterType;
      const matchesSeverity = filterSeverity === 'ALL' || r.severity === filterSeverity;
      const matchesStatus =
        filterStatus === 'ALL' ||
        (filterStatus === 'ENABLED' && r.is_enabled) ||
        (filterStatus === 'DISABLED' && !r.is_enabled);

      return matchesSearch && matchesType && matchesSeverity && matchesStatus;
    });
  }, [rules, searchQuery, filterType, filterSeverity, filterStatus]);

  return (
    <div className="space-y-5 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Sliders className="w-5 h-5 text-indigo-600" />
            Integrity Rules Configuration
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure, validate, and dry-run active constraints for orphans, duplicate column sets, NULL enforcement, and domains.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={RefreshCw}
            onClick={fetchRulesAndTables}
          >
            Refresh Rules
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setCreateModalOpen(true)}
          >
            Add New Rule
          </Button>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="panel p-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2 flex-1 min-w-[280px]">
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by code, table, or column..."
              className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          {/* Rule Type Filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="ALL">All Rule Types</option>
            <option value="ORPHAN">Orphan Check</option>
            <option value="DUPLICATE">Duplicate Check</option>
            <option value="NULL_CHECK">Null Check</option>
            <option value="DOMAIN_CHECK">Domain Check</option>
          </select>

          {/* Severity Filter */}
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Status Filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="ENABLED">Enabled Only</option>
            <option value="DISABLED">Disabled Only</option>
          </select>
        </div>

        <div className="text-xs text-slate-500 font-mono">
          Showing <span className="font-semibold text-slate-900">{filteredRules.length}</span> of {rules.length} rules
        </div>
      </div>

      {/* Rules Grid */}
      {loading ? (
        <LoadingSpinner label="Loading integrity rules..." />
      ) : filteredRules.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRules.map((rule) => (
            <div
              key={rule.rule_id}
              className={`panel p-4 flex flex-col justify-between transition-colors min-w-0 h-full ${
                rule.is_enabled
                  ? 'border-slate-200 hover:border-slate-300'
                  : 'border-slate-200/60 bg-slate-50/50 opacity-70'
              }`}
            >
              <div className="min-w-0 flex-1 flex flex-col">
                {/* Header: Rule Code & Severity Badge (Strictly safe grid) */}
                <div className="grid grid-cols-[1fr_auto] items-start gap-2.5 mb-2 min-w-0">
                  <span
                    className="text-xs font-mono font-semibold text-indigo-700 uppercase tracking-tight break-all min-w-0 leading-tight"
                    title={rule.rule_code}
                  >
                    {rule.rule_code}
                  </span>
                  <Badge variant={rule.severity} className="flex-shrink-0 self-start" />
                </div>

                <h3 className="text-sm font-semibold text-slate-900 line-clamp-1" title={rule.name}>
                  {rule.name}
                </h3>
                <p className="mt-1 text-xs text-slate-500 leading-relaxed line-clamp-2">
                  {rule.description}
                </p>

                {/* Target Column Monospace Pill */}
                <div className="mt-3 p-2 rounded bg-slate-50 border border-slate-200 font-mono text-xs text-slate-700 flex items-center justify-between gap-2 min-w-0">
                  <span
                    className="truncate min-w-0 text-slate-900 font-medium"
                    title={`\`${rule.target_table}\`.\`${rule.target_column}\``}
                  >
                    `{rule.target_table}`.{rule.target_column}
                  </span>
                  <span className="text-slate-500 uppercase text-[10px] font-semibold bg-white px-1.5 py-0.5 rounded border border-slate-200 flex-shrink-0">
                    {rule.rule_type}
                  </span>
                </div>

                {rule.parent_table && (
                  <div
                    className="mt-1.5 text-[11px] font-mono text-slate-500 pl-1 truncate"
                    title={`Parent: \`${rule.parent_table}\`.\`${rule.parent_column}\``}
                  >
                    ↳ Parent: `{rule.parent_table}`.{rule.parent_column}
                  </div>
                )}
              </div>

              {/* Action Footer */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => handleToggleRule(rule)}
                  className="flex items-center gap-1.5 text-xs font-medium transition-colors cursor-pointer select-none"
                >
                  {rule.is_enabled ? (
                    <>
                      <ToggleRight className="w-5 h-5 text-indigo-600" />
                      <span className="text-indigo-700 font-semibold">Enabled</span>
                    </>
                  ) : (
                    <>
                      <ToggleLeft className="w-5 h-5 text-slate-400" />
                      <span className="text-slate-500">Disabled</span>
                    </>
                  )}
                </button>

                <div className="flex items-center gap-1.5">
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={Play}
                    loading={testingRuleId === rule.rule_id}
                    onClick={() => handleTestRule(rule.rule_id)}
                    title="Dry-run Test Rule Against Current Data"
                  >
                    Test
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={Trash2}
                    onClick={() => handleDeleteRule(rule.rule_id)}
                    className="text-slate-400 hover:text-rose-600"
                    title="Delete Rule"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="panel p-12 text-center text-slate-500 text-xs">
          {searchQuery || filterType !== 'ALL' || filterSeverity !== 'ALL' || filterStatus !== 'ALL'
            ? 'No integrity rules match your search or filter criteria.'
            : 'No integrity rules configured. Click "Add New Rule" to create one.'}
        </div>
      )}

      {/* Test Result Feedback Modal */}
      <Modal
        isOpen={!!testResult}
        onClose={() => setTestResult(null)}
        title={`Dry-Run Test Result: ${testResult?.rule_code}`}
        subtitle="Safe real-time verification against live database records without persisting a scan."
        maxWidth="max-w-xl"
      >
        {testResult && (
          <div className="space-y-4">
            <div
              className={`p-3.5 rounded-md border flex items-center justify-between ${
                testResult.violations_detected_count > 0
                  ? 'bg-amber-50 border-amber-200 text-amber-900'
                  : 'bg-emerald-50 border-emerald-200 text-emerald-900'
              }`}
            >
              <div className="flex items-center gap-2.5">
                {testResult.violations_detected_count > 0 ? (
                  <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                ) : (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                )}
                <span className="text-xs font-semibold">
                  {testResult.violations_detected_count} Anomaly Match(es) Found
                </span>
              </div>
              <Badge variant={testResult.violations_detected_count > 0 ? 'HIGH' : 'SUCCESS'}>
                {testResult.violations_detected_count > 0 ? 'VIOLATIONS PRESENT' : 'PASS'}
              </Badge>
            </div>

            {testResult.violations && testResult.violations.length > 0 && (
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                <span className="text-[10px] uppercase font-bold text-slate-500 block font-mono">
                  Sample Matched Records:
                </span>
                {testResult.violations.map((v, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs font-mono"
                  >
                    <span className="text-indigo-700 font-semibold">ID {v.record_id}:</span> {v.description}
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <Button variant="primary" size="sm" onClick={() => setTestResult(null)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Add New Rule Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create New Integrity Rule"
        subtitle="Registers a parameterized integrity check executed during scans"
        maxWidth="max-w-lg"
      >
        <div className="space-y-3.5 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Rule Code (Unique ID):</label>
            <input
              type="text"
              value={ruleCode}
              onChange={(e) => setRuleCode(e.target.value.toUpperCase().replace(/\s+/g, '_'))}
              placeholder="e.g. RULE_DOMAIN_STUDENT_SCORE"
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-slate-900 font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Rule Name:</label>
            <input
              type="text"
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              placeholder="e.g. Student Exam Score Range"
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-slate-900 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Rule Category:</label>
              <select
                value={ruleType}
                onChange={(e) => setRuleType(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-slate-700 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="ORPHAN">Orphan Foreign Key</option>
                <option value="DUPLICATE">Duplicate Uniqueness</option>
                <option value="NULL_CHECK">Mandatory NOT NULL</option>
                <option value="DOMAIN_CHECK">Domain Range / Format</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Severity Level:</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-slate-700 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Target Table:</label>
              <select
                value={targetTable}
                onChange={(e) => setTargetTable(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-slate-700 font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {availableTables.map((t) => (
                  <option key={t.table_name} value={t.table_name}>
                    {t.table_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Target Column(s):</label>
              <input
                type="text"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                placeholder="e.g. grade_marks or student_id,course_id"
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-slate-900 font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          {ruleType === 'ORPHAN' && (
            <div className="grid grid-cols-2 gap-3 p-3 rounded-md bg-slate-50 border border-slate-200">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Parent Table:</label>
                <input
                  type="text"
                  value={parentTable}
                  onChange={(e) => setParentTable(e.target.value)}
                  placeholder="e.g. students"
                  className="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-md text-slate-900 font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Parent Column:</label>
                <input
                  type="text"
                  value={parentColumn}
                  onChange={(e) => setParentColumn(e.target.value)}
                  placeholder="e.g. student_id"
                  className="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-md text-slate-900 font-mono text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Rule Parameters (JSON):</label>
            <textarea
              value={parametersJson}
              onChange={(e) => setParametersJson(e.target.value)}
              rows={3}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-md text-slate-900 font-mono text-[11px] focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
            <Button variant="secondary" size="sm" onClick={() => setCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" loading={creating} onClick={handleCreateRule}>
              Save & Enable Rule
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default RulesConfigurationPage;
