import type { TraceEvent } from '@/lib/ws-client';
import { Activity, Bot, BotOff, Sparkles, SparklesIcon, Wrench, WrenchIcon } from 'lucide-react';

const TYPE_CONFIG: Record<string, { color: string; bg: string; icon: typeof Bot }> = {
  agent_start: { color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20', icon: Bot },
  agent_end: { color: 'text-blue-500', bg: 'bg-blue-500/10 border-blue-500/20', icon: BotOff },
  tool_call: {
    color: 'text-obs-tertiary',
    bg: 'bg-obs-tertiary/10 border-obs-tertiary/20',
    icon: Wrench
  },
  tool_result: {
    color: 'text-obs-tertiary',
    bg: 'bg-obs-tertiary/10 border-obs-tertiary/20',
    icon: WrenchIcon
  },
  llm_start: {
    color: 'text-obs-primary',
    bg: 'bg-obs-primary/10 border-obs-primary/20',
    icon: Sparkles
  },
  llm_end: {
    color: 'text-obs-primary-container',
    bg: 'bg-obs-primary/10 border-obs-primary/20',
    icon: SparklesIcon
  }
};

const FALLBACK = {
  color: 'text-obs-outline',
  bg: 'bg-obs-surface-highest border-obs-outline-variant/20',
  icon: Activity
};

export function TraceNode({ event }: { event: TraceEvent }) {
  const cfg = TYPE_CONFIG[event.type] ?? FALLBACK;
  const Icon = cfg.icon;

  return (
    <div className="glass-panel ghost-border rounded-xl p-4 hover:bg-white/[0.04] transition-all duration-200 group flex items-start gap-4">
      <div
        className={`h-9 w-9 rounded-lg border flex items-center justify-center shrink-0 ${cfg.bg}`}
      >
        <Icon className={`h-4 w-4 ${cfg.color}`} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span
            className={`font-label text-[10px] font-bold uppercase tracking-widest ${cfg.color}`}
          >
            {event.type.replace(/_/g, ' ')}
          </span>
          {event.agent_name && (
            <span className="text-xs text-obs-on-surface-variant font-body">
              {event.agent_name}
            </span>
          )}
        </div>

        <pre className="text-xs text-obs-outline font-mono leading-relaxed overflow-x-auto max-h-32 scrollbar-thin">
          {JSON.stringify(event.data, null, 2)}
        </pre>

        <div className="mt-2 flex gap-4 text-obs-outline">
          {event.duration_ms != null && (
            <span className="font-label text-[10px]">{event.duration_ms}ms</span>
          )}
          {event.tokens_in != null && (
            <span className="font-label text-[10px]">{event.tokens_in} tok ↓</span>
          )}
          {event.tokens_out != null && (
            <span className="font-label text-[10px]">{event.tokens_out} tok ↑</span>
          )}
          {event.cost != null && (
            <span className="font-label text-[10px] text-obs-tertiary">
              ${Number(event.cost).toFixed(4)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
