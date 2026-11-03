import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Database,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  Info,
  RefreshCw,
  Layers,
  Archive,
  Clock
} from 'lucide-react';
import { ingestionApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const isSqlDefaultExpr = (val) => {
  if (val === null || val === undefined) return true;
  if (typeof val !== 'string') return false;
  const s = val.trim().toLowerCase();
  return (
    s === '' ||
    s === 'current_timestamp' ||
    s === 'current_timestamp()' ||
    s === 'now()' ||
    s === 'now' ||
    s === 'default' ||
    s === 'null'
  );
};

const isDbGeneratedTimestamp = (col) => {
  if (!col) return false;
  if (col.is_generated_default) return true;
  const dt = (col.data_type || '').toLowerCase();
  const def = String(col.default_value || '').toLowerCase();
  const extra = String(col.extra || '').toLowerCase();
  if (dt.includes('timestamp') || dt.includes('datetime')) {
    if (def.includes('current_timestamp') || def.includes('now')) return true;
    if (extra.includes('default_generated') || extra.includes('current_timestamp')) return true;
  }
  return false;
};

const CORE_TABLES = [
  { id: 'departments', label: 'Departments', desc: 'Academic departments, buildings & operating budgets' },
  { id: 'instructors', label: 'Instructors', desc: 'Faculty profiles, departmental assignments & salaries' },
  { id: 'courses', label: 'Courses', desc: 'Curriculum offerings, credits & instructor assignments' },
  { id: 'students', label: 'Students', desc: 'Student registrations, ages, GPAs & departmental affiliations' },
  { id: 'enrollments', label: 'Enrollments', desc: 'Student course registrations, grades & enrollment statuses' },
  { id: 'classrooms', label: 'Classrooms', desc: 'Lecture halls, seating capacities & department allocations' }
];

export const DataIngestionPage = () => {
  const [selectedTable, setSelectedTable] = useState('students');
  const [schemaLoading, setSchemaLoading] = useState(false);
  const [schemaData, setSchemaData] = useState(null);
  const [formData, setFormData] = useState({});
  const [showCustomTimestamp, setShowCustomTimestamp] = useState({});
  const [externalRef, setExternalRef] = useState('');
  
  const [submitting, setSubmitting] = useState(false);
  const [ingestionResult, setIngestionResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchSchema = async (tableName) => {
    try {
      setSchemaLoading(true);
      setErrorMessage(null);
      setIngestionResult(null);
      setFormData({});
      setShowCustomTimestamp({});
      setExternalRef(`EXT-${Date.now().toString().slice(-4)}`);

      const res = await ingestionApi.getSchema(tableName);
      setSchemaData(res.data);

      // Initialize form fields with defaults or empty strings
      const initial = {};
      res.data?.columns?.forEach((col) => {
        if (!col.is_primary_key) {
          if (isDbGeneratedTimestamp(col)) {
            // Do not populate timestamp or datetime fields with SQL expressions
            initial[col.name] = '';
          } else if (col.default_value !== null && !isSqlDefaultExpr(col.default_value)) {
            initial[col.name] = col.default_value;
          } else {
            initial[col.name] = '';
          }
        }
      });
      setFormData(initial);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to retrieve table schema.');
    } finally {
      setSchemaLoading(false);
    }
  };

  useEffect(() => {
    fetchSchema(selectedTable);
  }, [selectedTable]);

  const handleInputChange = (colName, value) => {
    setFormData((prev) => ({ ...prev, [colName]: value }));
  };

  const handleQuickFill = (type) => {
    if (selectedTable === 'students') {
      if (type === 'valid') {
        setFormData({
          student_name: 'Ananya Deshmukh',
          email: `ananya.${Date.now().toString().slice(-3)}@univ.edu`,
          age: '21',
          gpa: '3.85',
          dept_id: schemaData?.fk_options?.dept_id?.[0]?.value || '1',
          enrollment_year: '2024'
        });
      } else if (type === 'orphan') {
        setFormData({
          student_name: 'Orphan Student Test',
          email: `orphan.${Date.now().toString().slice(-3)}@univ.edu`,
          age: '22',
          gpa: '3.20',
          dept_id: '999999', // Missing parent department
          enrollment_year: '2024'
        });
      } else if (type === 'domain') {
        setFormData({
          student_name: 'Domain Violation Test',
          email: 'invalid-email-format',
          age: '150', // Out of 16-65 range
          gpa: '7.50', // Out of 0-4 range
          dept_id: schemaData?.fk_options?.dept_id?.[0]?.value || '1',
          enrollment_year: '2024'
        });
      }
    } else if (selectedTable === 'classrooms') {
      if (type === 'valid') {
        setFormData({
          room_number: `RM-${Date.now().toString().slice(-3)}`,
          building: 'Alan Turing Hall',
          capacity: '60',
          dept_id: schemaData?.fk_options?.dept_id?.[0]?.value || '1'
        });
      } else if (type === 'orphan') {
        setFormData({
          room_number: `RM-${Date.now().toString().slice(-3)}`,
          building: 'Quantum Labs',
          capacity: '40',
          dept_id: '88888' // Missing parent
        });
      } else if (type === 'domain') {
        setFormData({
          room_number: `RM-${Date.now().toString().slice(-3)}`,
          building: 'Hall A',
          capacity: '1500', // Exceeds 500 capacity
          dept_id: schemaData?.fk_options?.dept_id?.[0]?.value || '1'
        });
      }
    } else if (selectedTable === 'enrollments') {
      if (type === 'valid') {
        setFormData({
          student_id: schemaData?.fk_options?.student_id?.[0]?.value || '1',
          course_id: schemaData?.fk_options?.course_id?.[0]?.value || '1',
          enrolled_on: new Date().toISOString().split('T')[0],
          grade_marks: '88.5',
          status: 'ENROLLED'
        });
      } else if (type === 'orphan') {
        setFormData({
          student_id: '999999', // Non-existent student
          course_id: schemaData?.fk_options?.course_id?.[0]?.value || '1',
          enrolled_on: new Date().toISOString().split('T')[0],
          grade_marks: '75',
          status: 'ENROLLED'
        });
      } else if (type === 'domain') {
        setFormData({
          student_id: schemaData?.fk_options?.student_id?.[0]?.value || '1',
          course_id: schemaData?.fk_options?.course_id?.[0]?.value || '1',
          enrolled_on: new Date().toISOString().split('T')[0],
          grade_marks: '195.0', // Out of 0-100 range
          status: 'INVALID_ENUM'
        });
      }
    } else if (selectedTable === 'departments') {
      if (type === 'valid') {
        setFormData({
          dept_code: `DEPT-${Date.now().toString().slice(-4)}`,
          dept_name: `Department of Data Science ${Date.now().toString().slice(-3)}`,
          building: 'Alan Turing Center',
          budget: '350000.00'
        });
      } else if (type === 'orphan') {
        // Departments has no FK parent; demonstrate duplicate code violation
        setFormData({
          dept_code: 'CS',
          dept_name: `Duplicate Dept Test ${Date.now().toString().slice(-3)}`,
          building: 'Main Hall',
          budget: '200000.00'
        });
      } else if (type === 'domain') {
        setFormData({
          dept_code: `DEPT-${Date.now().toString().slice(-4)}`,
          dept_name: 'Negative Budget Dept',
          building: 'Basement Lab',
          budget: '-50000.00'
        });
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setErrorMessage(null);
      setIngestionResult(null);

      // Exclude database-generated timestamp fields when empty or SQL default expressions
      const sanitizedRecordData = {};
      schemaData?.columns?.forEach((col) => {
        if (col.is_primary_key) return;
        const val = formData[col.name];
        const isGenTs = isDbGeneratedTimestamp(col);

        if (isGenTs) {
          // If empty or SQL default expression, omit from payload so DB default applies
          if (!isSqlDefaultExpr(val)) {
            sanitizedRecordData[col.name] = val;
          }
        } else {
          // Regular fields: include non-empty values
          if (val !== undefined && val !== null && val !== '') {
            sanitizedRecordData[col.name] = val;
          }
        }
      });

      const payload = {
        table_name: selectedTable,
        record_data: sanitizedRecordData,
        external_ref: externalRef || undefined
      };

      const res = await ingestionApi.insertRecord(payload);
      setIngestionResult(res.data);
    } catch (err) {
      setErrorMessage(err.message || 'Ingestion request failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-[1400px] mx-auto pb-12">
      {/* Header */}
      <div className="pb-4 border-b border-slate-200">
        <h2 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          <UploadCloud className="w-6 h-6 text-indigo-600" />
          Data Ingestion & Staging Pipeline
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          Simulate incoming data feeds via unconstrained staging tables with automated integrity verification before transactional commit or quarantine isolation.
        </p>
      </div>

      {/* Target Table Selector */}
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-3">
          Select Target Business Entity (Six Core Tables)
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {CORE_TABLES.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setSelectedTable(t.id)}
              className={`p-3 rounded-lg border text-left transition-all ${
                selectedTable === t.id
                  ? 'border-indigo-600 bg-indigo-50/50 shadow-sm ring-1 ring-indigo-600'
                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <Database className={`w-4 h-4 ${selectedTable === t.id ? 'text-indigo-600' : 'text-slate-400'}`} />
                <span className={`text-sm font-semibold ${selectedTable === t.id ? 'text-indigo-950' : 'text-slate-800'}`}>
                  {t.label}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 line-clamp-2">{t.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Staging Pipeline Architecture Flow Banner */}
      <div className="bg-slate-900 text-slate-200 p-4 rounded-lg flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-3">
          <Layers className="w-5 h-5 text-indigo-400 flex-shrink-0" />
          <div>
            <span className="font-semibold text-white">Staging Pipeline Workflow:</span>
            <span className="text-slate-400 ml-2">
              Incoming Payload &rarr; <code className="text-indigo-300">staging_{selectedTable}</code> &rarr; Integrity Validator &rarr; Production / Quarantine
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="LOW">ACID Isolated</Badge>
          <Badge variant="CRITICAL">Quarantine Protected</Badge>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form Column */}
        <div className="lg:col-span-7 bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>Record Attributes</span>
                <span className="text-xs font-mono font-normal text-slate-500">
                  (Target: <strong className="text-slate-900">{selectedTable}</strong>)
                </span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Staging buffer: <code className="text-indigo-600">staging_{selectedTable}</code>
              </p>
            </div>

            {/* Quick-Fill Presets for Demo */}
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-400 mr-1 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Presets:
              </span>
              <button
                type="button"
                onClick={() => handleQuickFill('valid')}
                className="px-2 py-1 text-xs rounded bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 font-medium transition-colors"
                title="Fill with valid data guaranteed to commit to production"
              >
                Valid Record
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('orphan')}
                className="px-2 py-1 text-xs rounded bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 font-medium transition-colors"
                title="Fill with missing foreign key to trigger quarantine isolation"
              >
                Orphan FK
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('domain')}
                className="px-2 py-1 text-xs rounded bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 font-medium transition-colors"
                title="Fill with out-of-range numerical domain to trigger rejection"
              >
                Domain Anomaly
              </button>
            </div>
          </div>

          {schemaLoading ? (
            <div className="py-12">
              <LoadingSpinner label="Inspecting table metadata and foreign key relationships..." />
            </div>
          ) : schemaData ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* External Reference */}
              <div className="bg-slate-50 p-3 rounded-md border border-slate-200 mb-2">
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  External Data Reference / Ingestion Batch ID
                </label>
                <input
                  type="text"
                  value={externalRef}
                  onChange={(e) => setExternalRef(e.target.value)}
                  placeholder="e.g. BATCH-SYS-2026-001"
                  className="w-full text-xs font-mono px-3 py-1.5 rounded border border-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              {/* Dynamic Columns */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {schemaData.columns
                  ?.filter((c) => !c.is_primary_key)
                  .map((col) => {
                    const isFk = col.is_foreign_key;
                    const fkOpts = schemaData.fk_options?.[col.name] || [];
                    const isRequired = !col.is_nullable && col.default_value === null;

                    return (
                      <div key={col.name} className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <label className="font-medium text-slate-800">
                            {col.name} {isRequired && <span className="text-rose-500 font-bold">*</span>}
                          </label>
                          <span className="text-[10px] font-mono text-slate-400">
                            {col.data_type} {isFk && `-> ${col.referenced_table}`}
                          </span>
                        </div>

                        {/* DB-Generated Timestamp/Datetime or Foreign key or standard input */}
                        {isDbGeneratedTimestamp(col) ? (
                          <div className="space-y-1.5">
                            <div className="flex items-center justify-between px-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-xs">
                              <div className="flex items-center gap-2 text-slate-700">
                                <Clock className="w-3.5 h-3.5 text-indigo-600 flex-shrink-0" />
                                <span className="font-medium text-slate-700">Automatically generated by database</span>
                              </div>
                              {showCustomTimestamp[col.name] ? (
                                <button
                                  type="button"
                                  onClick={() => {
                                    setShowCustomTimestamp((prev) => ({ ...prev, [col.name]: false }));
                                    handleInputChange(col.name, '');
                                  }}
                                  className="text-[11px] text-slate-500 hover:text-slate-800 underline font-sans"
                                >
                                  Use Auto
                                </button>
                              ) : (
                                <button
                                  type="button"
                                  onClick={() => setShowCustomTimestamp((prev) => ({ ...prev, [col.name]: true }))}
                                  className="text-[11px] text-indigo-600 hover:text-indigo-800 font-medium underline font-sans"
                                >
                                  Override
                                </button>
                              )}
                            </div>
                            {showCustomTimestamp[col.name] && (
                              <div className="space-y-1">
                                <input
                                  type="text"
                                  value={formData[col.name] || ''}
                                  onChange={(e) => handleInputChange(col.name, e.target.value)}
                                  placeholder="YYYY-MM-DD HH:MM:SS"
                                  className="w-full text-xs px-2.5 py-1.5 rounded border border-indigo-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono bg-indigo-50/20"
                                />
                                <p className="text-[10px] text-slate-400">
                                  Enter custom timestamp (e.g. 2026-11-04 10:00:00) or click 'Use Auto'.
                                </p>
                              </div>
                            )}
                          </div>
                        ) : isFk && fkOpts.length > 0 ? (
                          <div className="space-y-1">
                            <select
                              value={formData[col.name] || ''}
                              onChange={(e) => handleInputChange(col.name, e.target.value)}
                              className="w-full text-xs px-2.5 py-1.5 rounded border border-slate-300 bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                            >
                              <option value="">-- Select Valid Parent ({col.referenced_table}) --</option>
                              {fkOpts.map((opt) => (
                                <option key={opt.value} value={opt.value}>
                                  {opt.label}
                                </option>
                              ))}
                              <option value="999999">999999 - [Simulate Orphan Anomaly]</option>
                            </select>
                          </div>
                        ) : col.data_type === 'enum' || col.name === 'status' ? (
                          <select
                            value={formData[col.name] || ''}
                            onChange={(e) => handleInputChange(col.name, e.target.value)}
                            className="w-full text-xs px-2.5 py-1.5 rounded border border-slate-300 bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                          >
                            <option value="ENROLLED">ENROLLED</option>
                            <option value="COMPLETED">COMPLETED</option>
                            <option value="DROPPED">DROPPED</option>
                            <option value="SUSPENDED">SUSPENDED (Invalid Enum Demo)</option>
                          </select>
                        ) : (
                          <input
                            type={
                              col.data_type.includes('int') || col.data_type.includes('decimal') || col.data_type.includes('numeric')
                                ? 'number'
                                : col.data_type === 'date'
                                ? 'date'
                                : 'text'
                            }
                            step={col.data_type.includes('decimal') ? '0.01' : '1'}
                            value={formData[col.name] !== undefined ? formData[col.name] : ''}
                            onChange={(e) => handleInputChange(col.name, e.target.value)}
                            placeholder={`Enter ${col.name}...`}
                            className="w-full text-xs px-2.5 py-1.5 rounded border border-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                          />
                        )}
                      </div>
                    );
                  })}
              </div>

              {/* Submit Buttons */}
              <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-100">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => fetchSchema(selectedTable)}
                  disabled={submitting}
                >
                  <RefreshCw className="w-3.5 h-3.5 mr-1" />
                  Reset Form
                </Button>

                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={submitting}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white"
                >
                  {submitting ? (
                    'Processing Pipeline...'
                  ) : (
                    <>
                      <UploadCloud className="w-3.5 h-3.5 mr-1.5" />
                      Stage & Ingest Record
                    </>
                  )}
                </Button>
              </div>
            </form>
          ) : null}
        </div>

        {/* Right Status / Ingestion Pipeline Output */}
        <div className="lg:col-span-5 space-y-4">
          {/* Error Banner */}
          {errorMessage && (
            <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-rose-900">Ingestion Error</h4>
                <p className="mt-1">{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Success Ingestion Result */}
          {ingestionResult && ingestionResult.status === 'COMMITTED_TO_PRODUCTION' && (
            <div className="p-5 rounded-lg bg-emerald-50 border border-emerald-200 shadow-sm space-y-3">
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-bold text-emerald-950">Ingestion & Validation Passed!</h4>
                  <p className="text-xs text-emerald-800">Record safely committed to production database.</p>
                </div>
              </div>

              <div className="bg-white p-3 rounded border border-emerald-200/80 space-y-1.5 text-xs font-mono">
                <div className="flex justify-between py-1 border-b border-emerald-50">
                  <span className="text-slate-500">Target Table:</span>
                  <span className="font-bold text-slate-900">{ingestionResult.target_table}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-emerald-50">
                  <span className="text-slate-500">Staging ID:</span>
                  <span className="text-indigo-600 font-bold">{ingestionResult.staging_id}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-emerald-50">
                  <span className="text-slate-500">Production PK:</span>
                  <span className="text-emerald-700 font-bold">{ingestionResult.production_pk}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Status:</span>
                  <Badge variant="LOW">VALID & COMMITTED</Badge>
                </div>
              </div>

              <p className="text-xs text-emerald-900 font-medium">{ingestionResult.message}</p>
            </div>
          )}

          {/* Rejection / Quarantine Result */}
          {ingestionResult && ingestionResult.status === 'REJECTED_TO_QUARANTINE' && (
            <div className="p-5 rounded-lg bg-rose-50 border border-rose-200 shadow-sm space-y-3">
              <div className="flex items-center gap-2.5">
                <ShieldAlert className="w-6 h-6 text-rose-600 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-bold text-rose-950">Integrity Violation Detected!</h4>
                  <p className="text-xs text-rose-800">Production was guarded. Corrupted record isolated to quarantine.</p>
                </div>
              </div>

              <div className="bg-white p-3 rounded border border-rose-200/80 space-y-1.5 text-xs font-mono">
                <div className="flex justify-between py-1 border-b border-rose-50">
                  <span className="text-slate-500">Staging Buffer:</span>
                  <span className="font-bold text-slate-800">staging_{ingestionResult.target_table} (ID: {ingestionResult.staging_id})</span>
                </div>
                <div className="flex justify-between py-1 border-b border-rose-50">
                  <span className="text-slate-500">Quarantine Vault ID:</span>
                  <span className="text-rose-700 font-bold">QUAR-{ingestionResult.quarantine_id}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Production Table Impact:</span>
                  <span className="text-emerald-600 font-bold">0 Rows Mutated (ACID Safe)</span>
                </div>
              </div>

              {/* Itemized Validation Errors */}
              <div className="space-y-1.5 pt-1">
                <span className="text-xs font-bold text-rose-900 block">Identified Relational Inconsistencies:</span>
                <ul className="space-y-1">
                  {ingestionResult.validation_errors?.map((err, idx) => (
                    <li key={idx} className="text-xs text-rose-800 flex items-start gap-1.5 bg-rose-100/50 p-2 rounded">
                      <span className="font-bold text-rose-700">&bull;</span>
                      <span>{err}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Educational Architecture Info Card */}
          <div className="bg-white p-5 rounded-lg border border-slate-200 text-xs space-y-3">
            <h4 className="font-bold text-slate-900 flex items-center gap-1.5 text-xs uppercase tracking-wider">
              <Info className="w-4 h-4 text-indigo-600" />
              How the Self-Healing Staging Pattern Works
            </h4>
            <div className="space-y-2 text-slate-600 leading-relaxed">
              <p>
                1. <strong>Staging Landing:</strong> External data payloads enter unconstrained staging tables (<code className="text-slate-800">staging_*</code>) to prevent raw API ingestion crashes.
              </p>
              <p>
                2. <strong>Deep Validation:</strong> Integrity rules verify domain ranges, check nullability, and query parent tables (<code className="text-slate-800">SELECT COUNT(*) FROM parent WHERE id = ...</code>) to ensure foreign key integrity.
              </p>
              <p>
                3. <strong>ACID Guarantee:</strong> Valid records are transactionally inserted into the production business tables. Invalid records are immediately archived into <code className="text-slate-800">quarantine_records</code>, preventing any production database corruption.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataIngestionPage;

