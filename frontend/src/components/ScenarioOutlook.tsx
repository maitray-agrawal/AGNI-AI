import React, { useState, useEffect } from 'react';
import { GitBranch, TrendingUp, TrendingDown, Minus, Play, RefreshCw, Activity, ShieldAlert } from 'lucide-react';
import { fetchScenarios, runScenario } from '../api/client';

/* ──────────────────────────────────────────────────────────────────
   ScenarioOutlook — Analytical scenario panel.
   Shows potential developments based on current signal clusters.
   Conditional Stress-Scenario Engine with live VaR / ES simulation.
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
  var95?:      number;
  es95?:       number;
}

const DEMO_SCENARIOS: ScenarioItem[] = [
  {
    id:    'scen-redsea-protracted-01',
    title: 'Energy Supply Route Disruption — Sustained Red Sea Closure',
    description: 'Bab el-Mandeb corridor continues to divert cargo around Cape of Good Hope, compounding European energy costs.',
    trend: 'increasing', signalScore: 82, confidence: 'high', supportingSignals: 9, category: 'Energy / Trade', timeframe: '6–12 weeks',
    var95: -4.8, es95: -6.96,
  },
  {
    id:    'scen-taiwan-blockade-01',
    title: 'Taiwan Strait Maritime Quarantine & Semiconductor Interdiction',
    description: 'Advanced silicon foundry export scrutiny and naval exercises suppress global semiconductor supply elasticity.',
    trend: 'increasing', signalScore: 74, confidence: 'high', supportingSignals: 14, category: 'Geopolitical', timeframe: '2–6 weeks',
    var95: -6.8, es95: -9.86,
  },
  {
    id:    'scen-hormuz-closure-01',
    title: 'Strait of Hormuz Full Corridor Hydrocarbon Blockade',
    description: 'Mine-laying and asymmetric naval interdiction suppressing 21M bpd transit through Persian Gulf gates.',
    trend: 'increasing', signalScore: 88, confidence: 'high', supportingSignals: 12, category: 'Energy / Chokepoint', timeframe: '1–4 weeks',
    var95: -8.4, es95: -12.18,
  },
  {
    id:    'scen-base-deescalation-01',
    title: 'Baseline Diplomatic De-escalation & Route Normalization',
    description: 'Multilateral naval escorts and diplomatic negotiations stabilize transit frequency and lower spot war-risk insurance.',
    trend: 'stable', signalScore: 45, confidence: 'medium', supportingSignals: 4, category: 'Trade / Logistics', timeframe: '8–16 weeks',
    var95: -1.2, es95: -1.74,
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
  scenarios: initialScenarios = DEMO_SCENARIOS,
  className = '',
}) => {
  const [scenarioList, setScenarioList] = useState<ScenarioItem[]>(initialScenarios);
  const [activeResults, setActiveResults] = useState<Record<string, any>>({});
  const [runningId, setRunningId] = useState<string | null>(null);

  useEffect(() => {
    fetchScenarios()
      .then((backendScens: any[]) => {
        if (backendScens && backendScens.length > 0) {
          const mapped: ScenarioItem[] = backendScens.map(s => ({
            id: s.scenario_id,
            title: s.name,
            description: s.description,
            trend: s.scenario_type === 'SEVERE' || s.scenario_type === 'ADVERSE' ? 'increasing' : 'stable',
            signalScore: Math.round(Math.abs(s.var_95_portfolio_impact || 5.0) * 10),
            confidence: 'high',
            supportingSignals: s.shocks?.length || 4,
            category: s.affected_regions?.[0] ? `${s.affected_regions[0]} / Risk` : 'Geopolitical Stress',
            timeframe: `${s.horizon_days || 30} days`,
            var95: s.var_95_portfolio_impact,
            es95: s.expected_shortfall_95,
          }));
          setScenarioList(mapped);
        }
      })
      .catch((err) => console.warn('Live scenarios fetch fallback:', err));
  }, []);

  const handleRunStressSimulation = async (scId: string) => {
    setRunningId(scId);
    try {
      const res = await runScenario(scId);
      setActiveResults(prev => ({ ...prev, [scId]: res }));
    } catch (err) {
      console.warn('Stress test run failed, using client estimate:', err);
    } finally {
      setRunningId(null);
    }
  };
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
        {scenarioList.map((sc, i) => {
          const TrendIcon =
            sc.trend === 'increasing' ? <TrendingUp   className="w-3 h-3" style={{ color: 'var(--agni-red)' }} /> :
            sc.trend === 'decreasing' ? <TrendingDown className="w-3 h-3" style={{ color: 'var(--status-positive)' }} /> :
                                        <Minus        className="w-3 h-3" style={{ color: 'var(--astra-slate)' }} />;
          const confColor =
            sc.confidence === 'high'   ? 'var(--status-positive)' :
            sc.confidence === 'medium' ? 'var(--status-warning)'  : 'var(--status-critical)';

          const result = activeResults[sc.id];
          const isRunning = runningId === sc.id;

          return (
            <div
              key={sc.id}
              className="px-5 py-4 transition-colors hover:bg-black/[0.01]"
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
                    {sc.var95 !== undefined && (
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--agni-vermilion)', background: 'rgba(220, 38, 38, 0.08)', border: '1px solid rgba(220, 38, 38, 0.2)', padding: '1px 6px', borderRadius: 3 }}>
                        VaR₉₅: {sc.var95}%
                      </span>
                    )}
                  </div>
                  <h4 style={{ fontFamily: 'var(--font-display)', fontSize: '0.875rem', fontWeight: 600, color: 'var(--astra-ink)', lineHeight: 1.3, marginBottom: 3 }}>
                    {sc.title}
                  </h4>
                  <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.75rem', color: 'var(--astra-slate)', lineHeight: 1.5 }}>
                    {sc.description}
                  </p>
                </div>

                <button
                  onClick={() => handleRunStressSimulation(sc.id)}
                  disabled={isRunning}
                  className="flex-shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-mono border transition-all"
                  style={{
                    borderColor: 'var(--astra-sandstone-dark)',
                    background: isRunning ? 'var(--astra-sandstone)' : 'var(--astra-sandstone)/50',
                    color: 'var(--astra-ink)',
                  }}
                  title="Run conditional stress simulation"
                >
                  {isRunning ? (
                    <>
                      <RefreshCw className="w-3 h-3 animate-spin text-agni-copper" />
                      <span>Simulating…</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3 h-3 fill-current text-agni-red" />
                      <span>Simulate Shock</span>
                    </>
                  )}
                </button>
              </div>

              {/* Stress Simulation Results (if run) */}
              {result && (
                <div
                  className="my-2.5 p-2.5 rounded border text-[11px] font-mono space-y-1.5"
                  style={{
                    background: 'var(--astra-sandstone)',
                    borderColor: 'var(--astra-sandstone-dark)',
                  }}
                >
                  <div className="flex items-center justify-between text-[10px] text-astra-slate uppercase">
                    <span className="flex items-center gap-1 font-semibold text-agni-copper">
                      <Activity className="w-3 h-3" />
                      <span>Simulated Stress Regime: {result.current_regime}</span>
                    </span>
                    <span className="text-agni-vermilion font-bold">
                      VaR₉₅: {result.var_95_portfolio_impact}% · ES₉₅: {result.expected_shortfall_95}%
                    </span>
                  </div>
                  {result.asset_shock_distribution?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {result.asset_shock_distribution.map((sh: any, sIdx: number) => (
                        <span
                          key={sIdx}
                          className="px-2 py-0.5 rounded text-[10px] border"
                          style={{
                            background: 'var(--astra-sandstone-dark)',
                            borderColor: 'rgba(0,0,0,0.1)',
                            color: sh.shock_pct < 0 ? 'var(--agni-vermilion)' : 'var(--status-positive)',
                          }}
                        >
                          {sh.target}: {sh.shock_pct > 0 ? `+${sh.shock_pct}%` : `${sh.shock_pct}%`}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

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
