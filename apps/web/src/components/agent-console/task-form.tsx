'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { apiFetch } from '@/lib/api-client';
import type { AgentRun } from '@/lib/types';

export function TaskForm({ onSubmit }: { onSubmit: (run: AgentRun) => void }) {
  const [task, setTask] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!task.trim()) return;
    setSubmitting(true);
    try {
      const run = await apiFetch<AgentRun>('/api/agents/runs', {
        method: 'POST',
        body: JSON.stringify({ task }),
      });
      onSubmit(run);
      setTask('');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit Task</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="task" className="sr-only">
              Task
            </Label>
            <Input
              id="task"
              placeholder="Describe the task (e.g., 'Fix the login bug in auth handler')"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Run'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
