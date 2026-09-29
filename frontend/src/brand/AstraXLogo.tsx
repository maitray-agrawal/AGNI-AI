import React from 'react';
import { AstraXMark, AstraXMarkVariant } from './AstraXMark';
import { ASTRA_PALETTE } from './astraProducts';

export type AstraXLogoVariant =
  | 'primary'
  | 'dark'
  | 'monochrome'
  | 'sandstone'
  | 'transparent'
  | 'light'
  | 'inverted'
  | 'indigo'
  | 'icon'
  | 'mark';

export interface AstraXLogoProps {
  variant?: AstraXLogoVariant;
  size?: number | string;
  className?: string;
  showTagline?: boolean;
  withCardBackground?: boolean;
  layout?: 'horizontal' | 'vertical';
}

/**
 * AstraXLogo — Official Master Brand Component
 * Implements the 9 approved canonical variants from ASTRAX_PNG_MASTER_SET:
 * 1. PRIMARY: Ivory/light background, Blue + Copper symbol, ASTRAX wordmark
 * 2. DARK: Dark navy background (#0B132B), Blue + Copper symbol, light text
 * 3. MONOCHROME: Black single-color symbol and typography
 * 4. SANDSTONE: Sandstone background (#EADCC8), brown/copper treatment
 * 5. TRANSPARENT: Pure transparent background, primary symbol
 * 6. LIGHT: White background (#FFFFFF), crisp line treatment
 * 7. INVERTED: Black background (#000000), white symbol and typography
 * 8. INDIGO: Single color indigo (#1E3A8A) symbol and typography
 * 9. ICON: Symbol-only app mark suitable for favicon, cards, mobile app icon
 */
export const AstraXLogo: React.FC<AstraXLogoProps> = ({
  variant = 'primary',
  size = variant === 'icon' || variant === 'mark' ? 40 : 48,
  className = '',
  showTagline = true,
  withCardBackground = false,
  layout = 'horizontal',
}) => {
  // Map variant to AstraXMarkVariant
  const markVariant: AstraXMarkVariant =
    variant === 'icon' || variant === 'mark' ? 'primary' : (variant as AstraXMarkVariant);

  // Colors for wordmark & background based on variant
  let astraColor: string = ASTRA_PALETTE.indigo;
  let xColor: string = ASTRA_PALETTE.copper;
  let tagColor: string = '#6B7280';
  let cardBg: string = 'transparent';
  let cardBorder: string = 'transparent';

  switch (variant) {
    case 'dark':
      astraColor = '#FDF7EC';
      xColor = '#D48946';
      tagColor = '#9CA3AF';
      cardBg = '#0B132B';
      cardBorder = 'rgba(212, 137, 70, 0.2)';
      break;
    case 'monochrome':
      astraColor = '#000000';
      xColor = '#000000';
      tagColor = '#4B5563';
      cardBg = '#FFFFFF';
      cardBorder = '#E5E7EB';
      break;
    case 'sandstone':
      astraColor = '#3D2414';
      xColor = '#8B4513';
      tagColor = '#6E482F';
      cardBg = '#EADCC8';
      cardBorder = '#D4CABA';
      break;
    case 'inverted':
      astraColor = '#FFFFFF';
      xColor = '#FFFFFF';
      tagColor = '#D1D5DB';
      cardBg = '#000000';
      cardBorder = '#333333';
      break;
    case 'indigo':
      astraColor = ASTRA_PALETTE.indigo;
      xColor = ASTRA_PALETTE.indigo;
      tagColor = '#3B82F6';
      cardBg = '#F8FAFC';
      cardBorder = '#E2E8F0';
      break;
    case 'light':
      astraColor = ASTRA_PALETTE.ink;
      xColor = ASTRA_PALETTE.copper;
      tagColor = '#6B7280';
      cardBg = '#FFFFFF';
      cardBorder = '#F3F4F6';
      break;
    case 'transparent':
    case 'primary':
    default:
      astraColor = ASTRA_PALETTE.ink;
      xColor = ASTRA_PALETTE.copper;
      tagColor = '#6B7280';
      cardBg = variant === 'primary' && withCardBackground ? '#FDF7EC' : 'transparent';
      cardBorder = variant === 'primary' && withCardBackground ? '#EADCC8' : 'transparent';
      break;
  }

  // Mark-only Variant
  if (variant === 'mark') {
    return <AstraXMark variant={markVariant} size={size} className={className} />;
  }

  // Icon Variant (Symbol Only, with optional App Icon squircle container)
  if (variant === 'icon') {
    if (withCardBackground) {
      return (
        <div
          className={`inline-flex items-center justify-center rounded-2xl p-2 select-none shadow-sm ${className}`}
          style={{ background: cardBg, border: `1px solid ${cardBorder}` }}
        >
          <AstraXMark variant={markVariant} size={size} />
        </div>
      );
    }
    return <AstraXMark variant={markVariant} size={size} className={className} />;
  }

  // Vertical layout lockup
  if (layout === 'vertical') {
    return (
      <div
        className={`flex flex-col items-center text-center p-4 rounded-xl select-none ${className}`}
        style={withCardBackground ? { background: cardBg, border: `1px solid ${cardBorder}` } : {}}
      >
        <AstraXMark variant={markVariant} size={size} />
        <div className="mt-3 flex items-baseline font-serif tracking-[0.28em] uppercase text-2xl font-bold leading-none">
          <span style={{ color: astraColor }}>ASTRA</span>
          <span className="ml-1.5" style={{ color: xColor }}>X</span>
        </div>
        {showTagline && (
          <div
            className="mt-1.5 text-[8px] font-mono tracking-[0.18em] uppercase max-w-[28ch] font-medium"
            style={{ color: tagColor }}
          >
            INTELLIGENCE, BUILT ON INDIAN MATHEMATICAL GRAMMAR
          </div>
        )}
      </div>
    );
  }

  // Horizontal layout lockup (Standard)
  return (
    <div
      className={`inline-flex items-center gap-3.5 p-2 rounded-xl select-none ${className}`}
      style={withCardBackground ? { background: cardBg, border: `1px solid ${cardBorder}` } : {}}
    >
      <AstraXMark variant={markVariant} size={size} />
      <div className="flex flex-col justify-center leading-none">
        <div className="flex items-baseline font-serif tracking-[0.24em] uppercase text-xl font-bold">
          <span style={{ color: astraColor }}>ASTRA</span>
          <span className="ml-1" style={{ color: xColor }}>
            X
          </span>
        </div>
        {showTagline && (
          <div
            className="text-[7.5px] font-mono tracking-[0.16em] uppercase mt-1 opacity-80"
            style={{ color: tagColor }}
          >
            INTELLIGENCE, BUILT ON INDIAN MATHEMATICAL GRAMMAR
          </div>
        )}
      </div>
    </div>
  );
};
