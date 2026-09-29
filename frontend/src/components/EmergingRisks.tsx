import React from 'react';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, ChevronRight } from 'lucide-react';

/* ──────────────────────────────────────────────────────────────────
   EmergingRisks — Compact analytical risk panel.
   Demo data clearly labelled; replace with real API data when available.
   ────────────────────────────────────────────────────────────────── */

export interface RiskItem {
  id:          string;
  region:      string;
  title:       string;
  score:       number;   // 0–100
  trend:       'increasing' | 'stable' | 'decreasing';
  signals:     number;
  confidence:  'high' | 'medium' | 'low';
  category:    'conflict' | 'economic' | 'political' | 'cyber' | 'environmental';
}

// Demo fallback dataset — clearly marked
const DEMO_RISKS: RiskItem[] = [
  { id: 'r1', region: 'Middle East',     title: 'Regional Conflict Escalation',    score: 87, trend: 'increasing',  signals: 14, confidence: 'high',   category: 'conflict'    },
  { id: 'r2', region: 'Red Sea',         title: 'Shipping Route Disruption',       score: 79, trend: 'increasing',  signals: 9,  confidence: 'high',   category: 'economic'    },
  { id: 'r3', region: 'Eastern Europe',  title: 'Geopolitical Pressure',           score: 74, trend: 'stable',      signals: 8,  confidence: 'high',   category: 'conflict'    },
  { id: 'r4', region: 'South China Sea', title: 'Maritime Tension',                score: 68, trend: 'increasing',  signals: 7,  confidence: 'medium', category: 'political'   },
  { id: 'r5', region: 'West Africa',     title: 'Supply Chain Disruption',         score: 52, trend: 'stable',      signals: 4,  confidence: 'medium', category: 'economic'    },
  { id: 'r6', region: 'Indo-Pacific',    title: 'Trade Route Contestation',        score: 48, trend: 'increasing',  signals: 5,  confidence: 'medium', category: 'political'   },
];

const SCORE_COLOR = (score: number) =>
  score >= 75 ? 'var(--agni-vermilion)'  :
  score >= 55 ? 'var(--agni-red)'        :
  score >= 35 ? 'var(--agni-copper)'     :
                'var(--astra-slate)';

const SCORE_BG = (score: number) =>
  score >= 75 ? 'rgba(192,57,43,0.12)'  :
  score >= 55 ? 'rgba(126,36,29,0.09)'  :
  score >= 35 ? 'rgba(182,106,60,0.09)' :
                'rgba(102,112,122,0.07)';

const CATEGORY_COLORS: Record<string, string> = {
  conflict:    'var(--agni-vermilion)',
  economic:    'var(--agni-copper)',
  political:   'var(--astra-indigo)',
  cyber:       'var(--astra-slate)',
  environmental: 'var(--status-positive)',
};

interface EmergingRisksProps {
  risks?:     RiskItem[];
  onSelect?:  (risk: RiskItem) => void;
  className?: string;
}

export const EmergingRisks: React.FC<EmergingRisksProps> = ({
  risks = DEMO_RISKS,
  onSelect,
  className = '',
}) => {
  const TrendIcon = ({ trend }: { trend: RiskItem['trend'] }) => {
    if (trend === 'increasing')  return <TrendingUp   className="w-3 h-3" style={{ color: 'var(--agni-red)'        }} />;
    if (trend === 'decreasing')  return <TrendingDown className="w-3 h-3" style={{ color: 'var(--status-positive)' }} />;
    return                              <Minus        className="w-3 h-3" style={{ color: 'var(--astra-slate)'     }} />;
  };

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
          <AlertTriangle className="w-3.5 h-3.5" style={{ color: 'var(--agni-red)' }} />
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.875rem', fontWeight: 600, color: 'var(--astra-ink)' }}>
            Emerging Risks
          </span>
          <span className="intel-tag" style={{ fontSize: '0.4375rem' }}>AGNI / RISK-04</span>
        </div>
        <div
          style={{
            fontFamily: 'var(--font-display)', fontSize: '1.125rem', fontWeight: 600,
            color: 'var(--agni-red)', lineHeight: 1,
          }}
        >
          {risks.filter(r => r.score >= 55).length}
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)', fontWeight: 400, marginLeft: 4 }}>HIGH</span>
        </div>
      </div>

      {/* Risk items */}
      <div className="divide-y" style={{ borderColor: 'var(--astra-sandstone)' }}>
        {risks.map((risk, i) => (
          <button
            key={risk.id}
            className="w-full px-4 py-3 text-left flex items-center gap-3 group"
            style={{
              background:  'transparent',
              transition:  'background 0.15s ease',
              animation:   `fadeUp 0.25s ease-out ${i * 0.05}s both`,
              cursor:      onSelect ? 'pointer' : 'default',
            }}
            onMouseOver={e => (e.currentTarget.style.background = 'var(--astra-sandstone)')}
            onMouseOut={e  => (e.currentTarget.style.background = 'transparent')}
            onClick={() => onSelect?.(risk)}
          >
            {/* Score pill */}
            <div
              className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ background: SCORE_BG(risk.score), border: `1px solid ${SCORE_COLOR(risk.score)}22` }}
            >
              <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.875rem', fontWeight: 700, color: SCORE_COLOR(risk.score) }}>
                {risk.score}
              </span>
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 mb-0.5">
                <div style={{ width: 5, height: 5, borderRadius: '50%', background: CATEGORY_COLORS[risk.category], flexShrink: 0 }} />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--astra-slate)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                  {risk.region}
                </span>
              </div>
              <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--astra-ink)', marginBottom: 2, lineHeight: 1.3 }}>
                {risk.title}
              </p>
              {/* Score bar */}
              <div className="flex items-center gap-2">
                <div style={{ flex: 1, height: 3, background: 'var(--astra-sandstone-dark)', borderRadius: 2, overflow: 'hidden', maxWidth: 80 }}>
                  <div style={{ width: `${risk.score}%`, height: '100%', background: SCORE_COLOR(risk.score), borderRadius: 2, transition: 'width 0.8s ease' }} />
                </div>
                <div className="flex items-center gap-1">
                  <TrendIcon trend={risk.trend} />
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)' }}>
                    {risk.signals} sig
                  </span>
                  <span
                    className="confidence-badge"
                    style={{
                      padding: '1px 5px',
                      fontSize: '0.375rem',
                      background: risk.confidence === 'high' ? 'rgba(45,106,79,0.08)' : risk.confidence === 'medium' ? 'rgba(194,132,42,0.08)' : 'rgba(192,57,43,0.08)',
                      color:      risk.confidence === 'high' ? 'var(--status-positive)' : risk.confidence === 'medium' ? 'var(--status-warning)' : 'var(--status-critical)',
                      border:     `1px solid ${risk.confidence === 'high' ? 'rgba(45,106,79,0.2)' : risk.confidence === 'medium' ? 'rgba(194,132,42,0.2)' : 'rgba(192,57,43,0.2)'}`,
                    }}
                  >
                    {risk.confidence.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            {onSelect && (
              <ChevronRight
                className="w-3.5 h-3.5 flex-shrink-0 opacity-0 group-hover:opacity-60 transition-opacity"
                style={{ color: 'var(--astra-slate)' }}
              />
            )}
          </button>
        ))}
      </div>

      {/* Footer */}
      <div
        className="px-4 py-2"
        style={{ borderTop: '1px solid var(--astra-sandstone)', background: 'var(--astra-sandstone)' }}
      >
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.08em' }}>
          DEMO SIGNAL LAYER · Synthetic data for demonstration
        </span>
      </div>
    </div>
  );
};
