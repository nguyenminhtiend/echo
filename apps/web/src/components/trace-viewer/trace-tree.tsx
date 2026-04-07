import type { TraceEvent } from '@/lib/ws-client';
import { TraceNode } from './trace-node';

export function TraceTree({ events }: { events: TraceEvent[] }) {
  if (events.length === 0) {
    return <p className="text-muted-foreground">Waiting for trace events...</p>;
  }

  return (
    <div className="space-y-2">
      {events.map((event, i) => (
        <TraceNode key={i} event={event} />
      ))}
    </div>
  );
}
