import React from 'react';
import { Loader2 } from 'lucide-react';

const VARIANTS = {
  primary:
    'bg-indigo-600 hover:bg-indigo-700 text-white border border-indigo-700/50 shadow-xs active:bg-indigo-800',
  secondary:
    'bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 shadow-xs active:bg-slate-100',
  outline:
    'bg-transparent hover:bg-slate-100 text-slate-700 border border-slate-300 active:bg-slate-200',
  ghost:
    'bg-transparent hover:bg-slate-100 text-slate-600 hover:text-slate-900',
  danger:
    'bg-rose-600 hover:bg-rose-700 text-white border border-rose-700/60 shadow-xs active:bg-rose-800',
  success:
    'bg-emerald-600 hover:bg-emerald-700 text-white border border-emerald-700/60 shadow-xs active:bg-emerald-800',
};

const SIZES = {
  sm: 'h-7 px-2.5 text-xs font-medium rounded',
  md: 'h-8 px-3 text-xs font-medium rounded-md',
  lg: 'h-9 px-4 text-sm font-medium rounded-md',
};

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  className = '',
  onClick,
  type = 'button',
  ...props
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-1.5 transition-colors select-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none ${VARIANTS[variant] || VARIANTS.primary} ${SIZES[size] || SIZES.md} ${className}`}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-3.5 h-3.5 animate-spin text-current" />
      ) : Icon ? (
        <Icon className="w-3.5 h-3.5 text-current" />
      ) : null}
      <span className="truncate">{children}</span>
    </button>
  );
};

export default Button;
