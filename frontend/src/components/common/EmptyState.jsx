import React from 'react';
import { Database, ShieldCheck } from 'lucide-react';
import { Button } from './Button';

export const EmptyState = ({
  icon: Icon = ShieldCheck,
  title = 'No Data Found',
  description = 'No records or issues match the current query criteria.',
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center border border-dashed border-slate-300 rounded-lg bg-slate-50/50">
      <div className="p-2.5 rounded-md bg-slate-100 text-slate-500 mb-2.5 border border-slate-200">
        <Icon className="w-5 h-5 text-slate-500" />
      </div>
      <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
      <p className="mt-1 text-xs text-slate-500 max-w-sm leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <div className="mt-3">
          <Button variant="primary" size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};

export default EmptyState;
