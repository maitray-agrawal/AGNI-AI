import React from 'react';
import { ProjectMark, AstraProjectId } from './ProjectMark';
import { astraProducts, ASTRA_PALETTE } from './astraProducts';

export interface ProjectLogoProps {
  project?: AstraProjectId;
  variant?: 'full' | 'mark' | 'icon' | 'monochrome';
  theme?: 'primary' | 'monochrome' | 'dark' | 'sandstone';
  size?: number | string;
  className?: string;
  showAstraAttribution?: boolean;
  layout?: 'horizontal' | 'vertical';
}

/**
 * ProjectLogo — Reusable AstraX Intelligence Product Identity
 * Dispatches any of the 7 official products while guaranteeing 70% AstraX DNA / 30% project individuality.
 */
export const ProjectLogo: React.FC<ProjectLogoProps> = ({
  project = 'agni',
  variant = 'full',
  theme = 'primary',
  size = variant === 'full' ? 42 : 36,
  className = '',
  showAstraAttribution = true,
  layout = 'horizontal',
}) => {
  const prod = astraProducts[project] || astraProducts['agni'];
  const isMono = variant === 'monochrome' || theme === 'monochrome';
  const isDark = theme === 'dark';

  const textColor = isMono ? 'currentColor' : isDark ? '#FDF7EC' : ASTRA_PALETTE.ink;
  const subtextColor = isMono ? 'currentColor' : isDark ? '#D8CEB8' : '#6B7280';
  const accentColor = isMono ? 'currentColor' : isDark ? '#D48946' : prod.accentHex;

  // Mark only
  if (variant === 'mark' || variant === 'icon' || variant === 'monochrome') {
    return (
      <ProjectMark
        project={project}
        size={size}
        theme={theme}
        className={className}
      />
    );
  }

  // Vertical layout
  if (layout === 'vertical') {
    return (
      <div className={`flex flex-col items-center text-center select-none ${className}`}>
        <div className="mb-2">
          <ProjectMark project={project} size={size} theme={theme} />
        </div>
        <div
          className="tracking-[0.2em] font-serif text-xl font-bold uppercase leading-none"
          style={{ color: textColor }}
        >
          {prod.name}
        </div>
        <div
          className="mt-1 text-[8.5px] font-mono tracking-[0.22em] uppercase font-semibold"
          style={{ color: subtextColor }}
        >
          {prod.descriptor}
        </div>
        {showAstraAttribution && (
          <div
            className="mt-2 text-[7.5px] font-mono tracking-[0.16em] uppercase opacity-75 border-t border-white/10 pt-1.5"
            style={{ color: subtextColor }}
          >
            AN ASTRA X INTELLIGENCE SYSTEM
          </div>
        )}
      </div>
    );
  }

  // Horizontal layout
  return (
    <div className={`inline-flex items-center gap-3 select-none ${className}`}>
      <ProjectMark project={project} size={size} theme={theme} />
      <div className="flex flex-col justify-center leading-none">
        <div className="flex items-baseline gap-2">
          <span
            className="text-xl md:text-2xl font-serif font-bold tracking-[0.12em] uppercase"
            style={{ color: textColor }}
          >
            {prod.name}
          </span>
          <span
            className="hidden sm:inline-block text-[8px] font-mono tracking-[0.18em] uppercase font-semibold px-1.5 py-0.5 rounded border"
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
