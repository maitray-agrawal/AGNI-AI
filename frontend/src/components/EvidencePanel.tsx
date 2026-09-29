import React from 'react';
import { BookOpen, FileCheck, MapPin } from 'lucide-react';
import { AstraMark } from './AstraMark';

interface EvidencePanelProps {
  citations?: Array<{
    document: string;
    page:     number;
    section:  string;
    text:     string;
  }>;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ citations }) => {
  if (!citations || !citations.length) {
    return (
      <div
        className="astra-card flex flex-col items-center justify-center py-10 text-center"
        style={{ minHeight: 160 }}
      >
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center mb-3"
          style={{ background: 'var(--astra-sandstone)', color: 'var(--astra-slate)' }}
        >
          <BookOpen className="w-4.5 h-4.5" />
        </div>
        <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.8125rem', color: 'var(--astra-slate)', maxWidth: '26ch', lineHeight: 1.6 }}>
          No retrieved citations. Knowledge sources appear here upon RAG retrieval.
        </p>
      </div>
    );
  }

  return (
    <div className="astra-card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Card header */}
      <div
        className="px-5 py-3.5 flex items-center gap-2.5"
        style={{
          borderBottom: '1px solid var(--astra-sandstone-dark)',
          background:   'var(--astra-sandstone)',
        }}
      >
        <BookOpen className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--agni-copper)' }} />
        <h3
          style={{
            fontFamily: 'var(--font-display)',
            fontSize:   '0.9375rem',
            fontWeight: 600,
            color:      'var(--astra-ink)',
          }}
        >
          Grounded Source Citations
        </h3>
        <span className="intel-tag ml-auto">Local RAG</span>
      </div>

      {/* Citations */}
      <div className="p-4 space-y-3">
        {citations.map((c, i) => (
          <div
            key={i}
            className="evidence-card"
            style={{ animation: `fadeUp 0.3s ease-out ${i * 0.08}s both` }}
          >
            {/* Source metadata */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-2 min-w-0">
                <FileCheck className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--status-positive)' }} />
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize:   '0.6875rem',
                    fontWeight: 700,
                    color:      'var(--astra-indigo)',
                    overflow:   'hidden',
                    textOverflow:'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {c.document}
                </span>
              </div>
              <div
                className="flex items-center gap-1 flex-shrink-0 px-2 py-0.5 rounded"
                style={{
                  background:  'var(--astra-sandstone)',
                  border:      '1px solid var(--astra-sandstone-dark)',
                  fontFamily:  'var(--font-mono)',
                  fontSize:    '0.5625rem',
                  color:       'var(--astra-slate)',
                  fontWeight:  600,
                  whiteSpace:  'nowrap',
                }}
              >
                <MapPin className="w-2.5 h-2.5" style={{ color: 'var(--agni-copper)' }} />
                <span>p.{c.page}</span>
              </div>
            </div>

            {/* Section reference */}
            <div
              className="mb-2"
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize:   '0.5625rem',
                color:      'var(--astra-slate)',
                letterSpacing:'0.04em',
              }}
            >
              {c.section}
            </div>

            {/* Citation text */}
            <blockquote
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize:   '0.8125rem',
                color:      'var(--astra-ink)',
                lineHeight: 1.65,
                fontStyle:  'italic',
                margin:     0,
                paddingLeft:'10px',
                borderLeft: '2px solid var(--agni-copper)',
              }}
            >
              "{c.text}"
            </blockquote>

            {/* Confidence indicator */}
            <div className="mt-2 flex items-center gap-2">
              <span className="confidence-badge high">
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--status-positive)', display: 'inline-block' }} />
                High Confidence
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--astra-slate-light)' }}>
                Local Vector DB · Qdrant
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div
        className="px-5 py-2.5"
        style={{
          borderTop:  '1px solid var(--astra-sandstone-dark)',
          fontFamily: 'var(--font-mono)',
          fontSize:   '0.5625rem',
          color:      'var(--astra-slate)',
          fontStyle:  'italic',
        }}
      >
        Demo corpus — synthetic/public industrial demonstration documents; no proprietary information included.
      </div>
    </div>
  );
};
