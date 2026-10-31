import React, { useState, useEffect } from 'react';
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
  HelpCircle
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Integrity Rules Configuration
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure, validate, and test active constraints for orphans, duplicate column sets, NULL enforcement, and domains.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
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

      {/* Rules Grid */}
      {loading ? (
        <LoadingSpinner label="Loading integrity rules..." />
      ) : rules.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rules.map((rule) => (
            <div
              key={rule.rule_id}
              className={`p-5 rounded-2xl border glass-panel transition-all flex flex-col justify-between ${
                rule.is_enabled ? 'border-slate-800 hover:border-emerald-500/40' : 'border-slate-900 opacity-60'
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase">
                    {rule.rule_code}
                  </span>
                  <Badge variant={rule.severity} />
                </div>

                <h3 className="text-sm font-bold text-white line-clamp-1">{rule.name}</h3>
                <p className="mt-1 text-xs text-slate-400 leading-relaxed line-clamp-2">{rule.description}</p>

                {/* Target Column Pill */}
                <div className="mt-3 p-2 rounded-lg bg-slate-900/80 border border-slate-800 font-mono text-[11px] text-slate-300 flex items-center justify-between">
                  <span>
                    `{rule.target_table}`.{rule.target_column}
                  </span>
                  <span className="text-slate-500 uppercase text-[9px]">{rule.rule_type}</span>
                </div>

                {rule.parent_table && (
                  <div className="mt-1 text-[11px] font-mono text-slate-400 pl-1">
                    ↳ Parent: `{rule.parent_table}`.{rule.parent_column}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <button
                  onClick={() => handleToggleRule(rule)}
                  className="flex items-center gap-1 text-xs font-semibold text-slate-300 hover:text-white"
                >
                  {rule.is_enabled ? (
                    <>
                      <ToggleRight className="w-5 h-5 text-emerald-400" />
                      <span className="text-emerald-400">Enabled</span>
                    </>
                  ) : (
                    <>
                      <ToggleLeft className="w-5 h-5 text-slate-600" />
                      <span className="text-slate-500">Disabled</span>
                    </>
                  )}
                </button>

                <div className="flex items-center gap-1.5">
                  <Button
                    variant="outline"
                    size="sm"
                    icon={Play}
                    loading={testingRuleId === rule.rule_id}
                    onClick={() => handleTestRule(rule.rule_id)}
                    className="text-xs"
                    title="Dry-run Test Rule Against Current Data"
                  >
                    Test
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={Trash2}
                    onClick={() => handleDeleteRule(rule.rule_id)}
                    className="text-slate-500 hover:text-rose-400"
                    title="Delete Rule"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 text-slate-400 text-sm">
          No integrity rules configured. Click "Add New Rule" to create one.
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
            <div className={`p-4 rounded-xl border flex items-center justify-between ${
              testResult.violations_detected_count > 0
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            }`}>
              <div className="flex items-center gap-2">
                {testResult.violations_detected_count > 0 ? (
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                ) : (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                )}
                <span className="text-sm font-bold">
                  {testResult.violations_detected_count} Anomaly Match(es) Found
                </span>
              </div>
              <Badge variant={testResult.violations_detected_count > 0 ? 'HIGH' : 'SUCCESS'}>
                {testResult.violations_detected_count > 0 ? 'VIOLATIONS PRESENT' : 'PASS'}
              </Badge>
            </div>

            {testResult.violations && testResult.violations.length > 0 && (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                <span className="text-[10px] uppercase font-bold text-slate-400 block font-mono">
                  Sample Matched Records:
                </span>
                {testResult.violations.map((v, idx) => (
                  <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 text-xs font-mono">
                    <span className="text-emerald-400">ID {v.record_id}:</span> {v.description}
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <Button variant="primary" size="sm" onClick={() => setTestResult(null)}>
                Got it
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
        <div className="space-y-3 text-xs">
          <div>
            <label className="font-bold text-slate-300 block mb-1">Rule Code (Unique ID):</label>
            <input
              type="text"
              value={ruleCode}
              onChange={(e) => setRuleCode(e.target.value.toUpperCase().replace(/\s+/g, '_'))}
              placeholder="e.g. RULE_DOMAIN_STUDENT_SCORE"
              className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-slate-100 font-mono"
            />
          </div>

          <div>
            <label className="font-bold text-slate-300 block mb-1">Rule Name:</label>
            <input
              type="text"
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              placeholder="e.g. Student Exam Score Range"
              className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-slate-100"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-bold text-slate-300 block mb-1">Rule Category:</label>
              <select
                value={ruleType}
                onChange={(e) => setRuleType(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-slate-100"
              >
                <option value="ORPHAN">Orphan Foreign Key</option>
                <option value="DUPLICATE">Duplicate Uniqueness</option>
                <option value="NULL_CHECK">Mandatory NOT NULL</option>
                <option value="DOMAIN_CHECK">Domain Range / Format</option>
              </select>
            </div>

            <div>
              <label className="font-bold text-slate-300 block mb-1">Severity Level:</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-slate-100"
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
              <label className="font-bold text-slate-300 block mb-1">Target Table:</label>
              <select
                value={targetTable}
                onChange={(e) => setTargetTable(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-slate-100 font-mono"
              >
                {availableTables.map((t) => (
                  <option key={t.table_name} value={t.table_name}>{t.table_name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="font-bold text-slate-300 block mb-1">Target Column(s):</label>
              <input
                type="text"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                placeholder="e.g. grade_marks or student_id,course_id"
                className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-slate-100 font-mono"
              />
            </div>
          </div>

          {ruleType === 'ORPHAN' && (
            <div className="grid grid-cols-2 gap-3 p-2.5 rounded bg-slate-900 border border-slate-800">
              <div>
                <label className="font-bold text-slate-300 block mb-1">Parent Table:</label>
                <input
                  type="text"
                  value={parentTable}
                  onChange={(e) => setParentTable(e.target.value)}
                  placeholder="e.g. students"
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-slate-100 font-mono"
                />
              </div>
              <div>
                <label className="font-bold text-slate-300 block mb-1">Parent Column:</label>
                <input
                  type="text"
                  value={parentColumn}
                  onChange={(e) => setParentColumn(e.target.value)}
                  placeholder="e.g. student_id"
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-slate-100 font-mono"
                />
              </div>
            </div>
          )}

          <div>
            <label className="font-bold text-slate-300 block mb-1">Rule Parameters (JSON):</label>
            <textarea
              value={parametersJson}
              onChange={(e) => setParametersJson(e.target.value)}
              rows={3}
              className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded text-slate-100 font-mono text-[11px]"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
            <Button variant="outline" size="sm" onClick={() => setCreateModalOpen(false)}>
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
