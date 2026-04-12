'use client';

import { HITLCard } from '@/components/trace-viewer/hitl-card';
import { TraceTree } from '@/components/trace-viewer/trace-tree';
import { apiFetch } from '@/lib/api-client';
import type { AgentRun } from '@/lib/types';
import { useRunConsole } from '@/lib/ws-client';
import { Archive, Loader2, Send, Terminal, Wifi, WifiOff, Zap } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface Props {
  selectedRun: AgentRun | null;
  onNewRun: (run: AgentRun) => void;
}

function ConnectionBadge({ status, connected }: { status: string; connected: boolean }) {
  if (connected) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-label text-[10px] uppercase tracking-widest">
        <Wifi className="h-3 w-3" />
        Connected
      </span>
    );
  }
  if (['completed', 'failed'].includes(status)) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-obs-surface-highest text-obs-outline font-label text-[10px] uppercase tracking-widest">
        <Archive className="h-3 w-3" />
        Historical
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-obs-error/10 text-obs-error font-label text-[10px] uppercase tracking-widest">
      <WifiOff className="h-3 w-3" />
      Disconnected
    </span>
  );
}

export function RunConsole({ selectedRun, onNewRun }: Props) {
  const [task, setTask] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { events, hitlPending, respondHITL, connected, loading } = useRunConsole(
    selectedRun?.id ?? null,
    selectedRun?.status ?? ''
  );

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events.length]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!task.trim() || submitting) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const run = await apiFetch<AgentRun>('/api/agents/runs', {
        method: 'POST',
        body: JSON.stringify({ task })
      });
      onNewRun(run);
      setTask('');
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to submit task');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Task Input — Glass Panel */}
      <div className="px-6 pt-6 pb-4">
        <form onSubmit={handleSubmit}>
          <div className="glass-panel ghost-border rounded-2xl p-5 relative overflow-hidden shadow-2xl shadow-obs-primary-container/5">
            <div className="absolute top-0 right-0 p-4 opacity-[0.06] pointer-events-none">
              <Terminal className="h-16 w-16" />
            </div>
            <div className="flex items-center gap-2 mb-3">
              <span className="font-label text-[10px] uppercase tracking-[0.2em] text-obs-primary">
                Priority Input
              </span>
              <div className="h-px w-10 bg-obs-primary/30" />
            </div>
            <textarea
              value={task}
              onChange={(e) => setTask(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              className="w-full bg-obs-surface-lowest/50 border-none rounded-xl p-4 font-sans text-sm text-obs-on-surface placeholder:text-obs-outline-variant/60 focus:ring-2 focus:ring-obs-primary/20 resize-none transition-all outline-none"
              placeholder="Describe the task — e.g., 'Fix the login bug in auth handler'..."
              rows={2}
            />
            {submitError && <p className="text-obs-error text-xs font-label mt-2">{submitError}</p>}
            <div className="flex justify-end mt-3">
              <button
                type="submit"
                disabled={submitting || !task.trim()}
                className="lithic-glow px-6 py-2.5 rounded-full text-primary-foreground font-headline font-bold text-sm flex items-center gap-2 hover:shadow-[0_0_20px_rgba(160,120,255,0.4)] transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {submitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                {submitting ? 'Executing...' : 'Execute'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Console Body */}
      {!selectedRun ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center px-8">
          <div className="h-16 w-16 rounded-2xl bg-obs-surface-high/60 flex items-center justify-center">
            <Zap className="h-8 w-8 text-obs-primary/40" />
          </div>
          <p className="text-obs-on-surface-variant font-body text-sm max-w-xs">
            Submit a task to get started, or select a previous run from the history panel.
          </p>
        </div>
      ) : (
        <div className="flex-1 flex flex-col min-h-0 px-6 pb-6">
          {/* Run Header */}
          <div className="flex items-center justify-between py-3 mb-2">
            <div className="flex items-center gap-3">
              <h3 className="font-headline font-bold text-obs-on-surface text-base tracking-tight">
                Run {selectedRun.id.slice(0, 8)}…
              </h3>
              <ConnectionBadge status={selectedRun.status} connected={connected} />
            </div>
            {selectedRun.duration_ms != null && (
              <span className="font-label text-[10px] text-obs-outline uppercase tracking-wider">
                {(selectedRun.duration_ms / 1000).toFixed(1)}s
              </span>
            )}
          </div>

          {/* HITL Card */}
          {hitlPending && <HITLCard request={hitlPending} onRespond={respondHITL} />}

          {/* Trace Events — scrollable */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto min-h-0 pr-1">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-6 w-6 text-obs-primary animate-spin" />
              </div>
            ) : (
              <TraceTree events={events} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
