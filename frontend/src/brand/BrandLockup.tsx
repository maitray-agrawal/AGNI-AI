import React from 'react';
import { ProjectMark, AstraProjectId } from './ProjectMark';
import { AstraXMark } from './AstraXMark';
import { astraProducts, ASTRA_PALETTE } from './astraProducts';

export interface BrandLockupProps {
  project?: AstraProjectId;
  layout?: 'horizontal' | 'vertical' | 'compact';
  theme?: 'primary' | 'monochrome' | 'dark' | 'sandstone';
  useAstraMasterMark?: boolean;
  size?: number | string;
  className?: string;
  showTagline?: boolean;
}

/**
 * BrandLockup — Reusable Master Brand + Project Lockup Component
 * Implements Section 14 of the AstraX brand architecture:
 * Supports:
 * - horizontal: [Mark] PROJECT NAME / DESCRIPTOR / ATTRIBUTION
 * - vertical: Centered [Mark] / PROJECT NAME / DESCRIPTOR / ATTRIBUTION
 * - compact: Inline [Mark] PROJECT NAME / DESCRIPTOR
 */
export const BrandLockup: React.FC<BrandLockupProps> = ({
  project = 'agni',
  layout = 'horizontal',
  theme = 'primary',
  useAstraMasterMark = false,
  size = layout === 'compact' ? 24 : 36,
  className = '',
  showTagline = true,
}) => {
  const prod = astraProducts[project] || astraProducts['agni'];
  const isMono = theme === 'monochrome';
  const isDark = theme === 'dark';

  const textColor = isMono ? 'currentColor' : isDark ? '#FDF7EC' : ASTRA_PALETTE.ink;
  const subtextColor = isMono ? 'currentColor' : isDark ? '#D8CEB8' : '#6B7280';
  const accentColor = isMono ? 'currentColor' : isDark ? '#D48946' : prod.accentHex;

  const markElement = useAstraMasterMark ? (
    <AstraXMark
      variant={theme === 'dark' ? 'dark' : theme === 'sandstone' ? 'sandstone' : isMono ? 'monochrome' : 'primary'}
      size={size}
    />
  ) : (
    <ProjectMark project={project} size={size} theme={theme} />
  );

  // Compact Layout (Header / Mobile / Table Cells)
  if (layout === 'compact') {
    return (
      <div className={`inline-flex items-center gap-2 select-none ${className}`}>
        {markElement}
        <div className="flex flex-col leading-none">
          <span
            className="font-serif font-bold text-base tracking-[0.14em] uppercase"
            style={{ color: textColor }}
          >
            {prod.name}
          </span>
          <span
            className="text-[7.5px] font-mono tracking-[0.18em] uppercase font-semibold mt-0.5"
            style={{ color: subtextColor }}
          >
            {prod.descriptor}
          </span>
        </div>
      </div>
    );
  }

  // Vertical Layout (Sidebar Header / Splash / Reports)
  if (layout === 'vertical') {
    return (
      <div className={`flex flex-col items-center text-center select-none ${className}`}>
        <div className="mb-2.5">{markElement}</div>
        <div
          className="font-serif text-xl font-bold tracking-[0.22em] uppercase leading-none"
          style={{ color: textColor }}
        >
          {prod.name}
        </div>
        <div
          className="mt-1 text-[8.5px] font-mono tracking-[0.24em] uppercase font-semibold"
          style={{ color: subtextColor }}
        >
          {prod.descriptor}
        </div>
        {showTagline && (
          <div
            className="mt-2.5 text-[7px] font-mono tracking-[0.16em] uppercase opacity-70 border-t border-white/10 pt-1.5"
            style={{ color: subtextColor }}
          >
            AN ASTRA X INTELLIGENCE SYSTEM
          </div>
        )}
      </div>
    );
  }

  // Standard Horizontal Layout
  return (
    <div className={`inline-flex items-center gap-3.5 select-none ${className}`}>
      {markElement}
      <div className="flex flex-col justify-center leading-none">
        <div className="flex items-baseline gap-2">
          <span
            className="text-xl md:text-2xl font-serif font-bold tracking-[0.12em] uppercase"
            style={{ color: textColor }}
          >
            {prod.name}
          </span>
          <span
            className="hidden sm:inline-block text-[8px] font-mono tracking-[0.16em] uppercase font-semibold px-1.5 py-0.5 rounded border"
            style={{
              color: accentColor,
              borderColor: `${accentColor}40`,
              backgroundColor: `${accentColor}12`,
            }}
          >
            {prod.descriptor.split(' ')[0]}
          </span>
        </div>
        <div
          className="text-[8.5px] font-mono tracking-[0.2em] uppercase mt-1 font-medium"
          style={{ color: subtextColor }}
        >
          {prod.descriptor}
        </div>
        {showTagline && (
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
