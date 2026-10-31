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

    const width = 850;
    const height = 520;
    const centerX = width / 2;
    const centerY = height / 2;
    const radiusX = width * 0.38;
    const radiusY = height * 0.36;

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

  return (
    <div className="flex flex-col h-full rounded-lg bg-white border border-slate-200 shadow-xs overflow-hidden">
      {/* Graph Toolbar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2.5 border-b border-slate-200 bg-white gap-2">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Relational Schema Topology
          </span>
          {hasCycles ? (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-200">
              <AlertCircle className="w-3 h-3" /> Cycle Detected
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              Acyclic (DAG Valid)
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Table Type Filter Tabs */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded text-xs">
            {['ALL', 'BUSINESS', 'STAGING', 'SYSTEM'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                  filterType === type
                    ? 'bg-white text-slate-900 font-semibold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {type}
              </button>
            ))}
          </div>

          {/* Zoom controls */}
          <div className="flex items-center bg-slate-50 rounded border border-slate-200 text-xs">
            <button
              onClick={() => setZoom(z => Math.max(0.6, z - 0.1))}
              className="p-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-l"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="px-2 font-mono text-[11px] text-slate-600">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom(z => Math.min(1.6, z + 0.1))}
              className="p-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoom(1)}
              className="p-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-r border-l border-slate-200 pl-1.5"
              title="Reset View"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* SVG Canvas with Clean Professional Dot Matrix */}
      <div 
        className="relative flex-1 overflow-hidden min-h-[460px] flex items-center justify-center p-4 bg-white"
        style={{
          backgroundImage: 'radial-gradient(#E2E8F0 1px, transparent 1px)',
          backgroundSize: '16px 16px'
        }}
      >
        <svg
          viewBox="0 0 900 550"
          className="w-full h-full transition-transform duration-150"
          style={{ transform: `scale(${zoom})` }}
        >
          <defs>
            {/* Standard FK Arrow */}
            <marker
              id="arrowhead"
              markerWidth="7"
              markerHeight="5"
              refX="17"
              refY="2.5"
              orient="auto"
            >
              <polygon points="0 0, 7 2.5, 0 5" fill="#94A3B8" />
            </marker>
            {/* Active Highlight Arrow */}
            <marker
              id="arrowhead-active"
              markerWidth="8"
              markerHeight="6"
              refX="18"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#4F46E5" />
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
                  stroke={isHighlighted ? '#4F46E5' : isLogical ? '#D97706' : '#CBD5E1'}
                  strokeWidth={isHighlighted ? 2.5 : 1.25}
                  strokeDasharray={isLogical ? '4,3' : undefined}
                  markerEnd={isHighlighted ? 'url(#arrowhead-active)' : 'url(#arrowhead)'}
                  opacity={selectedTable && !isHighlighted ? 0.3 : 1}
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

            let strokeColor = '#6366F1';
            let fillColor = '#FFFFFF';
            if (node.table_type === 'STAGING') strokeColor = '#F59E0B';
            if (node.table_type === 'SYSTEM') strokeColor = '#64748B';
            if (node.table_type === 'QUARANTINE') strokeColor = '#EF4444';
            if (isCycle) strokeColor = '#DC2626';
            if (isSelected) {
              strokeColor = '#4F46E5';
              fillColor = '#EEF2FF';
            }

            return (
              <g
                key={`node-${node.id}`}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={() => onSelectTable && onSelectTable(node.id)}
                className="cursor-pointer transition-transform duration-150 hover:scale-105"
              >
                {/* Active Selection Glow Ring */}
                {isSelected && (
                  <circle
                    r="44"
                    fill="none"
                    stroke="#4F46E5"
                    strokeWidth="1.5"
                    strokeDasharray="3,3"
                  />
                )}

                {/* Main Node Circle */}
                <circle
                  r="36"
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  className="shadow-xs"
                />

                {/* Table Name Label */}
                <text
                  textAnchor="middle"
                  dy="-3"
                  className="text-[11px] font-bold font-mono fill-slate-900 select-none pointer-events-none"
                >
                  {node.label.length > 12 ? `${node.label.slice(0, 10)}..` : node.label}
                </text>

                {/* Subtitle: Row Count */}
                <text
                  textAnchor="middle"
                  dy="13"
                  className="text-[10px] font-mono fill-slate-500 select-none pointer-events-none"
                >
                  {node.row_count} rows
                </text>

                {/* Issue Badge */}
                {hasIssues && (
                  <g transform="translate(22, -22)">
                    <circle r="9" fill="#EF4444" />
                    <text
                      textAnchor="middle"
                      dy="3"
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
        <div className="absolute bottom-3 left-3 flex flex-wrap items-center gap-3 bg-white/95 backdrop-blur-xs px-3 py-1.5 rounded border border-slate-200 text-xs text-slate-700 shadow-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-indigo-600"></span> Business
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span> Staging
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-slate-500"></span> System
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span> Issues
          </div>
          <div className="text-slate-400 border-l border-slate-200 pl-2 font-mono text-[11px]">
            Parent ➔ Child Reference
          </div>
        </div>
      </div>
    </div>
  );
};

export default DependencyGraph;
