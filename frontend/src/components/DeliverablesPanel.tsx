import React from 'react';
import { FileText, Download, CheckCircle, ShieldCheck } from 'lucide-react';
import { OutputDeliverable } from '../types';
import { getDeliverableDownloadUrl } from '../api/client';

interface DeliverablesPanelProps {
  outputs: OutputDeliverable[];
}

const FILE_TYPE_COLORS: Record<string, { bg: string; color: string; border: string }> = {
  docx: { bg: 'rgba(46,58,94,0.08)',  color: 'var(--astra-indigo)',    border: 'rgba(46,58,94,0.18)'  },
  xlsx: { bg: 'rgba(45,106,79,0.08)', color: 'var(--status-positive)', border: 'rgba(45,106,79,0.18)' },
  pdf:  { bg: 'rgba(126,36,29,0.07)', color: 'var(--agni-red)',        border: 'rgba(126,36,29,0.15)' },
  png:  { bg: 'rgba(182,106,60,0.07)',color: 'var(--agni-copper)',      border: 'rgba(182,106,60,0.18)'},
};

export const DeliverablesPanel: React.FC<DeliverablesPanelProps> = ({ outputs }) => {
  if (!outputs || !outputs.length) return null;

  return (
    <div
      className="astra-card"
      style={{
        padding:  0,
        overflow: 'hidden',
        border:   '1px solid rgba(45,106,79,0.25)',
        boxShadow:'0 4px 20px rgba(45,106,79,0.08)',
      }}
    >
      {/* Card header */}
      <div
        className="px-5 py-3.5 flex items-center justify-between"
        style={{
          borderBottom: '1px solid rgba(45,106,79,0.18)',
          background:   'rgba(45,106,79,0.05)',
        }}
      >
        <div className="flex items-center gap-2.5">
          <FileText className="w-4 h-4" style={{ color: 'var(--status-positive)' }} />
          <h3
            style={{
              fontFamily: 'var(--font-display)',
              fontSize:   '0.9375rem',
              fontWeight: 600,
              color:      'var(--astra-ink)',
            }}
          >
            Verified Deliverables
          </h3>
        </div>
        <span
          className="flex items-center gap-1.5"
          style={{
            fontFamily:  'var(--font-mono)',
            fontSize:    '0.5625rem',
            fontWeight:  700,
            letterSpacing:'0.1em',
            textTransform:'uppercase',
            color:       'var(--status-positive)',
          }}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          Integrity Verified
        </span>
      </div>

      <div className="p-4 space-y-3">
        {outputs.map((out, idx) => {
          const ext   = out.type.toLowerCase();
          const style = FILE_TYPE_COLORS[ext] || FILE_TYPE_COLORS.docx;

          return (
            <div
              key={idx}
              className="flex items-center justify-between p-4 rounded-xl"
              style={{
                background: 'var(--astra-ivory)',
                border:     '1px solid var(--astra-sandstone-dark)',
                animation:  `fadeUp 0.3s ease-out ${idx * 0.08}s both`,
                transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
              }}
              onMouseOver={e => {
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(45,106,79,0.35)';
                (e.currentTarget as HTMLElement).style.boxShadow  = '0 4px 16px rgba(45,106,79,0.10)';
              }}
              onMouseOut={e => {
                (e.currentTarget as HTMLElement).style.borderColor = 'var(--astra-sandstone-dark)';
                (e.currentTarget as HTMLElement).style.boxShadow  = 'none';
              }}
            >
              <div className="flex items-center gap-3.5">
                {/* File type icon */}
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: style.bg, border: `1px solid ${style.border}` }}
                >
                  <FileText className="w-4.5 h-4.5" style={{ color: style.color }} />
                </div>

                <div>
                  <h4
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   '0.8125rem',
                      fontWeight: 700,
                      color:      'var(--astra-ink)',
                      marginBottom:'2px',
                    }}
                  >
                    {out.filename}
                  </h4>
                  <div
                    className="flex items-center gap-2"
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize:   '0.625rem',
                      color:      'var(--astra-slate)',
                    }}
                  >
                    <span
                      className="px-1.5 py-0.5 rounded"
                      style={{ background: style.bg, color: style.color, border: `1px solid ${style.border}`, fontWeight: 700 }}
                    >
                      {out.type.toUpperCase()}
                    </span>
                    <span>{(out.size_bytes / 1024).toFixed(1)} KB</span>
                    <span className="flex items-center gap-1" style={{ color: 'var(--status-positive)', fontWeight: 600 }}>
                      <CheckCircle className="w-3 h-3" />
                      Sign-off Ready
                    </span>
                  </div>
                </div>
              </div>

              <a
                href={getDeliverableDownloadUrl(out.filename)}
                download={out.filename}
                className="btn-secondary !px-3 !py-2 !text-xs"
                style={{ gap: '6px', flexShrink: 0 }}
              >
                <Download className="w-3.5 h-3.5" />
                Download
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
};
