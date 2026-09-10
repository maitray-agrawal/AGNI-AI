import React from 'react';
import { BookOpen, FileCheck, MapPin } from 'lucide-react';

interface EvidencePanelProps {
  citations?: Array<{
    document: string;
    page: number;
    section: string;
    text: string;
  }>;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ citations }) => {
  if (!citations || !citations.length) {
    return (
      <div className="rounded-xl border border-slate-800 bg-[#0f172a]/60 p-6 text-center text-slate-400 text-sm">
        <BookOpen className="w-8 h-8 mx-auto mb-2 text-slate-600 opacity-60" />
        No retrieved knowledge citations. Citations from Qdrant appear here upon RAG retrieval.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0f172a]/80 overflow-hidden shadow-xl">
      <div className="px-5 py-3.5 border-b border-slate-800/80 bg-slate-900/40 flex items-center space-x-2">
        <BookOpen className="w-4 h-4 text-sky-400" />
        <h3 className="text-sm font-semibold text-white tracking-wide">GROUNDED INDUSTRIAL CITATIONS (LOCAL RAG)</h3>
      </div>

      <div className="p-5 space-y-3">
        {citations.map((c, i) => (
          <div key={i} className="p-3.5 rounded-lg border border-slate-800/80 bg-slate-950/50 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileCheck className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-xs text-sky-300 font-mono">{c.document}</span>
              </div>
              <div className="flex items-center space-x-1 text-[11px] text-slate-400 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                <MapPin className="w-3 h-3 text-orange-400" />
                <span>Page {c.page} • {c.section}</span>
              </div>
            </div>
            <p className="text-xs text-slate-300 italic border-l-2 border-slate-700 pl-3 leading-relaxed">
              "{c.text}"
            </p>
          </div>
        ))}
      </div>

      <div className="px-5 py-2.5 bg-slate-900/40 border-t border-slate-800/80 text-[10px] text-slate-500 font-mono italic">
        Demo corpus — synthetic/public industrial demonstration documents; no proprietary MRPL information is included.
      </div>
    </div>
  );
};
