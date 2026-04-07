'use client';

import { use } from 'react';
import { Badge } from '@/components/ui/badge';
import { TraceTree } from '@/components/trace-viewer/trace-tree';
import { HITLCard } from '@/components/trace-viewer/hitl-card';
import { useAgentTrace } from '@/lib/ws-client';

export default function AgentRunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { events, hitlPending, respondHITL, connected } = useAgentTrace(id);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">Run {id.slice(0, 8)}...</h1>
        <Badge className={connected ? 'bg-green-500' : 'bg-red-500'}>
          {connected ? 'Connected' : 'Disconnected'}
        </Badge>
      </div>

      {hitlPending && <HITLCard request={hitlPending} onRespond={respondHITL} />}

      <TraceTree events={events} />
    </div>
  );
}
