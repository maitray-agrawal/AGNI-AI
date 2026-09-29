import React from 'react';
import { ASTRA_PALETTE } from './astraProducts';

export interface AstraSealProps {
  size?: number | string;
  className?: string;
  theme?: 'primary' | 'monochrome' | 'dark';
  caption?: string;
  provenanceId?: string;
}

/**
 * AstraSeal — Canonical Institutional Authentication Seal / Stamp
 * Directly derived from official AstraX visual identity board.
 * - Double concentric copper boundary rings
 * - Arched top typography: "ASTRAX"
 * - Arched bottom typography: "INTELLIGENCE FOR A HIGHER TOMORROW"
 * - Cardinal diamond markers
 * - Canonical AstraX master vector mark at core
 */
export const AstraSeal: React.FC<AstraSealProps> = ({
  size = 110,
  className = '',
  theme = 'primary',
  caption,
  provenanceId,
}) => {
  const isMono = theme === 'monochrome';
  const isDark = theme === 'dark';

  const copper = isMono ? 'currentColor' : isDark ? '#D48946' : ASTRA_PALETTE.copper;
  const indigo = isMono ? 'currentColor' : isDark ? '#93C5FD' : ASTRA_PALETTE.indigo;
  const textColor = isMono ? 'currentColor' : isDark ? '#FDF7EC' : ASTRA_PALETTE.copperDark;

  return (
    <div className={`inline-flex flex-col items-center select-none ${className}`}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 200 200"
        width={size}
        height={size}
        className="transition-transform duration-300 hover:rotate-2"
        aria-label="AstraX Institutional Seal"
        role="img"
      >
        <defs>
          {/* Top text arc path (clockwise) */}
          <path
            id="astraSealTopArc"
            d="M 32,100 A 68,68 0 0,1 168,100"
            fill="none"
          />
          {/* Bottom text arc path (clockwise, so text reads left-to-right at bottom) */}
          <path
            id="astraSealBottomArc"
            d="M 170,100 A 70,70 0 0,1 30,100"
            fill="none"
          />
        </defs>

        {/* Outer Circular Double Rim */}
        <circle
          cx="100"
          cy="100"
          r="95"
          fill={isDark ? '#1C1917' : '#FDF7EC'}
          stroke={copper}
          strokeWidth="2.2"
        />
        <circle
          cx="100"
          cy="100"
          r="89"
          fill="none"
          stroke={copper}
          strokeWidth="0.8"
          strokeDasharray="4 2"
          opacity="0.8"
        />
        <circle
          cx="100"
          cy="100"
          r="66"
          fill="none"
          stroke={copper}
          strokeWidth="1"
          opacity="0.7"
        />

        {/* Arched Top Text: ASTRAX */}
        <text
          fill={textColor}
          fontSize="11.5"
          fontFamily="'Fraunces', Georgia, serif"
          fontWeight="bold"
          letterSpacing="0.32em"
        >
          <textPath href="#astraSealTopArc" startOffset="50%" textAnchor="middle">
            ASTRAX
          </textPath>
        </text>

        {/* Arched Bottom Text: INTELLIGENCE FOR A HIGHER TOMORROW */}
        <text
          fill={textColor}
          fontSize="6.8"
          fontFamily="'IBM Plex Mono', ui-monospace, monospace"
          fontWeight="600"
          letterSpacing="0.22em"
        >
          <textPath href="#astraSealBottomArc" startOffset="50%" textAnchor="middle">
            INTELLIGENCE FOR A HIGHER TOMORROW
          </textPath>
        </text>

        {/* Cardinal Diamond Markers (9 o'clock and 3 o'clock) */}
        <polygon points="21,100 24.5,96.5 28,100 24.5,103.5" fill={copper} />
        <polygon points="172,100 175.5,96.5 179,100 175.5,103.5" fill={copper} />

        {/* Center AstraX Master Geometry */}
        <g id="seal-core-astrax" transform="translate(42, 42) scale(0.58)">
          {/* Vertical axis */}
          <line x1="100" y1="18" x2="100" y2="182" stroke={copper} strokeWidth="1.2" opacity="0.7" />
          <polygon points="100,16 104,20 100,24 96,20" fill={copper} />
          <polygon points="100,176 104,180 100,184 96,180" fill={copper} />

          {/* 4 Wings */}
          {/* Top-Left Wing */}
          <path d="M 100,82 C 72,50 48,32 26,22 C 60,56 78,80 88,94 Z" fill={isMono ? copper : indigo} />
          <path d="M 100,85 C 80,62 58,45 38,34 C 54,54 72,74 88,92 Z" fill={copper} opacity="0.85" />

          {/* Bottom-Left Wing */}
          <path d="M 88,106 C 78,120 60,144 26,178 C 48,168 72,150 100,118 Z" fill={isMono ? copper : indigo} />
          <path d="M 88,108 C 72,126 54,146 38,166 C 58,155 80,138 100,115 Z" fill={copper} opacity="0.85" />

          {/* Top-Right Wing */}
          <path d="M 100,82 C 128,50 152,32 174,22 C 140,56 122,80 112,94 Z" fill={copper} />
          <path d="M 100,85 C 120,62 142,45 162,34 C 146,54 128,74 112,92 Z" fill={isMono ? copper : indigo} opacity="0.85" />

          {/* Bottom-Right Wing */}
          <path d="M 112,106 C 122,120 140,144 174,178 C 152,168 128,150 100,118 Z" fill={copper} />
          <path d="M 112,108 C 128,126 146,146 162,166 C 142,155 120,138 100,115 Z" fill={isMono ? copper : indigo} opacity="0.85" />

          {/* Center Bindu Diamond */}
          <polygon points="100,86 114,100 100,114 86,100" fill={copper} />
          <polygon points="100,92 108,100 100,108 92,100" fill={isDark ? '#1C1917' : '#FDF7EC'} />
        </g>
      </svg>

      {caption && (
        <span className="mt-1 text-[8.5px] font-mono tracking-[0.14em] uppercase text-agni-copper/90 font-semibold">
          {caption}
        </span>
      )}
      {provenanceId && (
        <span className="text-[7px] font-mono tracking-widest text-agni-inkMuted/70">
          ID: {provenanceId}
        </span>
      )}
    </div>
  );
};
