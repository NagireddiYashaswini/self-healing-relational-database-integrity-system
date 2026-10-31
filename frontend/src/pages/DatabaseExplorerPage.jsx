import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Database,
  Key,
  Link as LinkIcon,
  Search,
  ScanSearch,
  Eye,
  Layers,
  Table as TableIcon,
  RefreshCw,
  List,
  LayoutGrid,
  CheckCircle2,
  Server
} from 'lucide-react';
import { databaseApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const DatabaseExplorerPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [tables, setTables] = useState([]);
  const [dbStatus, setDbStatus] = useState(null);
  const [search, setSearch] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'grid'
  const [inspectTable, setInspectTable] = useState(null);
  const [tableDetail, setTableDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('columns'); // 'columns', 'indexes', 'sample'

  const fetchTablesAndStatus = async () => {
    try {
      setLoading(true);
      const [tablesRes, statusRes] = await Promise.all([
        databaseApi.getTables(),
        databaseApi.getStatus().catch(() => ({ data: null })),
      ]);
      setTables(tablesRes.data || []);
      setDbStatus(statusRes.data);
    } catch (err) {
      console.error('Failed to fetch tables:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTablesAndStatus();
  }, []);

  const openTableDetails = async (tableName) => {
    setInspectTable(tableName);
    setDetailLoading(true);
    setActiveTab('columns');
    try {
      const res = await databaseApi.getTableDetail(tableName);
      setTableDetail(res.data);
    } catch (err) {
      console.error('Failed to load table details:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const filteredTables = tables.filter((t) => {
    const matchesSearch = t.table_name.toLowerCase().includes(search.toLowerCase());
    const matchesType = selectedType === 'ALL' || t.table_type === selectedType;
    return matchesSearch && matchesType;
  });

  const totalRecords = tables.reduce((acc, t) => acc + (t.row_count || 0), 0);

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Database Schema & Object Explorer
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Enterprise relational catalog of MariaDB / MySQL tables, columns, constraints, foreign keys, and indexes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={RefreshCw}
            loading={loading}
            onClick={fetchTablesAndStatus}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={ScanSearch}
            onClick={() => navigate('/scanner')}
          >
            Scan Database
          </Button>
        </div>
      </div>

      {/* TOP METRICS SUMMARY BAR */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3 rounded-lg bg-white border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Connected Catalog</span>
            <span className="font-mono text-xs font-bold text-slate-900 truncate block mt-0.5">
              {dbStatus?.database_name || 'self_healing_test_db'}
            </span>
          </div>
          <Badge variant="SUCCESS">Active</Badge>
        </div>

        <div className="p-3 rounded-lg bg-white border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Storage Engine</span>
            <span className="text-xs font-bold text-slate-900 block mt-0.5">
              {dbStatus?.engine || 'InnoDB'}
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">ACID</span>
        </div>

        <div className="p-3 rounded-lg bg-white border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Discovered Tables</span>
            <span className="font-mono text-base font-bold text-slate-900 block mt-0.5">
              {tables.length}
            </span>
          </div>
          <span className="text-[11px] text-slate-500">{filteredTables.length} shown</span>
        </div>

        <div className="p-3 rounded-lg bg-white border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Total Row Cardinality</span>
            <span className="font-mono text-base font-bold text-indigo-600 block mt-0.5">
              {totalRecords.toLocaleString()}
            </span>
          </div>
          <Layers className="w-4 h-4 text-slate-400" />
        </div>
      </div>

      {/* TOOLBAR: Search + Filter Tabs + View Mode Toggle */}
      <div className="p-3 bg-white border border-slate-200 rounded-lg shadow-xs flex flex-wrap items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter tables by name..."
            className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500 font-mono"
          />
        </div>

        {/* Filter Badges / Pills */}
        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-md text-xs">
          {['ALL', 'BUSINESS', 'STAGING', 'SYSTEM', 'QUARANTINE'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                selectedType === type
                  ? 'bg-white text-slate-900 shadow-xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 border-l border-slate-200 pl-3">
          <button
            onClick={() => setViewMode('table')}
            className={`p-1.5 rounded text-xs transition-colors ${
              viewMode === 'table' ? 'bg-slate-200 text-slate-900' : 'text-slate-400 hover:text-slate-700'
            }`}
            title="Dense Table View"
          >
            <List className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1.5 rounded text-xs transition-colors ${
              viewMode === 'grid' ? 'bg-slate-200 text-slate-900' : 'text-slate-400 hover:text-slate-700'
            }`}
            title="Card Grid View"
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* TABLE LIST / GRID VIEW */}
      {loading ? (
        <LoadingSpinner label="Inspecting database schema..." />
      ) : filteredTables.length > 0 ? (
        viewMode === 'table' ? (
          /* High-Density Enterprise Table View */
          <div className="bg-white border border-slate-200 rounded-lg shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Table Name</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Engine</th>
                    <th className="py-2.5 px-3 text-right">Row Count</th>
                    <th className="py-2.5 px-3 text-right">Columns</th>
                    <th className="py-2.5 px-3 text-right">Foreign Keys</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {filteredTables.map((tbl) => (
                    <tr key={tbl.table_name} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 px-3 text-slate-900 font-bold flex items-center gap-2 min-w-0">
                        <TableIcon className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                        <span className="truncate">{tbl.table_name}</span>
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge variant={tbl.table_type} />
                      </td>
                      <td className="py-2.5 px-3 text-slate-500 font-mono">{tbl.engine}</td>
                      <td className="py-2.5 px-3 text-right text-slate-900 font-bold">{tbl.row_count}</td>
                      <td className="py-2.5 px-3 text-right text-slate-600">{tbl.column_count}</td>
                      <td className="py-2.5 px-3 text-right text-indigo-600 font-bold">{tbl.foreign_key_count}</td>
                      <td className="py-2.5 px-3 text-right font-sans">
                        <div className="flex items-center justify-end gap-1.5">
                          <Button
                            variant="secondary"
                            size="sm"
                            icon={Eye}
                            onClick={() => openTableDetails(tbl.table_name)}
                          >
                            Inspect Schema
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            icon={ScanSearch}
                            onClick={() => navigate(`/scanner?table=${tbl.table_name}`)}
                            title="Run scanner against this table"
                          >
                            Scan
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          /* Compact Grid View with Guaranteed No Badge Overlap */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredTables.map((tbl) => (
              <div
                key={tbl.table_name}
                className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs hover:border-slate-300 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 min-w-0 mb-3">
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="p-1.5 rounded bg-slate-100 text-slate-600 flex-shrink-0">
                        <TableIcon className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-xs font-bold font-mono text-slate-900 truncate" title={tbl.table_name}>
                          {tbl.table_name}
                        </h3>
                        <span className="text-[10px] text-slate-500 font-mono block leading-none mt-0.5">{tbl.engine}</span>
                      </div>
                    </div>
                    <Badge variant={tbl.table_type} className="flex-shrink-0" />
                  </div>

                  <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-100 text-center text-xs">
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-medium">Rows</span>
                      <span className="font-mono font-bold text-slate-900">{tbl.row_count}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-medium">Cols</span>
                      <span className="font-mono font-bold text-slate-700">{tbl.column_count}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-medium">FKs</span>
                      <span className="font-mono font-bold text-indigo-600">{tbl.foreign_key_count}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-3 pt-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={Eye}
                    onClick={() => openTableDetails(tbl.table_name)}
                    className="flex-1 text-xs"
                  >
                    Inspect
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    icon={ScanSearch}
                    onClick={() => navigate(`/scanner?table=${tbl.table_name}`)}
                    className="text-xs"
                  >
                    Scan
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        <div className="p-10 text-center bg-white border border-slate-200 rounded-lg text-slate-500 text-xs">
          No database tables match your search or filter criteria.
        </div>
      )}

      {/* PROFESSIONAL SCHEMA INSPECTION MODAL */}
      <Modal
        isOpen={!!inspectTable}
        onClose={() => setInspectTable(null)}
        title={`Table Schema: ${inspectTable}`}
        subtitle={`Engine: ${tableDetail?.engine || 'InnoDB'} · Category: ${tableDetail?.table_type || ''} · Total Rows: ${tableDetail?.row_count || 0}`}
        maxWidth="max-w-4xl"
      >
        {detailLoading ? (
          <LoadingSpinner label={`Loading schema definition for ${inspectTable}...`} />
        ) : tableDetail ? (
          <div className="space-y-4">
            {/* Modal Navigation Tabs & Action Bar */}
            <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setActiveTab('columns')}
                  className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                    activeTab === 'columns'
                      ? 'bg-slate-100 text-slate-900 font-semibold'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Columns ({tableDetail.columns.length})
                </button>
                <button
                  onClick={() => setActiveTab('indexes')}
                  className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                    activeTab === 'indexes'
                      ? 'bg-slate-100 text-slate-900 font-semibold'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Foreign Keys & Indexes ({tableDetail.foreign_keys.length + tableDetail.indexes.length})
                </button>
                <button
                  onClick={() => setActiveTab('sample')}
                  className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                    activeTab === 'sample'
                      ? 'bg-slate-100 text-slate-900 font-semibold'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Sample Data ({tableDetail.sample_rows.length} rows)
                </button>
              </div>

              <Button
                variant="primary"
                size="sm"
                icon={ScanSearch}
                onClick={() => {
                  const target = inspectTable;
                  setInspectTable(null);
                  navigate(`/scanner?table=${target}`);
                }}
              >
                Scan This Table
              </Button>
            </div>

            {/* TAB 1: Columns & Constraints */}
            {activeTab === 'columns' && (
              <div className="overflow-x-auto max-h-96 border border-slate-200 rounded">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-50 sticky top-0 text-slate-600 border-b border-slate-200 font-semibold">
                    <tr>
                      <th className="py-2 px-3">Column Name</th>
                      <th className="py-2 px-3">Data Type</th>
                      <th className="py-2 px-3">Nullable</th>
                      <th className="py-2 px-3">Keys / Flags</th>
                      <th className="py-2 px-3">Default</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {tableDetail.columns.map((col) => (
                      <tr key={col.name} className="hover:bg-slate-50/70">
                        <td className="py-2 px-3 font-bold text-slate-900 flex items-center gap-1.5">
                          {col.is_primary_key && <Key className="w-3.5 h-3.5 text-amber-500" title="Primary Key" />}
                          {col.is_foreign_key && <LinkIcon className="w-3.5 h-3.5 text-indigo-500" title="Foreign Key" />}
                          {col.name}
                        </td>
                        <td className="py-2 px-3 text-slate-700 font-semibold">{col.data_type}</td>
                        <td className="py-2 px-3">
                          {col.is_nullable ? (
                            <span className="text-slate-400">NULL</span>
                          ) : (
                            <span className="text-slate-800 font-bold">NOT NULL</span>
                          )}
                        </td>
                        <td className="py-2 px-3">
                          {col.is_primary_key && <Badge variant="HIGH">PK</Badge>}
                          {col.is_foreign_key && <Badge variant="MEDIUM" className="ml-1">FK</Badge>}
                        </td>
                        <td className="py-2 px-3 text-slate-500">{col.default_value !== null && col.default_value !== undefined ? String(col.default_value) : 'None'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* TAB 2: Indexes and Foreign Keys */}
            {activeTab === 'indexes' && (
              <div className="space-y-4">
                {/* Foreign Keys Section */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">Foreign Key Constraints</h4>
                  {tableDetail.foreign_keys.length > 0 ? (
                    <div className="space-y-2">
                      {tableDetail.foreign_keys.map((fk) => (
                        <div key={fk.constraint_name} className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs font-mono">
                          <div className="text-indigo-700 font-bold">{fk.constraint_name}</div>
                          <div className="text-slate-800 mt-1">
                            `{fk.column_name}` ➔ `{fk.referenced_table}`.`{fk.referenced_column}`
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400">No declared foreign keys on this table.</p>
                  )}
                </div>

                {/* Storage Indexes */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">Storage Indexes</h4>
                  <div className="overflow-x-auto max-h-48 border border-slate-200 rounded">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                        <tr>
                          <th className="py-1.5 px-3">Index Name</th>
                          <th className="py-1.5 px-3">Column</th>
                          <th className="py-1.5 px-3">Unique</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {tableDetail.indexes.map((idx, i) => (
                          <tr key={i} className="hover:bg-slate-50/70">
                            <td className="py-1.5 px-3 text-slate-900 font-medium">{idx.index_name}</td>
                            <td className="py-1.5 px-3 text-slate-600">{idx.column_name}</td>
                            <td className="py-1.5 px-3 font-bold text-slate-800">{idx.is_unique ? 'YES' : 'NO'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: Sample Data */}
            {activeTab === 'sample' && (
              <div className="overflow-x-auto max-h-96 border border-slate-200 rounded">
                {tableDetail.sample_rows.length > 0 ? (
                  <table className="w-full text-left text-xs font-mono border-collapse">
                    <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                      <tr>
                        {Object.keys(tableDetail.sample_rows[0]).map((key) => (
                          <th key={key} className="py-2 px-3 whitespace-nowrap">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {tableDetail.sample_rows.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-slate-50/70">
                          {Object.values(row).map((val, cIdx) => (
                            <td key={cIdx} className="py-2 px-3 whitespace-nowrap text-slate-800">
                              {val === null ? <span className="text-slate-400 italic">NULL</span> : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="text-xs text-slate-500 py-6 text-center">Table contains 0 rows.</p>
                )}
              </div>
            )}
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

export default DatabaseExplorerPage;
