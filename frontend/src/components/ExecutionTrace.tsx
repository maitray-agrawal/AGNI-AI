import React from 'react';
import { CheckCircle2, Clock, Terminal, AlertCircle } from 'lucide-react';
import { TraceEvent } from '../types';
import { AstraMark } from './AstraMark';

interface ExecutionTraceProps {
  trace:      TraceEvent[];
  isLoading?: boolean;
}

const STEP_LABELS: Record<string, string> = {
  planner:        'Autonomous Task Planner',
  router:         'Capability Model Router',
  executor:       'Tool Execution & Model Synthesis',
  executor_retry: 'Adaptive Execution Retry & Self-Correction',
  verifier:       '8-Point Domain Verifier',
  finalizer:      'Deliverable Packaging & Audit Finalizer',
};

const STEP_DESCRIPTIONS: Record<string, string> = {
  planner:        'Decomposed task into strategic milestones',
  router:         'Selected optimal model for task type',
  executor:       'Invoked tools and synthesized output',
  executor_retry: 'Applied targeted corrections and re-ran failed checks',
  verifier:       'Ran 8-point domain verification guardrails',
  finalizer:      'Packaged deliverables and wrote audit trail',
};

export const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ trace, isLoading }) => {
  if (!trace.length && !isLoading) {
    return (
      <div
        className="astra-card flex flex-col items-center justify-center py-12 text-center"
        style={{ minHeight: 200 }}
      >
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center mb-3"
          style={{ background: 'var(--astra-sandstone)', color: 'var(--astra-slate)' }}
        >
          <Terminal className="w-5 h-5" />
        </div>
        <p
          style={{
            fontFamily:  'var(--font-sans)',
            fontSize:    '0.875rem',
            color:       'var(--astra-slate)',
            maxWidth:    '28ch',
            lineHeight:  1.6,
          }}
        >
          No active execution trace. Submit a task to observe the autonomous agent lifecycle.
        </p>
      </div>
    );
  }

  return (
    <div className="astra-card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Card header */}
      <div
        className="px-5 py-3.5 flex items-center justify-between"
        style={{
          borderBottom: '1px solid var(--astra-sandstone-dark)',
          background:   'var(--astra-sandstone)',
        }}
      >
        <div className="flex items-center gap-2.5">
          <Terminal className="w-4 h-4" style={{ color: 'var(--agni-copper)' }} />
          <h3
            style={{
              fontFamily:    'var(--font-display)',
              fontSize:      '0.9375rem',
              fontWeight:    600,
              color:         'var(--astra-ink)',
            }}
          >
            Agent Execution Trace
          </h3>
          <span className="intel-tag">LangGraph</span>
        </div>

        {isLoading && (
          <span
            className="flex items-center gap-2"
            style={{
              fontFamily:  'var(--font-mono)',
              fontSize:    '0.625rem',
              color:       'var(--agni-copper)',
              fontWeight:  600,
              letterSpacing:'0.08em',
              textTransform:'uppercase',
            }}
          >
            <span className="agni-bindu live" />
            Executing node…
          </span>
        )}
      </div>

      {/* Trace steps */}
      <div className="p-4 space-y-2">
        {/* Loading shimmer skeleton */}
        {isLoading && !trace.length && (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="shimmer h-14 rounded-lg" />
            ))}
          </div>
        )}

        {trace.map((item, idx) => {
          const isSuccess = item.status === 'completed' || item.status === 'passed';
          return (
            <div key={idx} className="trace-step" style={{ animation: `fadeUp 0.3s ease-out ${idx * 0.06}s both` }}>
              {/* Status icon */}
              <div className="flex-shrink-0 mt-0.5">
                {isSuccess ? (
                  <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--status-positive)' }} />
                ) : (
                  <AlertCircle className="w-4 h-4" style={{ color: 'var(--status-warning)' }} />
                )}
              </div>

              {/* Step info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                  <span
                    style={{
                      fontFamily: 'var(--font-sans)',
                      fontSize:   '0.875rem',
                      fontWeight: 600,
                      color:      'var(--astra-ink)',
                    }}
                  >
                    {STEP_LABELS[item.step] || item.step.toUpperCase()}
                  </span>
                  <span
                    className="intel-tag"
                    style={{ fontSize: '0.5rem' }}
                  >
                    {item.step}
                  </span>
                </div>

                {/* Description */}
                <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.75rem', color: 'var(--astra-slate)', marginBottom: item.details ? '6px' : 0 }}>
                  {STEP_DESCRIPTIONS[item.step] || item.status}
                </p>

                {/* Detail chips */}
                {item.details && (
                  <div
                    className="space-y-1"
                    style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem' }}
                  >
                    {item.details.selected_model && (
                      <div style={{ color: 'var(--astra-slate)' }}>
                        Model assigned:{' '}
                        <span style={{ color: 'var(--astra-indigo)', fontWeight: 700 }}>{item.details.selected_model}</span>
                      </div>
                    )}
                    {item.details.model && (
                      <div style={{ color: 'var(--astra-slate)' }}>
                        Model executed:{' '}
                        <span style={{ color: 'var(--astra-indigo)', fontWeight: 700 }}>{item.details.model}</span>
                      </div>
                    )}
                    {item.details.tools_invoked?.length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span style={{ color: 'var(--astra-slate)' }}>Tools:</span>
                        {item.details.tools_invoked.map((t: string, ti: number) => (
                          <span
                            key={ti}
                            className="px-1.5 py-0.5 rounded"
                            style={{
                              background: 'rgba(46,58,94,0.08)',
                              color:      'var(--astra-indigo)',
                              border:     '1px solid rgba(46,58,94,0.15)',
                              fontSize:   '0.5625rem',
                              fontWeight: 600,
                            }}
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                    {item.details.failed_checks_retried?.length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span style={{ color: 'var(--status-warning)' }}>Corrected:</span>
                        {item.details.failed_checks_retried.map((c: string, ci: number) => (
                          <span
                            key={ci}
                            className="px-1.5 py-0.5 rounded"
                            style={{
                              background: 'rgba(194,132,42,0.08)',
                              color:      'var(--status-warning)',
                              border:     '1px solid rgba(194,132,42,0.2)',
                              fontSize:   '0.5625rem',
                              fontWeight: 600,
                            }}
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    )}
                    {item.details.passed_checks !== undefined && (
                      <div style={{ color: 'var(--status-positive)', fontWeight: 700 }}>
                        Domain Checks: {item.details.passed_checks} / {item.details.total_checks} passed
                      </div>
                    )}
                    {item.details.deliverables > 0 && (
                      <div style={{ color: 'var(--agni-copper)', fontWeight: 600 }}>
                        {item.details.deliverables} deliverable(s) generated
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Duration */}
              <div
                className="flex items-center gap-1 flex-shrink-0"
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize:   '0.625rem',
                  color:      'var(--astra-slate-light)',
                }}
              >
                <Clock className="w-3 h-3" />
                <span>{item.duration_ms}ms</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
