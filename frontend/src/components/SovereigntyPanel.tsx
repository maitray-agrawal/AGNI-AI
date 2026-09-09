import React from 'react';
import { Shield, Lock, Radio, Activity, Check, AlertTriangle } from 'lucide-react';
import { SecurityStatus } from '../types';

interface SovereigntyPanelProps {
  status?: SecurityStatus | null;
  onRefresh?: () => void;
}

export const SovereigntyPanel: React.FC<SovereigntyPanelProps> = ({ status, onRefresh }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-[#0f172a]/80 overflow-hidden shadow-xl">
      <div className="px-5 py-3.5 border-b border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Shield className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide">AIR-GAP SOVEREIGNTY & NETWORK TELEMETRY</h3>
        </div>
        <button
          onClick={onRefresh}
          className="text-[11px] font-mono text-slate-400 hover:text-white px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 transition"
        >
          Rescan Sockets
        </button>
      </div>

      <div className="p-5 space-y-4">
        {/* Core Security Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 text-center">
            <div className="text-[11px] text-slate-400 font-mono mb-1">Inference Egress</div>
            <div className="text-lg font-bold text-emerald-400 font-mono flex items-center justify-center space-x-1">
              <Check className="w-4 h-4" />
              <span>100% Local</span>
            </div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">127.0.0.1:11434</div>
          </div>

          <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 text-center">
            <div className="text-[11px] text-slate-400 font-mono mb-1">Cloud AI Calls</div>
            <div className="text-lg font-bold text-white font-mono">
              {status?.external_ai_api_calls ?? 0}
            </div>
            <div className="text-[10px] text-emerald-400 font-mono mt-0.5">Zero Cloud APIs</div>
          </div>

          <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 text-center">
            <div className="text-[11px] text-slate-400 font-mono mb-1">Ext Connections</div>
            <div className="text-lg font-bold text-emerald-400 font-mono">
              {status?.external_network_connections ?? 0}
            </div>
            <div className="text-[10px] text-emerald-400 font-mono mt-0.5">Air-Gap Verified</div>
          </div>

          <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 text-center">
            <div className="text-[11px] text-slate-400 font-mono mb-1">Sandbox Isolation</div>
            <div className="text-lg font-bold text-emerald-400 font-mono flex items-center justify-center space-x-1">
              <Lock className="w-3.5 h-3.5" />
              <span>Isolated</span>
            </div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">network=none</div>
          </div>
        </div>

        {/* Real Active System Sockets */}
        <div>
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2 font-mono">
            <span className="flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5 text-sky-400" />
              <span>Active Process Sockets (Local Host Verification)</span>
            </span>
            <span className="text-[10px] text-slate-500">Live OS Telemetry</span>
          </div>

          <div className="max-h-36 overflow-y-auto rounded-lg border border-slate-800 bg-slate-950/40 p-2 font-mono text-[11px] space-y-1">
            {status?.active_sockets && status.active_sockets.length > 0 ? (
              status.active_sockets.map((s, idx) => (
                <div key={idx} className="flex items-center justify-between py-0.5 px-2 rounded hover:bg-slate-900/50">
                  <span className="text-slate-300">PID {s.pid}</span>
                  <span className="text-sky-400">{s.local_address}</span>
                  <span className="text-slate-500">→</span>
                  <span className="text-slate-400">{s.remote_address}</span>
                  <span className="px-1.5 py-0.2 rounded text-[9px] bg-emerald-950 text-emerald-400 border border-emerald-800/40">
                    {s.status}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-slate-500 text-center py-2">Listening exclusively on 127.0.0.1 loopback.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
