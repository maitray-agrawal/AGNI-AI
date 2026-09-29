/**
 * AstraX & AGNI Centralized Brand Tokens
 * Source of truth for identity palettes, theme variants, typography, and styling dimensions.
 */

export interface BrandColorConfig {
  background: string;
  surface: string;
  surfaceElevated: string;
  surfaceMuted: string;
  border: string;
  borderStrong: string;
  text: string;
  textMuted: string;
  textSubtle: string;
  primaryAccent: string;
  secondaryAccent: string;
  symbolWingsLeft: string;
  symbolWingsRight: string;
  symbolCore: string;
  orbitRing: string;
}

export const ASTRAX_PRIMARY: BrandColorConfig = {
  background: '#FDF7EC', // Warm Ivory
  surface: '#EADCC8',    // Sandstone
  surfaceElevated: '#FFFFFF',
  surfaceMuted: '#F5EFE3',
  border: '#D8CEB8',
  borderStrong: '#C5B79F',
  text: '#221B14',       // Deep Ink
  textMuted: '#5C5449',  // Warm Slate
  textSubtle: '#8C8275',
  primaryAccent: '#B87333', // Copper
  secondaryAccent: '#1E3A8A', // Astra Indigo
  symbolWingsLeft: '#1E3A8A',
  symbolWingsRight: '#B87333',
  symbolCore: '#B87333',
  orbitRing: '#B87333',
};

export const ASTRAX_DARK: BrandColorConfig = {
  background: '#111827', // Deep Navy
  surface: '#1F2937',    // Slate Navy
  surfaceElevated: '#374151',
  surfaceMuted: '#1E293B',
  border: '#374151',
  borderStrong: '#4B5563',
  text: '#F9FAFB',       // Crisp Light
  textMuted: '#9CA3AF',
  textSubtle: '#6B7280',
  primaryAccent: '#E59A5A', // Luminous Copper
  secondaryAccent: '#60A5FA', // Sky Indigo
  symbolWingsLeft: '#93C5FD',
  symbolWingsRight: '#F59E0B',
  symbolCore: '#F59E0B',
  orbitRing: '#D97706',
};

export const ASTRAX_SANDSTONE: BrandColorConfig = {
  background: '#EADCC8',
  surface: '#DFD1BC',
  surfaceElevated: '#F4E8D6',
  surfaceMuted: '#D8C9B3',
  border: '#CBBDA8',
  borderStrong: '#B8A892',
  text: '#221B14',
  textMuted: '#5C5449',
  textSubtle: '#7A7063',
  primaryAccent: '#A35D22',
  secondaryAccent: '#1E3A8A',
  symbolWingsLeft: '#1E3A8A',
  symbolWingsRight: '#A35D22',
  symbolCore: '#A35D22',
  orbitRing: '#A35D22',
};

export const ASTRAX_MONOCHROME: BrandColorConfig = {
  background: '#FFFFFF',
  surface: '#F4F4F5',
  surfaceElevated: '#FFFFFF',
  surfaceMuted: '#E4E4E7',
  border: '#D4D4D8',
  borderStrong: '#A1A1AA',
  text: '#09090B',
  textMuted: '#71717A',
  textSubtle: '#A1A1AA',
  primaryAccent: '#18181B',
  secondaryAccent: '#27272A',
  symbolWingsLeft: '#18181B',
  symbolWingsRight: '#18181B',
  symbolCore: '#18181B',
  orbitRing: '#71717A',
};

// ── AGNI Dedicated Product Color Tokens ─────────────────────────
export interface AgniProductColorConfig {
  spireColor: string;
  innerSailsLeft: string;
  innerSailsRight: string;
  outriggerWings: string;
  apexDiamond: string;
  centralBindu: string;
  guideLines: string;
  satelliteNodes: string;
  wordmarkColor: string;
  descriptorColor: string;
}

export const AGNI_PRIMARY: AgniProductColorConfig = {
  spireColor: '#B87333',
  innerSailsLeft: '#DC2626', // Vermilion
  innerSailsRight: '#991B1B', // Deep Rust
  outriggerWings: '#B87333',
  apexDiamond: '#DC2626',
  centralBindu: '#B87333',
  guideLines: '#B87333',
  satelliteNodes: '#DC2626',
  wordmarkColor: '#221B14',
  descriptorColor: '#6B7280',
};

export const AGNI_DARK: AgniProductColorConfig = {
  spireColor: '#E59A5A',
  innerSailsLeft: '#F87171',
  innerSailsRight: '#EF4444',
  outriggerWings: '#F59E0B',
  apexDiamond: '#F87171',
  centralBindu: '#F59E0B',
  guideLines: '#F59E0B',
  satelliteNodes: '#F87171',
  wordmarkColor: '#F9FAFB',
  descriptorColor: '#9CA3AF',
};

export const AGNI_SANDSTONE: AgniProductColorConfig = {
  spireColor: '#A35D22',
  innerSailsLeft: '#B91C1C',
  innerSailsRight: '#7F1D1D',
  outriggerWings: '#A35D22',
  apexDiamond: '#B91C1C',
  centralBindu: '#A35D22',
  guideLines: '#A35D22',
  satelliteNodes: '#B91C1C',
  wordmarkColor: '#221B14',
  descriptorColor: '#5C5449',
};

export const AGNI_MONOCHROME: AgniProductColorConfig = {
  spireColor: '#18181B',
  innerSailsLeft: '#27272A',
  innerSailsRight: '#09090B',
  outriggerWings: '#18181B',
  apexDiamond: '#09090B',
  centralBindu: '#18181B',
  guideLines: '#71717A',
  satelliteNodes: '#18181B',
  wordmarkColor: '#09090B',
  descriptorColor: '#71717A',
};

// ── Master Brand Color Dictionary ──────────────────────────────
export const BRAND_THEMES = {
  light: ASTRAX_PRIMARY,
  dark: ASTRAX_DARK,
  sandstone: ASTRAX_SANDSTONE,
  monochrome: ASTRAX_MONOCHROME,
} as const;

export const AGNI_THEMES = {
  light: AGNI_PRIMARY,
  dark: AGNI_DARK,
  sandstone: AGNI_SANDSTONE,
  monochrome: AGNI_MONOCHROME,
} as const;

// ── Typography Tokens ──────────────────────────────────────────
export const BRAND_FONTS = {
  display: 'Fraunces, "Cinzel", "Playfair Display", Georgia, serif',
  serif: 'Spectral, "EB Garamond", Georgia, serif',
  sans: 'Inter, "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  mono: '"JetBrains Mono", "IBM Plex Mono", "SF Mono", Menlo, Consolas, monospace',
} as const;
