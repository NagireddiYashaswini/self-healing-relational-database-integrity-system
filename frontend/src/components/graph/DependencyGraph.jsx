import React, { useState, useMemo } from 'react';
import { ZoomIn, ZoomOut, RefreshCw, AlertCircle, ArrowRight, ShieldAlert, Layers } from 'lucide-react';
import { Badge } from '../common/Badge';

export const DependencyGraph = ({
  nodes = [],
  edges = [],
  hasCycles = false,
  cycleNodes = [],
  onSelectTable,
  selectedTable = null,
}) => {
  const [zoom, setZoom] = useState(1);
  const [filterType, setFilterType] = useState('ALL'); // 'ALL', 'BUSINESS', 'STAGING', 'SYSTEM'

  // Filter nodes
  const filteredNodes = useMemo(() => {
    if (filterType === 'ALL') return nodes;
    return nodes.filter(n => n.table_type === filterType);
  }, [nodes, filterType]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  const filteredEdges = useMemo(() => {
    return edges.filter(e => filteredNodeIds.has(e.from_node) && filteredNodeIds.has(e.to_node));
  }, [edges, filteredNodeIds]);

  // Layout node coordinates in a circular or multi-tiered hierarchy
  const nodePositions = useMemo(() => {
    const positions = {};
    const n = filteredNodes.length;
    if (n === 0) return positions;

    // Distribute nodes in an elliptical layout with grouping
    const width = 850;
    const height = 550;
    const centerX = width / 2;
    const centerY = height / 2;
    const radiusX = width * 0.38;
    const radiusY = height * 0.38;

    filteredNodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / n;
      positions[node.id] = {
        x: centerX + radiusX * Math.cos(angle),
        y: centerY + radiusY * Math.sin(angle),
      };
    });

    return positions;
  }, [filteredNodes]);

  // Highlight connections for selected table
  const connectedEdgeSet = useMemo(() => {
    if (!selectedTable) return new Set();
    const set = new Set();
    edges.forEach((e, idx) => {
      if (e.from_node === selectedTable || e.to_node === selectedTable) {
        set.add(idx);
      }
    });
    return set;
  }, [selectedTable, edges]);

  const NODE_COLORS = {
    BUSINESS: 'fill-slate-900 stroke-blue-500 text-blue-400',
    STAGING: 'fill-slate-900 stroke-amber-500 text-amber-400',
    SYSTEM: 'fill-slate-900 stroke-purple-500 text-purple-400',
    QUARANTINE: 'fill-slate-900 stroke-rose-500 text-rose-400',
  };

  return (
    <div className="flex flex-col h-full rounded-2xl glass-panel border border-slate-800 overflow-hidden">
      {/* Graph Toolbar */}
      <div className="flex flex-wrap items-center justify-between p-3.5 border-b border-slate-800/80 bg-slate-900/60 gap-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Relational Network Canvas</span>
          {hasCycles ? (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-rose-500/20 text-rose-300 border border-rose-500/40">
              <AlertCircle className="w-3.5 h-3.5" /> Cycle Detected
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Acyclic (Valid DAG)
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Table Type Filter */}
          <div className="flex items-center bg-slate-950/80 rounded-lg p-0.5 border border-slate-800 text-xs">
            {['ALL', 'BUSINESS', 'STAGING', 'SYSTEM'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-2.5 py-1 rounded font-medium transition-colors ${
                  filterType === type ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {type}
              </button>
            ))}
          </div>

          {/* Zoom controls */}
          <div className="flex items-center bg-slate-950/80 rounded-lg p-0.5 border border-slate-800">
            <button
              onClick={() => setZoom(z => Math.max(0.6, z - 0.1))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="px-2 text-xs font-mono text-slate-400">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom(z => Math.min(1.6, z + 0.1))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setZoom(1)}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 ml-1 border-l border-slate-800 pl-1.5"
              title="Reset View"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative flex-1 bg-slate-950/90 overflow-hidden min-h-[460px] flex items-center justify-center p-4">
        <svg
          viewBox="0 0 900 600"
          className="w-full h-full transition-transform duration-150"
          style={{ transform: `scale(${zoom})` }}
        >
          <defs>
            {/* Standard FK Arrow */}
            <marker
              id="arrowhead"
              markerWidth="8"
              markerHeight="6"
              refX="18"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />
            </marker>
            {/* Active Highlight Arrow */}
            <marker
              id="arrowhead-active"
              markerWidth="10"
              markerHeight="7"
              refX="19"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#10b981" />
            </marker>
          </defs>

          {/* Directed Edges */}
          {filteredEdges.map((edge, idx) => {
            const p1 = nodePositions[edge.from_node];
            const p2 = nodePositions[edge.to_node];
            if (!p1 || !p2) return null;

            const isHighlighted = connectedEdgeSet.has(idx);
            const isLogical = edge.relationship_type === 'LOGICAL_RULE';

            return (
              <g key={`edge-${idx}`}>
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke={isHighlighted ? '#10b981' : isLogical ? '#f59e0b' : '#334155'}
                  strokeWidth={isHighlighted ? 2.5 : 1.5}
                  strokeDasharray={isLogical ? '4,4' : undefined}
                  markerEnd={isHighlighted ? 'url(#arrowhead-active)' : 'url(#arrowhead)'}
                  opacity={selectedTable && !isHighlighted ? 0.25 : 0.85}
                />
              </g>
            );
          })}

          {/* Interactive Nodes */}
          {filteredNodes.map((node) => {
            const pos = nodePositions[node.id];
            if (!pos) return null;

            const isSelected = selectedTable === node.id;
            const isCycle = cycleNodes.includes(node.id);
            const hasIssues = node.issue_count > 0;

            let strokeColor = '#3b82f6';
            if (node.table_type === 'STAGING') strokeColor = '#f59e0b';
            if (node.table_type === 'SYSTEM') strokeColor = '#a855f7';
            if (node.table_type === 'QUARANTINE') strokeColor = '#f43f5e';
            if (isCycle) strokeColor = '#ef4444';
            if (isSelected) strokeColor = '#10b981';

            return (
              <g
                key={`node-${node.id}`}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={() => onSelectTable && onSelectTable(node.id)}
                className="cursor-pointer transition-transform duration-100 hover:scale-105"
              >
                {/* Outer Glow when selected */}
                {isSelected && (
                  <circle r="46" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" strokeWidth="1.5" strokeDasharray="3,3" />
                )}

                {/* Main Node Circle */}
                <circle
                  r="38"
                  fill="#0f172a"
                  stroke={strokeColor}
                  strokeWidth={isSelected ? 3 : 2}
                  className="shadow-2xl"
                />

                {/* Table Name Label */}
                <text
                  textAnchor="middle"
                  dy="-4"
                  className="text-[11px] font-bold fill-slate-100 select-none pointer-events-none"
                >
                  {node.label.length > 13 ? `${node.label.slice(0, 11)}..` : node.label}
                </text>

                {/* Subtitle: Row Count */}
                <text
                  textAnchor="middle"
                  dy="14"
                  className="text-[9px] font-mono fill-slate-400 select-none pointer-events-none"
                >
                  {node.row_count} rows
                </text>

                {/* Issue Count Badge */}
                {hasIssues && (
                  <g transform="translate(24, -24)">
                    <circle r="10" fill="#f43f5e" />
                    <text
                      textAnchor="middle"
                      dy="3.5"
                      className="text-[9px] font-bold fill-white select-none pointer-events-none"
                    >
                      {node.issue_count}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 flex flex-wrap items-center gap-3 bg-slate-900/90 backdrop-blur-md p-2 rounded-lg border border-slate-800 text-[11px] text-slate-300">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Business
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Staging
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span> System
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Issue / Quarantine
          </div>
          <div className="flex items-center gap-1.5 text-slate-400 border-l border-slate-800 pl-2">
            <span>Parent ➔ Child Reference</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DependencyGraph;
