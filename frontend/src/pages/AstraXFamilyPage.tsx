import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Compass, Layers, Sparkles, Check, ArrowUpRight } from 'lucide-react';
import { AstraXLogo } from '../brand/AstraXLogo';
import { AstraXMark } from '../brand/AstraXMark';
import { AstraSeal } from '../brand/AstraSeal';
import { AstraWatermark } from '../brand/AstraWatermark';
import { AstraThemeSwitcher } from '../brand/AstraThemeSwitcher';
import { ProjectMark, AstraProjectId } from '../brand/ProjectMark';
import { astraProducts } from '../brand/astraProducts';
import { useAstraTheme } from '../brand/AstraThemeContext';

export const AstraXFamilyPage: React.FC = () => {
  const navigate = useNavigate();
  const { theme } = useAstraTheme();

  const isDark = theme === 'dark';
  const markVariant = theme === 'dark' ? 'dark' : theme === 'sandstone' ? 'sandstone' : theme === 'monochrome' ? 'monochrome' : 'primary';
  const projectTheme = theme === 'light' ? 'primary' : theme;
  const sealTheme = theme === 'dark' ? 'dark' : theme === 'monochrome' ? 'monochrome' : 'primary';

  return (
    <div
      className="min-h-screen relative overflow-x-hidden selection:bg-agni-copper/20"
      style={{
        backgroundColor: 'var(--astra-ivory)',
        color: 'var(--astra-ink)',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* ── Background Institutional Watermark ─────────── */}
      <AstraWatermark size={640} opacity={isDark ? 0.03 : 0.025} className="top-12 -right-48 pointer-events-none" />

      {/* ── Top Navigation Bar ──────────────────────────── */}
      <header
        className="sticky top-0 z-40 border-b backdrop-blur-md px-4 sm:px-8 py-3.5 flex items-center justify-between"
        style={{
          borderColor: 'var(--astra-sandstone-dark)',
          backgroundColor: isDark ? 'rgba(17, 24, 39, 0.85)' : 'rgba(253, 247, 236, 0.88)',
        }}
      >
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-mono transition-all hover:bg-black/5 dark:hover:bg-white/5 border-astra-sandstone-dark/70 text-astra-slate group"
            aria-label="Back to AGNI"
          >
            <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform text-agni-copper" />
            <span className="font-semibold text-astra-ink">Back to AGNI</span>
          </button>

          <span className="text-astra-sandstone-dark/80 hidden sm:inline">/</span>

          <span className="hidden sm:inline font-mono text-[10px] tracking-[0.16em] uppercase text-astra-slate">
            Institutional Ecosystem Directory
          </span>
        </div>

        <div className="flex items-center gap-3">
          <AstraThemeSwitcher />
        </div>
      </header>

      {/* ── Main Container ──────────────────────────────── */}
      <main className="max-w-6xl mx-auto px-4 sm:px-8 py-12 sm:py-16 space-y-16">

        {/* ── 01. Hero / Institutional Identity ──────────── */}
        <section className="text-center max-w-3xl mx-auto space-y-6">
          {/* Master AstraX Mark */}
          <div className="flex justify-center mb-2">
            <div className="p-4 rounded-2xl border border-astra-sandstone-dark/60 bg-astra-sandstone/30 shadow-sm relative group">
              <AstraXMark size={96} variant={markVariant} />
              <div
                className="absolute inset-0 rounded-2xl pointer-events-none border border-agni-copper/20"
                aria-hidden="true"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-astra-sandstone-dark/80 bg-astra-sandstone/40 text-[9px] font-mono tracking-[0.2em] uppercase text-astra-slate">
              <span className="w-1.5 h-1.5 rounded-full bg-agni-copper" />
              ASTRA X INSTITUTIONAL ARCHITECTURE
            </div>

            <h1
              className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold tracking-tight text-astra-ink leading-tight"
            >
              Intelligence, Built on<br />
              <span className="italic" style={{ color: 'var(--agni-copper)' }}>
                Indian Mathematical Grammar.
              </span>
            </h1>

            <p className="text-sm sm:text-base font-serif text-astra-slate max-w-2xl mx-auto leading-relaxed italic">
              AstraX is a sovereign intelligence foundation. A unified mathematical geometry uniting
              autonomous reasoning, structural determinism, and institutional evidence across specialized domains.
            </p>
          </div>

          {/* Institutional Metric Pill Bar */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-6 sm:gap-10 border-y border-astra-sandstone-dark/60 py-4 font-mono text-xs">
            <div className="text-center">
              <div className="text-lg font-bold text-astra-ink">7</div>
              <div className="text-[9px] text-astra-slate uppercase tracking-wider">Intelligence Systems</div>
            </div>
            <div className="w-px h-8 bg-astra-sandstone-dark/60" />
            <div className="text-center">
              <div className="text-lg font-bold text-astra-ink">100%</div>
              <div className="text-[9px] text-astra-slate uppercase tracking-wider">Deterministic Geometry</div>
            </div>
            <div className="w-px h-8 bg-astra-sandstone-dark/60" />
            <div className="text-center">
              <div className="text-lg font-bold text-astra-ink">Sovereign</div>
              <div className="text-[9px] text-astra-slate uppercase tracking-wider">On-Premise / Zero Egress</div>
            </div>
          </div>
        </section>

        {/* ── 02. The Intelligence Systems Family ────────── */}
        <section className="space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-astra-sandstone-dark/60 pb-4">
            <div>
              <div className="font-mono text-[9px] tracking-[0.2em] uppercase text-astra-slate font-bold">
                FAMILY ECOSYSTEM
              </div>
              <h2 className="text-2xl font-serif font-bold text-astra-ink mt-1">
                A Family of Specialized Intelligence Systems
              </h2>
            </div>
            <p className="text-xs font-serif text-astra-slate italic max-w-sm sm:text-right">
              One institutional architecture, multiple intelligence systems — each expressing domain autonomy.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {Object.values(astraProducts).map((product) => {
              const isAgni = product.id === 'agni';
              return (
                <div
                  key={product.id}
                  className={`rounded-xl border p-5 transition-all flex flex-col justify-between relative group ${
                    isAgni
                      ? 'border-agni-copper/60 bg-astra-sandstone/40 shadow-md ring-1 ring-agni-copper/20'
                      : 'border-astra-sandstone-dark/70 bg-astra-sandstone/15 hover:bg-astra-sandstone/30 hover:border-astra-sandstone-dark'
                  }`}
                >
                  {/* Card Header: Project Mark & Name */}
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="p-2.5 rounded-lg border border-black/5 dark:border-white/10 bg-white dark:bg-neutral-800 shadow-sm flex items-center justify-center">
                        <ProjectMark
                          project={product.id as AstraProjectId}
                          size={32}
                          theme={projectTheme}
                        />
                      </div>

                      <div className="flex flex-col items-end gap-1">
                        <span
                          className="font-mono text-[8px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider border"
                          style={{
                            borderColor: product.accentHex,
                            color: product.accentHex,
                            backgroundColor: `${product.accentHex}12`,
                          }}
                        >
                          {product.descriptor}
                        </span>
                        {isAgni && (
                          <span className="font-mono text-[7px] px-1.5 py-0.2 rounded bg-agni-vermilion text-white uppercase font-bold tracking-widest">
                            CURRENT PRODUCT
                          </span>
                        )}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-serif font-bold text-astra-ink tracking-wide flex items-center gap-1.5">
                        {product.name}
                      </h3>
                      <div className="font-serif text-xs text-astra-slate italic mt-0.5">
                        "{product.motto}"
                      </div>
                    </div>

                    <p className="text-xs text-astra-slate leading-relaxed pt-1">
                      {product.domain}
                    </p>
                  </div>

                  {/* Card Footer: Action / Status */}
                  <div className="pt-5 mt-4 border-t border-astra-sandstone-dark/40 flex items-center justify-between">
                    <span className="font-mono text-[8px] text-astra-slate tracking-widest uppercase flex items-center gap-1.5">
                      <span
                        className="w-1.5 h-1.5 rounded-full"
                        style={{ backgroundColor: product.accentHex }}
                      />
                      {isAgni ? 'Active Terminal' : 'Ecosystem Node'}
                    </span>

                    {isAgni ? (
                      <button
                        onClick={() => navigate('/')}
                        className="flex items-center gap-1 px-2.5 py-1 rounded border border-agni-copper/50 bg-agni-copper/15 hover:bg-agni-copper/25 text-agni-copper text-[10px] font-mono font-bold tracking-wider transition-colors"
                      >
                        <span>Launch AGNI</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    ) : (
                      <span className="text-[9.5px] font-mono text-astra-slate/60 tracking-wider uppercase">
                        Sovereign Ready
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* ── 03. AstraX Design Language ─────────────────── */}
        <section className="space-y-8 pt-4">
          <div className="border-b border-astra-sandstone-dark/60 pb-4">
            <div className="font-mono text-[9px] tracking-[0.2em] uppercase text-astra-slate font-bold">
              FOUNDATIONAL GRAMMAR
            </div>
            <h2 className="text-2xl font-serif font-bold text-astra-ink mt-1">
              AstraX Design Language
            </h2>
            <p className="text-xs font-serif text-astra-slate italic mt-1">
              Six mathematical pillars governing identity, layout density, and analytical interaction.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              {
                title: 'Bindu',
                subtitle: 'Coordinate Origin',
                desc: 'The central diamond core and anchor point from which all analytical vectors and reasoning wavefronts originate.',
                tag: '01 / GEOMETRY',
              },
              {
                title: 'Sutra',
                subtitle: 'Relational Threads',
                desc: 'Fine hairline rules and structural connections joining evidence citations, logical steps, and multi-agent states.',
                tag: '02 / STRUCTURE',
              },
              {
                title: 'Grid',
                subtitle: 'Mathematical Spacing',
                desc: 'Harmonious layout ratios derived from ancient Indian computational proportions, avoiding arbitrary whitespace.',
                tag: '03 / PROPORTION',
              },
              {
                title: 'Geometry',
                subtitle: 'Asymmetric Faceting',
                desc: 'Cardinal axes, 45-degree angle sails, and telemetry satellite nodes rendering deterministic vector precision.',
                tag: '04 / FORM',
              },
              {
                title: 'Material',
                subtitle: 'Sandstone & Ivory',
                desc: 'Tactile, non-fatiguing surfaces reminiscent of stone inscriptions and archival research desks rather than bright SaaS panels.',
                tag: '05 / SURFACE',
              },
              {
                title: 'Color',
                subtitle: 'Institutional Palette',
                desc: 'Rooted mineral accents: Copper (#B87333), Astra Indigo (#1E3A8A), Vermilion, and Ink with strict functional assignments.',
                tag: '06 / SPECTRUM',
              },
            ].map((pillar) => (
              <div
                key={pillar.title}
                className="p-5 rounded-xl border border-astra-sandstone-dark/70 bg-astra-sandstone/20 space-y-2.5"
              >
                <div className="font-mono text-[8px] tracking-[0.2em] uppercase text-agni-copper font-bold">
                  {pillar.tag}
                </div>
                <div className="flex items-baseline gap-2">
                  <h3 className="text-base font-serif font-bold text-astra-ink">
                    {pillar.title}
                  </h3>
                  <span className="text-xs font-mono text-astra-slate">
                    — {pillar.subtitle}
                  </span>
                </div>
                <p className="text-xs text-astra-slate leading-relaxed">
                  {pillar.desc}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ── 04. Institutional Seal & Back Navigation ───── */}
        <section className="pt-8 pb-4 border-t border-astra-sandstone-dark/60 flex flex-col items-center text-center space-y-6">
          <AstraSeal size={72} theme={sealTheme} />

          <div className="space-y-1 max-w-md">
            <div className="font-mono text-[8px] tracking-[0.24em] uppercase text-astra-slate font-bold">
              ASTRA X INTELLIGENCE PLATFORM
            </div>
            <div className="font-serif text-xs text-astra-slate italic">
              Veritas et Vigilantia — Sovereign Architecture
            </div>
          </div>

          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-agni-copper/50 bg-agni-copper text-white hover:bg-agni-copper/90 text-xs font-mono font-bold tracking-wider transition-all shadow-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to AGNI Intelligence Workspace</span>
          </button>
        </section>

      </main>
    </div>
  );
};
