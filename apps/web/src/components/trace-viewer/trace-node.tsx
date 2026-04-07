import { Badge } from '@/components/ui/badge';
import type { TraceEvent } from '@/lib/ws-client';

const TYPE_COLORS: Record<string, string> = {
  agent_start: 'bg-blue-500',
  agent_end: 'bg-blue-700',
  tool_call: 'bg-amber-500',
  tool_result: 'bg-amber-700',
  llm_start: 'bg-purple-500',
  llm_end: 'bg-purple-700',
};

export function TraceNode({ event }: { event: TraceEvent }) {
  return (
    <div className="flex items-start gap-3 rounded-md border p-3">
      <Badge className={TYPE_COLORS[event.type] ?? 'bg-gray-500'}>{event.type}</Badge>
      <div className="flex-1">
        {event.agent_name && <p className="text-sm font-medium">{event.agent_name}</p>}
        <pre className="mt-1 text-xs text-muted-foreground">
          {JSON.stringify(event.data, null, 2)}
        </pre>
        <div className="mt-1 flex gap-4 text-xs text-muted-foreground">
          {event.duration_ms != null && <span>{event.duration_ms}ms</span>}
          {event.tokens_in != null && <span>{event.tokens_in} tok in</span>}
          {event.tokens_out != null && <span>{event.tokens_out} tok out</span>}
          {event.cost != null && <span>${event.cost.toFixed(4)}</span>}
        </div>
      </div>
    </div>
  );
}
