import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Globe, TrendingUp, AlertTriangle,
  GitBranch, Network, FileText, Star, Database,
  Settings, Activity, ChevronRight
} from 'lucide-react';
import { AgniLogo } from '../brand/AgniLogo';
import { AstraSeal } from '../brand/AstraSeal';
import { AgniHeatField } from '../brand/AgniHeatField';

interface NavItem {
  id:       string;
  label:    string;
  icon:     React.ReactNode;
  section?: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'workbench',    label: 'Intelligence Workbench', icon: <LayoutDashboard className="w-4 h-4" />, section: 'ANALYSIS' },
  { id: 'monitor',     label: 'Global Monitor',          icon: <Globe            className="w-4 h-4" /> },
  { id: 'geopolitics', label: 'Geopolitical Analysis',   icon: <Activity         className="w-4 h-4" /> },
  { id: 'economics',   label: 'Economic Indicators',     icon: <TrendingUp       className="w-4 h-4" /> },
  { id: 'risk',        label: 'Risk Intelligence',        icon: <AlertTriangle    className="w-4 h-4" />, section: 'INTELLIGENCE' },
  { id: 'scenarios',   label: 'Scenario Modeling',       icon: <GitBranch        className="w-4 h-4" /> },
  { id: 'graph',       label: 'Knowledge Graph',          icon: <Network          className="w-4 h-4" /> },
  { id: 'reports',     label: 'Reports',                  icon: <FileText         className="w-4 h-4" />, section: 'WORKSPACE' },
  { id: 'watchlist',   label: 'Watchlist',                icon: <Star             className="w-4 h-4" /> },
  { id: 'datasources', label: 'Data Sources',             icon: <Database         className="w-4 h-4" /> },
  { id: 'settings',    label: 'Settings',                 icon: <Settings         className="w-4 h-4" />, section: 'SYSTEM' },
];

interface AstraSidebarProps {
  activeItem?: string;
  onItemSelect?: (id: string) => void;
  isOpen?: boolean;
}

export const AstraSidebar: React.FC<AstraSidebarProps> = ({
  activeItem = 'workbench',
  onItemSelect,
  isOpen = true,
}) => {
  const navigate = useNavigate();

  return (
    <aside
      className={`astra-sidebar ${isOpen ? 'open' : ''}`}
      aria-label="Primary navigation"
      role="navigation"
    >
      {/* ── Canonical AGNI Brand Lockup (Pure AGNI Focus) ───── */}
      <div className="px-5 pt-6 pb-4 border-b border-white/10">
        <div className="flex flex-col items-center text-center">
          {/* Canonical AGNI Mark */}
          <div className="mb-2">
            <AgniLogo variant="mark" size={46} theme="dark" />
          </div>

          {/* AGNI Product Title */}
          <div
            className="tracking-[0.22em] font-serif text-lg font-bold uppercase leading-none"
            style={{ color: 'var(--astra-ivory)' }}
          >
            AGNI
          </div>

          {/* Descriptor */}
          <div
            className="mt-1 text-[8.5px] font-mono tracking-[0.24em] uppercase font-semibold text-white/50"
          >
            RESEARCH INTELLIGENCE
          </div>

          {/* Subtle Institutional Attribution -> Navigates to /astrax */}
          <button
            onClick={() => navigate('/astrax')}
            className="mt-3.5 px-3 py-1.5 rounded-lg flex items-center justify-between w-full transition-all group bg-white/5 hover:bg-white/10 border border-white/10"
            title="View AstraX Family & Institutional Architecture"
            aria-label="AstraX - Member of the AstraX Family"
          >
            <div className="flex items-center gap-2 text-left">
              <span className="w-1.5 h-1.5 rounded-full bg-agni-copper animate-pulse" />
              <div>
                <div className="font-mono text-[6.5px] tracking-[0.16em] uppercase text-white/50 leading-tight">
                  MEMBER OF THE
                </div>
                <div className="font-mono text-[8px] tracking-[0.18em] uppercase font-bold text-white/80 group-hover:text-white leading-tight">
                  ASTRA X FAMILY
                </div>
              </div>
            </div>
            <ChevronRight className="w-3.5 h-3.5 text-white/40 group-hover:text-white/90 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>

      {/* ── Navigation ─────────────────────────────────── */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <React.Fragment key={item.id}>
            {item.section && (
              <div className="nav-section-label">{item.section}</div>
            )}
            <button
              className={`nav-item w-full ${activeItem === item.id ? 'active' : ''}`}
              onClick={() => onItemSelect?.(item.id)}
              aria-current={activeItem === item.id ? 'page' : undefined}
            >
              {item.icon}
              <span>{item.label}</span>
              {activeItem === item.id && (
                <ChevronRight
                  className="w-3 h-3 ml-auto"
                  style={{ color: 'var(--agni-copper)', opacity: 0.7 }}
                />
              )}
            </button>
          </React.Fragment>
        ))}
      </nav>

      {/* ── Lower Brand Statement & Institutional Link ───── */}
      <div
        className="relative px-5 py-5 border-t overflow-hidden"
        style={{ borderColor: 'rgba(245,239,227,0.08)' }}
      >
        {/* Heat-field watermark behind text */}
        <div
          className="absolute -bottom-8 -right-8"
          style={{ color: 'var(--astra-ivory)', opacity: 0.04 }}
          aria-hidden="true"
        >
          <AgniHeatField intensity="subtle" />
        </div>

        {/* Copper rule */}
        <div
          className="w-6 h-0.5 mb-2.5"
          style={{ background: 'var(--agni-copper)', opacity: 0.6 }}
        />

        <p
          style={{
            fontFamily:  'var(--font-display)',
            fontSize:    '0.75rem',
            lineHeight:  1.5,
            color:       'rgba(245,239,227,0.55)',
            fontStyle:   'italic',
          }}
        >
          Early insights.<br />
          Deeper context.<br />
          Stronger decisions.
        </p>

        {/* Institutional Attribution Link -> /astrax */}
        <button
          onClick={() => navigate('/astrax')}
          className="w-full mt-3 flex items-center gap-2.5 pt-2.5 border-t border-white/10 text-left hover:bg-white/5 p-1 rounded-lg transition-colors group"
          title="Explore AstraX Institutional Architecture"
          aria-label="AstraX Sovereign Architecture"
        >
          <AstraSeal size={28} theme="dark" />
          <div className="flex-1">
            <div className="font-mono text-[7px] tracking-[0.16em] uppercase text-white/50 font-semibold group-hover:text-white/80">
              ASTRA X INTELLIGENCE
            </div>
            <div className="font-mono text-[6.5px] tracking-widest text-white/30 group-hover:text-white/60 flex items-center gap-1">
              SOVEREIGN ARCHITECTURE
              <ChevronRight className="w-2.5 h-2.5 opacity-60 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </div>
        </button>
      </div>
    </aside>
  );
};
