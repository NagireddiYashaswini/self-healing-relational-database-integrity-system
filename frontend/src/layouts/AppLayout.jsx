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
  RefreshCw,
  Play,
  ChevronRight
} from 'lucide-react';
import { databaseApi, scansApi } from '../services/api';
import { Button } from '../components/common/Button';

const NAV_GROUPS = [
  {
    title: 'OBSERVABILITY & SCHEMA',
    items: [
      { path: '/', label: 'Dashboard', icon: LayoutDashboard },
      { path: '/explorer', label: 'Database Explorer', icon: Database },
      { path: '/scanner', label: 'Integrity Scanner', icon: ScanSearch },
      { path: '/dependencies', label: 'Dependency Analysis', icon: Network },
      { path: '/issues', label: 'Issue Management', icon: AlertTriangle },
    ]
  },
  {
    title: 'SELF-HEALING & SAFETY',
    items: [
      { path: '/repairs', label: 'Repair Center', icon: Wrench },
      { path: '/simulator', label: 'Transaction Simulator', icon: Activity },
      { path: '/recovery', label: 'Recovery & Checkpoints', icon: History },
    ]
  },
  {
    title: 'AUDIT & CONFIGURATION',
    items: [
      { path: '/audit', label: 'Query History & Logs', icon: FileText },
      { path: '/rules', label: 'Rules Configuration', icon: Sliders },
      { path: '/settings', label: 'Settings & MySQL', icon: Settings },
    ]
  }
];

export const AppLayout = () => {
  const [dbStatus, setDbStatus] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const fetchStatus = async () => {
    try {
      setIsRefreshing(true);
      const res = await databaseApi.getStatus();
      setDbStatus(res.data);
    } catch (err) {
      setDbStatus({ connected: false, message: 'Database server unreachable' });
    } finally {
      setIsRefreshing(false);
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

  // Compute breadcrumb title based on current route
  const getRouteTitle = () => {
    const p = location.pathname;
    if (p === '/') return { section: 'Monitoring', title: 'Dashboard' };
    if (p === '/explorer') return { section: 'Schema', title: 'Database Explorer' };
    if (p === '/scanner') return { section: 'Integrity', title: 'Integrity Scanner' };
    if (p === '/dependencies') return { section: 'Topology', title: 'Dependency Analysis' };
    if (p === '/issues') return { section: 'Issues', title: 'Issue Management' };
    if (p === '/repairs') return { section: 'Operations', title: 'Repair Center' };
    if (p === '/simulator') return { section: 'ACID', title: 'Transaction Simulator' };
    if (p === '/recovery') return { section: 'Backups', title: 'Recovery & Checkpoints' };
    if (p === '/audit') return { section: 'Traceability', title: 'Query History & Audit' };
    if (p === '/rules') return { section: 'Rules', title: 'Rules Configuration' };
    if (p === '/settings') return { section: 'System', title: 'Settings & Status' };
    return { section: 'Overview', title: 'Dashboard' };
  };

  const breadcrumb = getRouteTitle();

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden antialiased">
      {/* Sidebar Desktop */}
      <aside className="hidden md:flex flex-col w-60 border-r border-slate-200 bg-white select-none flex-shrink-0 z-20">
        {/* Brand Header */}
        <div className="flex items-center gap-2.5 px-4 h-14 border-b border-slate-200">
          <div className="w-7 h-7 rounded bg-indigo-600 flex items-center justify-center text-white shadow-xs flex-shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xs font-bold tracking-tight text-slate-900 leading-none truncate">
              Self-Healing DBMS
            </h1>
            <span className="text-[10px] text-slate-500 font-mono block mt-1">
              InnoDB · v2.4.0
            </span>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-4">
          {NAV_GROUPS.map((group) => (
            <div key={group.title} className="space-y-1">
              <div className="px-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                {group.title}
              </div>
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700 font-semibold border border-indigo-100 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-slate-500'}`} />
                    <span className="truncate">{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Database Engine Status Card */}
        <div className="p-3 m-2.5 rounded-md bg-slate-50 border border-slate-200 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-slate-500">Database Engine</span>
            {dbStatus?.connected ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Active
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-rose-700">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span> Offline
              </span>
            )}
          </div>
          <div className="mt-1.5 text-xs font-mono font-semibold text-slate-800 truncate" title={dbStatus?.database_name || 'self_healing_test_db'}>
            {dbStatus?.database_name || (dbStatus?.connected ? 'self_healing_test_db' : 'Not Connected')}
          </div>
          <div className="text-[11px] text-slate-500 flex items-center justify-between mt-1">
            <span>{dbStatus?.tables?.length || 0} Tables</span>
            {dbStatus?.latency_ms !== undefined && (
              <span className="font-mono text-slate-600">{dbStatus.latency_ms} ms</span>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Layout */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-14 flex items-center justify-between px-4 sm:px-6 border-b border-slate-200 bg-white z-10 flex-shrink-0 select-none">
          {/* Left: Mobile Toggle & Breadcrumbs */}
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-1.5 text-slate-500 hover:text-slate-800 rounded hover:bg-slate-100"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>

            {/* Breadcrumb Indicator */}
            <div className="flex items-center gap-1.5 text-xs text-slate-500 min-w-0">
              <span className="hidden sm:inline font-medium text-slate-400">{breadcrumb.section}</span>
              <ChevronRight className="hidden sm:inline w-3 h-3 text-slate-400 flex-shrink-0" />
              <span className="font-semibold text-slate-800 truncate">{breadcrumb.title}</span>
            </div>
          </div>

          {/* Right: Live Status & Actions */}
          <div className="flex items-center gap-2.5">
            {/* Live Connection Status Tag */}
            <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono border ${
              dbStatus?.connected 
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
                : 'bg-rose-50 text-rose-800 border-rose-200'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${dbStatus?.connected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span className="font-semibold">{dbStatus?.connected ? 'Connected' : 'Offline'}</span>
              <span className="text-slate-400">·</span>
              <span className="text-slate-600 font-medium truncate max-w-[140px]">
                {dbStatus?.database_name || 'self_healing_test_db'}
              </span>
            </div>

            {/* Quick Refresh Status Button */}
            <Button
              variant="secondary"
              size="sm"
              icon={RefreshCw}
              loading={isRefreshing}
              onClick={fetchStatus}
              title="Refresh database connection status"
            >
              Refresh
            </Button>

            {/* Quick Trigger Scan Button */}
            <Button
              variant="primary"
              size="sm"
              icon={Play}
              loading={isScanning}
              onClick={handleQuickScan}
            >
              Scan Now
            </Button>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-b border-slate-200 p-4 space-y-3 z-30 shadow-md">
            {NAV_GROUPS.map((group) => (
              <div key={group.title} className="space-y-1">
                <div className="px-2 text-[10px] font-bold uppercase text-slate-400">
                  {group.title}
                </div>
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center gap-2 px-2.5 py-1.5 rounded text-xs font-medium ${
                        isActive
                          ? 'bg-indigo-50 text-indigo-700 font-semibold border border-indigo-100'
                          : 'text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5 text-slate-500" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </div>
            ))}
          </div>
        )}

        {/* Page Content Body */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50/60">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
