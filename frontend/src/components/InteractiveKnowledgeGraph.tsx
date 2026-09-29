import React, { useState, useEffect } from 'react';
import {
  Network, ArrowRight, ShieldCheck, Compass, Anchor,
  Flame, DollarSign, TrendingUp, AlertTriangle, Layers, Info
} from 'lucide-react';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  region?: string;
  risk_index?: number;
  epistemic_state?: 'OBSERVED' | 'DERIVED' | 'MODELLED' | 'SCENARIO';
}

interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  weight: number;
  confidence: number;
  explanation?: string;
  epistemic_state?: 'OBSERVED' | 'DERIVED' | 'MODELLED' | 'SCENARIO';
}

interface Cascade {
  cascade_id: string;
  name: string;
  sequence: string[];
  description: string;
}

export const InteractiveKnowledgeGraph: React.FC = () => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [cascades, setCascades] = useState<Cascade[]>([]);
  const [activeCascadeId, setActiveCascadeId] = useState<string>('hormuz_energy_shock');
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch('/api/graph')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch graph data');
        return res.json();
      })
      .then((data) => {
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
        if (data.canonical_cascades?.length) {
          setCascades(data.canonical_cascades);
          // Set initial edge selection
          const firstEdge = data.edges.find((e: GraphEdge) => e.explanation);
          if (firstEdge) setSelectedEdge(firstEdge);
        }
        setIsLoading(false);
      })
      .catch((err) => {
        console.warn('Error loading knowledge graph:', err);
        setIsLoading(false);
      });
  }, []);

  const activeCascade = cascades.find((c) => c.cascade_id === activeCascadeId) || cascades[0];

  // Helper to get node by ID
  const getNode = (id: string): GraphNode | undefined => nodes.find((n) => n.id === id);

  // Helper to get edge between two node IDs
  const getEdge = (sourceId: string, targetId: string): GraphEdge | undefined =>
    edges.find((e) => e.source === sourceId && e.target === targetId);

  // Helper for node type iconography
  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'country':
        return <Compass className="w-3.5 h-3.5" style={{ color: 'var(--astra-indigo)' }} />;
      case 'chokepoint':
        return <Anchor className="w-3.5 h-3.5" style={{ color: 'var(--agni-copper)' }} />;
      case 'commodity':
        return <Flame className="w-3.5 h-3.5" style={{ color: 'var(--status-warning)' }} />;
      case 'financial_asset':
        return <DollarSign className="w-3.5 h-3.5" style={{ color: 'var(--status-positive)' }} />;
      case 'macro_indicator':
      case 'sovereign_rate':
        return <TrendingUp className="w-3.5 h-3.5" style={{ color: 'var(--status-negative)' }} />;
      case 'volatility_index':
        return <AlertTriangle className="w-3.5 h-3.5" style={{ color: '#E11D48' }} />;
      default:
        return <Layers className="w-3.5 h-3.5" style={{ color: 'var(--astra-slate)' }} />;
    }
  };

  const getEpistemicBadge = (state?: string) => {
    switch (state) {
      case 'OBSERVED':
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider bg-emerald-900/30 text-emerald-400 border border-emerald-700/50">
            OBSERVED
          </span>
        );
      case 'DERIVED':
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider bg-sky-900/30 text-sky-400 border border-sky-700/50">
            DERIVED
          </span>
        );
      case 'MODELLED':
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider bg-amber-900/30 text-amber-400 border border-amber-700/50">
            MODELLED
          </span>
        );
      case 'SCENARIO':
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider bg-rose-900/30 text-rose-400 border border-rose-700/50">
            SCENARIO
          </span>
        );
      default:
        return (
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono text-[var(--astra-slate)] bg-[var(--astra-sandstone)]">
            ANALYTICAL
          </span>
        );
    }
  };

  return (
    <div
      className="astra-card overflow-hidden"
      style={{
        padding: 0,
        background: 'var(--astra-sandstone)',
        border: '1px solid var(--astra-sandstone-dark)',
      }}
    >
      {/* Header Bar */}
      <div
        className="px-5 py-3.5 flex flex-wrap items-center justify-between gap-3"
        style={{
          borderBottom: '1px solid var(--astra-sandstone-dark)',
          background: 'rgba(255, 255, 255, 0.4)',
        }}
      >
        <div className="flex items-center gap-2.5">
          <Network className="w-4.5 h-4.5" style={{ color: 'var(--agni-copper)' }} />
          <div>
            <h3
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '0.9375rem',
                fontWeight: 600,
                color: 'var(--astra-ink)',
                letterSpacing: '0.02em',
              }}
            >
              Knowledge Graph & Transmission Cascades
            </h3>
            <p
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.625rem',
                color: 'var(--astra-slate)',
                letterSpacing: '0.05em',
              }}
            >
              TOPOLOGICAL PROPAGATION · GEOSHOCK TO MACRO VOLATILITY
            </p>
          </div>
        </div>

        {/* Epistemic State Legend */}
        <div className="flex items-center gap-2">
          {getEpistemicBadge('OBSERVED')}
          {getEpistemicBadge('DERIVED')}
          {getEpistemicBadge('MODELLED')}
          {getEpistemicBadge('SCENARIO')}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="p-5 space-y-5">
        {/* Cascade Selection Buttons */}
        <div className="flex flex-wrap gap-2 items-center">
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--astra-slate)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginRight: '4px',
            }}
          >
            Transmission Cascade:
          </span>
          {cascades.map((c) => (
            <button
              key={c.cascade_id}
              onClick={() => {
                setActiveCascadeId(c.cascade_id);
                setSelectedNode(null);
                const firstEdge = getEdge(c.sequence[0], c.sequence[1]);
                if (firstEdge) setSelectedEdge(firstEdge);
              }}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${
                activeCascadeId === c.cascade_id
                  ? 'bg-[var(--agni-copper)] text-white shadow-sm font-semibold'
                  : 'bg-[var(--astra-ivory)] text-[var(--astra-ink)] hover:bg-[var(--astra-sandstone-dark)] border border-[var(--astra-sandstone-dark)]'
              }`}
              style={{ fontFamily: 'var(--font-sans)' }}
            >
              {c.name}
            </button>
          ))}
        </div>

        {/* Interactive Chain Sequence */}
        {activeCascade && (
          <div
            className="p-4 rounded-lg"
            style={{
              background: 'var(--astra-ivory)',
              border: '1px solid var(--astra-sandstone-dark)',
            }}
          >
            <div className="flex items-center justify-between mb-3">
              <span
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.6875rem',
                  color: 'var(--astra-slate)',
                  letterSpacing: '0.04em',
                }}
              >
                INTERACTIVE TRANSMISSION CHAIN (CLICK NODES OR ARROWS TO EXPLAIN CAUSALITY)
              </span>
              <span className="intel-tag">Deterministic Graph</span>
            </div>

            {/* Horizontal Flow Container */}
            <div className="flex flex-wrap items-center gap-2 overflow-x-auto py-2">
              {activeCascade.sequence.map((nodeId, idx) => {
                const node = getNode(nodeId);
                const isLast = idx === activeCascade.sequence.length - 1;
                const nextNodeId = !isLast ? activeCascade.sequence[idx + 1] : null;
                const edge = nextNodeId ? getEdge(nodeId, nextNodeId) : null;
                const isNodeSelected = selectedNode?.id === nodeId;
                const isEdgeSelected =
                  selectedEdge?.source === nodeId && selectedEdge?.target === nextNodeId;

                return (
                  <React.Fragment key={nodeId}>
                    {/* Node Card */}
                    <div
                      onClick={() => {
                        setSelectedNode(node || null);
                        if (edge) setSelectedEdge(edge);
                      }}
                      className={`cursor-pointer px-3 py-2 rounded border transition-all flex items-center gap-2 shadow-xs ${
                        isNodeSelected
                          ? 'border-[var(--agni-copper)] bg-[var(--astra-sandstone)] ring-1 ring-[var(--agni-copper)]'
                          : 'border-[var(--astra-sandstone-dark)] bg-white hover:border-[var(--astra-slate)]'
                      }`}
                      style={{ minWidth: '120px' }}
                    >
                      <div className="p-1 rounded bg-[var(--astra-sandstone)] flex items-center justify-center">
                        {node ? getNodeIcon(node.type) : <Layers className="w-3.5 h-3.5" />}
                      </div>
                      <div className="min-w-0">
                        <div
                          style={{
                            fontFamily: 'var(--font-sans)',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: 'var(--astra-ink)',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {node?.label || nodeId}
                        </div>
                        <div className="flex items-center gap-1 mt-0.5">
                          <span
                            style={{
                              fontFamily: 'var(--font-mono)',
                              fontSize: '0.5625rem',
                              color: 'var(--astra-slate)',
                              textTransform: 'uppercase',
                            }}
                          >
                            {node?.type.replace('_', ' ') || 'ENTITY'}
                          </span>
                          {node?.epistemic_state && getEpistemicBadge(node.epistemic_state)}
                        </div>
                      </div>
                    </div>

                    {/* Edge Connector */}
                    {!isLast && (
                      <div
                        onClick={() => {
                          if (edge) {
                            setSelectedEdge(edge);
                            setSelectedNode(null);
                          }
                        }}
                        className={`cursor-pointer p-1.5 rounded transition-all flex flex-col items-center justify-center group ${
                          isEdgeSelected
                            ? 'bg-[var(--agni-copper)] text-white shadow-xs'
                            : 'hover:bg-[var(--astra-sandstone-dark)] text-[var(--astra-slate)]'
                        }`}
                        title={edge?.explanation || 'Click to inspect causal edge'}
                      >
                        <ArrowRight className="w-4 h-4" />
                        <span
                          style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '0.5625rem',
                            letterSpacing: '0.04em',
                          }}
                        >
                          {edge?.weight ? `${Math.round(edge.weight * 100)}%` : '→'}
                        </span>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>
        )}

        {/* Causal Explanation & Evidence Inspection Drawer */}
        {(selectedEdge || selectedNode) && (
          <div
            className="p-4 rounded-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            style={{
              background: 'white',
              border: '1px solid var(--astra-sandstone-dark)',
              borderLeft: '4px solid var(--agni-copper)',
            }}
          >
            <div className="space-y-1 max-w-3xl">
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4" style={{ color: 'var(--agni-copper)' }} />
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    color: 'var(--astra-ink)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  {selectedEdge
                    ? `Causal Edge: ${getNode(selectedEdge.source)?.label} → ${getNode(selectedEdge.target)?.label}`
                    : `Node Detail: ${selectedNode?.label}`}
                </span>
                {selectedEdge?.epistemic_state && getEpistemicBadge(selectedEdge.epistemic_state)}
                {selectedNode?.epistemic_state && getEpistemicBadge(selectedNode.epistemic_state)}
              </div>
              <p
                style={{
                  fontFamily: 'var(--font-sans)',
                  fontSize: '0.8125rem',
                  color: 'var(--astra-ink)',
                  lineHeight: 1.5,
                }}
              >
                {selectedEdge?.explanation ||
                  `Active graph node of class '${selectedNode?.type}'. Represents sovereign geopolitical or macroeconomic variable in the AGNI transmission matrix.`}
              </p>
            </div>

            {selectedEdge && (
              <div className="flex items-center gap-3 shrink-0">
                <div className="text-right">
                  <div
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: 'var(--astra-ink)',
                    }}
                  >
                    {(selectedEdge.weight * 100).toFixed(0)}%
                  </div>
                  <div
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.5625rem',
                      color: 'var(--astra-slate)',
                    }}
                  >
                    TRANSMISSION ELASTICITY
                  </div>
                </div>
                <div
                  className="w-px h-7"
                  style={{ background: 'var(--astra-sandstone-dark)' }}
                />
                <div className="text-right">
                  <div
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: 'var(--status-positive)',
                    }}
                  >
                    {(selectedEdge.confidence * 100).toFixed(0)}%
                  </div>
                  <div
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.5625rem',
                      color: 'var(--astra-slate)',
                    }}
                  >
                    EMPIRICAL CONFIDENCE
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
