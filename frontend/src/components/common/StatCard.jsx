import React from 'react';

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'emerald', // 'emerald', 'sky', 'amber', 'rose', 'purple'
  className = ''
}) => {
  const BORDER_ACCENTS = {
    emerald: 'border-emerald-500/30 hover:border-emerald-500/60 shadow-emerald-950/20',
    sky: 'border-sky-500/30 hover:border-sky-500/60 shadow-sky-950/20',
    amber: 'border-amber-500/30 hover:border-amber-500/60 shadow-amber-950/20',
    rose: 'border-rose-500/30 hover:border-rose-500/60 shadow-rose-950/20',
    purple: 'border-purple-500/30 hover:border-purple-500/60 shadow-purple-950/20',
  };

  const ICON_BG = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    sky: 'bg-sky-500/10 text-sky-400 border border-sky-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border border-rose-500/20',
    purple: 'bg-purple-500/10 text-purple-400 border border-purple-500/20',
  };

  return (
    <div className={`glass-panel p-5 rounded-xl transition-all duration-200 border shadow-lg ${BORDER_ACCENTS[variant]} ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg ${ICON_BG[variant]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-extrabold tracking-tight text-white font-mono">{value}</span>
      </div>
      {subtitle && (
        <p className="mt-1 text-xs text-slate-400 flex items-center gap-1">
          {subtitle}
        </p>
      )}
    </div>
  );
};

export default StatCard;
