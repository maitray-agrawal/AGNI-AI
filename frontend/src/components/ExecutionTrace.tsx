import React from 'react';
import { CheckCircle2, Clock, Terminal, AlertCircle, ArrowRight } from 'lucide-react';
import { TraceEvent } from '../types';

interface ExecutionTraceProps {
  trace: TraceEvent[];
  isLoading?: boolean;
}

export const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ trace, isLoading }) => {
  if (!trace.length && !isLoading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-[#0f172a]/60 p-6 text-center text-slate-400 text-sm">
        <Terminal className="w-8 h-8 mx-auto mb-2 text-slate-600 opacity-60" />
        No active execution trace. Submit a task to observe autonomous agent lifecycle.
      </div>
    );
  }

  const stepLabels: Record<string, string> = {
    planner: 'Autonomous Task Planner',
    router: 'Capability Model Router',
    executor: 'Tool Execution & Model Synthesis',
    executor_retry: 'Adaptive Execution Retry & Self-Correction',
    verifier: '8-Point Domain Verifier',
    finalizer: 'Deliverable Packaging & Audit Finalizer',
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0f172a]/80 overflow-hidden shadow-xl">
      <div className="px-5 py-3.5 border-b border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-orange-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide">LANGGRAPH EXECUTION TRACE</h3>
        </div>
        {isLoading && (
          <span className="flex items-center text-xs font-mono text-orange-400 animate-pulse">
            Executing Node...
          </span>
        )}
      </div>

      <div className="p-5 space-y-3 font-mono text-xs">
        {trace.map((item, idx) => {
          const isSuccess = item.status === 'completed' || item.status === 'passed';
          return (
            <div
              key={idx}
              className="flex items-start justify-between p-3 rounded-lg border border-slate-800/60 bg-slate-950/40 hover:bg-slate-900/40 transition-colors"
            >
              <div className="flex items-start space-x-3">
                <div className="mt-0.5">
                  {isSuccess ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                  )}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-200 font-semibold text-sm font-sans">
                      {stepLabels[item.step] || item.step.toUpperCase()}
                    </span>
                    <span className="px-2 py-0.2 rounded text-[10px] bg-slate-800 text-slate-400 uppercase">
                      {item.step}
                    </span>
                  </div>

                  {item.details && (
                    <div className="mt-1.5 text-slate-400 text-[11px] space-y-0.5">
                      {item.details.selected_model && (
                        <div>Model Assigned: <span className="text-sky-400 font-bold">{item.details.selected_model}</span></div>
                      )}
                      {item.details.model && (
                        <div>Model Executed: <span className="text-sky-400 font-bold">{item.details.model}</span></div>
                      )}
                      {item.details.tools_invoked && item.details.tools_invoked.length > 0 && (
                        <div className="text-slate-300 flex items-center space-x-1.5 flex-wrap pt-0.5">
                          <span className="text-slate-400">Tools Invoked:</span>
                          {item.details.tools_invoked.map((t: string, ti: number) => (
                            <span key={ti} className="px-1.5 py-0.2 rounded bg-sky-950/80 text-sky-300 border border-sky-800/40 text-[10px] font-mono">
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                      {item.details.failed_checks_retried && item.details.failed_checks_retried.length > 0 && (
                        <div className="text-amber-400 flex items-center space-x-1.5 flex-wrap pt-0.5">
                          <span>Targeted Corrections:</span>
                          {item.details.failed_checks_retried.map((c: string, ci: number) => (
                            <span key={ci} className="px-1.5 py-0.2 rounded bg-amber-950/80 text-amber-300 border border-amber-800/40 text-[10px] font-mono">
                              {c}
                            </span>
                          ))}
                        </div>
                      )}
                      {item.details.reason && (
                        <div className="text-slate-400 italic">"{item.details.reason}"</div>
                      )}
                      {item.details.plan_steps && (
                        <div className="text-slate-300">Generated {item.details.plan_steps} strategic milestones</div>
                      )}
                      {item.details.passed_checks !== undefined && (
                        <div className="text-emerald-400 font-semibold">
                          Domain Checks: {item.details.passed_checks} / {item.details.total_checks} PASSED
                        </div>
                      )}
                      {item.details.deliverables !== undefined && item.details.deliverables > 0 && (
                        <div className="text-orange-400">
                          {item.details.deliverables} Deliverable(s) generated successfully
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-1.5 text-slate-500 font-mono">
                <Clock className="w-3 h-3 text-slate-600" />
                <span>{item.duration_ms}ms</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
