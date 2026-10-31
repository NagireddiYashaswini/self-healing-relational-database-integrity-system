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
  Info
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
  const [search, setSearch] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [inspectTable, setInspectTable] = useState(null);
  const [tableDetail, setTableDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('columns'); // 'columns', 'indexes', 'sample'

  const fetchTables = async () => {
    try {
      setLoading(true);
      const res = await databaseApi.getTables();
      setTables(res.data || []);
    } catch (err) {
      console.error('Failed to fetch tables:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTables();
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Database Schema Explorer
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Live inspection of MySQL tables, data types, primary keys, foreign constraints, and row cardinality.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            loading={loading}
            onClick={fetchTables}
          >
            Refresh Tables
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={ScanSearch}
            onClick={() => navigate('/scanner')}
          >
            Scan Selected
          </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 glass-panel p-4 rounded-xl border border-slate-800">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tables by name..."
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 transition-colors font-mono"
          />
        </div>

        {/* Table Type Pill Filter */}
        <div className="flex items-center bg-slate-900 rounded-lg p-1 border border-slate-800 text-xs">
          {['ALL', 'BUSINESS', 'STAGING', 'SYSTEM', 'QUARANTINE'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                selectedType === type ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Tables Grid */}
      {loading ? (
        <LoadingSpinner label="Inspecting database schema..." />
      ) : filteredTables.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTables.map((tbl) => (
            <div
              key={tbl.table_name}
              className="glass-panel p-5 rounded-xl border border-slate-800 hover:border-emerald-500/40 transition-all shadow-lg flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-slate-800/80 text-emerald-400 border border-slate-700/60">
                      <TableIcon className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white font-mono group-hover:text-emerald-400 transition-colors">
                        {tbl.table_name}
                      </h3>
                      <span className="text-[10px] text-slate-400 font-mono">{tbl.engine} Engine</span>
                    </div>
                  </div>
                  <Badge variant={tbl.table_type} />
                </div>

                {/* Metadata Badges */}
                <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-800/80 text-center">
                  <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-[10px] uppercase text-slate-400 block font-semibold">Rows</span>
                    <span className="text-sm font-bold font-mono text-slate-100">{tbl.row_count}</span>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-[10px] uppercase text-slate-400 block font-semibold">Columns</span>
                    <span className="text-sm font-bold font-mono text-slate-100">{tbl.column_count}</span>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                    <span className="text-[10px] uppercase text-slate-400 block font-semibold">Foreign Keys</span>
                    <span className="text-sm font-bold font-mono text-emerald-400">{tbl.foreign_key_count}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-800/80">
                <Button
                  variant="outline"
                  size="sm"
                  icon={Eye}
                  onClick={() => openTableDetails(tbl.table_name)}
                  className="flex-1 text-xs"
                >
                  Inspect Schema
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={ScanSearch}
                  onClick={() => navigate(`/scanner?table=${tbl.table_name}`)}
                  className="text-xs"
                  title="Scan Table Only"
                >
                  Scan
                </Button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel p-12 text-center rounded-xl border border-slate-800 text-slate-400 text-sm">
          No database tables match your filter criteria.
        </div>
      )}

      {/* Schema Inspection Modal */}
      <Modal
        isOpen={!!inspectTable}
        onClose={() => setInspectTable(null)}
        title={`Table Schema: ${inspectTable}`}
        subtitle={`Type: ${tableDetail?.table_type || ''} • Total Rows: ${tableDetail?.row_count || 0}`}
        maxWidth="max-w-4xl"
      >
        {detailLoading ? (
          <LoadingSpinner label={`Loading schema definition for ${inspectTable}...`} />
        ) : tableDetail ? (
          <div className="space-y-4">
            {/* Modal Tabs */}
            <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
              <button
                onClick={() => setActiveTab('columns')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === 'columns' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Columns & Constraints ({tableDetail.columns.length})
              </button>
              <button
                onClick={() => setActiveTab('indexes')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === 'indexes' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Indexes & Foreign Keys ({tableDetail.indexes.length})
              </button>
              <button
                onClick={() => setActiveTab('sample')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeTab === 'sample' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Sample Data ({tableDetail.sample_rows.length} rows)
              </button>
            </div>

            {/* Tab 1: Columns */}
            {activeTab === 'columns' && (
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/80 sticky top-0 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2 px-3">Column Name</th>
                      <th className="py-2 px-3">Data Type</th>
                      <th className="py-2 px-3">Nullable</th>
                      <th className="py-2 px-3">Keys / Flags</th>
                      <th className="py-2 px-3">Default</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {tableDetail.columns.map((col) => (
                      <tr key={col.name} className="hover:bg-slate-800/30">
                        <td className="py-2.5 px-3 font-bold text-slate-200 flex items-center gap-1.5">
                          {col.is_primary_key && <Key className="w-3.5 h-3.5 text-amber-400" title="Primary Key" />}
                          {col.is_foreign_key && <LinkIcon className="w-3.5 h-3.5 text-blue-400" title="Foreign Key" />}
                          {col.name}
                        </td>
                        <td className="py-2.5 px-3 text-emerald-400">{col.data_type}</td>
                        <td className="py-2.5 px-3">
                          {col.is_nullable ? (
                            <span className="text-slate-400">NULL</span>
                          ) : (
                            <span className="text-rose-400 font-bold">NOT NULL</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3">
                          {col.is_primary_key && <Badge variant="HIGH">PK</Badge>}
                          {col.is_foreign_key && <Badge variant="MEDIUM" className="ml-1">FK</Badge>}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">{col.default_value || 'None'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Tab 2: Indexes and Foreign Keys */}
            {activeTab === 'indexes' && (
              <div className="space-y-4">
                {/* Foreign Keys Section */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Foreign Key Constraints</h4>
                  {tableDetail.foreign_keys.length > 0 ? (
                    <div className="space-y-2">
                      {tableDetail.foreign_keys.map((fk) => (
                        <div key={fk.constraint_name} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
                          <div className="text-emerald-400 font-bold">{fk.constraint_name}</div>
                          <div className="text-slate-300 mt-1">
                            `{fk.column_name}` ➔ `{fk.referenced_table}`.`{fk.referenced_column}`
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">No declared foreign keys on this table.</p>
                  )}
                </div>

                {/* Indexes Section */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Storage Indexes</h4>
                  <div className="overflow-x-auto max-h-48">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-1.5 px-3">Index Name</th>
                          <th className="py-1.5 px-3">Column</th>
                          <th className="py-1.5 px-3">Unique</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {tableDetail.indexes.map((idx, i) => (
                          <tr key={i} className="hover:bg-slate-800/30">
                            <td className="py-2 px-3 text-slate-200">{idx.index_name}</td>
                            <td className="py-2 px-3 text-slate-300">{idx.column_name}</td>
                            <td className="py-2 px-3">{idx.is_unique ? 'YES' : 'NO'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* Tab 3: Live Sample Rows */}
            {activeTab === 'sample' && (
              <div className="overflow-x-auto max-h-96">
                {tableDetail.sample_rows.length > 0 ? (
                  <table className="w-full text-left text-xs font-mono border-collapse">
                    <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                      <tr>
                        {Object.keys(tableDetail.sample_rows[0]).map((key) => (
                          <th key={key} className="py-2 px-3 whitespace-nowrap">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {tableDetail.sample_rows.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-slate-800/40">
                          {Object.values(row).map((val, cIdx) => (
                            <td key={cIdx} className="py-2 px-3 whitespace-nowrap text-slate-300">
                              {val === null ? <span className="text-slate-600 italic">NULL</span> : String(val)}
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
