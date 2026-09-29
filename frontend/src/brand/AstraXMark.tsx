import React from 'react';
import { ASTRA_PALETTE } from './astraProducts';

export type AstraXMarkVariant =
  | 'primary'
  | 'dark'
  | 'monochrome'
  | 'sandstone'
  | 'inverted'
  | 'indigo'
  | 'light'
  | 'transparent';

export interface AstraXMarkProps {
  variant?: AstraXMarkVariant;
  size?: number | string;
  className?: string;
  animated?: boolean;
}

/**
 * AstraXMark — Official AstraX Master Symbol Component
 * Directly derived from ASTRAX_PNG_MASTER_SET.
 * 
 * Supports all canonical theme treatments:
 * - primary: Blue (Indigo) + Copper on ivory/light
 * - dark: High-contrast Blue + Copper on dark navy
 * - monochrome: Pure black single-color
 * - sandstone: Brown/copper on sandstone
 * - inverted: Pure white on black
 * - indigo: Single-tone indigo on light
 * - light: Crisp blue + copper for white backgrounds
 * - transparent: Transparent background
 */
export const AstraXMark: React.FC<AstraXMarkProps> = ({
  variant = 'primary',
  size = 40,
  className = '',
  animated = false,
}) => {
  // Determine color assignments based on variant
  let copper: string = ASTRA_PALETTE.copper;
  let indigo: string = ASTRA_PALETTE.indigo;
  let guide: string = ASTRA_PALETTE.copper;
  let hollowHole: string = '#FDF7EC';

  switch (variant) {
    case 'dark':
      copper = '#D48946';
      indigo = '#60A5FA';
      guide = '#D48946';
      hollowHole = '#111827';
      break;
    case 'monochrome':
      copper = '#000000';
      indigo = '#000000';
      guide = '#000000';
      hollowHole = '#FFFFFF';
      break;
    case 'sandstone':
      copper = '#8B4513';
      indigo = '#6E3A1E';
      guide = '#8B4513';
      hollowHole = '#EADCC8';
      break;
    case 'inverted':
      copper = '#FFFFFF';
      indigo = '#FFFFFF';
      guide = '#FFFFFF';
      hollowHole = '#000000';
      break;
    case 'indigo':
      copper = ASTRA_PALETTE.indigo;
      indigo = ASTRA_PALETTE.indigo;
      guide = ASTRA_PALETTE.indigo;
      hollowHole = '#FFFFFF';
      break;
    case 'light':
    case 'transparent':
    case 'primary':
    default:
      copper = ASTRA_PALETTE.copper;
      indigo = ASTRA_PALETTE.indigo;
      guide = ASTRA_PALETTE.copper;
      hollowHole = '#FDF7EC';
      break;
  }

  const isMono = variant === 'monochrome' || variant === 'inverted' || variant === 'indigo';

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 200"
      width={size}
      height={size}
      className={`inline-block flex-shrink-0 select-none ${animated ? 'hover:scale-105 transition-transform duration-300' : ''} ${className}`}
      aria-label="AstraX Symbol"
      role="img"
    >
      <defs>
        <linearGradient id={`astraxCopper-${variant}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={copper} />
          <stop offset="100%" stopColor={variant === 'dark' ? '#B87333' : '#8A5222'} />
        </linearGradient>
        <linearGradient id={`astraxIndigo-${variant}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={indigo} />
          <stop offset="100%" stopColor={variant === 'dark' ? '#1E3A8A' : '#172554'} />
        </linearGradient>
      </defs>

      <g id={`astrax-mark-${variant}`}>
        {/* Guide Circle (r = 75px, dashed 1px) */}
        <circle
          cx="100"
          cy="100"
          r="75"
          fill="none"
          stroke={guide}
          strokeWidth="0.75"
          strokeDasharray="3 3"
          opacity={isMono ? 0.35 : 0.55}
        />

        {/* Cardinal Axis Lines */}
        <line
          x1="100"
          y1="12"
          x2="100"
          y2="188"
          stroke={guide}
          strokeWidth="0.8"
          opacity={isMono ? 0.4 : 0.65}
        />
        <line
          x1="12"
          y1="100"
          x2="188"
          y2="100"
          stroke={guide}
          strokeWidth="0.8"
          opacity={isMono ? 0.4 : 0.65}
        />

        {/* Diagonal Cross Rays to guide circle */}
        <line
          x1="38"
          y1="38"
          x2="162"
          y2="162"
          stroke={guide}
          strokeWidth="0.5"
          opacity={isMono ? 0.25 : 0.4}
        />
        <line
          x1="162"
          y1="38"
          x2="38"
          y2="162"
          stroke={guide}
          strokeWidth="0.5"
          opacity={isMono ? 0.25 : 0.4}
        />

        {/* Diamond Telemetry Nodes on Cardinal Axes */}
        {/* Top vertical nodes */}
        <polygon points="100,12 105,17 100,22 95,17" fill={copper} />
        <polygon points="100,42 103,45 100,48 97,45" fill={copper} />
        <polygon points="100,68 103,71 100,74 97,71" fill={copper} />

        {/* Bottom vertical nodes */}
        <polygon points="100,178 105,183 100,188 95,183" fill={copper} />
        <polygon points="100,152 103,155 100,158 97,155" fill={copper} />
        <polygon points="100,126 103,129 100,132 97,129" fill={copper} />

        {/* Left horizontal nodes */}
        <polygon points="12,100 17,95 22,100 17,105" fill={copper} />
        <polygon points="45,100 48,97 51,100 48,103" fill={copper} />

        {/* Right horizontal nodes */}
        <polygon points="178,100 183,95 188,100 183,105" fill={copper} />
        <polygon points="149,100 152,97 155,100 152,103" fill={copper} />

        {/* Diagonal Guide Circle Intersection Nodes */}
        <polygon points="47,43 51,47 47,51 43,47" fill="none" stroke={copper} strokeWidth="1" />
        <polygon points="153,43 157,47 153,51 149,47" fill="none" stroke={copper} strokeWidth="1" />
        <polygon points="47,149 51,153 47,157 43,153" fill="none" stroke={copper} strokeWidth="1" />
        <polygon points="153,149 157,153 153,157 149,153" fill="none" stroke={copper} strokeWidth="1" />

        {/* 4 Primary Curved Aerodynamic Strokes */}
        {/* Top-Left Wing */}
        <path
          d="M 100,82 C 72,50 48,32 26,22 C 60,56 78,80 88,94 Z"
          fill={indigo}
        />
        {!isMono && (
          <path
            d="M 100,85 C 80,62 58,45 38,34 C 54,54 72,74 88,92 Z"
            fill={copper}
            opacity="0.9"
          />
        )}

        {/* Bottom-Left Wing */}
        <path
          d="M 88,106 C 78,120 60,144 26,178 C 48,168 72,150 100,118 Z"
          fill={indigo}
        />
        {!isMono && (
          <path
            d="M 88,108 C 72,126 54,146 38,166 C 58,155 80,138 100,115 Z"
            fill={copper}
            opacity="0.9"
          />
        )}

        {/* Top-Right Wing */}
        <path
          d="M 100,82 C 128,50 152,32 174,22 C 140,56 122,80 112,94 Z"
          fill={copper}
        />
        {!isMono && (
          <path
            d="M 100,85 C 120,62 142,45 162,34 C 146,54 128,74 112,92 Z"
            fill={indigo}
            opacity="0.9"
          />
        )}

        {/* Bottom-Right Wing */}
        <path
          d="M 112,106 C 122,120 140,144 174,178 C 152,168 128,150 100,118 Z"
          fill={copper}
        />
        {!isMono && (
          <path
            d="M 112,108 C 128,126 146,146 162,166 C 142,155 120,138 100,115 Z"
            fill={indigo}
            opacity="0.9"
          />
        )}

        {/* Central Core Bindu Diamond (18x18px) */}
        <polygon
          points="100,86 114,100 100,114 86,100"
          fill={copper}
        />
        {/* Hollow Diamond Cutout */}
        <polygon
          points="100,92 108,100 100,108 92,100"
          fill={hollowHole}
        />
      </g>
    </svg>
  );
};
