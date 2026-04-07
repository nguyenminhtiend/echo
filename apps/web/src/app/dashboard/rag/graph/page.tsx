import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function GraphPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Knowledge Graph</h1>
      <Card>
        <CardHeader>
          <CardTitle>Graph Visualization</CardTitle>
        </CardHeader>
        <CardContent className="flex h-96 items-center justify-center text-muted-foreground">
          Graph visualization will render here once the RAG indexing pipeline has run. Use `mise run
          index` to index the codebase.
        </CardContent>
      </Card>
    </div>
  );
}
