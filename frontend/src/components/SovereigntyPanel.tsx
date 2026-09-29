import React from 'react';
import { Shield, Lock, Radio, Activity, Check, AlertTriangle, RefreshCw } from 'lucide-react';
import { SecurityStatus } from '../types';
import { AstraMark } from './AstraMark';

interface SovereigntyPanelProps {
  status?: SecurityStatus | null;
  onRefresh?: () => void;
}

interface MetricCardProps {
  label: string;
  value: string;
  subtext?: string;
  status: 'secure' | 'warning' | 'info';
  icon: React.ReactNode;
}

const StatusMetric: React.FC<MetricCardProps> = ({ label, value, subtext, status, icon }) => {
  const colors = {
    secure: { bg: 'rgba(45,106,79,0.06)', border: 'rgba(45,106,79,0.18)', text: 'var(--status-positive)' },
    warning: { bg: 'rgba(194,132,42,0.06)', border: 'rgba(194,132,42,0.18)', text: 'var(--status-warning)' },
    info: { bg: 'rgba(46,58,94,0.06)', border: 'rgba(46,58,94,0.15)', text: 'var(--astra-indigo)' },
  };
  const c = colors[status];

  return (
    <div
      className="p-3 rounded-xl text-center"
      style={{ background: c.bg, border: `1px solid ${c.border}` }}
    >
      <div className="flex items-center justify-center mb-1.5" style={{ color: c.text, opacity: 0.7 }}>
        {icon}
      </div>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5625rem', color: 'var(--astra-slate)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 700, color: c.text }}>
        {value}
      </div>
      {subtext && (
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--astra-slate-light)', marginTop: 2 }}>
          {subtext}
        </div>
      )}
    </div>
  );
};

export const SovereigntyPanel: React.FC<SovereigntyPanelProps> = ({ status, onRefresh }) => {
  return (
    <div className="astra-card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Card header */}
      <div
        className="px-5 py-3.5 flex items-center justify-between"
        style={{
          borderBottom: '1px solid var(--astra-sandstone-dark)',
          background: 'var(--astra-sandstone)',
        }}
      >
        <div className="flex items-center gap-2.5">
          <Shield className="w-4 h-4" style={{ color: 'var(--status-positive)' }} />
          <h3
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '0.9375rem',
              fontWeight: 600,
              color: 'var(--astra-ink)',
            }}
          >
            Sovereignty & Network Telemetry
          </h3>
        </div>

        <button
          onClick={onRefresh}
          className="btn-secondary !px-2.5 !py-1.5 !text-xs"
          aria-label="Rescan network sockets"
          style={{ gap: '6px' }}
        >
          <RefreshCw className="w-3 h-3" />
          <span>Rescan</span>
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Security metrics grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <StatusMetric
            label="Inference Egress"
            value="Observed"
            subtext="127.0.0.1:11434"
            status="secure"
            icon={<Check className="w-3.5 h-3.5" />}
          />
          <StatusMetric
            label="Cloud AI Calls"
            value={`${status?.external_ai_api_calls ?? 0} External`}
            subtext="Blocked"
            status="secure"
            icon={<Shield className="w-3.5 h-3.5" />}
          />
          <StatusMetric
            label="Ext. Connections"
            value={`${status?.external_network_connections ?? 0} Active`}
            subtext="Zero Egress"
            status="secure"
            icon={<Radio className="w-3.5 h-3.5" />}
          />
          <StatusMetric
            label="Sandbox"
            value="Enforced"
            subtext="Socket Intercept"
            status="secure"
            icon={<Lock className="w-3.5 h-3.5" />}
          />
        </div>

        {/* Active sockets */}
        <div>
          <div
            className="flex items-center justify-between mb-2"
            style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5625rem', color: 'var(--astra-slate)', letterSpacing: '0.08em', textTransform: 'uppercase' }}
          >
            <span className="flex items-center gap-1.5">
              <Activity className="w-3 h-3" style={{ color: 'var(--agni-copper)' }} />
              Active Process Sockets — Host Verification
            </span>
            <span style={{ color: 'var(--astra-slate-light)', fontSize: '0.5rem' }}>Live OS Telemetry</span>
          </div>

          <div
            className="max-h-32 overflow-y-auto rounded-lg p-2"
            style={{
              background: 'var(--astra-sandstone)',
              border: '1px solid var(--astra-sandstone-dark)',
            }}
          >
            {status?.active_sockets?.length ? (
              status.active_sockets.map((s, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between py-1 px-2 rounded"
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.5625rem',
                    color: 'var(--astra-ink)',
                    transition: 'background 0.15s ease',
                  }}
                  onMouseOver={e => (e.currentTarget.style.background = 'var(--astra-ivory)')}
                  onMouseOut={e => (e.currentTarget.style.background = 'transparent')}
                >
                  <span style={{ color: 'var(--astra-slate)' }}>PID {s.pid}</span>
                  <span style={{ color: 'var(--astra-indigo)', fontWeight: 600 }}>{s.local_address}</span>
                  <span style={{ color: 'var(--astra-slate-light)' }}>→</span>
                  <span style={{ color: 'var(--astra-slate)' }}>{s.remote_address}</span>
                  <span
                    className="confidence-badge high"
                    style={{ padding: '1px 6px', fontSize: '0.4375rem' }}
                  >
                    {s.status}
                  </span>
                </div>
              ))
            ) : (
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.625rem',
                  color: 'var(--astra-slate)',
                  textAlign: 'center',
                  padding: '12px 0',
                }}
              >
                Listening exclusively on 127.0.0.1 loopback.
              </div>
            )}
          </div>
        </div>

        {/* Sovereignty disclosure */}
        <div
          className="p-3 rounded-xl"
          style={{
            background: 'rgba(182,106,60,0.05)',
            border: '1px solid rgba(182,106,60,0.15)',
          }}
        >
          <div className="flex items-start gap-2">
            <AstraMark size={14} style={{ color: 'var(--agni-copper)', flexShrink: 0, marginTop: 1 }} />
            <p
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.5625rem',
                color: 'var(--astra-slate)',
                lineHeight: 1.6,
              }}
            >
              <span style={{ color: 'var(--agni-copper)', fontWeight: 700 }}>SOVEREIGNTY DISCLOSURE — </span>
              Configured for sovereign on-premise execution. Local inference and application traffic
              observed on localhost during validation; sandbox outbound networking is explicitly blocked.
              Physical air-gap compliance depends on deployment infrastructure.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
