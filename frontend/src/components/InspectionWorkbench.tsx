import React, { useState } from 'react';
import { Play, Upload, FileText, CheckCircle2, XCircle, Sparkles, RefreshCw } from 'lucide-react';
import { TaskRunResponse } from '../types';
import { submitTask, uploadDocument } from '../api/client';

interface InspectionWorkbenchProps {
  onTaskCompleted: (res: TaskRunResponse) => void;
  isLoading: boolean;
  setIsLoading: (v: boolean) => void;
  latestResponse: TaskRunResponse | null;
}

export const InspectionWorkbench: React.FC<InspectionWorkbenchProps> = ({
  onTaskCompleted,
  isLoading,
  setIsLoading,
  latestResponse,
}) => {
  const [prompt, setPrompt] = useState<string>(
    'Analyze this inspection report, identify critical findings, consult relevant local procedures, determine the recommended action, verify the result and generate an approval note.'
  );
  const [selectedFile, setSelectedFile] = useState<string>(
    'data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf'
  );
  const [uploadStatus, setUploadStatus] = useState<string>('Preloaded: MRPL_Inspection_Report_P204.pdf');

  const presets = [
    {
      title: 'Flagship: Inspection Approval Note',
      prompt: 'Analyze this inspection report, identify critical findings, consult relevant local procedures, determine the recommended action, verify the result and generate an approval note.',
      file: 'data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf',
    },
    {
      title: 'Calculation: Wall Thickness Reduction',
      prompt: 'Calculate the percentage reduction from 8.2 mm to 4.2 mm wall thickness for Heavy Gas Oil piping and compare against 4.0 mm API 570 retirement limit.',
      file: '',
    },
    {
      title: 'P&ID: Unit Flow & Valve Inspection',
      prompt: 'Inspect the CDU-II pump P-204 A/B P&ID schematic. Identify feed vessel, pumps, critical discharge elbow, and flow control valve FCV-204.',
      file: 'data/raw/pidqa/pid_cdu_pump_p204.png',
    },
  ];

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    const file = e.target.files[0];
    try {
      setUploadStatus(`Uploading ${file.name}...`);
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
      const res = await submitTask(prompt, files);
      onTaskCompleted(res);
    } catch (err: any) {
      alert(`Execution failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0f172a]/90 overflow-hidden shadow-2xl">
      <div className="px-6 py-4 border-b border-slate-800/80 bg-slate-900/50 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-orange-400" />
          <h2 className="text-base font-bold text-white tracking-wide">AUTONOMOUS WORKBENCH</h2>
        </div>
        <span className="text-xs font-mono text-slate-400">Deterministic On-Premise Workflow</span>
      </div>

      <div className="p-6 space-y-5">
        {/* Presets Row */}
        <div>
          <label className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-2 block">
            Select Industrial Workflow Preset
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {presets.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setPrompt(preset.prompt);
                  setSelectedFile(preset.file);
                  setUploadStatus(preset.file ? `Selected: ${preset.file.split('/').pop()}` : 'No file required');
                }}
                className={`p-3 rounded-lg border text-left transition-all text-xs font-sans ${
                  prompt === preset.prompt
                    ? 'border-orange-500/60 bg-orange-500/10 text-white shadow-sm'
                    : 'border-slate-800 bg-slate-950/40 text-slate-300 hover:bg-slate-900/60'
                }`}
              >
                <div className="font-semibold">{preset.title}</div>
                <div className="text-[11px] text-slate-500 mt-1 truncate">{preset.prompt}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Input Textarea */}
        <div>
          <label className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-1.5 block">
            Task Instruction / Engineering Query
          </label>
          <textarea
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full rounded-lg border border-slate-800 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 font-mono transition leading-relaxed"
            placeholder="Specify industrial task, document analysis request, or engineering calculation..."
          />
        </div>

        {/* File Selection & Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
          <div className="flex items-center space-x-3">
            <label className="cursor-pointer flex items-center space-x-2 px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-mono transition">
              <Upload className="w-3.5 h-3.5 text-sky-400" />
              <span>Upload Document</span>
              <input
                type="file"
                className="hidden"
                accept=".pdf,.png,.jpg,.jpeg,.csv"
                onChange={handleFileUpload}
              />
            </label>
            <span className="text-xs text-slate-400 font-mono flex items-center">
              <FileText className="w-3.5 h-3.5 mr-1.5 text-orange-400 inline" />
              {uploadStatus}
            </span>
          </div>

          <button
            onClick={handleExecute}
            disabled={isLoading}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-lg bg-gradient-to-r from-orange-600 via-amber-600 to-orange-500 hover:from-orange-500 hover:to-amber-500 text-white font-bold text-xs tracking-wider uppercase transition shadow-lg shadow-orange-600/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Executing Agent...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Execute Autonomous Workflow</span>
              </>
            )}
          </button>
        </div>

        {/* Latest Response & Synthesis Card */}
        {latestResponse && (
          <div className="mt-5 rounded-lg border border-slate-800 bg-slate-950/70 p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-400 font-mono">Assigned Model:</span>
                <span className="px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono text-xs font-bold">
                  {latestResponse.selected_model || 'Local Model'}
                </span>
              </div>

              {latestResponse.verification && (
                <span
                  className={`flex items-center space-x-1.5 text-xs font-mono font-semibold px-2.5 py-0.5 rounded ${
                    latestResponse.verification.status === 'passed'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}
                >
                  {latestResponse.verification.status === 'passed' ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>8-POINT VERIFICATION PASSED</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-3.5 h-3.5" />
                      <span>VERIFICATION FAILED</span>
                    </>
                  )}
                </span>
              )}
            </div>

            {/* Structured Synthesis Content */}
            <div className="text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
              {latestResponse.summary}
            </div>

            {/* Verification checklist pills */}
            {latestResponse.verification?.checks && (
              <div className="pt-2 border-t border-slate-800/80">
                <div className="text-[11px] font-mono text-slate-400 mb-2">Automated Verification Guardrails:</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
                  {latestResponse.verification.checks.map((c, i) => (
                    <div
                      key={i}
                      className="flex items-center space-x-2 p-2 rounded bg-slate-900/60 border border-slate-800/60"
                    >
                      {c.passed ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : (
                        <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                      )}
                      <div className="truncate">
                        <span className="text-slate-300 font-semibold">{c.name}: </span>
                        <span className="text-slate-500">{c.details}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
