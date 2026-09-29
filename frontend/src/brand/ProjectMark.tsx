import React from 'react';
import { AgniLogo } from './AgniLogo';
import { ASTRA_PALETTE } from './astraProducts';

export type AstraProjectId =
  | 'agni'
  | 'kubersetu'
  | 'vajra'
  | 'niyukti'
  | 'margadarshi'
  | 'satyam'
  | 'vaidhya';

export interface ProjectMarkProps {
  project: AstraProjectId;
  size?: number | string;
  theme?: 'primary' | 'monochrome' | 'dark' | 'sandstone';
  className?: string;
}

/**
 * ProjectMark — Dedicated Vector Symbol Dispatcher
 * Directly recreates the 7 canonical project-specific marks from the AstraX identity system:
 * - AGNI: Research Intelligence (Spire, faceted sails, outrigger wings)
 * - KuberSetu: Financial Intelligence (Network bridge truss, diagonal beams)
 * - Vajra: Crisis Intelligence (Thunderbolt blades, descending chevron)
 * - Niyukti: Talent Intelligence (Ascending sprout, human opportunity wings)
 * - Margadarshi: Career Intelligence (Directional compass rays, quadrant nodes)
 * - Satyam: Trust & Governance (Verification balance, dual beam)
 * - Vaidhya: Clinical Intelligence (Botanical healing nodes, calibration axis)
 */
export const ProjectMark: React.FC<ProjectMarkProps> = ({
  project,
  size = 36,
  theme = 'primary',
  className = '',
}) => {
  const isMono = theme === 'monochrome';
  const isDark = theme === 'dark';

  // AGNI uses its dedicated canonical mark
  if (project === 'agni') {
    return (
      <AgniLogo
        variant="mark"
        theme={theme}
        size={size}
        className={className}
      />
    );
  }

  // KUBERSETU — Financial Intelligence (Network / Bridge Truss)
  if (project === 'kubersetu') {
    const indigo = isMono ? 'currentColor' : isDark ? '#60A5FA' : ASTRA_PALETTE.indigo;
    const copper = isMono ? 'currentColor' : isDark ? '#D48946' : ASTRA_PALETTE.copper;

    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 100"
        width={size}
        height={size}
        className={`inline-block flex-shrink-0 select-none ${className}`}
        aria-label="KuberSetu Mark"
        role="img"
      >
        <g id="kubersetu-mark">
          {/* Vertical copper axis */}
          <line x1="50" y1="12" x2="50" y2="88" stroke={copper} strokeWidth="1.2" />
          <polygon points="50,6 54,10 50,14 46,10" fill={copper} />
          <polygon points="50,22 52.5,24.5 50,27 47.5,24.5" fill={copper} />
          <polygon points="50,86 54,90 50,94 46,90" fill={copper} />

          {/* Diagonal Bridge Beams (Indigo) */}
          <polygon points="50,50 20,24 24,20 50,44" fill={indigo} />
          <polygon points="50,50 80,24 76,20 50,44" fill={indigo} />
          <polygon points="50,50 20,76 24,80 50,56" fill={indigo} />
          <polygon points="50,50 80,76 76,80 50,56" fill={indigo} />

          {/* Network tension lines */}
          <line x1="20" y1="24" x2="20" y2="76" stroke={copper} strokeWidth="0.6" strokeDasharray="2 2" opacity="0.6" />
          <line x1="80" y1="24" x2="80" y2="76" stroke={copper} strokeWidth="0.6" strokeDasharray="2 2" opacity="0.6" />

          {/* Terminal nodes */}
          <polygon points="20,20 24,24 20,28 16,24" fill={indigo} />
          <polygon points="80,20 84,24 80,28 76,24" fill={indigo} />
          <polygon points="20,72 24,76 20,80 16,76" fill={indigo} />
          <polygon points="80,72 84,76 80,80 76,76" fill={indigo} />

          {/* Central Bindu diamond */}
          <polygon points="50,40 60,50 50,60 40,50" fill={copper} />
          <polygon points="50,44 56,50 50,56 44,50" fill={isDark ? '#111827' : '#FDF7EC'} />
        </g>
      </svg>
    );
  }

  // VAJRA — Crisis Intelligence (Crossed Thunderbolt Blades)
  if (project === 'vajra') {
    const vermilion = isMono ? 'currentColor' : isDark ? '#F87171' : ASTRA_PALETTE.vermilion;
    const copper = isMono ? 'currentColor' : isDark ? '#D48946' : ASTRA_PALETTE.copper;

    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 100"
        width={size}
        height={size}
        className={`inline-block flex-shrink-0 select-none ${className}`}
        aria-label="Vajra Mark"
        role="img"
      >
        <g id="vajra-mark">
          {/* Top Axis & Diamond */}
          <line x1="50" y1="8" x2="50" y2="50" stroke={vermilion} strokeWidth="1.2" />
          <polygon points="50,4 55,9 50,14 45,9" fill={vermilion} />
          <polygon points="50,18 53,21 50,24 47,21" fill="none" stroke={vermilion} strokeWidth="1" />

          {/* Crossed Diagonal Blades */}
          <polygon points="22,26 50,64 46,68 18,30" fill={copper} />
          <polygon points="78,26 50,64 54,68 82,30" fill={vermilion} />

          {/* Blade tips */}
          <polygon points="22,22 26,26 22,30 18,26" fill={copper} />
          <polygon points="78,22 82,26 78,30 74,26" fill={vermilion} />

          {/* Descending Chevron (Observe -> Respond -> Recover) */}
          <polygon points="50,72 24,48 28,44 50,62 72,44 76,48" fill={copper} />

          {/* Central Bindu diamond */}
          <polygon points="50,42 58,50 50,58 42,50" fill={vermilion} />
          <polygon points="50,45 55,50 50,55 45,50" fill={isDark ? '#111827' : '#FDF7EC'} />
        </g>
      </svg>
    );
  }

  // NIYUKTI — Talent Intelligence (Growth Sprout & Flared Wings)
  if (project === 'niyukti') {
    const indigo = isMono ? 'currentColor' : isDark ? '#60A5FA' : ASTRA_PALETTE.indigo;
    const saffron = isMono ? 'currentColor' : isDark ? '#FBBF24' : ASTRA_PALETTE.saffron;

    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 100"
        width={size}
        height={size}
        className={`inline-block flex-shrink-0 select-none ${className}`}
        aria-label="Niyukti Mark"
        role="img"
      >
        <g id="niyukti-mark">
          {/* Top Ascending Saffron Sprout */}
          <path d="M 50,46 Q 44,28 36,18" stroke={saffron} strokeWidth="1.8" fill="none" strokeLinecap="round" />
          <path d="M 50,46 Q 56,28 64,18" stroke={saffron} strokeWidth="1.8" fill="none" strokeLinecap="round" />
          <polygon points="36,15 39,18 36,21 33,18" fill={saffron} />
          <polygon points="64,15 67,18 64,21 61,18" fill={saffron} />
          <polygon points="50,6 55,11 50,16 45,11" fill={saffron} />

          {/* Flared Indigo Wings */}
          <path d="M 44,48 Q 24,32 14,24 Q 30,50 42,54 Z" fill={indigo} />
          <path d="M 56,48 Q 76,32 86,24 Q 70,50 58,54 Z" fill={indigo} />
          <path d="M 42,56 Q 24,70 14,82 Q 32,74 46,62 Z" fill={indigo} />
          <path d="M 58,56 Q 76,70 86,82 Q 68,74 54,62 Z" fill={indigo} />

          {/* Central Bindu diamond */}
          <polygon points="50,42 59,51 50,60 41,51" fill={saffron} />
          <polygon points="50,45 56,51 50,57 44,51" fill={isDark ? '#111827' : '#FDF7EC'} />
        </g>
      </svg>
    );
  }

  // MARGADARSHI — Career Intelligence (Directional Compass Quadrant Rays)
  if (project === 'margadarshi') {
    const teal = isMono ? 'currentColor' : isDark ? '#2DD4BF' : '#0D9488';
    const saffron = isMono ? 'currentColor' : isDark ? '#FBBF24' : ASTRA_PALETTE.saffron;

    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 100"
        width={size}
        height={size}
        className={`inline-block flex-shrink-0 select-none ${className}`}
        aria-label="Margadarshi Mark"
        role="img"
      >
        <g id="margadarshi-mark">
          {/* Vertical axis */}
          <line x1="50" y1="10" x2="50" y2="90" stroke={saffron} strokeWidth="1.2" />
          <polygon points="50,6 55,11 50,16 45,11" fill={saffron} />
          <polygon points="50,84 55,89 50,94 45,89" fill={saffron} />

          {/* 4 Directional Teal Beams */}
          <polygon points="50,44 20,24 24,20 50,48" fill={teal} />
          <polygon points="50,44 80,24 76,20 50,48" fill={teal} />
          <polygon points="50,56 20,76 24,80 50,52" fill={teal} />
          <polygon points="50,56 80,76 76,80 50,52" fill={teal} />

          {/* Quadrant Satellite Nodes */}
          <polygon points="20,20 24,24 20,28 16,24" fill={teal} />
          <polygon points="80,20 84,24 80,28 76,24" fill={teal} />
          <polygon points="20,72 24,76 20,80 16,76" fill={teal} />
          <polygon points="80,72 84,76 80,80 76,76" fill={teal} />

          {/* Central Core Bindu Diamond */}
          <polygon points="50,38 62,50 50,62 38,50" fill={saffron} />
          <polygon points="50,43 57,50 50,57 43,50" fill={isDark ? '#111827' : '#FDF7EC'} />
        </g>
      </svg>
    );
  }

  // SATYAM — Trust & Governance (Dual-Beam Verification Balance)
  if (project === 'satyam') {
    const indigo = isMono ? 'currentColor' : isDark ? '#60A5FA' : ASTRA_PALETTE.indigo;
    const copper = isMono ? 'currentColor' : isDark ? '#D48946' : ASTRA_PALETTE.copper;

    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 100"
        width={size}
        height={size}
        className={`inline-block flex-shrink-0 select-none ${className}`}
        aria-label="Satyam Mark"
        role="img"
      >
        <g id="satyam-mark">
          {/* Vertical verification spine */}
          <line x1="50" y1="8" x2="50" y2="88" stroke={copper} strokeWidth="1.2" />
          <polygon points="50,5 54,9 50,13 46,9" fill={copper} />
          <polygon points="50,85 54,89 50,93 46,89" fill={copper} />

          {/* Upper Pyramid Verification Truss (Indigo) */}
          <polygon points="50,18 20,44 26,44 50,25" fill={indigo} />
          <polygon points="50,18 80,44 74,44 50,25" fill={indigo} />

          {/* Horizontal Balance Beams */}
          <line x1="18" y1="52" x2="82" y2="52" stroke={indigo} strokeWidth="2" />
          <polygon points="20,52 38,68 34,70 16,54" fill={copper} />
          <polygon points="80,52 62,68 66,70 84,54" fill={copper} />

          {/* Central Core Bindu Diamond */}
          <polygon points="50,42 60,52 50,62 40,52" fill={copper} />
          <polygon points="50,46 56,52 50,58 44,52" fill={isDark ? '#111827' : '#FDF7EC'} />
        </g>
      </svg>
    );
  }

  // VAIDHYA — Clinical Intelligence (Botanical Healing Nodes)
  if (project === 'vaidhya') {
    const green = isMono ? 'currentColor' : isDark ? '#4ADE80' : ASTRA_PALETTE.forestGreen;
    const copper = isMono ? 'currentColor' : isDark ? '#D48946' : ASTRA_PALETTE.copper;

    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 100"
        width={size}
        height={size}
        className={`inline-block flex-shrink-0 select-none ${className}`}
        aria-label="Vaidhya Mark"
        role="img"
      >
        <g id="vaidhya-mark">
          {/* Vertical calibration needle */}
          <line x1="50" y1="10" x2="50" y2="88" stroke={copper} strokeWidth="1.2" />
          <polygon points="50,6 55,11 50,16 45,11" fill={copper} />
          <polygon points="50,84 54,88 50,92 46,88" fill={copper} />

          {/* Dual Botanical Healing Leaves (Green) */}
          <path
            d="M 50,50 C 40,30 20,24 28,18 C 36,12 48,34 50,50 Z"
            fill={green}
          />
          <path
            d="M 50,50 C 60,30 80,24 72,18 C 64,12 52,34 50,50 Z"
            fill={green}
          />
          <polygon points="28,16 32,20 28,24 24,20" fill={green} />
          <polygon points="72,16 76,20 72,24 68,20" fill={green} />

          {/* Lower diagonal stability struts (Copper) */}
          <line x1="50" y1="56" x2="28" y2="78" stroke={copper} strokeWidth="1.5" />
          <line x1="50" y1="56" x2="72" y2="78" stroke={copper} strokeWidth="1.5" />
          <polygon points="28,76 31,79 28,82 25,79" fill={copper} />
          <polygon points="72,76 75,79 72,82 69,79" fill={copper} />

          {/* Central Bindu diamond */}
          <polygon points="50,44 58,52 50,60 42,52" fill={copper} />
          <polygon points="50,47 55,52 50,57 45,52" fill={isDark ? '#111827' : '#FDF7EC'} />
        </g>
      </svg>
    );
  }

  // Fallback to Agni
  return <AgniLogo variant="mark" theme={theme} size={size} className={className} />;
};
