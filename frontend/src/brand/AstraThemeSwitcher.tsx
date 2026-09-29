import React, { useState, useRef, useEffect } from 'react';
import { Sun, Moon, Palette, Compass, ChevronDown, Check } from 'lucide-react';
import { useAstraTheme, AstraThemeMode } from './AstraThemeContext';

export const AstraThemeSwitcher: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, setTheme } = useAstraTheme();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const THEMES: { id: AstraThemeMode; label: string; icon: React.ReactNode; color: string }[] = [
    { id: 'light', label: 'Primary (Ivory)', icon: <Sun className="w-3.5 h-3.5 text-amber-600" />, color: '#FDF7EC' },
    { id: 'dark', label: 'Dark (Navy/Ink)', icon: <Moon className="w-3.5 h-3.5 text-blue-400" />, color: '#111827' },
    { id: 'sandstone', label: 'Sandstone', icon: <Palette className="w-3.5 h-3.5 text-orange-700" />, color: '#EADCC8' },
    { id: 'monochrome', label: 'Monochrome', icon: <Compass className="w-3.5 h-3.5 text-neutral-800" />, color: '#FFFFFF' },
  ];

  const currentTheme = THEMES.find((t) => t.id === theme) || THEMES[0];

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-mono transition-all hover:bg-black/5 dark:hover:bg-white/5 border-astra-sandstone-dark/60 text-astra-slate"
        aria-label="Theme Switcher"
        title="Switch AstraX Theme"
      >
        <span
          className="w-2.5 h-2.5 rounded-full border border-black/10 dark:border-white/20"
          style={{ backgroundColor: currentTheme.color }}
        />
        <span className="capitalize text-[10px] tracking-wide font-medium">{theme}</span>
        <ChevronDown className="w-3 h-3 opacity-60" />
      </button>

      {open && (
        <div
          className="absolute right-0 mt-1.5 w-48 rounded-xl shadow-xl border bg-white dark:bg-neutral-900 border-astra-sandstone-dark/80 p-2.5 z-50 animate-fadeIn text-astra-ink dark:text-neutral-100"
          style={{ backdropFilter: 'blur(16px)' }}
        >
          <div className="text-[8px] font-mono tracking-widest uppercase text-astra-slate mb-2 font-bold px-1">
            ASTRA X THEME VARIANTS
          </div>
          <div className="space-y-1">
            {THEMES.map((t) => (
              <button
                key={t.id}
                onClick={() => {
                  setTheme(t.id);
                  setOpen(false);
                }}
                className={`flex items-center justify-between w-full px-2 py-1.5 rounded-md text-[10px] font-mono transition-colors text-left ${
                  theme === t.id
                    ? 'bg-agni-copper/15 border border-agni-copper/40 text-agni-copper font-bold'
                    : 'hover:bg-black/5 dark:hover:bg-white/5 text-astra-slate'
                }`}
              >
                <div className="flex items-center gap-2">
                  {t.icon}
                  <span>{t.label}</span>
                </div>
                {theme === t.id && <Check className="w-3 h-3 text-agni-copper" />}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
