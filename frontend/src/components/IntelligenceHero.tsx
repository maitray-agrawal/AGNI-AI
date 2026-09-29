import React from 'react';
import { ArrowRight } from 'lucide-react';
import { AgniLogo } from '../brand/AgniLogo';
import { AgniWatermark } from '../brand/AgniWatermark';
import { AstraMark } from './AstraMark';

/* ──────────────────────────────────────────────────────────────────
   IntelligenceHero V2 — AGNI editorial hero with Live Signal Field.
   Right side: mini signal field replaces empty space.
   ────────────────────────────────────────────────────────────────── */

const WORKFLOW_STAGES = [
  { id: 'monitor',  label: 'MONITOR'  },
  { id: 'analyze',  label: 'ANALYZE'  },
  { id: 'model',    label: 'MODEL'    },
  { id: 'forecast', label: 'FORECAST' },
  { id: 'act',      label: 'ACT'      },
];

// Mini signal nodes for the hero right panel
const HERO_NODES = [
  { x: 72,  y: 28,  r: 5,   color: '#DC2626', label: 'Middle East',    count: 14 },
  { x: 58,  y: 18,  r: 3.5, color: '#9E3B24', label: 'E. Europe',      count: 9  },
  { x: 88,  y: 36,  r: 3.5, color: '#9E3B24', label: 'S. China Sea',   count: 7  },
  { x: 62,  y: 42,  r: 3,   color: '#B87333', label: 'Red Sea',        count: 6  },
  { x: 50,  y: 32,  r: 2.5, color: '#B87333', label: 'N. Africa',      count: 4  },
  { x: 80,  y: 50,  r: 2.5, color: '#CA8A04', label: 'Indo-Pacific',   count: 5  },
  { x: 30,  y: 55,  r: 2,   color: '#CA8A04', label: 'Latin America',  count: 3  },
  { x: 78,  y: 20,  r: 2,   color: '#66707A', label: 'Central Asia',   count: 2  },
];

const HERO_CONNECTIONS = [
  [0, 1], [0, 3], [0, 4], [1, 7], [2, 5],
];

interface IntelligenceHeroProps {
  activeModel?:   string;
  signalCount?:   number;
  newSignals?:    number;
}

export const IntelligenceHero: React.FC<IntelligenceHeroProps> = ({
  activeModel,
  signalCount  = 1284,
  newSignals   = 7,
}) => {
  const KPI_METRICS = [
    { label: 'Signals Detected',       value: signalCount.toLocaleString(), delta: '+12%',  positive: true  },
    { label: 'Emerging Risks',         value: '28',                          delta: '+3',    positive: false },
    { label: 'Correlated Events',      value: '134',                         delta: '+8',    positive: true  },
    { label: 'High-Confidence Insights', value: '87',                        delta: '94%',   positive: true  },
  ];

  return (
    <section
      className="relative rounded-xl overflow-hidden"
      style={{
        background: 'linear-gradient(120deg, var(--astra-sandstone) 0%, var(--astra-ivory) 55%)',
        border:     '1px solid var(--astra-sandstone-dark)',
        boxShadow:  'var(--shadow-lg)',
      }}
      aria-label="AGNI Intelligence Workspace"
    >
      {/* Background Canonical AgniWatermark */}
      <AgniWatermark
        size={420}
        opacity={0.035}
        className="-right-12 -top-12 z-0"
      />

      <div className="relative z-10 flex flex-col lg:flex-row">
        {/* ── Left: Brand + Copy ────────────────────────── */}
        <div className="flex-1 px-7 md:px-10 py-8 md:py-10">
          {/* Section 13: Top Attribution */}
          <div className="flex items-center gap-2 mb-3">
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.5625rem',
                letterSpacing: '0.18em',
                textTransform: 'uppercase',
                color: 'var(--agni-copper)',
                fontWeight: 700,
              }}
            >
              ASTRA X · INTELLIGENCE SYSTEM
            </span>
            <div style={{ width: 14, height: 1, background: 'var(--agni-copper)', opacity: 0.4 }} />
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.5rem',
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: 'var(--astra-slate)',
                fontWeight: 600,
              }}
            >
              SOVEREIGN · ON-PREMISE
            </span>
          </div>

          {/* Section 13: Product Mark + AGNI title + Live Counter */}
          <div className="flex items-center gap-3.5 mb-4">
            <AgniLogo variant="mark" size={44} theme="primary" />
            <div>
              <div className="flex items-baseline gap-2">
                <span
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '1.75rem',
                    fontWeight: 700,
                    letterSpacing: '0.12em',
                    lineHeight: 1,
                    color: 'var(--astra-ink)',
                  }}
                >
                  AGNI
                </span>
                <span
                  className="status-ring"
                  style={{ color: 'var(--agni-red)', width: 7, height: 7 }}
                  aria-hidden="true"
                />
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.5rem',
                    color: 'var(--agni-red)',
                    fontWeight: 700,
                    letterSpacing: '0.1em',
                  }}
                >
                  {newSignals} NEW SIGNALS
                </span>
              </div>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.5625rem',
                  letterSpacing: '0.2em',
                  textTransform: 'uppercase',
                  color: 'var(--agni-copper)',
                  fontWeight: 600,
                  marginTop: 2,
                }}
              >
                RESEARCH INTELLIGENCE
              </div>
            </div>
          </div>

          {/* Primary heading */}
          <h1
            style={{
              fontFamily:    'var(--font-display)',
              fontSize:      'clamp(1.6rem, 3.5vw, 2.5rem)',
              fontWeight:    500,
              lineHeight:    1.15,
              color:         'var(--astra-ink)',
              marginBottom:  '0.65rem',
              letterSpacing: '-0.01em',
            }}
          >
            From Signals to<br />
            <em style={{ fontStyle: 'italic', color: 'var(--agni-red)' }}>Strategic Clarity.</em>
          </h1>

          <p
            style={{
              fontFamily:   'var(--font-sans)',
              fontSize:     '0.9375rem',
              color:        'var(--astra-slate)',
              lineHeight:   1.65,
              marginBottom: '1.5rem',
              maxWidth:     '42ch',
            }}
          >
            Geopolitical and financial intelligence through data, context, and foresight —
            grounded in evidence, verified at every step.
          </p>

          {/* Workflow pipeline */}
          <div className="flex items-center gap-1 flex-wrap mb-6">
            {WORKFLOW_STAGES.map((stage, i) => (
              <React.Fragment key={stage.id}>
                <span
                  style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      '0.5rem',
                    fontWeight:    700,
                    letterSpacing: '0.12em',
                    color:
                      i === 0                          ? 'var(--agni-red)'    :
                      i === WORKFLOW_STAGES.length - 1 ? 'var(--agni-copper)' : 'var(--astra-slate)',
                    padding:    '3px 9px',
                    borderRadius: 3,
                    background:
                      i === 0                          ? 'rgba(126,36,29,0.07)'  :
                      i === WORKFLOW_STAGES.length - 1 ? 'rgba(182,106,60,0.09)' : 'rgba(102,112,122,0.06)',
                    border: `1px solid ${
                      i === 0                          ? 'rgba(126,36,29,0.16)'  :
                      i === WORKFLOW_STAGES.length - 1 ? 'rgba(182,106,60,0.18)' : 'rgba(102,112,122,0.10)'}`,
                  }}
                >
                  {stage.label}
                </span>
                {i < WORKFLOW_STAGES.length - 1 && (
                  <ArrowRight className="w-2.5 h-2.5 flex-shrink-0" style={{ color: 'var(--astra-sandstone-dark)', opacity: 0.8 }} />
                )}
              </React.Fragment>
            ))}
          </div>

          {/* KPI strip */}
          <div
            className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-5 border-t"
            style={{ borderColor: 'var(--astra-sandstone-dark)' }}
          >
            {KPI_METRICS.map((kpi) => (
              <div key={kpi.label}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--astra-slate)', marginBottom: 3 }}>
                  {kpi.label}
                </div>
                <div className="flex items-baseline gap-2">
                  <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.625rem', fontWeight: 500, color: 'var(--astra-ink)', lineHeight: 1 }}>
                    {kpi.value}
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5625rem', fontWeight: 700, color: kpi.positive ? 'var(--status-positive)' : 'var(--agni-red)' }}>
                    {kpi.delta}
                  </span>
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.06em', marginTop: 2 }}>
                  24H
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Right: Mini Signal Field ────────────────────── */}
        <div
          className="hidden lg:block relative"
          style={{
            width: 280,
            flexShrink: 0,
            borderLeft: '1px solid var(--astra-sandstone-dark)',
            background: 'linear-gradient(135deg, var(--astra-ivory) 0%, var(--astra-sandstone) 100%)',
            overflow: 'hidden',
          }}
        >
          {/* Panel label */}
          <div
            className="px-4 pt-4 pb-2 flex items-center gap-2"
            style={{ borderBottom: '1px solid var(--astra-sandstone-dark)' }}
          >
            <span className="agni-bindu live" aria-hidden="true" />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
              Live Signal Field
            </span>
          </div>

          {/* SVG mini map */}
          <div className="relative" style={{ flex: 1, padding: '8px 12px 12px' }}>
            <svg
              viewBox="0 0 100 72"
              width="100%"
              height="100%"
              style={{ display: 'block', maxHeight: 220 }}
              aria-label="Mini live signal field"
              role="img"
            >
              {/* Grid */}
              {[25, 50, 75].map(x => (
                <line key={x} x1={x} y1="0" x2={x} y2="72" stroke="var(--astra-sandstone-dark)" strokeWidth="0.3" opacity="0.6" />
              ))}
              {[24, 48].map(y => (
                <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="var(--astra-sandstone-dark)" strokeWidth="0.3" opacity="0.6" />
              ))}

              {/* Sutra connections */}
              {HERO_CONNECTIONS.map(([a, b], i) => {
                const na = HERO_NODES[a];
                const nb = HERO_NODES[b];
                return (
                  <line
                    key={i}
                    x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
                    stroke="var(--agni-copper)" strokeWidth="0.5" opacity="0.3" strokeDasharray="2 3"
                  />
                );
              })}

              {/* Heat blobs */}
              {HERO_NODES.filter(n => n.count > 8).map((n, i) => (
                <ellipse key={i} cx={n.x} cy={n.y} rx={n.r * 4} ry={n.r * 3}
                  fill={n.color} opacity="0.07" />
              ))}

              {/* Signal nodes */}
              {HERO_NODES.map((node, i) => (
                <g key={i}>
                  <circle cx={node.x} cy={node.y} r={node.r + 2.5} fill={node.color} opacity="0.08" />
                  <circle cx={node.x} cy={node.y} r={node.r} fill={node.color} stroke="var(--astra-ivory)" strokeWidth="0.8" opacity="0.9" />
                  {node.count > 6 && (
                    <text x={node.x} y={node.y + 0.4} textAnchor="middle" dominantBaseline="middle"
                      style={{ fontFamily: 'var(--font-mono)', fontSize: '2.2px', fill: 'var(--astra-ivory)', fontWeight: 700 }}>
                      {node.count}
                    </text>
                  )}
                  {node.label && (
                    <text x={node.x} y={node.y + node.r + 3.5} textAnchor="middle"
                      style={{ fontFamily: 'var(--font-mono)', fontSize: '3px', fill: node.color, fontWeight: 600, letterSpacing: '0.02em' }}
                      opacity="0.85">
                      {node.label}
                    </text>
                  )}
                </g>
              ))}

              {/* Central Bindu */}
              <circle cx="50" cy="36" r="2.5" fill="none" stroke="var(--agni-copper)" strokeWidth="0.5" opacity="0.3" />
              <circle cx="50" cy="36" r="1"   fill="var(--agni-copper)" opacity="0.4" />
            </svg>

            {/* Region risk summary */}
            <div className="mt-2 space-y-1.5">
              {HERO_NODES.filter(n => n.count > 4).slice(0, 4).map((node, i) => (
                <div key={i} className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <div style={{ width: 5, height: 5, borderRadius: '50%', background: node.color, flexShrink: 0 }} />
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)' }}>{node.label}</span>
                  </div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', fontWeight: 700, color: node.color }}>{node.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
