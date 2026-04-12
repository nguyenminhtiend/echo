import type { TraceEvent } from '@/lib/ws-client';
import { Loader2 } from 'lucide-react';
import { TraceNode } from './trace-node';

export function TraceTree({ events }: { events: TraceEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Loader2 className="h-5 w-5 text-obs-primary/40 animate-spin mb-3" />
        <p className="text-obs-outline font-label text-xs uppercase tracking-wider">
          Waiting for trace events…
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event, i) => (
        <TraceNode key={`${event.type}-${event.created_at}-${i}`} event={event} />
      ))}
    </div>
  );
}
