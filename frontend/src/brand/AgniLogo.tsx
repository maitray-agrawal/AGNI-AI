import React from 'react';
import { ASTRA_PALETTE } from './astraProducts';

export interface AgniLogoProps {
  variant?: 'full' | 'mark' | 'monochrome' | 'icon';
  theme?: 'primary' | 'monochrome' | 'light' | 'dark' | 'sandstone';
  size?: number | string;
  className?: string;
  showAstraAttribution?: boolean;
  orientation?: 'horizontal' | 'vertical';
}

/**
 * AgniLogo — Canonical Product Logo Component
 * Derived directly from the official AstraX visual identity board.
 * Mathematical triangular converging geometry:
 * - Central Bindu / diamond core
 * - Faceted inner sails & sweeping outrigger wings
 * - Vertical spire & apex diamond nodes
 * - Coordinate wireframe guide lines & satellite telemetry nodes
 * Pure vector SVG with no raster assets, no flames, no arbitrary curves.
 */
export const AgniLogo: React.FC<AgniLogoProps> = ({
  variant = 'full',
  theme = 'primary',
  size = variant === 'full' ? 42 : 36,
  className = '',
  showAstraAttribution = true,
  orientation = 'horizontal',
}) => {
  // Color resolution based on theme
  const isMono = variant === 'monochrome' || theme === 'monochrome';
  const isDark = theme === 'dark';

  const copper = isMono ? 'currentColor' : isDark ? '#D48946' : ASTRA_PALETTE.copper;
  const copperLight = isMono ? 'currentColor' : isDark ? '#E59A5A' : '#D97706';
  const vermilion = isMono ? 'currentColor' : isDark ? '#F87171' : ASTRA_PALETTE.vermilion;
  const rust = isMono ? 'currentColor' : isDark ? '#DC2626' : ASTRA_PALETTE.vermilionRust;
  const guideColor = isMono ? 'currentColor' : isDark ? '#F87171' : ASTRA_PALETTE.vermilion;
  const textColor = isMono ? 'currentColor' : isDark ? '#FDF7EC' : ASTRA_PALETTE.ink;
  const subtextColor = isMono ? 'currentColor' : isDark ? '#D8CEB8' : '#6B7280';

  // Streamlined Icon Variant (optimized for 16px - 32px)
  if (variant === 'icon') {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 85"
        width={size}
        height={typeof size === 'number' ? (size * 85) / 100 : size}
        className={`inline-block flex-shrink-0 select-none ${className}`}
        aria-label="AGNI Icon"
        role="img"
      >
        <g id="agni-icon-mark">
          {/* Top Apex Diamond */}
          <polygon points="50,4 53.5,8 50,12 46.5,8" fill={vermilion} />
          {/* Spire */}
          <line x1="50" y1="12" x2="50" y2="48" stroke={copper} strokeWidth="2.2" strokeLinecap="round" />
          {/* Left Wing Sail */}
          <polygon points="47,20 34,42 47,48" fill={copper} />
          {/* Right Wing Sail */}
          <polygon points="53,20 66,42 53,48" fill={vermilion} />
          {/* Center Bindu */}
          <polygon points="50,44 42,54 50,66 58,54" fill={isMono ? 'currentColor' : copper} />
          {/* Swept Outrigger Wings */}
          <polygon points="46,53 14,70 44,61" fill={copper} />
          <polygon points="54,53 86,70 56,61" fill={vermilion} />
          {/* Flank Nodes */}
          <polygon points="12,60 14.5,63 12,66 9.5,63" fill={vermilion} />
          <polygon points="88,60 90.5,63 88,66 85.5,63" fill={vermilion} />
        </g>
      </svg>
    );
  }

  // Canonical Master Mark Vector (220 x 160 coordinate space)
  const markSvg = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 220 160"
      width={size}
      height={typeof size === 'number' ? (size * 160) / 220 : size}
      className={`inline-block flex-shrink-0 select-none transition-transform duration-200 ${className}`}
      aria-label="AGNI Brand Mark"
      role="img"
    >
      <defs>
        <linearGradient id="agniCopperGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={copperLight} />
          <stop offset="100%" stopColor={copper} />
        </linearGradient>
        <linearGradient id="agniRustGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={vermilion} />
          <stop offset="100%" stopColor={rust} />
        </linearGradient>
      </defs>

      <g id="agni-canonical-mark">
        {/* Coordinate Wireframe Guide Lines (Mathematical Grammar) */}
        <line
          x1="110"
          y1="48"
          x2="33"
          y2="128"
          stroke={guideColor}
          strokeWidth="0.8"
          opacity={isMono ? 0.7 : 0.85}
        />
        <line
          x1="110"
          y1="48"
          x2="187"
          y2="128"
          stroke={guideColor}
          strokeWidth="0.8"
          opacity={isMono ? 0.7 : 0.85}
        />
        <line
          x1="110"
          y1="48"
          x2="89"
          y2="102"
          stroke={copper}
          strokeWidth="0.6"
          opacity={isMono ? 0.5 : 0.65}
        />
        <line
          x1="110"
          y1="48"
          x2="131"
          y2="102"
          stroke={copper}
          strokeWidth="0.6"
          opacity={isMono ? 0.5 : 0.65}
        />
        <line
          x1="33"
          y1="128"
          x2="35"
          y2="146"
          stroke={guideColor}
          strokeWidth="0.7"
          opacity={isMono ? 0.6 : 0.75}
        />
        <line
          x1="187"
          y1="128"
          x2="185"
          y2="146"
          stroke={guideColor}
          strokeWidth="0.7"
          opacity={isMono ? 0.6 : 0.75}
        />
        <line
          x1="33"
          y1="128"
          x2="65"
          y2="129"
          stroke={guideColor}
          strokeWidth="0.5"
          opacity={isMono ? 0.4 : 0.6}
        />
        <line
          x1="187"
          y1="128"
          x2="155"
          y2="129"
          stroke={guideColor}
          strokeWidth="0.5"
          opacity={isMono ? 0.4 : 0.6}
        />

        {/* Outer Flank Satellite Diamonds */}
        <polygon
          points="33,124 37,128 33,132 29,128"
          fill={vermilion}
        />
        <polygon
          points="187,124 191,128 187,132 183,128"
          fill={vermilion}
        />

        {/* Apex Vertical Axis Structures */}
        {/* Top Diamond Node */}
        <polygon
          points="110,13.5 114,17.5 110,21.5 106,17.5"
          fill={vermilion}
        />
        {/* Connector */}
        <line
          x1="110"
          y1="21.5"
          x2="110"
          y2="26"
          stroke={vermilion}
          strokeWidth="1"
        />

        {/* Hollow Diamond Node */}
        <polygon
          points="110,26 115.5,31.5 110,37 104.5,31.5"
          fill="none"
          stroke={vermilion}
          strokeWidth="1.2"
        />
        <polygon
          points="110,28.5 113,31.5 110,34.5 107,31.5"
          fill={vermilion}
        />

        {/* Connector to Mid-junction */}
        <line
          x1="110"
          y1="37"
          x2="110"
          y2="43"
          stroke={vermilion}
          strokeWidth="1"
        />

        {/* Mid-Junction Diamond */}
        <polygon
          points="110,43 115,48 110,53 105,48"
          fill={vermilion}
        />

        {/* Central Spire Needle (tapers downward to Bindu) */}
        <polygon
          points="109,53 111,53 110.6,104 109.4,104"
          fill={copper}
        />

        {/* Left Inner Sail (Two-tone Facet) */}
        {/* Upper Facet */}
        <polygon
          points="107,70 89,102 107,88"
          fill={isMono ? 'currentColor' : copperLight}
        />
        {/* Lower Facet */}
        <polygon
          points="89,102 107,88 107,106 65,129"
          fill={isMono ? 'currentColor' : rust}
        />

        {/* Right Inner Sail (Symmetrical Two-tone Facet) */}
        {/* Upper Facet */}
        <polygon
          points="113,70 131,102 113,88"
          fill={isMono ? 'currentColor' : vermilion}
        />
        {/* Lower Facet */}
        <polygon
          points="131,102 113,88 113,106 155,129"
          fill={isMono ? 'currentColor' : copper}
        />

        {/* Central Bindu Diamond (Core intelligence anchor) */}
        <polygon
          points="110,106 97,124 110,142 110,146"
          fill={isMono ? 'currentColor' : rust}
        />
        <polygon
          points="110,106 123,124 110,142 110,146"
          fill={isMono ? 'currentColor' : copper}
        />

        {/* Left Swept Outrigger Wing (Faceted) */}
        <polygon
          points="96,126 35,146 98,131"
          fill={isMono ? 'currentColor' : copper}
        />
        <polygon
          points="98,131 35,146 106,134"
          fill={isMono ? 'currentColor' : rust}
        />

        {/* Right Swept Outrigger Wing (Faceted) */}
        <polygon
          points="124,126 185,146 122,131"
          fill={isMono ? 'currentColor' : vermilion}
        />
        <polygon
          points="122,131 185,146 114,134"
          fill={isMono ? 'currentColor' : copper}
        />
      </g>
    </svg>
  );

  // Mark-only variant
  if (variant === 'mark' || variant === 'monochrome') {
    return markSvg;
  }

  // Full Lockup Variant: Mark + AGNI typography + Descriptor + Attribution
  if (orientation === 'vertical') {
    return (
      <div className={`flex flex-col items-center text-center ${className}`}>
        <div className="mb-2">{markSvg}</div>
        <div className="tracking-[0.2em] font-serif text-2xl font-bold uppercase leading-none" style={{ color: textColor }}>
          AGNI
        </div>
        <div className="mt-1 text-[9px] font-mono tracking-[0.22em] uppercase font-medium" style={{ color: subtextColor }}>
          RESEARCH INTELLIGENCE
        </div>
        {showAstraAttribution && (
          <div className="mt-2 text-[8px] font-mono tracking-[0.16em] uppercase opacity-75 border-t border-agni-copper/25 pt-1.5" style={{ color: subtextColor }}>
            AN ASTRA X INTELLIGENCE SYSTEM
          </div>
        )}
      </div>
    );
  }

  // Horizontal Lockup Variant
  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>
      {markSvg}
      <div className="flex flex-col justify-center leading-none">
        <div className="flex items-baseline gap-2">
          <span
            className="text-xl md:text-2xl font-serif font-bold tracking-[0.12em] uppercase"
            style={{ color: textColor }}
          >
            AGNI
          </span>
          <span
            className="hidden sm:inline-block text-[9px] font-mono tracking-[0.18em] uppercase font-semibold px-1.5 py-0.5 rounded border border-agni-copper/30 bg-agni-copper/10"
            style={{ color: isDark ? '#E59A5A' : ASTRA_PALETTE.copper }}
          >
            RESEARCH
          </span>
        </div>
        <div
          className="text-[9px] font-mono tracking-[0.2em] uppercase mt-1 font-medium"
          style={{ color: subtextColor }}
        >
          RESEARCH INTELLIGENCE
        </div>
        {showAstraAttribution && (
          <div
            className="text-[7.5px] font-mono tracking-[0.14em] uppercase opacity-70 mt-0.5"
            style={{ color: subtextColor }}
          >
            AN ASTRA X INTELLIGENCE SYSTEM
          </div>
        )}
      </div>
    </div>
  );
};
