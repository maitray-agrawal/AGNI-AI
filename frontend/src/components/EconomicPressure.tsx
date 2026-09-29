import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

/* ──────────────────────────────────────────────────────────────────
   EconomicPressure — Inline sparkline charts for key indicators.
   Uses SVG sparklines — no external chart library required.
   Demo data clearly labelled.
   ────────────────────────────────────────────────────────────────── */

interface Indicator {
  id:       string;
  label:    string;
  value:    string;
  unit:     string;
  change:   string;
  positive: boolean;
  data:     number[]; // sparkline values
  color:    string;
}

const DEMO_INDICATORS: Indicator[] = [
  {
    id: 'crude',    label: 'Crude Oil (Brent)',  value: '91.4',   unit: 'USD/bbl',
    change: '+6.2%', positive: false,
    data: [72, 74, 71, 76, 78, 75, 80, 82, 85, 88, 86, 91],
    color: 'var(--agni-red)',
  },
  {
    id: 'freight',  label: 'Baltic Freight Idx', value: '2,840',  unit: 'BDI',
    change: '+34%',  positive: false,
    data: [1800, 1900, 1750, 2100, 2200, 2050, 2300, 2500, 2600, 2800, 2750, 2840],
    color: 'var(--agni-red)',
  },
  {
    id: 'gold',     label: 'Gold',               value: '2,618',  unit: 'USD/oz',
    change: '+2.4%', positive: true,
    data: [2480, 2500, 2490, 2520, 2540, 2560, 2580, 2590, 2600, 2605, 2610, 2618],
    color: 'var(--agni-copper)',
  },
  {
    id: 'inr',      label: 'USD / INR',           value: '84.21',  unit: '',
    change: '+0.6%', positive: false,
    data: [83.5, 83.6, 83.7, 83.8, 83.85, 83.9, 84.0, 84.05, 84.1, 84.15, 84.18, 84.21],
    color: 'var(--agni-terracotta)',
  },
  {
    id: 'trade',    label: 'Trade Flow Index',    value: '−18%',   unit: 'YTD',
    change: '−18%',  positive: false,
    data: [100, 98, 97, 95, 92, 90, 88, 86, 84, 82, 83, 82],
    color: 'var(--astra-indigo)',
  },
  {
    id: 'supply',   label: 'Supply Chain Stress', value: '78',     unit: '/100',
    change: '+12',   positive: false,
    data: [55, 57, 58, 62, 63, 65, 68, 70, 72, 74, 76, 78],
    color: 'var(--agni-ochre)',
  },
];

/* Tiny SVG sparkline */
const Sparkline: React.FC<{ data: number[]; color: string; height?: number; width?: number }> = ({
  data, color, height = 32, width = 80,
}) => {
  if (!data.length) return null;
  const min  = Math.min(...data);
  const max  = Math.max(...data);
  const range = max - min || 1;
  const pts   = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x},${y}`;
  }).join(' ');

  const lastX = width;
  const lastY = height - ((data[data.length - 1] - min) / range) * (height - 4) - 2;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      <polyline
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinejoin="round"
        strokeLinecap="round"
        opacity="0.8"
      />
      {/* End dot */}
      <circle cx={lastX} cy={lastY} r="2.5" fill={color} opacity="0.9" />
    </svg>
  );
};

interface EconomicPressureProps {
  indicators?: Indicator[];
  className?:  string;
}

export const EconomicPressure: React.FC<EconomicPressureProps> = ({
  indicators = DEMO_INDICATORS,
  className  = '',
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
          <TrendingUp className="w-3.5 h-3.5" style={{ color: 'var(--agni-copper)' }} />
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '0.9375rem', fontWeight: 600, color: 'var(--astra-ink)' }}>
            Economic Pressure
          </span>
          <span className="intel-tag" style={{ fontSize: '0.4375rem' }}>AGNI / ECON-02</span>
        </div>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          DEMO DATA
        </span>
      </div>

      {/* Indicators grid */}
      <div
        className="grid grid-cols-2 md:grid-cols-3 gap-px"
        style={{ background: 'var(--astra-sandstone-dark)' }}
      >
        {indicators.map((ind) => (
          <div
            key={ind.id}
            className="p-4 flex flex-col justify-between"
            style={{ background: 'var(--astra-ivory)', minHeight: 96 }}
          >
            {/* Top row */}
            <div className="flex items-start justify-between gap-2">
              <div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 4 }}>
                  {ind.label}
                </div>
                <div className="flex items-baseline gap-1.5">
                  <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.125rem', fontWeight: 600, color: 'var(--astra-ink)', lineHeight: 1 }}>
                    {ind.value}
                  </span>
                  {ind.unit && (
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)' }}>{ind.unit}</span>
                  )}
                </div>
              </div>
              <Sparkline data={ind.data} color={ind.color} />
            </div>

            {/* Change indicator */}
            <div className="flex items-center gap-1 mt-2">
              {ind.positive
                ? <TrendingDown className="w-3 h-3" style={{ color: 'var(--status-positive)' }} />
                : <TrendingUp   className="w-3 h-3" style={{ color: 'var(--agni-red)' }} />
              }
              <span style={{
                fontFamily: 'var(--font-mono)', fontSize: '0.5rem', fontWeight: 700,
                color: ind.positive ? 'var(--status-positive)' : 'var(--agni-red)',
              }}>
                {ind.change}
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate)' }}>30D</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
