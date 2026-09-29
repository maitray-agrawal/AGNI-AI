import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, ChevronDown, Menu } from 'lucide-react';
import { AgniLogo } from '../brand/AgniLogo';
import { AstraThemeSwitcher } from '../brand/AstraThemeSwitcher';
import { AstraMark } from './AstraMark';
import { SystemStatus, IntelligenceCommandBar } from './AstraShared';

interface HeaderProps {
  airGapped:    boolean;
  activeModel?: string;
  onMenuToggle?: () => void;
  sidebarOpen?:  boolean;
}

export const Header: React.FC<HeaderProps> = ({
  airGapped,
  activeModel,
  onMenuToggle,
  sidebarOpen,
}) => {
  const navigate = useNavigate();

  return (
    <header className="astra-topbar flex items-center gap-4 px-4 py-2.5" role="banner">
      {/* ── Menu toggle (mobile) ─────────────────────────── */}
      <button
        onClick={onMenuToggle}
        className="md:hidden btn-secondary !p-2 flex-shrink-0"
        aria-label="Toggle navigation"
        aria-expanded={sidebarOpen}
      >
        <Menu className="w-4 h-4" />
      </button>

      {/* ── Canonical AGNI Header Lockup (Desktop/Tablet) ── */}
      <div
        className="flex-shrink-0 flex items-center pr-2 border-r border-astra-sandstone-dark/40 cursor-pointer"
        onClick={() => navigate('/')}
        title="Return to AGNI Intelligence Dashboard"
      >
        <AgniLogo
          variant="full"
          size={30}
          showAstraAttribution={true}
          theme="light"
          className="hidden sm:flex"
        />
        <AgniLogo
          variant="mark"
          size={24}
          theme="light"
          className="sm:hidden"
        />
      </div>

      {/* ── Intelligence command bar ─────────────────────── */}
      <IntelligenceCommandBar className="flex-1 max-w-xl" />

      {/* ── Right side controls ──────────────────────────── */}
      <div className="flex items-center gap-3 ml-auto flex-shrink-0">

        {/* Compact system status strip */}
        <SystemStatus
          airGapped={airGapped}
          model={activeModel}
          ragOnline={true}
        />

        {/* Live AstraX Theme & Project Switcher (Section 12 & 28) */}
        <AstraThemeSwitcher />

        {/* Notifications */}
        <button
          className="relative p-2 rounded-lg transition-colors flex-shrink-0"
          style={{ color: 'var(--astra-slate)' }}
          aria-label="View notifications — 2 unread"
          onMouseOver={e => (e.currentTarget.style.background = 'var(--astra-sandstone)')}
          onMouseOut={e  => (e.currentTarget.style.background = 'transparent')}
        >
          <Bell className="w-4 h-4" />
          <span
            className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full"
            style={{ background: 'var(--agni-red)' }}
            aria-hidden="true"
          />
        </button>

        {/* User profile */}
        <button
          className="flex items-center gap-1.5 px-1.5 py-1 rounded-lg transition-colors flex-shrink-0"
          style={{ color: 'var(--astra-slate)' }}
          aria-label="User profile menu"
          onMouseOver={e => (e.currentTarget.style.background = 'var(--astra-sandstone)')}
          onMouseOut={e  => (e.currentTarget.style.background = 'transparent')}
        >
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center"
            style={{ background: 'var(--agni-red)', color: 'var(--astra-ivory)' }}
          >
            <AstraMark size={14} />
          </div>
          <ChevronDown className="w-3 h-3 hidden sm:block" />
        </button>
      </div>
    </header>
  );
};
