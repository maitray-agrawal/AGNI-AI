import React from 'react';
import { Shield, Cpu, Database, Flame } from 'lucide-react';

interface HeaderProps {
  airGapped: boolean;
  activeModel?: string;
}

export const Header: React.FC<HeaderProps> = ({ airGapped, activeModel }) => {
  return (
    <header className="border-b border-slate-800 bg-[#0b1120]/90 backdrop-blur px-6 py-4 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Identity */}
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
            <Flame className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white font-mono">AGNI-AI</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-md bg-orange-500/10 text-orange-400 border border-orange-500/20">
                MRPL SOVEREIGN
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Agentic Government Neural Intelligence • SIH PS 26117
            </p>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center space-x-4">
          {/* Active Model */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <Cpu className="w-3.5 h-3.5 text-sky-400" />
            <span className="text-slate-400">Runtime:</span>
            <span className="font-mono text-slate-200">{activeModel || 'Ollama (Local)'}</span>
          </div>

          {/* Local Vector DB */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400">RAG:</span>
            <span className="font-mono text-slate-200">Qdrant (Disk)</span>
          </div>

          {/* Sovereignty Badge */}
          <div className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-xs font-medium shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <Shield className="w-3.5 h-3.5" />
            <span className="tracking-wide font-mono font-semibold">SOVEREIGN AIR-GAP</span>
          </div>
        </div>
      </div>
    </header>
  );
};
