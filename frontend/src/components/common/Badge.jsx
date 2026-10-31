import React from 'react';

const VARIANTS = {
  // Severities
  CRITICAL: 'bg-rose-50 text-rose-700 border-rose-200',
  HIGH: 'bg-amber-50 text-amber-800 border-amber-200',
  MEDIUM: 'bg-sky-50 text-sky-700 border-sky-200',
  LOW: 'bg-slate-100 text-slate-700 border-slate-200',

  // Statuses
  OPEN: 'bg-amber-50 text-amber-800 border-amber-200',
  REVIEWED: 'bg-sky-50 text-sky-700 border-sky-200',
  APPROVED: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  REPAIRED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  IGNORED: 'bg-slate-100 text-slate-600 border-slate-200',
  FAILED: 'bg-rose-50 text-rose-700 border-rose-200',
  SUCCESS: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  COMPLETED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  COMMITTED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  ROLLED_BACK: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  RUNNING: 'bg-sky-50 text-sky-700 border-sky-200',
  IN_PROGRESS: 'bg-sky-50 text-sky-700 border-sky-200',
  PENDING: 'bg-amber-50 text-amber-800 border-amber-200',
  ACTIVE: 'bg-emerald-50 text-emerald-700 border-emerald-200',

  // Table Types
  BUSINESS: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  STAGING: 'bg-amber-50 text-amber-800 border-amber-200',
  SYSTEM: 'bg-slate-100 text-slate-700 border-slate-200',
  QUARANTINE: 'bg-rose-50 text-rose-700 border-rose-200',
};

export const Badge = ({ variant = 'LOW', children, className = '' }) => {
  const normKey = String(variant).toUpperCase();
  const classes = VARIANTS[normKey] || 'bg-slate-100 text-slate-700 border-slate-200';
  const label = children || variant;

  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium border leading-none tracking-tight whitespace-nowrap flex-shrink-0 ${classes} ${className}`}
    >
      {label}
    </span>
  );
};

export default Badge;
