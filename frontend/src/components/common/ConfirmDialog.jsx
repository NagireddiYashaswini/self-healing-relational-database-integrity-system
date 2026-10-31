import React from 'react';
import { Modal } from './Modal';
import { Button } from './Button';
import { AlertTriangle } from 'lucide-react';

export const ConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm Database Action',
  message = 'Are you sure you want to proceed with this database operation? This change may alter or update records in the active catalog.',
  confirmText = 'Execute Action',
  cancelText = 'Cancel',
  variant = 'danger',
  loading = false,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} maxWidth="max-w-md">
      <div className="flex flex-col gap-4">
        <div className="flex items-start gap-3 p-3.5 rounded bg-rose-50 border border-rose-200 text-rose-800">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-rose-600" />
          <p className="text-xs leading-relaxed text-rose-900">{message}</p>
        </div>

        <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
          <Button variant="secondary" onClick={onClose} disabled={loading} size="sm">
            {cancelText}
          </Button>
          <Button variant={variant} onClick={onConfirm} loading={loading} size="sm">
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default ConfirmDialog;
