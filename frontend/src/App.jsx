import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';

import DashboardPage from './pages/DashboardPage';
import DatabaseExplorerPage from './pages/DatabaseExplorerPage';
import IntegrityScannerPage from './pages/IntegrityScannerPage';
import DependencyVisualizerPage from './pages/DependencyVisualizerPage';
import RecoveryCenterPage from './pages/RecoveryCenterPage';
import DataIngestionPage from './pages/DataIngestionPage';
import TransactionSimulatorPage from './pages/TransactionSimulatorPage';
import AuditLogsPage from './pages/AuditLogsPage';
import RulesConfigurationPage from './pages/RulesConfigurationPage';
import SettingsPage from './pages/SettingsPage';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="scanner" element={<IntegrityScannerPage />} />
          <Route path="dependencies" element={<DependencyVisualizerPage />} />
          <Route path="recovery" element={<RecoveryCenterPage />} />
          <Route path="ingestion" element={<DataIngestionPage />} />

          {/* Backward compatibility redirects */}
          <Route path="repairs" element={<Navigate to="/recovery" replace />} />
          <Route path="issues" element={<Navigate to="/recovery" replace />} />

          {/* Database Admin & Utility Tool Routes */}
          <Route path="explorer" element={<DatabaseExplorerPage />} />
          <Route path="simulator" element={<TransactionSimulatorPage />} />
          <Route path="audit" element={<AuditLogsPage />} />
          <Route path="rules" element={<RulesConfigurationPage />} />
          <Route path="settings" element={<SettingsPage />} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
