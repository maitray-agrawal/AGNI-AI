import React from 'react';
import { ASTRA_PALETTE } from './astraProducts';

export interface AgniLoadingMarkProps {
  size?: number;
  className?: string;
  label?: string;
}

/**
 * AgniLoadingMark — Institutional Intelligence Processing Indicator
 * Elegant mathematical progression:
 * signal -> bindu -> convergence -> propagation
 * No particle explosions, no flashy spinning fire.
 */
export const AgniLoadingMark: React.FC<AgniLoadingMarkProps> = ({
  size = 54,
  className = '',
  label = 'SYNTHESIZING INTELLIGENCE...',
}) => {
  return (
    <div className={`inline-flex flex-col items-center justify-center select-none ${className}`}>
      <div className="relative" style={{ width: size, height: (size * 85) / 100 }}>
        {/* Pulsing Bindu background wavefront */}
        <div
          className="absolute inset-0 rounded-full animate-ping opacity-20 pointer-events-none"
          style={{ backgroundColor: ASTRA_PALETTE.vermilion }}
        />

        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 100 85"
          width={size}
          height={(size * 85) / 100}
          className="relative z-10 transition-transform duration-700 animate-pulse"
          aria-label="Processing"
          role="status"
        >
          {/* Top Apex Node */}
          <polygon points="50,4 53.5,8 50,12 46.5,8" fill={ASTRA_PALETTE.vermilion} />

          {/* Central Spire */}
          <line
            x1="50"
            y1="12"
            x2="50"
            y2="46"
            stroke={ASTRA_PALETTE.copper}
            strokeWidth="1.8"
            strokeDasharray="2 2"
          />

          {/* Converging Inner Sails */}
          <polygon
            points="47,20 34,42 47,48"
            fill={ASTRA_PALETTE.copper}
            className="transition-opacity duration-500"
          />
          <polygon
            points="53,20 66,42 53,48"
            fill={ASTRA_PALETTE.vermilion}
            className="transition-opacity duration-500"
          />

          {/* Central Bindu Core (Active decision node) */}
          <polygon
            points="50,44 42,54 50,66 58,54"
            fill={ASTRA_PALETTE.copper}
            stroke={ASTRA_PALETTE.vermilion}
            strokeWidth="0.8"
          />

          {/* Swept Outrigger Wings */}
          <polygon points="46,53 14,70 44,61" fill={ASTRA_PALETTE.copper} />
          <polygon points="54,53 86,70 56,61" fill={ASTRA_PALETTE.vermilion} />

          {/* Flank Satellite Telemetry Nodes */}
          <polygon points="12,60 14.5,63 12,66 9.5,63" fill={ASTRA_PALETTE.vermilion} />
          <polygon points="88,60 90.5,63 88,66 85.5,63" fill={ASTRA_PALETTE.vermilion} />
        </svg>
      </div>

      {label && (
        <span className="mt-2.5 text-[9px] font-mono tracking-[0.2em] uppercase text-agni-copper font-medium animate-pulse">
          {label}
        </span>
      )}
    </div>
  );
};
