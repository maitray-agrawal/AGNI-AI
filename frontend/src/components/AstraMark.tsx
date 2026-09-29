import React from 'react';

interface AstraMarkProps {
  size?: number;
  className?: string;
  opacity?: number;
  animated?: boolean;
  style?: React.CSSProperties;
}

/**
 * AstraMark — The AstraX geometric identity mark.
 * Continuous line → Bindu → convergence
 * Represents signal → analysis → strategic insight.
 */
export const AstraMark: React.FC<AstraMarkProps> = ({
  size = 32,
  className = '',
  opacity = 1,
  animated = false,
  style,
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      style={{ opacity, ...style }}
      aria-hidden="true"
    >
      {/* Astra Sutra — converging lines */}
      <line x1="2" y1="10" x2="14" y2="16" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.7" />
      <line x1="2" y1="22" x2="14" y2="16" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.7" />
      <line x1="30" y1="10" x2="18" y2="16" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.7" />
      <line x1="30" y1="22" x2="18" y2="16" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.7" />
      {/* Central Bindu — intelligence convergence point */}
      <circle
        cx="16"
        cy="16"
        r="2.5"
        fill="currentColor"
        className={animated ? 'animate-[binduPulse_3s_ease-in-out_infinite]' : ''}
      />
      {/* Secondary ring */}
      <circle cx="16" cy="16" r="5" stroke="currentColor" strokeWidth="0.8" opacity="0.25" />
    </svg>
  );
};

/**
 * AstraSeal — Larger AstraX identity seal for prominent placement.
 */
export const AstraSeal: React.FC<{ size?: number; className?: string }> = ({
  size = 64,
  className = '',
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* Outer ring */}
      <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="0.6" opacity="0.15" />
      {/* Middle ring */}
      <circle cx="32" cy="32" r="20" stroke="currentColor" strokeWidth="0.6" opacity="0.1" />
      {/* Sutra lines */}
      <line x1="4"  y1="20" x2="28" y2="32" stroke="currentColor" strokeWidth="1"   strokeLinecap="round" opacity="0.5" />
      <line x1="4"  y1="44" x2="28" y2="32" stroke="currentColor" strokeWidth="1"   strokeLinecap="round" opacity="0.5" />
      <line x1="60" y1="20" x2="36" y2="32" stroke="currentColor" strokeWidth="1"   strokeLinecap="round" opacity="0.5" />
      <line x1="60" y1="44" x2="36" y2="32" stroke="currentColor" strokeWidth="1"   strokeLinecap="round" opacity="0.5" />
      {/* Vertical axis */}
      <line x1="32" y1="4"  x2="32" y2="28" stroke="currentColor" strokeWidth="0.8" strokeLinecap="round" opacity="0.35" />
      <line x1="32" y1="36" x2="32" y2="60" stroke="currentColor" strokeWidth="0.8" strokeLinecap="round" opacity="0.35" />
      {/* Bindu */}
      <circle cx="32" cy="32" r="5"   fill="currentColor" opacity="0.9" />
      <circle cx="32" cy="32" r="8"   stroke="currentColor" strokeWidth="0.8" opacity="0.3" />
    </svg>
  );
};

/**
 * AgniHeatField — Radial heat-field geometry (AGNI signature motif).
 * Represents signal propagation / geopolitical pressure / systemic risk.
 */
export const AgniHeatField: React.FC<{
  size?: number;
  className?: string;
  intensity?: 'low' | 'medium' | 'high';
}> = ({ size = 280, className = '', intensity = 'medium' }) => {
  const opacities = {
    low:    [0.04, 0.03, 0.02, 0.015, 0.01],
    medium: [0.07, 0.05, 0.035, 0.025, 0.015],
    high:   [0.10, 0.07, 0.05,  0.035, 0.02],
  };
  const ops = opacities[intensity];

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 280 280"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* Concentric rings — heat propagation */}
      <circle cx="140" cy="140" r="130" stroke="currentColor" strokeWidth="0.5" opacity={ops[0]} />
      <circle cx="140" cy="140" r="100" stroke="currentColor" strokeWidth="0.5" opacity={ops[1]} />
      <circle cx="140" cy="140" r="72"  stroke="currentColor" strokeWidth="0.5" opacity={ops[2]} />
      <circle cx="140" cy="140" r="48"  stroke="currentColor" strokeWidth="0.5" opacity={ops[3]} />
      <circle cx="140" cy="140" r="26"  stroke="currentColor" strokeWidth="0.5" opacity={ops[4]} />
      {/* Radial spokes */}
      {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => {
        const rad = (angle * Math.PI) / 180;
        const x1  = 140 + 26  * Math.cos(rad);
        const y1  = 140 + 26  * Math.sin(rad);
        const x2  = 140 + 130 * Math.cos(rad);
        const y2  = 140 + 130 * Math.sin(rad);
        return (
          <line
            key={angle}
            x1={x1} y1={y1} x2={x2} y2={y2}
            stroke="currentColor"
            strokeWidth="0.4"
            opacity={ops[1] * 0.8}
          />
        );
      })}
      {/* Signal nodes */}
      {[
        { cx: 140, cy: 68,  r: 2.5 },
        { cx: 212, cy: 140, r: 2.5 },
        { cx: 140, cy: 212, r: 2.5 },
        { cx: 68,  cy: 140, r: 2.5 },
        { cx: 192, cy: 88,  r: 1.8 },
        { cx: 192, cy: 192, r: 1.8 },
        { cx: 88,  cy: 192, r: 1.8 },
        { cx: 88,  cy: 88,  r: 1.8 },
      ].map((node, i) => (
        <circle key={i} cx={node.cx} cy={node.cy} r={node.r} fill="currentColor" opacity={ops[0] * 1.5} />
      ))}
      {/* Central Bindu */}
      <circle cx="140" cy="140" r="5" fill="currentColor" opacity={ops[2] * 3} />
    </svg>
  );
};

/**
 * AstraWatermark — Very subtle background watermark (2–6% opacity).
 */
export const AstraWatermark: React.FC<{
  size?: number;
  className?: string;
}> = ({ size = 400, className = '' }) => {
  return (
    <div
      className={`astra-watermark ${className}`}
      aria-hidden="true"
    >
      <AgniHeatField size={size} intensity="low" />
    </div>
  );
};
