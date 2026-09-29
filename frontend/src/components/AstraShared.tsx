import React from 'react';
import { Shield, Cpu, Database, Wifi, WifiOff, Search, Command } from 'lucide-react';

/* ──────────────────────────────────────────────────────────────────
   Shared utility components for the AstraX / AGNI V2 workspace.
   ────────────────────────────────────────────────────────────────── */

/* ── SectionRule ─────────────────────────────────────────────────
   Copper section rule with sequential numbering.
   Usage: <SectionRule number="01" title="GLOBAL SITUATION" />
   ────────────────────────────────────────────────────────────────── */
interface SectionRuleProps {
  number:    string;
  title:     string;
  className?: string;
}
export const SectionRule: React.FC<SectionRuleProps> = ({ number, title, className = '' }) => (
  <div className={`flex items-center gap-3 mb-4 ${className}`} role="heading" aria-level={2}>
    <span
      style={{
        fontFamily: 'var(--font-mono)', fontSize: '0.5rem', fontWeight: 700,
        color: 'var(--agni-copper)', letterSpacing: '0.1em', flexShrink: 0,
      }}
    >
      {number}
    </span>
    <span
      style={{
        fontFamily: 'var(--font-mono)', fontSize: '0.5rem', fontWeight: 700,
        color: 'var(--astra-slate)', letterSpacing: '0.14em', textTransform: 'uppercase', flexShrink: 0,
      }}
    >
      /
    </span>
    <span
      style={{
        fontFamily: 'var(--font-mono)', fontSize: '0.5625rem', fontWeight: 700,
        color: 'var(--astra-ink)', letterSpacing: '0.1em', textTransform: 'uppercase', flexShrink: 0,
      }}
    >
      {title}
    </span>
    <div
      style={{ flex: 1, height: 1, background: 'linear-gradient(90deg, var(--agni-copper) 0%, transparent 100%)', opacity: 0.35 }}
      aria-hidden="true"
    />
  </div>
);

/* ── AstraCoordinate ─────────────────────────────────────────────
   Research-system panel identifier. Tiny, understated.
   Usage: <AstraCoordinate id="GM-01" label="GLOBAL MONITOR" />
   ────────────────────────────────────────────────────────────────── */
interface AstraCoordinateProps {
  id:         string;
  label?:     string;
  className?: string;
}
export const AstraCoordinate: React.FC<AstraCoordinateProps> = ({ id, label, className = '' }) => (
  <div
    className={`inline-flex items-center gap-1 ${className}`}
    aria-label={`Panel identifier: AGNI ${id}${label ? ` — ${label}` : ''}`}
  >
    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.1em' }}>
      AGNI /
    </span>
    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--agni-copper)', fontWeight: 700, letterSpacing: '0.1em' }}>
      {id}
    </span>
    {label && (
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem', color: 'var(--astra-slate-light)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
        {label}
      </span>
    )}
  </div>
);

/* ── SystemStatus ────────────────────────────────────────────────
   Compact sovereignty + system status bar for the topbar.
   Usage: <SystemStatus airGapped={true} model="llama3.1:8b" />
   ────────────────────────────────────────────────────────────────── */
interface SystemStatusProps {
  airGapped?:  boolean;
  model?:      string;
  ragOnline?:  boolean;
  className?:  string;
}
export const SystemStatus: React.FC<SystemStatusProps> = ({
  airGapped = true,
  model,
  ragOnline = true,
  className = '',
}) => {
  const items = [
    {
      icon:  <Cpu className="w-2.5 h-2.5" />,
      label: 'LOCAL INFERENCE',
      ok:    true,
      title: `Model: ${model || 'Ollama (Local)'}`,
    },
    {
      icon:  <Database className="w-2.5 h-2.5" />,
      label: 'QDRANT',
      ok:    ragOnline,
      title: 'Qdrant vector database',
    },
    {
      icon:  airGapped ? <WifiOff className="w-2.5 h-2.5" /> : <Wifi className="w-2.5 h-2.5" />,
      label: 'ZERO EGRESS',
      ok:    true,
      title: 'No external network connections',
    },
    {
      icon:  <Shield className="w-2.5 h-2.5" />,
      label: 'AIR-GAP',
      ok:    airGapped,
      title: airGapped ? 'Sovereign air-gap enforced' : 'Air-gap status unverified',
    },
  ];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {items.map((item, i) => (
        <div
          key={i}
          className="hidden xl:flex items-center gap-1.5"
          title={item.title}
        >
          <span
            style={{
              color:   item.ok ? 'var(--status-positive)' : 'var(--status-warning)',
              display: 'flex', alignItems: 'center',
            }}
          >
            {item.icon}
          </span>
          <span
            style={{
              fontFamily:    'var(--font-mono)',
              fontSize:      '0.4375rem',
              fontWeight:    700,
              color:         item.ok ? 'var(--status-positive)' : 'var(--status-warning)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
            }}
          >
            {item.label}
          </span>
        </div>
      ))}

      {/* Mobile: just the shield badge */}
      <div
        className="xl:hidden flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg"
        style={{
          background:  airGapped ? 'rgba(45,106,79,0.08)' : 'rgba(194,132,42,0.08)',
          border:      `1px solid ${airGapped ? 'rgba(45,106,79,0.25)' : 'rgba(194,132,42,0.25)'}`,
          color:       airGapped ? 'var(--status-positive)' : 'var(--status-warning)',
        }}
        title={airGapped ? 'Sovereign air-gap enforced' : 'Air-gap status unverified'}
      >
        <span className="status-ring" style={{ color: airGapped ? 'var(--status-positive)' : 'var(--status-warning)', width: 8, height: 8 }} aria-hidden="true" />
        <Shield className="w-3 h-3" />
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5625rem', fontWeight: 700, letterSpacing: '0.06em' }}>
          {airGapped ? 'SOVEREIGN' : 'UNVERIFIED'}
        </span>
      </div>
    </div>
  );
};

/* ── IntelligenceCommandBar ──────────────────────────────────────
   Upgraded search / command field for the topbar.
   Preserves existing search functionality; visually enriched.
   ────────────────────────────────────────────────────────────────── */
interface IntelligenceCommandBarProps {
  onSearch?:  (query: string) => void;
  className?: string;
}
export const IntelligenceCommandBar: React.FC<IntelligenceCommandBarProps> = ({
  onSearch,
  className = '',
}) => {
  const [value, setValue] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(value);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`astra-search ${className}`}
      role="search"
      style={{ maxWidth: 520, gap: 8 }}
    >
      <Search className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--astra-slate-light)' }} />
      <input
        type="search"
        value={value}
        onChange={e => setValue(e.target.value)}
        placeholder="Ask AGNI about a country, event, market, or signal…"
        aria-label="Intelligence search"
        style={{ fontSize: '0.8125rem' }}
      />
      <div
        className="hidden sm:flex items-center gap-1 px-1.5 py-0.5 rounded border flex-shrink-0"
        style={{ borderColor: 'var(--astra-sandstone-dark)', color: 'var(--astra-slate-light)' }}
        aria-label="Keyboard shortcut: Command K"
      >
        <Command className="w-2.5 h-2.5" />
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.4375rem' }}>K</span>
      </div>
    </form>
  );
};
