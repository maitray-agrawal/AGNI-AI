/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        agni: {
          dark: "#0a0f1d",
          card: "#111827",
          border: "#1f293d",
          accent: "#f97316", // Flame orange
          navy: "#0284c7",
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
        }
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
