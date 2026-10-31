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
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Settings & MySQL Connection
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Engine diagnostics, environment configuration parameters, and demonstration replay tools.
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

      {/* Grid: Server Health + Environment Settings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Connection Diagnostics Card */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <Server className="w-4 h-4 text-emerald-400" /> XAMPP MySQL Engine
            </h3>
            {dbStatus?.connected ? (
              <Badge variant="SUCCESS">Connected</Badge>
            ) : (
              <Badge variant="FAILED">Offline</Badge>
            )}
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Server Version:</span>
              <span className="text-slate-200 font-bold">{dbStatus?.server_version || 'Unknown'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Connected User:</span>
              <span className="text-slate-200">{dbStatus?.connected_user || 'root@localhost'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Active Database:</span>
              <span className="text-emerald-400 font-bold">{dbStatus?.database_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Total Tables:</span>
              <span className="text-slate-200">{dbStatus?.table_count || 0} tables discovered</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Ping Latency:</span>
              <span className="text-emerald-400">{dbStatus?.latency_ms || 0} ms</span>
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            {dbStatus?.message}
          </p>
        </div>

        {/* Environment Configuration Parameters */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <Settings className="w-4 h-4 text-blue-400" /> Environment Parameters
          </h3>

          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Database Host:</span>
              <span className="text-slate-200">{config.db_host || '127.0.0.1'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Database Port:</span>
              <span className="text-slate-200">{config.db_port || 3306}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Database Encoding:</span>
              <span className="text-slate-200">{config.db_charset || 'utf8mb4'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Storage Engine:</span>
              <span className="text-slate-200">InnoDB (ACID + Foreign Keys)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Credentials Security:</span>
              <span className="text-emerald-400">Environment Redacted</span>
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Application connection parameters are loaded from <code className="text-slate-200 font-mono">backend/.env</code>. Passwords and secret credentials are never exposed through API responses or frontend client code.
          </p>
        </div>
      </div>

      {/* Demonstration Data Replay Tools */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
          <RotateCcw className="w-4 h-4 text-amber-400" /> Demonstration Data Replay Tools
        </h3>
        <p className="text-xs text-slate-400">
          Use these one-click tools to reset the database to a baseline clean state or re-inject controlled integrity anomalies for demonstration evaluation.
        </p>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Button
            variant="outline"
            size="md"
            icon={RotateCcw}
            loading={resetting}
            onClick={() => setResetConfirmOpen(true)}
          >
            Reset Database to Clean Baseline
          </Button>

          <Button
            variant="primary"
            size="md"
            icon={Play}
            loading={injecting}
            onClick={() => setInjectConfirmOpen(true)}
          >
            Re-Inject Demonstration Violations
          </Button>
        </div>
      </div>

      {/* Academic Project Metadata */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Academic DBMS Project Deliverable</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono text-slate-300">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <span className="text-[10px] text-slate-500 block uppercase">Project Title</span>
            <span className="font-bold text-white">Self-Healing Relational DBMS</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <span className="text-[10px] text-slate-500 block uppercase">Target Environment</span>
            <span>XAMPP MySQL / MariaDB</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <span className="text-[10px] text-slate-500 block uppercase">Core Concepts</span>
            <span className="text-emerald-400">ACID, FK Graph, Self-Healing</span>
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
        message="This operation will populate 10 controlled integrity violations (orphans, duplicates, out-of-range marks, invalid enums) into staging and active tables for scanning and healing demonstration."
        confirmText="Inject Violations"
      />
    </div>
  );
};

export default SettingsPage;
