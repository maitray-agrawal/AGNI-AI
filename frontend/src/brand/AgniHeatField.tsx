import React from 'react';
import { ASTRA_PALETTE } from './astraProducts';

export interface AgniHeatFieldProps {
  className?: string;
  intensity?: 'subtle' | 'moderate' | 'prominent';
  interactive?: boolean;
}

/**
 * AgniHeatField — AGNI Domain Visual Motif
 * Conceptualizes Research -> Propagation -> Transformation:
 * - Radial concentric propagation rings
 * - Connected nodes along mathematical ray axes
 * - Signal intensity gradients & Bindu convergence
 * - Strictly NO literal flames
 */
export const AgniHeatField: React.FC<AgniHeatFieldProps> = ({
  className = '',
  intensity = 'subtle',
}) => {
  const opacity = intensity === 'subtle' ? 0.05 : intensity === 'moderate' ? 0.09 : 0.15;

  return (
    <div
      className={`pointer-events-none absolute inset-0 overflow-hidden select-none ${className}`}
      style={{ opacity }}
      aria-hidden="true"
    >
      <svg
        className="w-full h-full"
        viewBox="0 0 1000 600"
        preserveAspectRatio="xMidYMid slice"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <radialGradient id="agniHeatCore" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={ASTRA_PALETTE.vermilion} stopOpacity="0.8" />
            <stop offset="40%" stopColor={ASTRA_PALETTE.copper} stopOpacity="0.4" />
            <stop offset="100%" stopColor={ASTRA_PALETTE.copper} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Concentric Propagation Wavefronts */}
        <g stroke={ASTRA_PALETTE.copper} fill="none" strokeWidth="1">
          <circle cx="500" cy="300" r="60" strokeDasharray="3 3" opacity="0.6" />
          <circle cx="500" cy="300" r="130" opacity="0.45" />
          <circle cx="500" cy="300" r="210" strokeDasharray="5 5" opacity="0.35" />
          <circle cx="500" cy="300" r="300" opacity="0.25" />
          <circle cx="500" cy="300" r="410" strokeDasharray="4 6" opacity="0.18" />
          <circle cx="500" cy="300" r="520" opacity="0.1" />
        </g>

        {/* Radial Axis Rays (Navadisha / Mathematical Angles) */}
        <g stroke={ASTRA_PALETTE.vermilion} strokeWidth="0.8" opacity="0.35">
          <line x1="500" y1="300" x2="500" y2="40" />
          <line x1="500" y1="300" x2="500" y2="560" />
          <line x1="500" y1="300" x2="180" y2="300" />
          <line x1="500" y1="300" x2="820" y2="300" />
          <line x1="500" y1="300" x2="260" y2="120" strokeDasharray="2 4" />
          <line x1="500" y1="300" x2="740" y2="120" strokeDasharray="2 4" />
          <line x1="500" y1="300" x2="260" y2="480" strokeDasharray="2 4" />
          <line x1="500" y1="300" x2="740" y2="480" strokeDasharray="2 4" />
        </g>

        {/* Bindu Nodes along wavefront intersections */}
        <g fill={ASTRA_PALETTE.vermilion}>
          <polygon points="500,165 504,170 500,175 496,170" />
          <polygon points="500,425 504,430 500,435 496,430" />
          <polygon points="365,300 370,296 375,300 370,304" />
          <polygon points="625,300 630,296 635,300 630,304" />

          <polygon points="350,185 354,190 350,195 346,190" fill={ASTRA_PALETTE.copper} />
          <polygon points="650,185 654,190 650,195 646,190" fill={ASTRA_PALETTE.copper} />
          <polygon points="350,415 354,420 350,425 346,420" fill={ASTRA_PALETTE.copper} />
          <polygon points="650,415 654,420 650,425 646,420" fill={ASTRA_PALETTE.copper} />

          {/* Central Bindu */}
          <polygon points="500,292 508,300 500,308 492,300" fill={ASTRA_PALETTE.vermilion} />
        </g>
      </svg>
    </div>
  );
};
