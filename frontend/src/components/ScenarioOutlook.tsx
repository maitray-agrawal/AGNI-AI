import React from 'react';
import { GitBranch, TrendingUp, TrendingDown, Minus } from 'lucide-react';

/* ──────────────────────────────────────────────────────────────────
   ScenarioOutlook — Analytical scenario panel.
   Shows potential developments based on current signal clusters.
   Demo data clearly labelled.
   ────────────────────────────────────────────────────────────────── */

export interface ScenarioItem {
  id:          string;
  title:       string;
  description: string;
  trend:       'increasing' | 'stable' | 'decreasing';
  signalScore: number; // 0–100 (signal support weight, NOT a probability)
  confidence:  'high' | 'medium' | 'low';
  supportingSignals: number;
  category:    string;
  timeframe:   string;
}

const DEMO_SCENARIOS: ScenarioItem[] = [
  {
    id:    's1',
    title: 'Energy Supply Route Disruption — Sustained',
    description: 'Red Sea corridor continues to divert cargo, compounding European energy costs.',
    trend: 'increasing', signalScore: 82, confidence: 'high', supportingSignals: 9, category: 'Energy / Trade', timeframe: '6–12 weeks',
  },
  {
    id:    's2',
    title: 'Regional Conflict Escalation',
    description: 'Current ceasefire breakdown increases risk of broader regional involvement.',
    trend: 'increasing', signalScore: 74, confidence: 'high', supportingSignals: 14, category: 'Geopolitical', timeframe: '2–6 weeks',
  },
  {
    id:    's3',
    title: 'Freight Cost Normalization',
    description: 'Alternative routes absorb pressure, freight rates stabilize at elevated levels.',
    trend: 'stable', signalScore: 45, confidence: 'medium', supportingSignals: 4, category: 'Trade / Logistics', timeframe: '8–16 weeks',
  },
  {
    id:    's4',
    title: 'Policy Realignment — Sanctions Cascade',
    description: 'Secondary sanctions pressure triggers policy realignment among regional actors.',
    trend: 'increasing', signalScore: 61, confidence: 'medium', supportingSignals: 6, category: 'Policy / Political', timeframe: '4–10 weeks',
  },
];

const BAR_COLOR = (score: number) =>
  score >= 75 ? 'var(--agni-vermilion)' :
  score >= 55 ? 'var(--agni-red)'       :
  score >= 35 ? 'var(--agni-copper)'    :
                'var(--astra-slate)';

interface ScenarioOutlookProps {
  scenarios?: ScenarioItem[];
  className?: string;
}

export const ScenarioOutlook: React.FC<ScenarioOutlookProps> = ({
  scenarios = DEMO_SCENARIOS,
  className = '',
}) => {
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
          <GitBranch className="w-3.5 h-3.5" style={{ color: 'var(--agni-red)' }} />
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.9375rem', fontWeight: 600, color: 'var(--astra-ink)' }}>
            Scenario Outlook
          </span>
          <span className="intel-tag" style={{ fontSize: '0.4375rem' }}>AGNI / SCEN-05</span>
        </div>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.08em' }}>
          SIGNAL SUPPORT WEIGHT · NOT PROBABILITY
        </span>
      </div>

      {/* Scenarios */}
      <div className="divide-y" style={{ borderColor: 'var(--astra-sandstone)' }}>
        {scenarios.map((sc, i) => {
          const TrendIcon =
            sc.trend === 'increasing' ? <TrendingUp   className="w-3 h-3" style={{ color: 'var(--agni-red)' }} /> :
            sc.trend === 'decreasing' ? <TrendingDown className="w-3 h-3" style={{ color: 'var(--status-positive)' }} /> :
                                        <Minus        className="w-3 h-3" style={{ color: 'var(--astra-slate)' }} />;
          const confColor =
            sc.confidence === 'high'   ? 'var(--status-positive)' :
            sc.confidence === 'medium' ? 'var(--status-warning)'  : 'var(--status-critical)';

          return (
            <div
              key={sc.id}
              className="px-5 py-4"
              style={{ animation: `fadeUp 0.25s ease-out ${i * 0.07}s both` }}
            >
              {/* Top row */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)', background: 'var(--astra-sandstone)', border: '1px solid var(--astra-sandstone-dark)', padding: '1px 6px', borderRadius: 3, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                      {sc.category}
                    </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)' }}>
                      {sc.timeframe}
                    </span>
                  </div>
                  <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '0.875rem', fontWeight: 600, color: 'var(--astra-ink)', lineHeight: 1.3, marginBottom: 3 }}>
                    {sc.title}
                  </h4>
                  <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.75rem', color: 'var(--astra-slate)', lineHeight: 1.5 }}>
                    {sc.description}
                  </p>
                </div>
              </div>

              {/* Signal support bar + metadata */}
              <div className="flex items-center gap-3 mt-2.5">
                {/* Bar */}
                <div style={{ flex: 1, height: 4, background: 'var(--astra-sandstone-dark)', borderRadius: 3, overflow: 'hidden', maxWidth: 140 }}>
                  <div
                    style={{
                      width: `${sc.signalScore}%`, height: '100%',
                      background: BAR_COLOR(sc.signalScore),
                      borderRadius: 3,
                      transition: 'width 1s ease',
                    }}
                  />
                </div>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.875rem', fontWeight: 600, color: BAR_COLOR(sc.signalScore), lineHeight: 1 }}>
                  {sc.signalScore}
                </span>

                <div className="flex items-center gap-2 ml-auto">
                  {TrendIcon}
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)' }}>
                    {sc.supportingSignals} sig
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.375rem', fontWeight: 700, color: confColor, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                    {sc.confidence}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer disclaimer */}
      <div
        className="px-5 py-2"
        style={{ borderTop: '1px solid var(--astra-sandstone)', background: 'var(--astra-sandstone)' }}
      >
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.06em' }}>
          SCENARIO SUPPORT WEIGHTS DERIVED FROM SIGNAL CLUSTERING · NOT PROBABILISTIC FORECASTS · DEMO DATA
        </span>
      </div>
    </div>
  );
};
