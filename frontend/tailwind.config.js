/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── AstraX Core ──────────────────────────────────────────────
        astra: {
          ivory:      '#F5EFE3',
          'ivory-dim':'#EDE4D5',
          sandstone:  '#E8D8C2',
          'sandstone-dark': '#D9C4A8',
          ink:        '#18202B',
          'ink-light':'#2A3444',
          slate:      '#66707A',
          'slate-light': '#8A949E',
          indigo:     '#2E3A5E',
          'indigo-dim':'#3D4F7A',
        },
        // ── AGNI Product ─────────────────────────────────────────────
        agni: {
          red:        '#7E241D',
          'red-deep': '#5C1A15',
          'red-muted':'#9B3730',
          vermilion:  '#C0392B',
          copper:     '#B66A3C',
          'copper-light': '#C47A46',
          terracotta: '#A05C3A',
          clay:       '#8B6355',
          ochre:      '#C2842A',
          sienna:     '#8E4A2E',
        },
        // ── Status / Semantic ─────────────────────────────────────────
        status: {
          positive:   '#2D6A4F',
          'positive-light': '#40916C',
          warning:    '#C2842A',
          critical:   '#C0392B',
          info:       '#2E3A5E',
        },
      },
      fontFamily: {
        display:  ['Fraunces', 'Source Serif 4', 'Georgia', 'serif'],
        serif:    ['Fraunces', 'Source Serif 4', 'Georgia', 'serif'],
        sans:     ['Inter', 'IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono:     ['IBM Plex Mono', 'JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      spacing: {
        '4.5': '1.125rem',
        '5.5': '1.375rem',
        '18':  '4.5rem',
        '22':  '5.5rem',
        '72':  '18rem',
        '80':  '20rem',
        '88':  '22rem',
        '96':  '24rem',
      },
      borderRadius: {
        'xs': '4px',
        'sm': '6px',
        DEFAULT: '8px',
        'md': '10px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '20px',
      },
      boxShadow: {
        'astra-sm':  '0 1px 3px 0 rgba(24,32,43,0.08), 0 1px 2px -1px rgba(24,32,43,0.06)',
        'astra-md':  '0 4px 12px -1px rgba(24,32,43,0.10), 0 2px 6px -2px rgba(24,32,43,0.08)',
        'astra-lg':  '0 10px 28px -4px rgba(24,32,43,0.12), 0 4px 12px -4px rgba(24,32,43,0.08)',
        'astra-xl':  '0 20px 48px -8px rgba(24,32,43,0.16), 0 8px 20px -6px rgba(24,32,43,0.10)',
        'agni-card': '0 2px 8px rgba(24,32,43,0.07), 0 0 0 1px rgba(232,216,194,0.6)',
        'agni-red':  '0 4px 16px rgba(126,36,29,0.18)',
        'copper':    '0 4px 16px rgba(182,106,60,0.18)',
      },
      backgroundImage: {
        'astra-grain': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E\")",
      },
      transitionDuration: {
        '150': '150ms',
        '200': '200ms',
        '250': '250ms',
        '300': '300ms',
      },
      transitionTimingFunction: {
        'astra': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      animation: {
        'bindu-pulse': 'binduPulse 3s ease-in-out infinite',
        'sutra-draw':  'sutraDraw 1.2s ease-out forwards',
        'heat-expand': 'heatExpand 4s ease-in-out infinite',
        'fade-up':     'fadeUp 0.35s ease-out forwards',
        'shimmer':     'shimmer 2s linear infinite',
      },
      keyframes: {
        binduPulse: {
          '0%, 100%': { opacity: '0.6', transform: 'scale(1)' },
          '50%':      { opacity: '1',   transform: 'scale(1.15)' },
        },
        sutraDraw: {
          '0%':   { strokeDashoffset: '100%', opacity: '0' },
          '100%': { strokeDashoffset: '0%',   opacity: '1' },
        },
        heatExpand: {
          '0%, 100%': { transform: 'scale(1)',    opacity: '0.12' },
          '50%':      { transform: 'scale(1.04)', opacity: '0.18' },
        },
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
