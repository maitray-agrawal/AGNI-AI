import React, { useState } from 'react';
import {
  Play, Upload, FileText, CheckCircle2, XCircle,
  RefreshCw, Clock, AlertTriangle, ShieldCheck, Zap,
  BookOpen, ChevronRight
} from 'lucide-react';
import { TaskRunResponse } from '../types';
import { submitTask, uploadDocument } from '../api/client';
import { AgniLogo } from '../brand/AgniLogo';
import { AstraSeal } from '../brand/AstraSeal';
import { AgniLoadingMark } from '../brand/AgniLoadingMark';

interface InspectionWorkbenchProps {
  onTaskCompleted: (res: TaskRunResponse) => void;
  isLoading:       boolean;
  setIsLoading:    (v: boolean) => void;
  latestResponse:  TaskRunResponse | null;
}

const PRESETS = [
  {
    title:  'Flagship: Inspection Approval Note',
    prompt: 'Analyze this inspection report, identify critical findings, consult relevant local procedures, determine the recommended action, verify the result and generate an approval note.',
    file:   'data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf',
    tag:    'Inspection',
  },
  {
    title:  'Calculation: Wall Thickness Reduction',
    prompt: 'Calculate the percentage reduction from 8.2 mm to 4.2 mm wall thickness for Heavy Gas Oil piping and compare against 4.0 mm API 570 retirement limit.',
    file:   '',
    tag:    'Engineering',
  },
  {
    title:  'P&ID: Unit Flow & Valve Inspection',
    prompt: 'Inspect the CDU-II pump P-204 A/B P&ID schematic. Identify feed vessel, pumps, critical discharge elbow, and flow control valve FCV-204.',
    file:   'data/raw/pidqa/pid_cdu_pump_p204.png',
    tag:    'P&ID',
  },
];

export const InspectionWorkbench: React.FC<InspectionWorkbenchProps> = ({
  onTaskCompleted,
  isLoading,
  setIsLoading,
  latestResponse,
}) => {
  const [prompt, setPrompt] = useState<string>(PRESETS[0].prompt);
  const [selectedFile, setSelectedFile]     = useState<string>(PRESETS[0].file);
  const [uploadStatus, setUploadStatus]     = useState<string>('Preloaded: MRPL_Inspection_Report_P204.pdf');
  const [activePreset, setActivePreset]     = useState<number>(0);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    const file = e.target.files[0];
    try {
      setUploadStatus(`Uploading ${file.name}…`);
      const res = await uploadDocument(file);
      setSelectedFile(res.saved_path);
      setUploadStatus(`Uploaded: ${res.filename}`);
    } catch (err: any) {
      setUploadStatus(`Upload failed: ${err.message}`);
    }
  };

  const handleExecute = async () => {
    if (!prompt.trim() || isLoading) return;
    setIsLoading(true);
    try {
      const files = selectedFile ? [selectedFile] : [];
      const res   = await submitTask(prompt, files);
      onTaskCompleted(res);
    } catch (err: any) {
      alert(`Execution failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const selectPreset = (idx: number) => {
    const p = PRESETS[idx];
    setActivePreset(idx);
    setPrompt(p.prompt);
    setSelectedFile(p.file);
    setUploadStatus(p.file ? `Selected: ${p.file.split('/').pop()}` : 'No document required');
  };

  return (
    <div
      className="astra-card"
      style={{ padding: 0, overflow: 'hidden' }}
    >
      {/* ── Card header ──────────────────────────────────── */}
      <div
        className="px-6 py-4 flex items-center justify-between"
        style={{
          borderBottom: '1px solid var(--astra-sandstone-dark)',
          background:   'var(--astra-sandstone)',
        }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center p-1"
            style={{ background: 'var(--astra-sandstone-dark)', color: 'var(--astra-ink)' }}
          >
            <AgniLogo variant="mark" size={22} theme="primary" />
          </div>
          <div>
            <h2
              style={{
                fontFamily:    'var(--font-display)',
                fontSize:      '1rem',
                fontWeight:    600,
                color:         'var(--astra-ink)',
                lineHeight:    1.2,
              }}
            >
              Autonomous Intelligence Workbench
            </h2>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5625rem', color: 'var(--astra-slate)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
              Deterministic On-Premise Workflow · Evidence-Grounded
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isLoading && (
            <span
              style={{
                fontFamily:  'var(--font-mono)',
                fontSize:    '0.625rem',
                color:       'var(--agni-copper)',
                letterSpacing:'0.08em',
                textTransform:'uppercase',
                fontWeight:  600,
              }}
              className="flex items-center gap-1.5"
            >
              <span className="agni-bindu live" />
              Processing
            </span>
          )}
        </div>
      </div>

      <div className="p-6 space-y-5">
        {/* ── Workflow presets ───────────────────────────── */}
        <div>
          <div className="astra-label mb-3">Select Analytical Workflow Preset</div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {PRESETS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => selectPreset(idx)}
                className={`preset-card ${activePreset === idx ? 'active' : ''}`}
                aria-pressed={activePreset === idx}
              >
                <div className="flex items-start justify-between gap-2 mb-1">
                  <span
                    style={{
                      fontFamily: 'var(--font-sans)',
                      fontSize:   '0.8125rem',
                      fontWeight: 600,
                      color:      activePreset === idx ? 'var(--agni-red)' : 'var(--astra-ink)',
                      lineHeight: 1.3,
                    }}
                  >
                    {preset.title}
                  </span>
                  <span className="intel-tag flex-shrink-0">{preset.tag}</span>
                </div>
                <p
                  style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize:   '0.6875rem',
                    color:      'var(--astra-slate)',
                    lineHeight: 1.5,
                    display:    '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient:'vertical',
                    overflow:   'hidden',
                  }}
                >
                  {preset.prompt}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* ── Task instruction textarea ──────────────────── */}
        <div>
          <label
            htmlFor="intel-query"
            className="astra-label mb-2 block"
          >
            Intelligence Query / Task Instruction
          </label>
          <textarea
            id="intel-query"
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="intel-textarea"
            placeholder="Specify an intelligence task, document analysis request, or engineering calculation…"
          />
        </div>

        {/* ── File & action bar ─────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
          <div className="flex items-center gap-3">
            <label className="btn-secondary cursor-pointer">
              <Upload className="w-3.5 h-3.5" style={{ color: 'var(--agni-copper)' }} />
              <span>Upload Document</span>
              <input
                type="file"
                className="hidden"
                accept=".pdf,.png,.jpg,.jpeg,.csv"
                onChange={handleFileUpload}
              />
            </label>
            <span
              className="flex items-center gap-1.5"
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize:   '0.6875rem',
                color:      'var(--astra-slate)',
              }}
            >
              <FileText className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--agni-copper)' }} />
              {uploadStatus}
            </span>
          </div>

          <button
            onClick={handleExecute}
            disabled={isLoading}
            className="btn-primary"
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Executing Agent…</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Execute Autonomous Workflow</span>
              </>
            )}
          </button>
        </div>

        {/* ── Active Loading State (Section 19) ─────────── */}
        {isLoading && (
          <div className="my-8 py-6 flex flex-col items-center justify-center rounded-xl bg-astra-sandstone/30 border border-astra-sandstone-dark/50">
            <AgniLoadingMark
              size={56}
              label="SYNTHESIZING INTELLIGENCE & EXECUTING REASONING PIPELINE..."
            />
          </div>
        )}

        {/* ── Response card ─────────────────────────────── */}
        {latestResponse && !isLoading && (
          <div
            className="mt-2 rounded-xl overflow-hidden"
            style={{
              border:    '1px solid var(--astra-sandstone-dark)',
              background:'var(--astra-sandstone)',
              animation: 'fadeUp 0.3s ease-out',
            }}
          >
            {/* Dossier Institutional Header (Sections 20 & 21) */}
            <div
              className="px-6 py-4 flex items-center justify-between border-b border-astra-sandstone-dark bg-astra-ivory"
            >
              <AgniLogo
                variant="full"
                size={34}
                theme="light"
                showAstraAttribution={true}
              />
              <AstraSeal
                size={62}
                caption="AUTHENTICATED DOSSIER"
                provenanceId={latestResponse.task_id ? latestResponse.task_id.substring(0, 14) : 'AGNI-COR-01'}
              />
            </div>

            {/* Response metadata strip */}
            <div
              className="px-5 py-3 flex flex-wrap items-center justify-between gap-3"
              style={{ borderBottom: '1px solid var(--astra-sandstone-dark)', background: 'var(--astra-ivory)' }}
            >
              <div className="flex flex-wrap items-center gap-2">
                {/* Model badge */}
                <div
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg"
                  style={{
                    background:  'rgba(46,58,94,0.07)',
                    border:      '1px solid rgba(46,58,94,0.15)',
                    fontFamily:  'var(--font-mono)',
                    fontSize:    '0.625rem',
                    color:       'var(--astra-indigo)',
                    fontWeight:  700,
                  }}
                >
                  <Zap className="w-3 h-3" />
                  {latestResponse.selected_model || 'Local Model'}
                </div>

                {latestResponse.task_type && (
                  <span className="intel-tag">
                    {latestResponse.task_type}
                  </span>
                )}

                {latestResponse.total_duration_ms !== undefined && latestResponse.total_duration_ms > 0 && (
                  <span
                    className="flex items-center gap-1"
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   '0.625rem',
                      color:      'var(--astra-slate)',
                    }}
                  >
                    <Clock className="w-3 h-3" />
                    {(latestResponse.total_duration_ms / 1000).toFixed(1)}s
                  </span>
                )}
              </div>

              {/* Verification status */}
              <div className="flex items-center gap-2">
                {latestResponse.verification && (
                  <span
                    className={`confidence-badge ${latestResponse.verification.status === 'passed' ? 'high' : 'low'}`}
                  >
                    {latestResponse.verification.status === 'passed' ? (
                      <><CheckCircle2 className="w-3 h-3" /> 8-Point Verified</>
                    ) : (
                      <><XCircle className="w-3 h-3" /> Verification Failed</>
                    )}
                  </span>
                )}

                {latestResponse.summary?.includes('DEGRADED MODE') ? (
                  <span className="confidence-badge medium">
                    <AlertTriangle className="w-3 h-3" /> Degraded Mode
                  </span>
                ) : latestResponse.task_type === 'inspection_workflow' ? (
                  <span className="confidence-badge high">
                    <ShieldCheck className="w-3 h-3" /> Live Extraction
                  </span>
                ) : null}
              </div>
            </div>

            {/* Routing rationale */}
            {latestResponse.routing_reason && (
              <div
                className="px-5 py-3 flex items-start gap-3"
                style={{ borderBottom: '1px solid var(--astra-sandstone-dark)', background: 'var(--astra-ivory)' }}
              >
                <span
                  style={{
                    fontFamily:    'var(--font-mono)',
                    fontSize:      '0.5625rem',
                    fontWeight:    700,
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    color:         'var(--agni-copper)',
                    background:    'rgba(182,106,60,0.08)',
                    border:        '1px solid rgba(182,106,60,0.2)',
                    padding:       '2px 8px',
                    borderRadius:  '4px',
                    flexShrink:    0,
                    alignSelf:     'flex-start',
                    marginTop:     '1px',
                  }}
                >
                  Routing
                </span>
                <span
                  style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize:   '0.8125rem',
                    color:      'var(--astra-slate)',
                    fontStyle:  'italic',
                    lineHeight: 1.5,
                  }}
                >
                  {latestResponse.routing_reason}
                </span>
              </div>
            )}

            {/* Summary content */}
            <div
              className="px-5 py-4"
              style={{
                fontFamily: 'var(--font-sans)',
                fontSize:   '0.9rem',
                color:      'var(--astra-ink)',
                lineHeight: 1.7,
                whiteSpace: 'pre-wrap',
              }}
            >
              {latestResponse.summary}
            </div>

            {/* Verification guardrails */}
            {latestResponse.verification?.checks && (
              <div
                className="px-5 py-4"
                style={{ borderTop: '1px solid var(--astra-sandstone-dark)' }}
              >
                <div className="astra-label mb-3">Automated Verification Guardrails</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {latestResponse.verification.checks.map((c, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 px-3 py-2.5 rounded-lg"
                      style={{
                        background: c.passed ? 'rgba(45,106,79,0.06)' : 'rgba(192,57,43,0.05)',
                        border:     `1px solid ${c.passed ? 'rgba(45,106,79,0.15)' : 'rgba(192,57,43,0.15)'}`,
                      }}
                    >
                      {c.passed ? (
                        <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" style={{ color: 'var(--status-positive)' }} />
                      ) : (
                        <XCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" style={{ color: 'var(--status-critical)' }} />
                      )}
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', color: 'var(--astra-ink)', lineHeight: 1.5 }}>
                        <span style={{ fontWeight: 700, color: c.passed ? 'var(--status-positive)' : 'var(--status-critical)' }}>
                          {c.name}
                        </span>
                        {c.details && (
                          <span style={{ color: 'var(--astra-slate)', marginLeft: '4px' }}>— {c.details}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Disclaimer */}
            <div
              className="px-5 py-2.5"
              style={{
                borderTop:  '1px solid var(--astra-sandstone-dark)',
                fontFamily: 'var(--font-mono)',
                fontSize:   '0.5625rem',
                color:      'var(--astra-slate)',
                textAlign:  'right',
                fontStyle:  'italic',
              }}
            >
              Demo corpus — synthetic/public industrial demonstration documents; no proprietary information included.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
