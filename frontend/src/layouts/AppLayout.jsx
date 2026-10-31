import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Database,
  ScanSearch,
  AlertTriangle,
  Network,
  Wrench,
  Activity,
  History,
  FileText,
  Sliders,
  Settings,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Menu,
  X,
  Play
} from 'lucide-react';
import { databaseApi, scansApi } from '../services/api';
import { Button } from '../components/common/Button';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/explorer', label: 'Database Explorer', icon: Database },
  { path: '/scanner', label: 'Integrity Scanner', icon: ScanSearch },
  { path: '/issues', label: 'Issue Management', icon: AlertTriangle },
  { path: '/dependencies', label: 'Dependency Graph', icon: Network },
  { path: '/repairs', label: 'Repair Center', icon: Wrench },
  { path: '/simulator', label: 'Transaction Simulator', icon: Activity },
  { path: '/recovery', label: 'Recovery Center', icon: History },
  { path: '/audit', label: 'Audit Logs', icon: FileText },
  { path: '/rules', label: 'Rules Configuration', icon: Sliders },
  { path: '/settings', label: 'Settings & Status', icon: Settings },
];

export const AppLayout = () => {
  const [dbStatus, setDbStatus] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const fetchStatus = async () => {
    try {
      const res = await databaseApi.getStatus();
      setDbStatus(res.data);
    } catch (err) {
      setDbStatus({ connected: false, message: 'Server unreachable' });
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleQuickScan = async () => {
    try {
      setIsScanning(true);
      await scansApi.triggerScan({ scan_type: 'FULL' });
      navigate('/scanner');
    } catch (err) {
      console.error('Scan trigger error:', err);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar Desktop */}
      <aside className="hidden md:flex flex-col w-64 border-r border-slate-800/80 bg-slate-925 select-none">
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-800/80">
          <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
              Self-Healing DBMS
            </h1>
            <span className="text-[10px] font-mono tracking-wider text-emerald-400 uppercase font-semibold">
              InnoDB v2.4.0
            </span>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-600/15 text-emerald-400 border border-emerald-500/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Database Quick Health Card */}
        <div className="p-3.5 m-3 rounded-xl glass-panel border border-slate-800 bg-slate-900/50">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-slate-400">Database Engine</span>
            {dbStatus?.connected ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Active
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-rose-400">
                <span className="w-2 h-2 rounded-full bg-rose-500"></span> Offline
              </span>
            )}
          </div>
          <div className="mt-2 text-xs font-mono text-slate-300">
            {dbStatus?.database_name || 'self_healing_db'}
          </div>
          <div className="text-[11px] text-slate-400 flex items-center justify-between mt-1">
            <span>{dbStatus?.tables?.length || 0} Tables</span>
            {dbStatus?.latency_ms && <span>{dbStatus.latency_ms} ms</span>}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="hidden sm:flex items-center gap-2">
              <span className="text-xs px-2.5 py-1 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60 font-mono">
                XAMPP MySQL / MariaDB
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Port 3306
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Connection Status Pill */}
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
              {dbStatus?.connected ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-300 font-medium hidden sm:inline">MySQL Connected</span>
                </>
              ) : (
                <>
                  <XCircle className="w-3.5 h-3.5 text-rose-400" />
                  <span className="text-rose-300 font-medium">Offline</span>
                </>
              )}
            </div>

            {/* Quick Trigger Scan Button */}
            <Button
              variant="primary"
              size="sm"
              icon={Play}
              loading={isScanning}
              onClick={handleQuickScan}
              className="text-xs"
            >
              Scan Database
            </Button>
          </div>
        </header>

        {/* Mobile Nav Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden glass-panel border-b border-slate-800 p-4 space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800"
                >
                  <Icon className="w-4 h-4 text-emerald-400" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        )}

        {/* Page View Body */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
