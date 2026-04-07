import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import type { AgentRun } from '@/lib/types';

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-500',
  running: 'bg-blue-500',
  hitl_waiting: 'bg-purple-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
};

export function AgentList({ runs }: { runs: AgentRun[] }) {
  if (runs.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No agent runs yet. Submit a task above to get started.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      {runs.map((run) => (
        <Link key={run.id} href={`/dashboard/agents/${run.id}`}>
          <Card className="cursor-pointer transition-colors hover:bg-muted/50">
            <CardContent className="flex items-center justify-between py-4">
              <div>
                <p className="font-medium">{run.task}</p>
                <p className="text-sm text-muted-foreground">
                  {run.task_type ?? 'unclassified'} &middot; {run.total_tokens} tokens &middot; $
                  {run.total_cost.toFixed(4)}
                </p>
              </div>
              <Badge className={STATUS_COLORS[run.status] ?? 'bg-gray-500'}>{run.status}</Badge>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
