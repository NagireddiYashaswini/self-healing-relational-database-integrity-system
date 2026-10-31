import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ label = 'Loading data...', size = 'md' }) => {
  const SIZES = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3 text-slate-400">
      <Loader2 className={`${SIZES[size]} animate-spin text-emerald-500`} />
      <span className="text-sm font-medium tracking-wide">{label}</span>
    </div>
  );
};

export default LoadingSpinner;
