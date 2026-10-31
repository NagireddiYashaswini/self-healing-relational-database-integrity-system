import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ label = 'Loading data...', size = 'md' }) => {
  const SIZES = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className="flex flex-col items-center justify-center py-10 gap-2.5 text-slate-500">
      <Loader2 className={`${SIZES[size]} animate-spin text-indigo-600`} />
      <span className="text-xs font-medium text-slate-500">{label}</span>
    </div>
  );
};

export default LoadingSpinner;
