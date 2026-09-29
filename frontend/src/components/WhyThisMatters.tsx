import React from 'react';
import { ArrowDown, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { AstraMark } from './AstraMark';

/* ──────────────────────────────────────────────────────────────────
   WhyThisMatters — Signal → Evidence → Analysis → Implication chain.
   The primary analytical interpretation component in AGNI.
   ────────────────────────────────────────────────────────────────── */

export interface ImplicationIndicator {
  label:     string;
  direction: 'up' | 'down' | 'stable';
  delta?:    string;
}

export interface SignalChain {
  id:          string;
  signal:      string;
  evidence:    string;
  evidenceCount: number;
  analysis:    string;
  implication: string;
  scenario:    string;
  confidence:  'high' | 'medium' | 'low';
  indicators:  ImplicationIndicator[];
  timestamp:   string;
  sources:     string[];
}

// Demo fallback data — clearly marked
const DEMO_CHAIN: SignalChain = {
  id:            'chain-001',
  signal:        'Regional shipping disruption detected across Red Sea corridor',
  evidence:      '9 corroborating signals from 5 independent sources',
  evidenceCount: 9,
  analysis:      'Freight diversion adding 14–18 days to European supply routes. Insurance premiums elevated 340%. Energy cargo delays compounding upstream pressure.',
  implication:   'Energy volatility and supply chain disruption risk elevated across Europe and South Asia. Secondary inflation effects possible within 6–8 weeks.',
  scenario:      'Regional Supply Route Disruption — Sustained',
  confidence:    'high',
  indicators: [
    { label: 'Energy',      direction: 'up',   delta: '+8.4%'  },
    { label: 'Freight',     direction: 'up',   delta: '+34%'   },
    { label: 'Risk',        direction: 'up',   delta: '+22pts' },
    { label: 'Trade Flow',  direction: 'down', delta: '−18%'   },
    { label: 'USD/INR',     direction: 'up',   delta: '+0.6%'  },
  ],
  timestamp: '03:42 IST, 29 Sep 2026',
  sources:   ['Reuters', 'IMF Trade Monitor', 'Freightos Baltic Index', 'Lloyd\'s Intelligence', 'UNCTAD'],
};

const STEP_LABELS = ['SIGNAL', 'EVIDENCE', 'ANALYSIS', 'IMPLICATION', 'SCENARIO', 'CONFIDENCE'];

interface WhyThisMattersProps {
  chain?:     SignalChain;
  className?: string;
}

export const WhyThisMatters: React.FC<WhyThisMattersProps> = ({
  chain     = DEMO_CHAIN,
  className = '',
}) => {
  const confColor =
    chain.confidence === 'high'   ? 'var(--status-positive)'  :
    chain.confidence === 'medium' ? 'var(--status-warning)'   : 'var(--status-critical)';

  const IndicatorArrow = ({ dir }: { dir: ImplicationIndicator['direction'] }) =>
    dir === 'up'   ? <TrendingUp   className="w-3 h-3" style={{ color: 'var(--agni-red)' }} /> :
    dir === 'down' ? <TrendingDown className="w-3 h-3" style={{ color: 'var(--status-positive)' }} /> :
                     <Minus        className="w-3 h-3" style={{ color: 'var(--astra-slate)' }} />;

  return (
    <div
      className={`astra-card ${className}`}
      style={{ padding: 0, overflow: 'hidden' }}
    >
      {/* Header */}
      <div
        className="px-5 py-3 flex items-center justify-between"
        style={{ borderBottom: '1px solid var(--astra-sandstone-dark)', background: 'var(--astra-sandstone)' }}
      >
        <div className="flex items-center gap-2.5">
          <AstraMark size={16} style={{ color: 'var(--agni-copper)' }} />
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.9375rem', fontWeight: 600, color: 'var(--astra-ink)' }}>
            Why This Matters
          </span>
          <span className="intel-tag" style={{ fontSize: '0.4375rem' }}>AGNI / ANAL-03</span>
        </div>
        <span
          className="confidence-badge"
          style={{
            background: chain.confidence === 'high' ? 'rgba(45,106,79,0.08)' : 'rgba(194,132,42,0.08)',
            color: confColor,
            border: `1px solid ${confColor}33`,
          }}
        >
          <span style={{ width: 5, height: 5, borderRadius: '50%', background: confColor, display: 'inline-block' }} />
          {chain.confidence.toUpperCase()} CONFIDENCE
        </span>
      </div>

      <div className="flex flex-col lg:flex-row gap-0">
        {/* Left: Signal chain */}
        <div className="flex-1 p-5" style={{ minWidth: 0 }}>
          {/* Copper section rule */}
          <div className="flex items-center gap-2 mb-4">
            <div style={{ height: 1, flex: 1, background: 'linear-gradient(90deg, var(--agni-copper) 0%, transparent 100%)', opacity: 0.4 }} />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--agni-copper)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>Signal → Insight</span>
          </div>

          {/* Chain steps */}
          <div className="relative">
            {/* Sutra vertical line */}
            <div
              style={{
                position: 'absolute', left: 9, top: 14, bottom: 14, width: 1,
                background: 'linear-gradient(to bottom, var(--agni-copper) 0%, transparent 100%)',
                opacity: 0.25,
              }}
              aria-hidden="true"
            />

            {/* SIGNAL */}
            <ChainStep
              step="SIGNAL"
              content={chain.signal}
              accent="var(--agni-red)"
              isFirst
            />

            {/* EVIDENCE */}
            <ChainStep
              step="EVIDENCE"
              content={chain.evidence}
              accent="var(--agni-copper)"
              badge={`${chain.evidenceCount} signals`}
            />

            {/* ANALYSIS */}
            <ChainStep
              step="ANALYSIS"
              content={chain.analysis}
              accent="var(--astra-indigo)"
            />

            {/* IMPLICATION */}
            <ChainStep
              step="IMPLICATION"
              content={chain.implication}
              accent="var(--agni-red)"
            />

            {/* SCENARIO */}
            <ChainStep
              step="SCENARIO"
              content={chain.scenario}
              accent="var(--agni-terracotta)"
            />

            {/* CONFIDENCE */}
            <ChainStep
              step="CONFIDENCE"
              content={chain.confidence.toUpperCase()}
              accent={confColor}
              isLast
            />
          </div>

          {/* Source provenance */}
          <div
            className="mt-4 p-3 rounded-lg"
            style={{ background: 'var(--astra-sandstone)', border: '1px solid var(--astra-sandstone-dark)' }}
          >
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6 }}>
              Source Provenance
            </div>
            <div className="flex flex-wrap gap-1.5">
              {chain.sources.map((src, i) => (
                <span
                  key={i}
                  style={{
                    fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--astra-slate)',
                    background: 'var(--astra-ivory)', border: '1px solid var(--astra-sandstone-dark)',
                    padding: '2px 7px', borderRadius: 4,
                  }}
                >
                  {src}
                </span>
              ))}
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', marginTop: 6 }}>
              Updated {chain.timestamp} · DEMO SYNTHETIC DATA
            </div>
          </div>
        </div>

        {/* Right: Why it matters — indicator grid */}
        <div
          className="lg:w-52 p-5 border-t lg:border-t-0 lg:border-l"
          style={{ borderColor: 'var(--astra-sandstone-dark)', background: 'var(--astra-sandstone)' }}
        >
          <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', fontWeight: 600, color: 'var(--astra-ink)', marginBottom: 12 }}>
            Systemic Impact
          </div>

          <div className="space-y-2.5">
            {chain.indicators.map((ind, i) => (
              <div key={i} className="flex items-center justify-between gap-2">
                <span style={{ fontFamily: 'var(--font-sans)', fontSize: '0.75rem', color: 'var(--astra-slate)', flex: 1 }}>
                  {ind.label}
                </span>
                <div className="flex items-center gap-1.5">
                  {ind.delta && (
                    <span style={{
                      fontFamily: 'var(--font-mono)', fontSize: '0.625rem', fontWeight: 700,
                      color: ind.direction === 'up' ? 'var(--agni-red)' : ind.direction === 'down' ? 'var(--status-positive)' : 'var(--astra-slate)',
                    }}>
                      {ind.delta}
                    </span>
                  )}
                  <IndicatorArrow dir={ind.direction} />
                </div>
              </div>
            ))}
          </div>

          {/* Evidence count callout */}
          <div
            className="mt-5 p-3 rounded-lg text-center"
            style={{ background: 'rgba(182,106,60,0.08)', border: '1px solid rgba(182,106,60,0.2)' }}
          >
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600, color: 'var(--agni-red)', lineHeight: 1 }}>
              {chain.evidenceCount}
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)', letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: 4 }}>
              Corroborating Signals
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* Sub-component — individual chain step */
const ChainStep: React.FC<{
  step:    string;
  content: string;
  accent:  string;
  badge?:  string;
  isFirst?: boolean;
  isLast?:  boolean;
}> = ({ step, content, accent, badge, isFirst, isLast }) => (
  <div className="flex items-start gap-3 mb-4 relative" style={{ paddingLeft: 24 }}>
    {/* Step node (Bindu on the Sutra line) */}
    <div
      style={{
        position: 'absolute', left: 5, top: 4,
        width: 9, height: 9, borderRadius: '50%',
        background: 'var(--astra-ivory)',
        border: `1.5px solid ${accent}`,
        boxShadow: `0 0 0 2px ${accent}1A`,
        flexShrink: 0,
      }}
      aria-hidden="true"
    />
    <div>
      <div className="flex items-center gap-2 mb-0.5">
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: accent }}>
          {step}
        </span>
        {badge && (
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.375rem', color: 'var(--astra-slate)', background: 'var(--astra-sandstone)', border: '1px solid var(--astra-sandstone-dark)', padding: '1px 5px', borderRadius: 3 }}>
            {badge}
          </span>
        )}
      </div>
      <p style={{ fontFamily: isFirst || isLast ? 'var(--font-display)' : 'var(--font-sans)', fontSize: isFirst ? '0.9375rem' : '0.8125rem', fontWeight: isFirst ? 600 : 400, color: 'var(--astra-ink)', lineHeight: 1.45 }}>
        {content}
      </p>
    </div>
  </div>
);
