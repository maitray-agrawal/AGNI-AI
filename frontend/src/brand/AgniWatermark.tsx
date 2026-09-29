import React from 'react';
import { AgniLogo } from './AgniLogo';

export interface AgniWatermarkProps {
  size?: number | string;
  opacity?: number;
  className?: string;
}

/**
 * AgniWatermark — AGNI Product Geometric Watermark
 * Scaled vector watermark derived from the canonical AGNI mark.
 * Used at 2-4% opacity in hero, reports, and analytical panels.
 */
export const AgniWatermark: React.FC<AgniWatermarkProps> = ({
  size = 380,
  opacity = 0.035,
  className = '',
}) => {
  return (
    <div
      className={`pointer-events-none absolute select-none flex items-center justify-center ${className}`}
      style={{ opacity }}
      aria-hidden="true"
    >
      <AgniLogo variant="mark" theme="monochrome" size={size} />
    </div>
  );
};
