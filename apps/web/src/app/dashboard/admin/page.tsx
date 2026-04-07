import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin Panel</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            User management will be available once Better Auth is fully integrated.
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Cost Reports</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            Aggregated cost data from the cost_ledger table will appear here.
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Audit Logs</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            All LLM calls and agent actions are logged for compliance review.
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
