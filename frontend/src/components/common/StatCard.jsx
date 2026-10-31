import React from 'react';

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default',
  className = ''
}) => {
  const ICON_COLORS = {
    default: 'bg-slate-100 text-slate-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    sky: 'bg-sky-50 text-sky-600',
    amber: 'bg-amber-50 text-amber-600',
    rose: 'bg-rose-50 text-rose-600',
    purple: 'bg-indigo-50 text-indigo-600',
  };

  return (
    <div
      className={`bg-white border border-slate-200 rounded-lg p-4 shadow-xs flex flex-col justify-between h-full ${className}`}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 truncate">
          {title}
        </span>
        {Icon && (
          <div className={`p-1.5 rounded flex-shrink-0 ${ICON_COLORS[variant] || ICON_COLORS.default}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold font-mono text-slate-900 tracking-tight">
          {value}
        </span>
      </div>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-500 truncate" title={typeof subtitle === 'string' ? subtitle : undefined}>
          {subtitle}
        </p>
      )}
    </div>
  );
};

export default StatCard;
