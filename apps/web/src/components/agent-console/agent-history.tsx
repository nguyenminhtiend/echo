'use client';

import type { AgentRun } from '@/lib/types';
import { CircleDot, Clock } from 'lucide-react';

const STATUS_DOT: Record<string, string> = {
  pending: 'bg-yellow-400 shadow-[0_0_6px_rgba(250,204,21,0.5)]',
  running: 'bg-blue-400 shadow-[0_0_6px_rgba(96,165,250,0.5)]',
  hitl_waiting: 'bg-obs-primary-container shadow-[0_0_6px_rgba(160,120,255,0.5)]',
  completed: 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]',
  failed: 'bg-obs-error shadow-[0_0_6px_rgba(255,180,171,0.5)]'
};

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

interface Props {
  runs: AgentRun[];
  selectedId: string | null;
  onSelect: (run: AgentRun) => void;
}

export function AgentHistory({ runs, selectedId, onSelect }: Props) {
  return (
    <aside className="w-72 flex flex-col bg-obs-surface-lowest/60 backdrop-blur-2xl border-l border-white/5">
      <div className="px-5 py-5 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-obs-outline" />
          <h2 className="font-headline text-sm font-bold tracking-tight text-obs-on-surface">
            Run History
          </h2>
        </div>
        <p className="font-label text-[10px] uppercase tracking-widest text-obs-outline mt-1">
          Latest operations
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
        {runs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full px-6 text-center">
            <CircleDot className="h-8 w-8 text-obs-outline-variant/40 mb-3" />
            <p className="text-xs text-obs-outline font-label">No runs yet</p>
          </div>
        ) : (
          <div className="py-2">
            {runs.map((run) => {
              const isSelected = run.id === selectedId;
              return (
                <button
                  key={run.id}
                  type="button"
                  onClick={() => onSelect(run)}
                  className={`w-full text-left px-5 py-3 transition-all duration-200 group ${
                    isSelected
                      ? 'bg-obs-primary/8 border-l-2 border-obs-primary'
                      : 'border-l-2 border-transparent hover:bg-white/[0.04]'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`h-2 w-2 rounded-full shrink-0 ${STATUS_DOT[run.status] ?? 'bg-obs-outline'}`}
                    />
                    <span
                      className={`text-xs font-body truncate ${
                        isSelected
                          ? 'text-obs-on-surface font-medium'
                          : 'text-obs-on-surface-variant'
                      }`}
                    >
                      {run.task}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1.5 ml-[18px]">
                    <span className="font-label text-[10px] uppercase tracking-wider text-obs-outline">
                      {run.status.replace('_', ' ')}
                    </span>
                    <span className="text-obs-outline-variant text-[10px]">·</span>
                    <span className="font-label text-[10px] text-obs-outline">
                      {relativeTime(run.created_at)}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </aside>
  );
}
