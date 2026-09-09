import React from 'react';
import { FileText, Download, CheckCircle, ShieldCheck } from 'lucide-react';
import { OutputDeliverable } from '../types';
import { getDeliverableDownloadUrl } from '../api/client';

interface DeliverablesPanelProps {
  outputs: OutputDeliverable[];
}

export const DeliverablesPanel: React.FC<DeliverablesPanelProps> = ({ outputs }) => {
  if (!outputs || !outputs.length) {
    return null;
  }

  return (
    <div className="rounded-xl border border-emerald-500/30 bg-[#0f172a]/90 overflow-hidden shadow-xl">
      <div className="px-5 py-3.5 border-b border-emerald-500/20 bg-emerald-950/30 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide">VERIFIED INDUSTRIAL DELIVERABLES</h3>
        </div>
        <span className="flex items-center space-x-1 text-xs text-emerald-400 font-mono">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Integrity Verified</span>
        </span>
      </div>

      <div className="p-5 space-y-3">
        {outputs.map((out, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-4 rounded-lg border border-slate-800 bg-slate-950/60 hover:border-emerald-500/40 transition-all"
          >
            <div className="flex items-center space-x-3.5">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                <FileText className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-white font-mono">{out.filename}</h4>
                <div className="flex items-center space-x-2 text-xs text-slate-400 mt-0.5 font-mono">
                  <span>Type: {out.type.toUpperCase()}</span>
                  <span>•</span>
                  <span>Size: {(out.size_bytes / 1024).toFixed(1)} KB</span>
                  <span>•</span>
                  <span className="text-emerald-400 flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1 inline" /> Sign-off Ready
                  </span>
                </div>
              </div>
            </div>

            <a
              href={getDeliverableDownloadUrl(out.filename)}
              download={out.filename}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-900/30"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Deliverable</span>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};
