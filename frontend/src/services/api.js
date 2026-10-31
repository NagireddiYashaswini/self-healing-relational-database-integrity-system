import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const errorMsg = error.response?.data?.message || error.response?.data?.error || error.message || 'Network request failed';
    console.error('API Request Error:', errorMsg);
    return Promise.reject(new Error(errorMsg));
  }
);

export const databaseApi = {
  getStatus: () => api.get('/database/status'),
  testConnection: () => api.post('/database/test-connection'),
  getTables: () => api.get('/database/tables'),
  getTableDetail: (tableName) => api.get(`/database/tables/${tableName}`),
  getRelationships: () => api.get('/database/relationships'),
  resetData: () => api.post('/database/reset'),
  injectViolations: () => api.post('/database/inject-violations'),
};

export const scansApi = {
  triggerScan: (payload) => api.post('/scans', payload),
  getScans: (limit = 20) => api.get('/scans', { params: { limit } }),
  getScan: (scanId) => api.get(`/scans/${scanId}`),
  getScanIssues: (scanId) => api.get(`/scans/${scanId}/issues`),
};

export const issuesApi = {
  getIssues: (params) => api.get('/issues', { params }),
  getIssue: (issueId) => api.get(`/issues/${issueId}`),
  updateStatus: (issueId, payload) => api.patch(`/issues/${issueId}/status`, payload),
};

export const repairsApi = {
  getRecommendations: (approvalStatus) => api.get('/repairs/recommendations', { params: { approval_status: approvalStatus } }),
  getRecommendation: (recId) => api.get(`/repairs/recommendations/${recId}`),
  previewRepair: (payload) => api.post('/repairs/preview', payload),
  approveRepair: (recommendationId) => api.post('/repairs/approve', null, { params: { recommendation_id: recommendationId } }),
  executeRepair: (payload) => api.post('/repairs/execute', payload),
  getExecutions: (limit = 50) => api.get('/repairs/executions', { params: { limit } }),
  getExecution: (execId) => api.get(`/repairs/executions/${execId}`),
};

export const dependenciesApi = {
  getGraph: () => api.get('/dependencies/graph'),
  getTableDependencies: (tableName) => api.get(`/dependencies/table/${tableName}`),
  assessImpact: (tableName, recordId, action) => api.get('/dependencies/impact', { params: { table_name: tableName, record_id: recordId, action } }),
};

export const transactionsApi = {
  runDemo: (scenario) => api.post('/transactions/demo', null, { params: { scenario } }),
  getTransactions: (limit = 50) => api.get('/transactions', { params: { limit } }),
};

export const recoveryApi = {
  getCheckpoints: (limit = 50) => api.get('/recovery/checkpoints', { params: { limit } }),
  createCheckpoint: (payload) => api.post('/recovery/checkpoints', payload),
  rollback: (payload) => api.post('/recovery/rollback', payload),
  getHistory: () => api.get('/recovery/history'),
};

export const auditApi = {
  getLogs: (params) => api.get('/audit-logs', { params }),
};

export const rulesApi = {
  getRules: (params) => api.get('/rules', { params }),
  createRule: (payload) => api.post('/rules', payload),
  updateRule: (ruleId, payload) => api.patch(`/rules/${ruleId}`, payload),
  testRule: (ruleId) => api.post(`/rules/${ruleId}/test`),
  deleteRule: (ruleId) => api.delete(`/rules/${ruleId}`),
};

export default api;
