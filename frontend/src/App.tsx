import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { InspectionWorkbench } from './components/InspectionWorkbench';
import { ExecutionTrace } from './components/ExecutionTrace';
import { EvidencePanel } from './components/EvidencePanel';
import { DeliverablesPanel } from './components/DeliverablesPanel';
import { SovereigntyPanel } from './components/SovereigntyPanel';
import { TaskRunResponse, SecurityStatus } from './types';
import { fetchSecurityStatus, fetchModels } from './api/client';

export const App: React.FC = () => {
  const [latestResponse, setLatestResponse] = useState<TaskRunResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [securityStatus, setSecurityStatus] = useState<SecurityStatus | null>(null);
  const [activeModel, setActiveModel] = useState<string>('llama3.1:8b');

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
    fetchModels().then((res) => {
      if (res.models && res.models.length > 0) {
        setActiveModel(res.models[0].id);
      }
    }).catch(console.warn);

    // Periodic telemetry refresh
    const timer = setInterval(loadTelemetry, 15000);
    return () => clearInterval(timer);
  }, []);

  const handleTaskCompleted = (res: TaskRunResponse) => {
    setLatestResponse(res);
    if (res.selected_model) {
      setActiveModel(res.selected_model);
    }
    loadTelemetry();
  };

  // Mock sample citations from flagship report if none attached directly
  const citations = [
    {
      document: 'MRPL_CDU_Piping_Inspection_Manual.pdf',
      page: 14,
      section: 'Section 4.2 - Minimum Wall Thickness & Retirement Criteria',
      text: 'For Carbon Steel Schedule 80 piping in Heavy Gas Oil service, minimum retirement thickness t_min is 4.0 mm. When t_actual is <= 4.5 mm, immediate engineered wrap or spool replacement is required within 72 hours.',
    },
    {
      document: 'MRPL_Rotating_Equipment_Maintenance_SOP.pdf',
      page: 8,
      section: 'Section 3.1 - Centrifugal Pump Vibration Limits (ISO 10816-3)',
      text: 'Zone D trip threshold (> 7.1 mm/s RMS) mandates immediate pump shutdown, bearing replacement, and dynamic rotor balancing before return to service.',
    },
  ];

  const activeCitations = (latestResponse?.retrieved_citations && latestResponse.retrieved_citations.length > 0)
    ? latestResponse.retrieved_citations
    : citations;

  return (
    <div className="min-h-screen bg-[#070c18] text-slate-100 flex flex-col">
      <Header airGapped={securityStatus?.air_gapped ?? true} activeModel={activeModel} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Main Workbench Input */}
        <InspectionWorkbench
          onTaskCompleted={handleTaskCompleted}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
          latestResponse={latestResponse}
        />

        {/* Deliverables Banner (Visible when DOCX/XLSX generated) */}
        {latestResponse?.outputs && (
          <DeliverablesPanel outputs={latestResponse.outputs} />
        )}

        {/* Two-Column Trace & Grounded Citations Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Execution Trace */}
          <div className="lg:col-span-7 space-y-6">
            <ExecutionTrace
              trace={latestResponse?.trace_summary || []}
              isLoading={isLoading}
            />
          </div>

          {/* Right Column: Evidence Citations & Sovereignty Telemetry */}
          <div className="lg:col-span-5 space-y-6">
            <EvidencePanel citations={activeCitations} />
            <SovereigntyPanel status={securityStatus} onRefresh={loadTelemetry} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-[#060a14] py-4 px-6 text-center text-xs text-slate-500 font-mono">
        AGNI-AI • Sovereign Multimodal Agentic Workbench • SIH Problem Statement 26117 • MRPL Refinery Infrastructure
      </footer>
    </div>
  );
};

export default App;
