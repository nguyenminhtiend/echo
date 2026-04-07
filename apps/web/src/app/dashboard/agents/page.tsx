'use client';

import { useEffect, useState } from 'react';
import { TaskForm } from '@/components/agent-console/task-form';
import { AgentList } from '@/components/agent-console/agent-list';
import { apiFetch } from '@/lib/api-client';
import type { AgentRun, AgentRunList } from '@/lib/types';

export default function AgentsPage() {
  const [runs, setRuns] = useState<AgentRun[]>([]);

  useEffect(() => {
    apiFetch<AgentRunList>('/api/agents/runs').then((data) => setRuns(data.runs));
  }, []);

  function handleNewRun(run: AgentRun) {
    setRuns((prev) => [run, ...prev]);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Agent Console</h1>
      <TaskForm onSubmit={handleNewRun} />
      <AgentList runs={runs} />
    </div>
  );
}
