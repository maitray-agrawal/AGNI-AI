import React from 'react';
import { Radio, ChevronRight, TrendingUp, Zap } from 'lucide-react';

/* ──────────────────────────────────────────────────────────────────
   LiveSignals — Live intelligence activity feed.
   Demo data clearly labelled; replace with real API data when available.
   ────────────────────────────────────────────────────────────────── */

export interface SignalItem {
  id:          string;
  category:    'economic' | 'conflict' | 'political' | 'trade' | 'cyber' | 'environmental' | 'policy';
  title:       string;
  region:      string;
  timestamp:   string;
  sources:     number;
  confidence:  'high' | 'medium' | 'low';
  severity:    'critical' | 'high' | 'elevated' | 'moderate' | 'info';
  isNew?:      boolean;
}

const DEMO_SIGNALS: SignalItem[] = [
  { id: 's1', category: 'economic',     title: 'Energy supply disruption detected',        region: 'Red Sea',         timestamp: '03:42', sources: 3, confidence: 'high',   severity: 'critical', isNew: true  },
  { id: 's2', category: 'conflict',     title: 'Regional ceasefire talks collapse',         region: 'Middle East',     timestamp: '03:31', sources: 5, confidence: 'high',   severity: 'high',     isNew: true  },
  { id: 's3', category: 'trade',        title: 'Container freight rates surging +34%',      region: 'Global',          timestamp: '03:18', sources: 2, confidence: 'high',   severity: 'elevated', isNew: true  },
  { id: 's4', category: 'political',    title: 'Military posturing in disputed waters',     region: 'S. China Sea',    timestamp: '02:55', sources: 4, confidence: 'medium', severity: 'high',     isNew: false },
  { id: 's5', category: 'policy',       title: 'Emergency sanctions package announced',     region: 'Eastern Europe',  timestamp: '02:43', sources: 6, confidence: 'high',   severity: 'high',     isNew: false },
  { id: 's6', category: 'economic',     title: 'Crude oil futures spike +6.2% on open',    region: 'Global Markets',  timestamp: '02:28', sources: 2, confidence: 'high',   severity: 'elevated', isNew: false },
  { id: 's7', category: 'environmental','title': 'Monsoon disruption affecting supply chain', region: 'South Asia',   timestamp: '01:55', sources: 2, confidence: 'medium', severity: 'moderate', isNew: false },
];

const CATEGORY_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  economic:     { color: 'var(--agni-copper)',      bg: 'rgba(182,106,60,0.10)',   label: 'ECONOMIC'     },
  conflict:     { color: 'var(--agni-vermilion)',   bg: 'rgba(192,57,43,0.10)',    label: 'CONFLICT'     },
  political:    { color: 'var(--astra-indigo)',     bg: 'rgba(46,58,94,0.10)',     label: 'POLITICAL'    },
  trade:        { color: 'var(--agni-ochre)',       bg: 'rgba(194,132,42,0.10)',   label: 'TRADE'        },
  cyber:        { color: 'var(--astra-slate)',      bg: 'rgba(102,112,122,0.10)',  label: 'CYBER'        },
  environmental:{ color: 'var(--status-positive)',  bg: 'rgba(45,106,79,0.10)',    label: 'ENV'          },
  policy:       { color: 'var(--astra-indigo)',     bg: 'rgba(46,58,94,0.08)',     label: 'POLICY'       },
};

const SEVERITY_DOT: Record<string, string> = {
  critical: 'var(--agni-vermilion)',
  high:     'var(--agni-red)',
  elevated: 'var(--agni-copper)',
  moderate: 'var(--agni-ochre)',
  info:     'var(--astra-slate)',
};

interface LiveSignalsProps {
  signals?:   SignalItem[];
  onSelect?:  (signal: SignalItem) => void;
  className?: string;
  maxItems?:  number;
}

export const LiveSignals: React.FC<LiveSignalsProps> = ({
  signals   = DEMO_SIGNALS,
  onSelect,
  className = '',
  maxItems  = 6,
}) => {
  const newCount = signals.filter(s => s.isNew).length;

  return (
    <div
      className={`astra-card ${className}`}
      style={{ padding: 0, overflow: 'hidden' }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 flex items-center justify-between"
        style={{ borderBottom: '1px solid var(--astra-sandstone-dark)', background: 'var(--astra-sandstone)' }}
      >
        <div className="flex items-center gap-2.5">
          <Radio className="w-3.5 h-3.5" style={{ color: 'var(--agni-copper)' }} />
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.875rem', fontWeight: 600, color: 'var(--astra-ink)' }}>
            Live Intelligence
          </span>
          <span className="intel-tag" style={{ fontSize: '0.4375rem' }}>AGNI / SIG-07</span>
        </div>
        {newCount > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="status-ring" style={{ color: 'var(--agni-red)', width: 7, height: 7 }} />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', fontWeight: 700, color: 'var(--agni-red)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              {newCount} NEW
            </span>
          </div>
        )}
      </div>

      {/* Signal list */}
      <div className="divide-y" style={{ borderColor: 'var(--astra-sandstone)' }}>
        {signals.slice(0, maxItems).map((sig, i) => {
          const cat = CATEGORY_CONFIG[sig.category] || CATEGORY_CONFIG.policy;
          return (
            <button
              key={sig.id}
              className="w-full px-4 py-2.5 text-left group"
              style={{
                background:  sig.isNew ? 'rgba(182,106,60,0.04)' : 'transparent',
                transition:  'background 0.15s ease',
                animation:   `fadeUp 0.25s ease-out ${i * 0.04}s both`,
                cursor:      onSelect ? 'pointer' : 'default',
              }}
              onMouseOver={e => (e.currentTarget.style.background = 'var(--astra-sandstone)')}
              onMouseOut={e  => (e.currentTarget.style.background = sig.isNew ? 'rgba(182,106,60,0.04)' : 'transparent')}
              onClick={() => onSelect?.(sig)}
            >
              <div className="flex items-start gap-2.5">
                {/* Severity dot */}
                <div
                  className="flex-shrink-0 mt-1"
                  style={{ width: 7, height: 7, borderRadius: '50%', background: SEVERITY_DOT[sig.severity] }}
                  aria-label={`${sig.severity} severity`}
                />

                <div className="flex-1 min-w-0">
                  {/* Category + timestamp */}
                  <div className="flex items-center justify-between gap-2 mb-0.5">
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', fontWeight: 700,
                        color: cat.color, background: cat.bg,
                        padding: '1px 6px', borderRadius: 3, letterSpacing: '0.08em',
                      }}
                    >
                      {cat.label}
                    </span>
                    <div className="flex items-center gap-1.5">
                      {sig.isNew && (
                        <Zap className="w-2.5 h-2.5" style={{ color: 'var(--agni-copper)' }} />
                      )}
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--astra-slate-light)' }}>
                        {sig.timestamp} IST
                      </span>
                    </div>
                  </div>

                  {/* Title */}
                  <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.8125rem', fontWeight: sig.isNew ? 600 : 500, color: 'var(--astra-ink)', lineHeight: 1.35, marginBottom: 2 }}>
                    {sig.title}
                  </p>

                  {/* Region + sources + confidence */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)', letterSpacing: '0.06em' }}>
                      {sig.region}
                    </span>
                    <span style={{ color: 'var(--astra-sandstone-dark)' }}>·</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)' }}>
                      {sig.sources} source{sig.sources !== 1 ? 's' : ''}
                    </span>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)', fontSize: '0.375rem', fontWeight: 700,
                        color:      sig.confidence === 'high' ? 'var(--status-positive)' : sig.confidence === 'medium' ? 'var(--status-warning)' : 'var(--status-critical)',
                        textTransform: 'uppercase', letterSpacing: '0.06em',
                      }}
                    >
                      {sig.confidence} conf.
                    </span>
                  </div>
                </div>

                {onSelect && (
                  <ChevronRight
                    className="w-3 h-3 flex-shrink-0 mt-1 opacity-0 group-hover:opacity-50 transition-opacity"
                    style={{ color: 'var(--astra-slate)' }}
                  />
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Footer */}
      <div
        className="px-4 py-2 flex items-center justify-between"
        style={{ borderTop: '1px solid var(--astra-sandstone)', background: 'var(--astra-sandstone)' }}
      >
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.08em' }}>
          DEMO SIGNAL LAYER · Synthetic data
        </span>
        {onSelect && (
          <button
            style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--agni-copper)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            ALL SIGNALS →
          </button>
        )}
      </div>
    </div>
  );
};
