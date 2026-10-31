import React, { useState, useEffect } from 'react';
import {
  Settings,
  Database,
  Server,
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  AlertTriangle,
  Play,
  Layers,
  Code
} from 'lucide-react';
import { databaseApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const SettingsPage = () => {
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [dbStatus, setDbStatus] = useState(null);
  const [resetting, setResetting] = useState(false);
  const [injecting, setInjecting] = useState(false);
  const [resetConfirmOpen, setResetConfirmOpen] = useState(false);
  const [injectConfirmOpen, setInjectConfirmOpen] = useState(false);

  const fetchConnectionStatus = async () => {
    try {
      setLoading(true);
      const res = await databaseApi.getStatus();
      setDbStatus(res.data);
    } catch (err) {
      console.error('Failed to get database status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnectionStatus();
  }, []);

  const handleTestConnection = async () => {
    setTesting(true);
    try {
      const res = await databaseApi.testConnection();
      setDbStatus(prev => ({ ...prev, ...res.data }));
      alert(res.message);
    } catch (err) {
      alert(`Connection test failed: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  const handleResetData = async () => {
    setResetting(true);
    try {
      const res = await databaseApi.resetData();
      alert(res.message);
      setResetConfirmOpen(false);
      fetchConnectionStatus();
    } catch (err) {
      alert(`Reset failed: ${err.message}`);
    } finally {
      setResetting(false);
    }
  };

  const handleInjectViolations = async () => {
    setInjecting(true);
    try {
      const res = await databaseApi.injectViolations();
      alert(res.message);
      setInjectConfirmOpen(false);
      fetchConnectionStatus();
    } catch (err) {
      alert(`Violation injection failed: ${err.message}`);
    } finally {
      setInjecting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner label="Querying server configuration..." size="lg" />;
  }

  const config = dbStatus?.config || {};

  return (
    <div className="space-y-5 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Settings className="w-5 h-5 text-indigo-600" />
            Settings & Database Engine Diagnostics
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time MySQL/MariaDB server diagnostics, runtime connection parameters, and controlled data replay tools.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          icon={Activity}
          loading={testing}
          onClick={handleTestConnection}
        >
          Test Live Connectivity
        </Button>
      </div>

      {/* Grid: Server Diagnostics + Environment Settings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Engine Diagnostics Card */}
        <div className="panel p-4 sm:p-5 space-y-3.5">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Server className="w-4 h-4 text-indigo-600" /> XAMPP MySQL Engine
            </h3>
            {dbStatus?.connected ? (
              <Badge variant="SUCCESS">Connected</Badge>
            ) : (
              <Badge variant="FAILED">Offline</Badge>
            )}
          </div>

          <div className="p-3 rounded-md bg-slate-50 border border-slate-200 space-y-2 text-xs font-mono">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Server Version:</span>
              <span className="text-slate-900 font-semibold">{dbStatus?.server_version || 'Unknown'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Connected User:</span>
              <span className="text-slate-900 font-semibold">{dbStatus?.connected_user || 'root@localhost'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Active Catalog:</span>
              <span className="text-indigo-700 font-bold">{dbStatus?.database_name}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Discovered Tables:</span>
              <span className="text-slate-900 font-semibold">{dbStatus?.table_count || 0} tables</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Ping Latency:</span>
              <span className="text-emerald-700 font-bold">{dbStatus?.latency_ms || 0} ms</span>
            </div>
          </div>

          <p className="text-xs text-slate-500 leading-relaxed">
            {dbStatus?.message}
          </p>
        </div>

        {/* Environment Configuration Card */}
        <div className="panel p-4 sm:p-5 space-y-3.5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Settings className="w-4 h-4 text-indigo-600" /> Connection Parameters
          </h3>

          <div className="p-3 rounded-md bg-slate-50 border border-slate-200 space-y-2 text-xs font-mono">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Host Address:</span>
              <span className="text-slate-900 font-semibold">{config.db_host || '127.0.0.1'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">TCP Port:</span>
              <span className="text-slate-900 font-semibold">{config.db_port || 3306}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Charset / Collation:</span>
              <span className="text-slate-900 font-semibold">{config.db_charset || 'utf8mb4'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Storage Engine:</span>
              <span className="text-indigo-700 font-bold">InnoDB (Transactional)</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Auth Privacy:</span>
              <span className="text-emerald-700 font-bold">Environment Redacted</span>
            </div>
          </div>

          <p className="text-xs text-slate-500 leading-relaxed">
            Connection parameters are managed via <code className="text-indigo-700 font-mono font-semibold bg-slate-100 px-1 py-0.5 rounded border border-slate-200">backend/.env</code>. Passwords and secret credentials are never exposed in API payloads or client-side bundles.
          </p>
        </div>
      </div>

      {/* Demonstration Data Replay Tools */}
      <div className="panel p-4 sm:p-5 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
          <RotateCcw className="w-4 h-4 text-indigo-600" /> Demonstration Data Replay Tools
        </h3>
        <p className="text-xs text-slate-500 leading-relaxed">
          One-click utility tools to reset the test database to a clean baseline or re-inject controlled integrity anomalies for demonstration and grading verification.
        </p>

        <div className="flex flex-wrap items-center gap-2.5 pt-1">
          <Button
            variant="secondary"
            size="sm"
            icon={RotateCcw}
            loading={resetting}
            onClick={() => setResetConfirmOpen(true)}
          >
            Reset Database to Clean Baseline
          </Button>

          <Button
            variant="primary"
            size="sm"
            icon={Play}
            loading={injecting}
            onClick={() => setInjectConfirmOpen(true)}
          >
            Re-Inject Demonstration Violations
          </Button>
        </div>
      </div>

      {/* Academic Project Metadata */}
      <div className="panel p-4 sm:p-5 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Academic DBMS Project Deliverable
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
          <div className="p-3 rounded-md bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Project Name</span>
            <span className="font-semibold text-slate-900">Self-Healing Relational DBMS</span>
          </div>
          <div className="p-3 rounded-md bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Target Runtime</span>
            <span className="font-semibold text-slate-900">XAMPP MariaDB 10.4.32</span>
          </div>
          <div className="p-3 rounded-md bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Core Modules</span>
            <span className="text-indigo-700 font-semibold">InnoDB ACID, FK Graph, Healer</span>
          </div>
        </div>
      </div>

      {/* Confirm Reset Dialog */}
      <ConfirmDialog
        isOpen={resetConfirmOpen}
        onClose={() => setResetConfirmOpen(false)}
        onConfirm={handleResetData}
        loading={resetting}
        title="Reset to Clean Baseline State"
        message="This operation will clear staging demo records and restore clean valid baseline data. Table structures and system logs will be preserved."
        confirmText="Confirm Reset"
      />

      {/* Confirm Inject Violations Dialog */}
      <ConfirmDialog
        isOpen={injectConfirmOpen}
        onClose={() => setInjectConfirmOpen(false)}
        onConfirm={handleInjectViolations}
        loading={injecting}
        variant="primary"
        title="Inject Demonstration Violations"
        message="This operation will populate controlled integrity violations (orphans, duplicates, negative prices, invalid enums) into staging and active tables for scanning and healing demonstration."
        confirmText="Inject Violations"
      />
    </div>
  );
};

export default SettingsPage;
