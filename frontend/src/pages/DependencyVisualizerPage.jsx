import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Network,
  Layers,
  ArrowRight,
  ShieldAlert,
  AlertTriangle,
  RefreshCw,
  GitCommit,
  Radio,
  FileQuestion
} from 'lucide-react';
import { dependenciesApi } from '../services/api';
import { DependencyGraph } from '../components/graph/DependencyGraph';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const DependencyVisualizerPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [graphData, setGraphData] = useState(null);
  const [selectedTable, setSelectedTable] = useState('courses');
  const [tableNeighborhood, setTableNeighborhood] = useState(null);
  const [neighborhoodLoading, setNeighborhoodLoading] = useState(false);

  const fetchGraph = async () => {
    try {
      setLoading(true);
      const res = await dependenciesApi.getGraph();
      setGraphData(res.data);
    } catch (err) {
      console.error('Failed to load dependency graph:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  const fetchNeighborhood = async (tableName) => {
    setSelectedTable(tableName);
    setNeighborhoodLoading(true);
    try {
      const res = await dependenciesApi.getTableDependencies(tableName);
      setTableNeighborhood(res.data);
    } catch (err) {
      console.error('Failed to load table neighborhood:', err);
    } finally {
      setNeighborhoodLoading(false);
    }
  };

  useEffect(() => {
    if (selectedTable) {
      fetchNeighborhood(selectedTable);
    }
  }, [selectedTable]);

  if (loading) {
    return <LoadingSpinner label="Computing relational schema graph and analyzing foreign key topology..." size="lg" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            Relational Dependency Graph Visualizer
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Topological network of parent-child constraints, foreign keys, cycle detection, and repair blast radius calculations.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          onClick={fetchGraph}
        >
          Refresh Topology
        </Button>
      </div>

      {/* Main Grid: Interactive Canvas + Side Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Interactive Graph Canvas */}
        <div className="lg:col-span-2 h-[600px] flex flex-col">
          <DependencyGraph
            nodes={graphData?.nodes || []}
            edges={graphData?.edges || []}
            hasCycles={graphData?.has_cycles || false}
            cycleNodes={graphData?.cycle_nodes || []}
            selectedTable={selectedTable}
            onSelectTable={fetchNeighborhood}
          />
        </div>

        {/* Right Col: Table Neighborhood & Impact Inspector */}
        <div className="space-y-4">
          {/* Table Selection Dropdown Card */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Radio className="w-4 h-4 text-emerald-400" /> Focus Target Table
            </h3>

            <select
              value={selectedTable || ''}
              onChange={(e) => fetchNeighborhood(e.target.value)}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-emerald-400 font-bold focus:outline-none"
            >
              {graphData?.nodes?.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.label} ({n.row_count} rows)
                </option>
              ))}
            </select>
          </div>

          {/* Neighborhood Inspection Details */}
          {neighborhoodLoading ? (
            <div className="glass-panel p-8 rounded-2xl border border-slate-800 flex justify-center">
              <LoadingSpinner label="Traversing dependency subtree..." size="sm" />
            </div>
          ) : tableNeighborhood ? (
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="text-sm font-bold font-mono text-white">`{tableNeighborhood.table_name}`</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/issues?table_name=${tableNeighborhood.table_name}`)}
                  className="text-xs"
                >
                  View Issues
                </Button>
              </div>

              {/* Direct Parents */}
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
                  Direct Parent Tables (Foreign Key Sources)
                </span>
                {tableNeighborhood.direct_parents.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {tableNeighborhood.direct_parents.map((p) => (
                      <span
                        key={p}
                        onClick={() => fetchNeighborhood(p)}
                        className="px-2.5 py-1 rounded bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-mono cursor-pointer hover:bg-blue-500/20"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic">No parent dependencies (Root Entity)</p>
                )}
              </div>

              {/* Direct Children */}
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
                  Direct Children (Dependent Tables)
                </span>
                {tableNeighborhood.direct_children.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {tableNeighborhood.direct_children.map((c) => (
                      <span
                        key={c}
                        onClick={() => fetchNeighborhood(c)}
                        className="px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono cursor-pointer hover:bg-amber-500/20"
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic">No dependent child tables (Leaf Entity)</p>
                )}
              </div>

              {/* Blast Radius Assessment */}
              <div className="pt-3 border-t border-slate-800">
                <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-rose-400 mb-1">
                  <ShieldAlert className="w-4 h-4" /> Repair Blast Radius
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Modifying or deleting records in <strong className="text-slate-200">`{tableNeighborhood.table_name}`</strong> will cascade or require verification across{' '}
                  <strong className="text-rose-400">{tableNeighborhood.blast_radius_tables.length}</strong> downstream table(s):
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {tableNeighborhood.blast_radius_tables.map((tbl) => (
                    <span key={tbl} className="px-2 py-0.5 rounded bg-rose-500/15 border border-rose-500/30 text-rose-300 text-[11px] font-mono">
                      {tbl}
                    </span>
                  ))}
                  {tableNeighborhood.blast_radius_tables.length === 0 && (
                    <span className="text-emerald-400 text-xs font-mono">None (Safe from cascade side-effects)</span>
                  )}
                </div>
              </div>
            </div>
          ) : null}

          {/* Topological Ordering Summary */}
          {graphData?.topological_order && graphData.topological_order.length > 0 && (
            <div className="glass-panel p-4 rounded-xl border border-slate-800 text-xs space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                Topological Deletion Order (Safe Cleanup Order)
              </span>
              <p className="text-[11px] text-slate-400">
                Children must be repaired/quarantined before parents:
              </p>
              <div className="flex flex-wrap gap-1 font-mono text-[10px] text-slate-300">
                {graphData.topological_order.slice(-6).map((tbl, i) => (
                  <span key={tbl} className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    {i + 1}. {tbl}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DependencyVisualizerPage;
