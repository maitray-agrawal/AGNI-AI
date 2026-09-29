import React, { useState, useEffect } from 'react';
import { Header }              from './components/Header';
import { AstraSidebar }        from './components/AstraSidebar';
import { IntelligenceHero }    from './components/IntelligenceHero';
import { InspectionWorkbench } from './components/InspectionWorkbench';
import { ExecutionTrace }      from './components/ExecutionTrace';
import { EvidencePanel }       from './components/EvidencePanel';
import { DeliverablesPanel }   from './components/DeliverablesPanel';
import { SovereigntyPanel }    from './components/SovereigntyPanel';
import { GlobalSignalField }   from './components/GlobalSignalField';
import { EmergingRisks }       from './components/EmergingRisks';
import { LiveSignals }         from './components/LiveSignals';
import { WhyThisMatters }      from './components/WhyThisMatters';
import { EconomicPressure }    from './components/EconomicPressure';
import { ScenarioOutlook }     from './components/ScenarioOutlook';
import { AstraMark }           from './components/AstraMark';
import { SectionRule }         from './components/AstraShared';
import { AgniLogo }            from './brand/AgniLogo';
import { AstraWatermark }       from './brand/AstraWatermark';
import { TaskRunResponse, SecurityStatus } from './types';
import { fetchSecurityStatus, fetchModels } from './api/client';

// ──────────────────────────────────────────────────────────────────
// AGNI — AstraX Intelligence Workspace V2
// Architecture: What's Changing → Why It Matters → What Supports It
// ──────────────────────────────────────────────────────────────────

export const App: React.FC = () => {
  const [latestResponse,  setLatestResponse]  = useState<TaskRunResponse | null>(null);
  const [isLoading,       setIsLoading]        = useState<boolean>(false);
  const [securityStatus,  setSecurityStatus]   = useState<SecurityStatus | null>(null);
  const [activeModel,     setActiveModel]      = useState<string>('llama3.1:8b');
  const [sidebarOpen,     setSidebarOpen]      = useState<boolean>(() => typeof window !== 'undefined' ? window.innerWidth >= 768 : true);
  const [activeNavItem,   setActiveNavItem]    = useState<string>('workbench');

  // ── Telemetry ──────────────────────────────────────────────────
  const loadTelemetry = async () => {
    try {
      const sec = await fetchSecurityStatus();
      setSecurityStatus(sec);
    } catch (e) {
      console.warn('Telemetry load failed:', e);
    }
  };

  useEffect(() => {
    loadTelemetry();
    fetchModels()
      .then(res => { if (res.models?.length > 0) setActiveModel(res.models[0].id); })
      .catch(console.warn);
    const timer = setInterval(loadTelemetry, 15000);
    return () => clearInterval(timer);
  }, []);

  const handleTaskCompleted = (res: TaskRunResponse) => {
    setLatestResponse(res);
    if (res.selected_model) setActiveModel(res.selected_model);
    loadTelemetry();
  };

  // ── Fallback citations ─────────────────────────────────────────
  const citations = [
    {
      document: 'MRPL_CDU_Piping_Inspection_Manual.pdf',
      page:     14,
      section:  'Section 4.2 — Minimum Wall Thickness & Retirement Criteria',
      text:     'For Carbon Steel Schedule 80 piping in Heavy Gas Oil service, minimum retirement thickness t_min is 4.0 mm. When t_actual is ≤ 4.5 mm, immediate engineered wrap or spool replacement is required within 72 hours.',
    },
    {
      document: 'MRPL_Rotating_Equipment_Maintenance_SOP.pdf',
      page:     8,
      section:  'Section 3.1 — Centrifugal Pump Vibration Limits (ISO 10816-3)',
      text:     'Zone D trip threshold (> 7.1 mm/s RMS) mandates immediate pump shutdown, bearing replacement, and dynamic rotor balancing before return to service.',
    },
  ];
  const activeCitations = latestResponse?.retrieved_citations?.length
    ? latestResponse.retrieved_citations
    : citations;

  return (
    <div className="min-h-screen" style={{ background: 'var(--astra-ivory)', color: 'var(--astra-ink)' }}>
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <AstraSidebar
        activeItem={activeNavItem}
        onItemSelect={(id) => {
          setActiveNavItem(id);
          if (typeof window !== 'undefined' && window.innerWidth < 768) setSidebarOpen(false);
        }}
        isOpen={sidebarOpen}
      />

      {/* ── Mobile overlay ──────────────────────────────────────── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 md:hidden"
          style={{ background: 'rgba(24,32,43,0.4)' }}
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ── Main content area ────────────────────────────────────── */}
      <div
        className="md:pl-[240px] flex flex-col"
        style={{ minHeight: '100vh', transition: 'padding-left 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}
      >
        {/* Top bar */}
        <Header
          airGapped={securityStatus?.air_gapped ?? true}
          activeModel={activeModel}
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />

        {/* ════════════════════════════════════════════════════════
            PAGE CONTENT
            Section structure:
            01 — Hero / Signal overview
            02 — Global Signal Field (primary map)
            03 — What's Changing: Risks + Signals
            04 — Why This Matters (analysis chain)
            05 — Economic Pressure
            06 — Scenario Outlook
            07 — Intelligence Workbench (existing functionality)
            08 — Evidence + Sovereignty telemetry
            ════════════════════════════════════════════════════════ */}
        <main
          className="flex-1 px-4 sm:px-5 lg:px-7 py-6 space-y-7"
          style={{ maxWidth: 1360, width: '100%', margin: '0 auto' }}
          id="main-content"
        >

          {/* ── 01. HERO ──────────────────────────────────────── */}
          <IntelligenceHero newSignals={7} signalCount={1284} />

          {/* ── 02. GLOBAL SITUATION ─────────────────────────── */}
          <div>
            <SectionRule number="01" title="Global Situation" />
            <GlobalSignalField liveCount={7} />
          </div>

          {/* ── 03. WHAT IS CHANGING ─────────────────────────── */}
          <div>
            <SectionRule number="02" title="What Is Changing" />
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <div className="lg:col-span-7">
                <EmergingRisks />
              </div>
              <div className="lg:col-span-5">
                <LiveSignals maxItems={7} />
              </div>
            </div>
          </div>

          {/* ── 04. WHY THIS MATTERS ─────────────────────────── */}
          <div>
            <SectionRule number="03" title="Why This Matters" />
            <WhyThisMatters />
          </div>

          {/* ── 05. ECONOMIC PRESSURE ────────────────────────── */}
          <div>
            <SectionRule number="04" title="Economic Pressure" />
            <EconomicPressure />
          </div>

          {/* ── 06. SCENARIO OUTLOOK ─────────────────────────── */}
          <div>
            <SectionRule number="05" title="Scenario Outlook" />
            <ScenarioOutlook />
          </div>

          {/* ── 07. INTELLIGENCE WORKBENCH ───────────────────── */}
          <div>
            <SectionRule number="06" title="Intelligence Workbench" />
            <InspectionWorkbench
              onTaskCompleted={handleTaskCompleted}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
              latestResponse={latestResponse}
            />
          </div>

          {/* ── Deliverables banner ───────────────────────────── */}
          {latestResponse?.outputs && latestResponse.outputs.length > 0 && (
            <DeliverablesPanel outputs={latestResponse.outputs} />
          )}

          {/* ── 08. EVIDENCE & SOVEREIGNTY ───────────────────── */}
          <div>
            <SectionRule number="07" title="Evidence & Sovereignty" />
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <div className="lg:col-span-7 space-y-5">
                <ExecutionTrace
                  trace={latestResponse?.trace_summary || []}
                  isLoading={isLoading}
                />
              </div>
              <div className="lg:col-span-5 space-y-5">
                <EvidencePanel citations={activeCitations} />
                <SovereigntyPanel status={securityStatus} onRefresh={loadTelemetry} />
              </div>
            </div>
          </div>
        </main>

        {/* ── Footer ──────────────────────────────────────────── */}
        <footer
          className="relative px-7 py-5 overflow-hidden"
          style={{ borderTop: '1px solid var(--astra-sandstone-dark)', background: 'var(--astra-sandstone)' }}
          role="contentinfo"
        >
          <AstraWatermark size={320} opacity={0.02} className="right-4 -bottom-10" />

          <div className="relative z-10 max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <AgniLogo variant="mark" size={20} theme="light" />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5625rem', color: 'var(--astra-ink)', letterSpacing: '0.12em', fontWeight: 600 }}>
                AGNI · RESEARCH INTELLIGENCE · AN ASTRA X INTELLIGENCE SYSTEM
              </span>
            </div>
            <p style={{ fontFamily: 'var(--font-serif)', fontSize: '0.75rem', color: 'var(--astra-slate)', fontStyle: 'italic' }}>
              Sovereign Agentic Intelligence for Evidence-Grounded Research & Geopolitical Foresight
            </p>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--astra-slate)', letterSpacing: '0.1em' }}>
              v2.0 · SOVEREIGN
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default App;
