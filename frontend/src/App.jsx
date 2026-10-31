import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';

import DashboardPage from './pages/DashboardPage';
import DatabaseExplorerPage from './pages/DatabaseExplorerPage';
import IntegrityScannerPage from './pages/IntegrityScannerPage';
import IssueManagementPage from './pages/IssueManagementPage';
import DependencyVisualizerPage from './pages/DependencyVisualizerPage';
import RepairCenterPage from './pages/RepairCenterPage';
import TransactionSimulatorPage from './pages/TransactionSimulatorPage';
import RecoveryCenterPage from './pages/RecoveryCenterPage';
import AuditLogsPage from './pages/AuditLogsPage';
import RulesConfigurationPage from './pages/RulesConfigurationPage';
import SettingsPage from './pages/SettingsPage';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="explorer" element={<DatabaseExplorerPage />} />
          <Route path="scanner" element={<IntegrityScannerPage />} />
          <Route path="issues" element={<IssueManagementPage />} />
          <Route path="dependencies" element={<DependencyVisualizerPage />} />
          <Route path="repairs" element={<RepairCenterPage />} />
          <Route path="simulator" element={<TransactionSimulatorPage />} />
          <Route path="recovery" element={<RecoveryCenterPage />} />
          <Route path="audit" element={<AuditLogsPage />} />
          <Route path="rules" element={<RulesConfigurationPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
