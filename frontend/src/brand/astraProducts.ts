/**
 * AstraX Intelligence Systems Registry
 * Canonical product directory defining the AstraX product family,
 * visual signatures, color accents, and domain descriptors.
 */

export interface AstraProduct {
  id: string;
  name: string;
  descriptor: string;
  domain: string;
  accent: string;
  secondaryAccent: string;
  accentHex: string;
  secondaryHex: string;
  motif: string;
  motto: string;
  coreValues: string[];
  status: 'active' | 'preview' | 'reserved';
}

export const astraProducts: Record<string, AstraProduct> = {
  kubersetu: {
    id: 'kubersetu',
    name: 'KuberSetu',
    descriptor: 'FINANCIAL INTELLIGENCE',
    domain: 'Wealth · Opportunity · Market Intelligence · Inclusion',
    accent: 'indigo',
    secondaryAccent: 'copper',
    accentHex: '#1E3A8A',
    secondaryHex: '#B87333',
    motif: 'network',
    motto: 'CONNECTING OPPORTUNITIES',
    coreValues: ['Wealth', 'Opportunity', 'Market Intelligence', 'Inclusion'],
    status: 'preview',
  },

  vajra: {
    id: 'vajra',
    name: 'Vajra',
    descriptor: 'CRISIS INTELLIGENCE',
    domain: 'Resilience · Rapid Response · Risk Analysis · Continuity',
    accent: 'vermilion',
    secondaryAccent: 'copper',
    accentHex: '#DC2626',
    secondaryHex: '#B87333',
    motif: 'fracture-convergence',
    motto: 'OBSERVE · RESPOND · RECOVER',
    coreValues: ['Resilience', 'Rapid Response', 'Risk Analysis', 'Continuity'],
    status: 'preview',
  },

  niyukti: {
    id: 'niyukti',
    name: 'Niyukti',
    descriptor: 'TALENT INTELLIGENCE',
    domain: 'People · Skills · Opportunity · Growth',
    accent: 'indigo',
    secondaryAccent: 'saffron',
    accentHex: '#1E3A8A',
    secondaryHex: '#F59E0B',
    motif: 'connection',
    motto: 'TALENT MEETS OPPORTUNITY',
    coreValues: ['People', 'Skills', 'Opportunity', 'Growth'],
    status: 'preview',
  },

  margadarshi: {
    id: 'margadarshi',
    name: 'Margadarshi',
    descriptor: 'CAREER INTELLIGENCE',
    domain: 'Guidance · Learning · Pathways · Potential',
    accent: 'teal',
    secondaryAccent: 'saffron',
    accentHex: '#0D9488',
    secondaryHex: '#F59E0B',
    motif: 'path',
    motto: 'CLARITY · DIRECTION · GROWTH',
    coreValues: ['Guidance', 'Learning', 'Pathways', 'Potential'],
    status: 'preview',
  },

  agni: {
    id: 'agni',
    name: 'Agni',
    descriptor: 'RESEARCH INTELLIGENCE',
    domain: 'Geopolitical + Financial Intelligence · Strategic Foresight',
    accent: 'vermilion',
    secondaryAccent: 'copper',
    accentHex: '#DC2626',
    secondaryHex: '#B87333',
    motif: 'heat-field',
    motto: 'IDEAS · ANALYZE · TRANSFORM',
    coreValues: ['Research', 'Innovation', 'Knowledge', 'Real Impact'],
    status: 'active',
  },

  satyam: {
    id: 'satyam',
    name: 'Satyam',
    descriptor: 'TRUST & GOVERNANCE',
    domain: 'Verification · Transparency · Compliance · Trust',
    accent: 'indigo',
    secondaryAccent: 'copper',
    accentHex: '#1E3A8A',
    secondaryHex: '#B87333',
    motif: 'evidence-seal',
    motto: 'EVIDENCE · VERIFICATION · TRUST',
    coreValues: ['Verification', 'Transparency', 'Compliance', 'Trust'],
    status: 'preview',
  },

  vaidhya: {
    id: 'vaidhya',
    name: 'Vaidhya',
    descriptor: 'CLINICAL INTELLIGENCE',
    domain: 'Healthcare · Accessibility · Accuracy · Better Outcomes',
    accent: 'forest-green',
    secondaryAccent: 'copper',
    accentHex: '#166534',
    secondaryHex: '#B87333',
    motif: 'clinical-wave',
    motto: 'PEOPLE · CARE · BETTER HEALTH',
    coreValues: ['Healthcare', 'Accessibility', 'Accuracy', 'Better Outcomes'],
    status: 'preview',
  },
};

/** Official AstraX Color Palette Tokens */
export const ASTRA_PALETTE = {
  ivory: '#FDF7EC',
  sandstone: '#E4DCC8',
  sandstoneBorder: '#D8CEB8',
  ink: '#221B14',
  inkMuted: '#5C5449',
  copper: '#B87333',
  copperLight: '#D48946',
  copperDark: '#8A5222',
  indigo: '#1E3A8A',
  indigoMuted: '#2B4C9B',
  vermilion: '#DC2626',
  vermilionRust: '#9E3B24',
  saffron: '#F59E0B',
  forestGreen: '#166534',
  ochre: '#CA8A04',
} as const;
