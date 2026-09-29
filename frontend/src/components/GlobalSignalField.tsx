import React, { useState, useMemo, useRef, useEffect } from 'react';
import { geoEqualEarth, geoPath, geoGraticule } from 'd3-geo';
import { feature, mesh } from 'topojson-client';
import { X, Globe2, Radio, Compass, ShieldAlert, ArrowUpRight } from 'lucide-react';
import worldData from '../data/world-110m.json';
import { useAstraTheme } from '../brand/AstraThemeContext';

/* ──────────────────────────────────────────────────────────────────
   GlobalSignalField — AGNI Geopolitical & Maritime Intelligence Map
   Cartographic Foundation: Natural Earth + D3 Equal Earth Projection
   Equal-area pseudocylindrical projection designed for institutional
   world cartography, preserving true comparative geographic scale.
   ────────────────────────────────────────────────────────────────── */

export interface GeopoliticalSignal {
  id: string;
  name: string;
  region: string;
  country: string;
  longitude: number; // Real longitude coordinate (-180 to 180)
  latitude: number;  // Real latitude coordinate (-90 to 90)
  severity: 'critical' | 'high' | 'elevated' | 'moderate' | 'info';
  signalCount: number;
  category: 'Maritime Chokepoint' | 'Supply Chain' | 'Energy Flow' | 'Security Corridor' | 'Sanctions Cascade';
  timestamp: string;
  headline: string;
  intelligenceBrief: string;
  strategicImpact: string;
}

export const REAL_SIGNALS: GeopoliticalSignal[] = [
  {
    id: 'taiwan-strait',
    name: 'Taiwan Strait / East Asia Chokepoint',
    region: 'East Asia',
    country: 'Taiwan / China',
    longitude: 119.5,
    latitude: 24.0,
    severity: 'critical',
    signalCount: 18,
    category: 'Maritime Chokepoint',
    timestamp: '12m ago',
    headline: 'High-density naval patrols & semiconductor export scrutiny',
    intelligenceBrief: 'Elevated naval escorts around southwest maritime corridors. 48% of global container capacity traverses this corridor.',
    strategicImpact: 'Critical risk to advanced semiconductor fabrication schedules and trans-Pacific freight schedules.',
  },
  {
    id: 'red-sea-mandeb',
    name: 'Bab el-Mandeb / Southern Red Sea',
    region: 'Middle East & Horn of Africa',
    country: 'Yemen / Djibouti',
    longitude: 43.3,
    latitude: 12.6,
    severity: 'critical',
    signalCount: 16,
    category: 'Maritime Chokepoint',
    timestamp: '24m ago',
    headline: 'Commercial vessel rerouting around Cape of Good Hope',
    intelligenceBrief: 'Continued anti-ship missile telemetry and asymmetric maritime drone probes forcing Cape deviations.',
    strategicImpact: '+12 to 14 days transit times on Asia-Europe trade lanes; container spot rates elevated by +110%.',
  },
  {
    id: 'strait-hormuz',
    name: 'Strait of Hormuz',
    region: 'Persian Gulf',
    country: 'Iran / Oman',
    longitude: 56.3,
    latitude: 26.6,
    severity: 'critical',
    signalCount: 14,
    category: 'Energy Flow',
    timestamp: '38m ago',
    headline: 'Hydrocarbon transit monitoring & electronic spoofing clusters',
    intelligenceBrief: 'GPS telemetry interference reported across UAE/Oman maritime approach sectors. 21 million barrels/day flow rate under elevated alert.',
    strategicImpact: 'Crude tanker insurance premiums elevated; immediate volatility transmission to Brent futures.',
  },
  {
    id: 'black-sea-danube',
    name: 'Black Sea / Danube Grain Corridor',
    region: 'Eastern Europe',
    country: 'Ukraine / Romania',
    longitude: 30.5,
    latitude: 45.2,
    severity: 'high',
    signalCount: 9,
    category: 'Supply Chain',
    timestamp: '1h ago',
    headline: 'Port infrastructure strikes & agricultural insurance repricing',
    intelligenceBrief: 'Disrupted bulk cargo loading along western Black Sea ports; coastal defense mine-clearing ongoing.',
    strategicImpact: 'Regional grain shipment delays affecting Middle East/North African caloric balances.',
  },
  {
    id: 'south-china-sea',
    name: 'Second Thomas Shoal / Spratly Islands',
    region: 'South China Sea',
    country: 'Philippines / China',
    longitude: 115.8,
    latitude: 9.8,
    severity: 'high',
    signalCount: 8,
    category: 'Security Corridor',
    timestamp: '2h ago',
    headline: 'Coast guard water cannon encounters & acoustic disruption',
    intelligenceBrief: 'Repeated interdiction attempts during resupply missions; treaty ally consultation thresholds approached.',
    strategicImpact: 'Heightened risk of tactical escalation drawing regional maritime security alliances.',
  },
  {
    id: 'malacca-strait',
    name: 'Strait of Malacca / Singapore Roads',
    region: 'Southeast Asia',
    country: 'Singapore / Malaysia / Indonesia',
    longitude: 103.8,
    latitude: 1.3,
    severity: 'elevated',
    signalCount: 6,
    category: 'Maritime Chokepoint',
    timestamp: '3h ago',
    headline: 'Bunkering congestion & transshipment container pileup',
    intelligenceBrief: 'Container yard utilization exceeds 88% due to schedule unreliability caused by Red Sea diversions.',
    strategicImpact: 'Feedering vessel delays cascading through intra-Asia manufacturing supply chains.',
  },
  {
    id: 'baltic-suwalki',
    name: 'Baltic Sea / Suwalki Gap Corridor',
    region: 'Northern Europe',
    country: 'Poland / Lithuania / Baltic States',
    longitude: 23.2,
    latitude: 54.3,
    severity: 'high',
    signalCount: 7,
    category: 'Security Corridor',
    timestamp: '4h ago',
    headline: 'Undersea telecom cable anomaly & enhanced border surveillance',
    intelligenceBrief: 'Acoustic survey vessels deployed following fiber route severance; air defense rotations activated.',
    strategicImpact: 'European energy and data grid infrastructure redundancy testing under hybrid threat pressure.',
  },
  {
    id: 'panama-canal',
    name: 'Panama Canal Transit Zone',
    region: 'Central America',
    country: 'Panama',
    longitude: -79.6,
    latitude: 9.1,
    severity: 'elevated',
    signalCount: 5,
    category: 'Supply Chain',
    timestamp: '5h ago',
    headline: 'Draft restrictions & auction slot pricing normalization',
    intelligenceBrief: 'Lake Gatun water levels stabilized following precipitation recovery, but maximum draft remains strictly monitored.',
    strategicImpact: 'US Gulf-to-Asia LNG and grain transit constraints normalizing gradually.',
  },
  {
    id: 'gulf-of-guinea',
    name: 'Gulf of Guinea Maritime Zone',
    region: 'West Africa',
    country: 'Nigeria / Ghana',
    longitude: 4.2,
    latitude: 4.5,
    severity: 'elevated',
    signalCount: 4,
    category: 'Energy Flow',
    timestamp: '6h ago',
    headline: 'Offshore crude loading security & boarding attempts',
    intelligenceBrief: 'Armed security escorts deployed for FPSO crude offloading operations in deepwater sectors.',
    strategicImpact: 'West African sweet crude export schedules and bunkering premiums.',
  },
  {
    id: 'suez-canal',
    name: 'Suez Canal Northern Approach',
    region: 'North Africa',
    country: 'Egypt',
    longitude: 32.3,
    latitude: 31.2,
    severity: 'elevated',
    signalCount: 5,
    category: 'Maritime Chokepoint',
    timestamp: '6h ago',
    headline: 'Transit revenue suppression & canal authority tariff concessions',
    intelligenceBrief: 'Canal transit volume down -62% year-on-year; container vessel traffic remains depressed.',
    strategicImpact: 'Fiscal pressure on Egyptian foreign exchange reserves and Euro-Mediterranean delivery lead times.',
  },
  {
    id: 'arctic-bering',
    name: 'Bering Strait / Arctic Gateway',
    region: 'Arctic & Polar Corridor',
    country: 'USA / Russia',
    longitude: -168.9,
    latitude: 65.8,
    severity: 'moderate',
    signalCount: 3,
    category: 'Maritime Chokepoint',
    timestamp: '8h ago',
    headline: 'Non-ice class cargo convoy monitoring & seasonal ice retreat',
    intelligenceBrief: 'Northern Sea Route commercial transit registrations observed; sovereign polar navigation claims active.',
    strategicImpact: 'Emerging alternate summer routing between East Asian manufacturing hubs and North Sea ports.',
  },
  {
    id: 'south-asia-vizhinjam',
    name: 'Indian Ocean Transshipment Sector',
    region: 'South Asia',
    country: 'India / Sri Lanka',
    longitude: 77.0,
    latitude: 8.4,
    severity: 'moderate',
    signalCount: 4,
    category: 'Supply Chain',
    timestamp: '9h ago',
    headline: 'Deepwater transshipment hub capacity absorption',
    intelligenceBrief: 'Vizhinjam & Colombo terminals expanding ultra-large container vessel handling during Indian Ocean rerouting.',
    strategicImpact: 'Strategic realignment of South Asian transshipment dependencies away from regional feeder hubs.',
  },
];

// Strategic Sutra Corridor Correlations
const SUTRA_CORRIDORS: [string, string][] = [
  ['red-sea-mandeb', 'strait-hormuz'],
  ['strait-hormuz', 'south-asia-vizhinjam'],
  ['south-asia-vizhinjam', 'malacca-strait'],
  ['malacca-strait', 'south-china-sea'],
  ['south-china-sea', 'taiwan-strait'],
  ['black-sea-danube', 'suez-canal'],
  ['suez-canal', 'red-sea-mandeb'],
  ['baltic-suwalki', 'black-sea-danube'],
];

const SEVERITY_COLORS = {
  critical: { fill: '#DC2626', ring: 'rgba(220, 38, 38, 0.22)', border: '#991B1B', label: 'Critical' },
  high:     { fill: '#B87333', ring: 'rgba(184, 115, 51, 0.20)', border: '#8A5222', label: 'High' },
  elevated: { fill: '#CA8A04', ring: 'rgba(202, 138, 4, 0.18)', border: '#854D0E', label: 'Elevated' },
  moderate: { fill: '#1E3A8A', ring: 'rgba(30, 58, 138, 0.16)', border: '#172554', label: 'Moderate' },
  info:     { fill: '#64748B', ring: 'rgba(100, 116, 139, 0.14)', border: '#334155', label: 'Info' },
};

export const GlobalSignalField: React.FC<{ className?: string; liveCount?: number }> = ({
  className = '',
  liveCount = 7,
}) => {
  const { theme } = useAstraTheme();
  const isDark = theme === 'dark';
  const isSandstone = theme === 'sandstone';

  const [activeSignal, setActiveSignal] = useState<GeopoliticalSignal | null>(null);
  const [hoveredSignal, setHoveredSignal] = useState<GeopoliticalSignal | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number } | null>(null);

  // Map SVG Dimensions
  const MAP_WIDTH = 960;
  const MAP_HEIGHT = 480;

  // ── D3 Equal Earth Projection & TopoJSON Features ───────────────
  const { landPath, borderPath, graticulePath, spherePath, projection } = useMemo(() => {
    // Equal Earth equal-area pseudocylindrical projection
    const proj = geoEqualEarth().fitSize([MAP_WIDTH, MAP_HEIGHT], { type: 'Sphere' });
    const pathGen = geoPath().projection(proj);

    // Extract geometries from world-110m TopoJSON
    const landFeature = feature(worldData as any, (worldData as any).objects.land);
    const borderMesh = mesh(worldData as any, (worldData as any).objects.countries, (a, b) => a !== b);
    const grat = geoGraticule().step([30, 30])();

    return {
      landPath: pathGen(landFeature) || '',
      borderPath: pathGen(borderMesh) || '',
      graticulePath: pathGen(grat) || '',
      spherePath: pathGen({ type: 'Sphere' }) || '',
      projection: proj,
    };
  }, []);

  // Compute screen coordinates for each real signal
  const projectedSignals = useMemo(() => {
    return REAL_SIGNALS.map(sig => {
      const coords = projection([sig.longitude, sig.latitude]) || [0, 0];
      return {
        ...sig,
        x: coords[0],
        y: coords[1],
      };
    });
  }, [projection]);

  const signalMap = useMemo(() => {
    const m: Record<string, typeof projectedSignals[0]> = {};
    projectedSignals.forEach(s => { m[s.id] = s; });
    return m;
  }, [projectedSignals]);

  // Color Tokens based on Theme
  const surfaceFill = isDark ? '#1F2937' : isSandstone ? '#DFD1BC' : '#EDE3D2';
  const landFill = isDark ? '#111827' : isSandstone ? '#F5EFE3' : '#FBF7EE';
  const borderStroke = isDark ? '#374151' : isSandstone ? '#CBBDA8' : '#DCD0BE';
  const graticuleStroke = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(34,27,20,0.07)';

  return (
    <div
      className={`relative overflow-hidden rounded-xl border ${className}`}
      style={{
        backgroundColor: 'var(--astra-sandstone)',
        borderColor: 'var(--astra-sandstone-dark)',
        boxShadow: 'var(--shadow-md)',
      }}
    >
      {/* ── Section Header ────────────────────────────────────────── */}
      <div
        className="px-5 py-3.5 flex items-center justify-between border-b"
        style={{
          borderColor: 'var(--astra-sandstone-dark)',
          backgroundColor: isDark ? 'rgba(31,41,55,0.7)' : 'rgba(245,239,227,0.75)',
        }}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-agni-vermilion animate-pulse" />
            <h3
              className="text-base font-serif font-bold text-astra-ink"
            >
              Global Signal Field
            </h3>
          </div>
          <span
            className="px-2 py-0.5 rounded font-mono text-[9px] font-semibold tracking-wider border border-agni-copper/30 bg-agni-copper/10 text-agni-copper uppercase"
          >
            AGNI / GM-01 · EQUAL EARTH PROJECTION
          </span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 sm:gap-6">
          <div className="flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 text-agni-vermilion" />
            <span className="font-mono text-[10px] font-bold text-agni-vermilion uppercase tracking-wider">
              {liveCount} NEW SIGNALS
            </span>
          </div>

          <div className="hidden sm:flex items-center gap-3">
            {(['critical', 'high', 'elevated', 'moderate'] as const).map(sev => (
              <div key={sev} className="flex items-center gap-1">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: SEVERITY_COLORS[sev].fill }}
                />
                <span className="font-mono text-[8.5px] uppercase tracking-wider text-astra-slate">
                  {SEVERITY_COLORS[sev].label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Interactive Equal Earth Map Canvas ─────────────────────── */}
      <div className="relative w-full overflow-hidden" style={{ minHeight: 380, maxHeight: 540 }}>
        <svg
          viewBox={`0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`}
          className="w-full h-auto block select-none"
          preserveAspectRatio="xMidYMid meet"
          aria-label="Global Equal Earth Geopolitical Intelligence Map"
          role="img"
        >
          {/* Defs for subtle node glows and gradients */}
          <defs>
            <radialGradient id="signal-glow-critical" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#DC2626" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#DC2626" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="signal-glow-high" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#B87333" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#B87333" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* 1. Global Sphere Ocean Background */}
          <path
            d={spherePath}
            fill={surfaceFill}
            stroke={borderStroke}
            strokeWidth="0.8"
            style={{ pointerEvents: 'none' }}
          />

          {/* 2. Equal Earth Graticule (30° intervals) */}
          <path
            d={graticulePath}
            fill="none"
            stroke={graticuleStroke}
            strokeWidth="0.5"
            strokeDasharray="2 3"
            style={{ pointerEvents: 'none' }}
          />

          {/* 3. Real Country Land Polygons */}
          <path
            d={landPath}
            fill={landFill}
            stroke={borderStroke}
            strokeWidth="0.6"
            strokeLinejoin="round"
            style={{ pointerEvents: 'none' }}
          />

          {/* 4. Real Sovereign Boundaries (Mesh) */}
          <path
            d={borderPath}
            fill="none"
            stroke={borderStroke}
            strokeWidth="0.4"
            opacity="0.6"
            style={{ pointerEvents: 'none' }}
          />

          {/* 5. Strategic Sutra Corridors between chokepoints */}
          {SUTRA_CORRIDORS.map(([fromId, toId]) => {
            const a = signalMap[fromId];
            const b = signalMap[toId];
            if (!a || !b) return null;
            const midX = (a.x + b.x) / 2;
            const midY = (a.y + b.y) / 2 - 14;
            return (
              <path
                key={`sutra-${fromId}-${toId}`}
                d={`M ${a.x} ${a.y} Q ${midX} ${midY} ${b.x} ${b.y}`}
                fill="none"
                stroke="var(--agni-copper)"
                strokeWidth="1.2"
                strokeDasharray="3 4"
                opacity="0.4"
                style={{ pointerEvents: 'none' }}
              />
            );
          })}

          {/* 6. Geographically Positioned Signals */}
          {projectedSignals.map(sig => {
            const isHovered = hoveredSignal?.id === sig.id;
            const isSelected = activeSignal?.id === sig.id;
            const colors = SEVERITY_COLORS[sig.severity];

            return (
              <g
                key={sig.id}
                className="cursor-pointer transition-transform duration-200"
                onClick={() => setActiveSignal(sig)}
                onMouseEnter={(e) => {
                  setHoveredSignal(sig);
                  const rect = e.currentTarget.getBoundingClientRect();
                  setTooltipPos({ x: rect.left + rect.width / 2, y: rect.top });
                }}
                onMouseLeave={() => setHoveredSignal(null)}
                aria-label={`${sig.name}: ${sig.headline}`}
                role="button"
                tabIndex={0}
              >
                {/* Generous Invisible Click Target (36px diameter) */}
                <circle cx={sig.x} cy={sig.y} r={18} fill="transparent" />

                {/* Outer Pulse Wavefront */}
                <circle
                  cx={sig.x}
                  cy={sig.y}
                  r={isSelected ? 16 : isHovered ? 13 : 9}
                  fill={colors.ring}
                  className={sig.severity === 'critical' ? 'animate-ping' : ''}
                  style={{ animationDuration: '3s', pointerEvents: 'none' }}
                />

                {/* Ambient Core Ring */}
                <circle
                  cx={sig.x}
                  cy={sig.y}
                  r={isSelected ? 10 : 7}
                  fill={colors.ring}
                  style={{ pointerEvents: 'none' }}
                />

                {/* Core Anchor Bindu */}
                <circle
                  cx={sig.x}
                  cy={sig.y}
                  r={isSelected ? 5.5 : 4}
                  fill={colors.fill}
                  stroke="#FFFFFF"
                  strokeWidth="1.2"
                  style={{ pointerEvents: 'none' }}
                />

                {/* Signal Badge Count for active hotspots */}
                {sig.signalCount >= 8 && (
                  <text
                    x={sig.x}
                    y={sig.y - 8}
                    textAnchor="middle"
                    className="font-mono text-[7px] font-bold fill-current"
                    style={{ fill: colors.fill, pointerEvents: 'none' }}
                  >
                    {sig.signalCount}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* ── Hover Tooltip Overlay ─────────────────────────────────── */}
        {hoveredSignal && !activeSignal && (
          <div
            className="absolute z-20 pointer-events-none p-3 rounded-lg shadow-xl border bg-white dark:bg-neutral-900 border-astra-sandstone-dark/90 text-astra-ink dark:text-neutral-100 max-w-xs animate-fadeIn text-xs"
            style={{
              left: '50%',
              top: '14px',
              transform: 'translateX(-50%)',
              backdropFilter: 'blur(12px)',
            }}
          >
            <div className="flex items-center justify-between gap-3 mb-1">
              <span className="font-serif font-bold text-sm text-astra-ink">
                {hoveredSignal.name}
              </span>
              <span
                className="font-mono text-[8px] px-1.5 py-0.5 rounded font-bold uppercase"
                style={{
                  color: SEVERITY_COLORS[hoveredSignal.severity].fill,
                  backgroundColor: `${SEVERITY_COLORS[hoveredSignal.severity].fill}15`,
                }}
              >
                {hoveredSignal.severity}
              </span>
            </div>
            <div className="font-mono text-[9px] text-astra-slate mb-1">
              {hoveredSignal.country} · [{hoveredSignal.longitude.toFixed(1)}°E, {hoveredSignal.latitude.toFixed(1)}°N]
            </div>
            <p className="text-[11px] text-astra-slate line-clamp-2 leading-relaxed">
              {hoveredSignal.headline}
            </p>
            <div className="mt-1.5 pt-1.5 border-t border-black/5 dark:border-white/10 flex items-center justify-between text-[9px] font-mono text-astra-slate">
              <span>{hoveredSignal.category}</span>
              <span className="text-agni-copper font-semibold">Click for full dossier →</span>
            </div>
          </div>
        )}

        {/* ── Signal Detail Drawer (On Node Click) ───────────────────── */}
        {activeSignal && (
          <div
            className="absolute top-3 right-3 bottom-3 w-80 sm:w-96 rounded-xl shadow-2xl border p-5 z-30 flex flex-col justify-between animate-fadeIn bg-white/95 dark:bg-neutral-900/95 border-astra-sandstone-dark"
            style={{ backdropFilter: 'blur(16px)' }}
          >
            <div className="space-y-4 overflow-y-auto pr-1">
              <div className="flex items-start justify-between gap-3 pb-3 border-b border-astra-sandstone-dark/50">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: SEVERITY_COLORS[activeSignal.severity].fill }}
                  />
                  <div>
                    <h4 className="font-serif font-bold text-base text-astra-ink leading-tight">
                      {activeSignal.name}
                    </h4>
                    <div className="font-mono text-[9px] text-astra-slate mt-0.5">
                      {activeSignal.country} · {activeSignal.region}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setActiveSignal(null)}
                  className="p-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 text-astra-slate"
                  aria-label="Close dossier"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Coordinates & Category Pill */}
              <div className="flex items-center justify-between text-[9.5px] font-mono py-1">
                <span className="px-2 py-0.5 rounded bg-astra-sandstone/50 border border-astra-sandstone-dark/60 text-astra-slate">
                  LAT: {activeSignal.latitude.toFixed(2)}° · LON: {activeSignal.longitude.toFixed(2)}°
                </span>
                <span className="font-semibold text-agni-copper">
                  {activeSignal.category}
                </span>
              </div>

              {/* Headline */}
              <div className="p-2.5 rounded-lg bg-astra-sandstone/30 border border-astra-sandstone-dark/60 font-serif text-xs font-semibold text-astra-ink">
                "{activeSignal.headline}"
              </div>

              {/* Analytical Brief */}
              <div className="space-y-1">
                <div className="font-mono text-[8px] tracking-widest uppercase text-astra-slate font-bold">
                  TACTICAL INTELLIGENCE BRIEF
                </div>
                <p className="text-xs text-astra-slate leading-relaxed">
                  {activeSignal.intelligenceBrief}
                </p>
              </div>

              {/* Strategic Impact */}
              <div className="space-y-1">
                <div className="font-mono text-[8px] tracking-widest uppercase text-agni-copper font-bold">
                  STRATEGIC CHOKEPOINT IMPACT
                </div>
                <p className="text-xs text-astra-slate leading-relaxed">
                  {activeSignal.strategicImpact}
                </p>
              </div>
            </div>

            {/* Bottom Telemetry Bar */}
            <div className="pt-3 border-t border-astra-sandstone-dark/60 flex items-center justify-between font-mono text-[9px] text-astra-slate">
              <span>ACTIVE CLUSTERS: {activeSignal.signalCount}</span>
              <span className="text-agni-copper font-bold">STATUS: MONITORED</span>
            </div>
          </div>
        )}
      </div>

      {/* ── Bottom Metric Summary Bar ─────────────────────────────── */}
      <div
        className="px-5 py-3 flex items-center justify-between gap-4 flex-wrap border-t"
        style={{
          borderColor: 'var(--astra-sandstone-dark)',
          backgroundColor: isDark ? 'rgba(31,41,55,0.7)' : 'rgba(245,239,227,0.7)',
        }}
      >
        <div className="flex items-center gap-5 sm:gap-8 flex-wrap font-mono text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-astra-slate uppercase">TOTAL SIGNALS:</span>
            <span className="font-bold text-astra-ink">1,284</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-astra-slate uppercase">CRITICAL:</span>
            <span className="font-bold text-agni-vermilion">14</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-astra-slate uppercase">HIGH:</span>
            <span className="font-bold text-agni-copper">22</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-astra-slate uppercase">ELEVATED:</span>
            <span className="font-bold text-amber-600">41</span>
          </div>
        </div>

        <div className="font-mono text-[9px] text-astra-slate/80 uppercase tracking-wider flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>REAL-TIME STREAM ACTIVE · EQUAL EARTH PSEUDOCYLINDRICAL</span>
        </div>
      </div>
    </div>
  );
};
