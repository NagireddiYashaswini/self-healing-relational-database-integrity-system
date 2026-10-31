import React from 'react';

const SEVERITY_STYLES = {
  CRITICAL: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
  HIGH: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  MEDIUM: 'bg-sky-500/15 text-sky-400 border border-sky-500/30',
  LOW: 'bg-slate-500/15 text-slate-400 border border-slate-500/30',
};

const STATUS_STYLES = {
  OPEN: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
  REVIEWED: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  APPROVED: 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30',
  REPAIRED: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  IGNORED: 'bg-slate-500/15 text-slate-400 border border-slate-500/30',
  FAILED: 'bg-red-600/20 text-red-300 border border-red-500/40',
  PENDING: 'bg-amber-500/15 text-amber-300 border border-amber-500/30',
  SUCCESS: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  COMMITTED: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  ROLLED_BACK: 'bg-purple-500/15 text-purple-400 border border-purple-500/30',
  ACTIVE: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  RESTORED: 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
  BUSINESS: 'bg-blue-500/15 text-blue-300 border border-blue-500/30',
  STAGING: 'bg-amber-500/15 text-amber-300 border border-amber-500/30',
  SYSTEM: 'bg-purple-500/15 text-purple-300 border border-purple-500/30',
  QUARANTINE: 'bg-rose-500/15 text-rose-300 border border-rose-500/30',
};

export const Badge = ({ children, variant, className = '' }) => {
  const style = SEVERITY_STYLES[variant] || STATUS_STYLES[variant] || 'bg-slate-800 text-slate-300 border border-slate-700';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium tracking-wide uppercase ${style} ${className}`}>
      {children || variant}
    </span>
  );
};

export default Badge;
