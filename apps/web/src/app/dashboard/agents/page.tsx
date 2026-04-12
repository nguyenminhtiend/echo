'use client';

import { AgentHistory } from '@/components/agent-console/agent-history';
import { RunConsole } from '@/components/agent-console/run-console';
import { apiFetch } from '@/lib/api-client';
import type { AgentRun, AgentRunList } from '@/lib/types';
import { useEffect, useState } from 'react';

export default function AgentsPage() {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<AgentRun | null>(null);

  useEffect(() => {
    apiFetch<AgentRunList>('/api/agents/runs').then((data) => setRuns(data.runs));
  }, []);

  function handleNewRun(run: AgentRun) {
    setRuns((prev) => [run, ...prev]);
    setSelectedRun(run);
  }

  function handleSelect(run: AgentRun) {
    setSelectedRun(run);
  }

  return (
    <div className="flex h-full">
      <RunConsole selectedRun={selectedRun} onNewRun={handleNewRun} />
      <AgentHistory runs={runs} selectedId={selectedRun?.id ?? null} onSelect={handleSelect} />
    </div>
  );
}
