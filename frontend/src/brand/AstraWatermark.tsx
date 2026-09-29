import React from 'react';
import { AstraXMark } from './AstraXMark';

export interface AstraWatermarkProps {
  size?: number | string;
  opacity?: number;
  className?: string;
}

/**
 * AstraWatermark — AstraX Master Brand Geometric Watermark
 * Scaled vector watermark derived from the master AstraX construction geometry.
 * Used at 2-5% opacity across the workspace shell and dossiers.
 */
export const AstraWatermark: React.FC<AstraWatermarkProps> = ({
  size = 460,
  opacity = 0.03,
  className = '',
}) => {
  return (
    <div
      className={`pointer-events-none absolute select-none flex items-center justify-center ${className}`}
      style={{ opacity }}
      aria-hidden="true"
    >
      <AstraXMark variant="monochrome" size={size} />
    </div>
  );
};
