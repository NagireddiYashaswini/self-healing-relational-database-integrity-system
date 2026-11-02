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
  const [selectedTable, setSelectedTable] = useState('departments');
  const [tableNeighborhood, setTableNeighborhood] = useState(null);
  const [neighborhoodLoading, setNeighborhoodLoading] = useState(false);

  const fetchGraph = async () => {
    try {
      setLoading(true);
      const res = await dependenciesApi.getGraph();
      setGraphData(res.data);
      const nodes = res.data?.nodes || [];
      if (nodes.length > 0) {
        const hasCurrent = nodes.some(n => n.id === selectedTable);
        if (!hasCurrent) {
          const defaultNode = nodes.find(n => n.table_type === 'BUSINESS') || nodes[0];
          setSelectedTable(defaultNode.id);
        }
      }
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
    <div className="space-y-4 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
            Relational Dependency & Topology Analyzer
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Directed acyclic graph (DAG) of parent-child constraints, foreign key relationships, cycle prevention, and blast radius impact.
          </p>
        </div>

        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          onClick={fetchGraph}
        >
          Refresh Topology
        </Button>
      </div>

      {/* Main Grid: Interactive Canvas + Side Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: Interactive Graph Canvas */}
        <div className="lg:col-span-2 h-[580px] flex flex-col">
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
        <div className="space-y-3.5">
          {/* Table Selection Dropdown Card */}
          <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-indigo-600" /> Focus Target Entity
            </h3>

            <select
              value={selectedTable || ''}
              onChange={(e) => fetchNeighborhood(e.target.value)}
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded text-xs font-mono text-slate-900 font-bold focus:outline-none focus:border-indigo-500"
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
            <div className="bg-white border border-slate-200 rounded-lg p-6 flex justify-center shadow-xs">
              <LoadingSpinner label="Traversing dependency subtree..." size="sm" />
            </div>
          ) : tableNeighborhood ? (
            <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-2.5 border-b border-slate-200">
                <span className="text-xs font-bold font-mono text-slate-900">`{tableNeighborhood.table_name}`</span>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => navigate(`/issues?table_name=${tableNeighborhood.table_name}`)}
                >
                  View Issues
                </Button>
              </div>

              {/* Direct Parents */}
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1.5">
                  Direct Parents (Referenced Tables)
                </span>
                {tableNeighborhood.direct_parents.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {tableNeighborhood.direct_parents.map((p) => (
                      <button
                        key={p}
                        onClick={() => fetchNeighborhood(p)}
                        className="px-2 py-0.5 rounded bg-indigo-50 border border-indigo-200 text-indigo-800 text-xs font-mono font-medium hover:bg-indigo-100 transition-colors"
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">No parent dependencies (Root Entity)</p>
                )}
              </div>

              {/* Direct Children */}
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1.5">
                  Direct Children (Dependent Tables)
                </span>
                {tableNeighborhood.direct_children.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {tableNeighborhood.direct_children.map((c) => (
                      <button
                        key={c}
                        onClick={() => fetchNeighborhood(c)}
                        className="px-2 py-0.5 rounded bg-amber-50 border border-amber-200 text-amber-800 text-xs font-mono font-medium hover:bg-amber-100 transition-colors"
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">No dependent child tables (Leaf Entity)</p>
                )}
              </div>

              {/* Blast Radius Assessment */}
              <div className="pt-3 border-t border-slate-200">
                <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-rose-700 mb-1">
                  <ShieldAlert className="w-3.5 h-3.5" /> Repair Blast Radius
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Modifications to <strong className="text-slate-800">`{tableNeighborhood.table_name}`</strong> cascade verification across{' '}
                  <strong className="text-rose-600 font-bold">{tableNeighborhood.blast_radius_tables.length}</strong> downstream table(s):
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {tableNeighborhood.blast_radius_tables.map((tbl) => (
                    <span key={tbl} className="px-2 py-0.5 rounded bg-rose-50 border border-rose-200 text-rose-800 text-[11px] font-mono">
                      {tbl}
                    </span>
                  ))}
                  {tableNeighborhood.blast_radius_tables.length === 0 && (
                    <span className="text-emerald-700 text-xs font-mono font-medium bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      Isolated (Zero cascade risk)
                    </span>
                  )}
                </div>
              </div>
            </div>
          ) : null}

          {/* Topological Ordering Summary */}
          {graphData?.topological_order && graphData.topological_order.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-lg p-3.5 shadow-xs text-xs space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                Topological Safe Deletion Order
              </span>
              <p className="text-[11px] text-slate-500">
                Children must be repaired before parent entities:
              </p>
              <div className="flex flex-wrap gap-1 font-mono text-[10px]">
                {graphData.topological_order.slice(-6).map((tbl, i) => (
                  <span key={tbl} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200 font-medium">
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
