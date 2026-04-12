'use client';

import type { HITLRequest } from '@/lib/ws-client';
import { Check, ShieldAlert, X } from 'lucide-react';
import { useState } from 'react';

interface Props {
  request: HITLRequest;
  onRespond: (action: 'approve' | 'reject', feedback?: string) => void;
}

export function HITLCard({ request, onRespond }: Props) {
  const [feedback, setFeedback] = useState('');

  return (
    <div className="glass-panel rounded-2xl p-5 mb-4 border-l-4 border-obs-primary-container neural-glow">
      <div className="flex items-center gap-2 mb-3">
        <ShieldAlert className="h-5 w-5 text-obs-primary-container" />
        <h4 className="font-headline text-sm font-bold text-obs-on-surface">
          Human Review Required
        </h4>
        <span className="font-label text-[10px] uppercase tracking-widest text-obs-primary px-2 py-0.5 rounded bg-obs-primary/10">
          {request.checkpoint}
        </span>
      </div>

      <pre className="text-xs text-obs-outline font-mono bg-obs-surface-lowest/50 rounded-lg p-3 mb-3 max-h-40 overflow-auto">
        {JSON.stringify(request.data, null, 2)}
      </pre>

      <input
        type="text"
        className="w-full bg-obs-surface-highest border-none rounded-lg py-3 px-4 text-sm text-obs-on-surface placeholder:text-obs-outline-variant font-body focus:ring-1 focus:ring-obs-primary-container/40 transition-all outline-none mb-3"
        placeholder="Optional feedback..."
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
      />

      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => onRespond('approve', feedback)}
          className="flex items-center gap-2 px-5 py-2 rounded-full lithic-glow text-primary-foreground font-headline font-bold text-xs active:scale-95 transition-all"
        >
          <Check className="h-3.5 w-3.5" />
          Approve
        </button>
        <button
          type="button"
          onClick={() => onRespond('reject', feedback)}
          className="flex items-center gap-2 px-5 py-2 rounded-full bg-obs-error/20 text-obs-error hover:bg-obs-error/30 font-headline font-bold text-xs active:scale-95 transition-all"
        >
          <X className="h-3.5 w-3.5" />
          Reject
        </button>
      </div>
    </div>
  );
}
