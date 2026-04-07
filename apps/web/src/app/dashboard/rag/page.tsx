'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { apiFetch } from '@/lib/api-client';
import type { RAGResult, RAGQueryResponse } from '@/lib/types';

export default function RAGPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<RAGResult[]>([]);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const data = await apiFetch<RAGQueryResponse>('/api/rag/query', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
    setResults(data.results);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">RAG Explorer</h1>
      <form onSubmit={handleSearch} className="flex gap-2">
        <Input
          placeholder="Search the knowledge graph..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1"
        />
        <Button type="submit">Search</Button>
      </form>
      <div className="space-y-2">
        {results.map((r, i) => (
          <Card key={i}>
            <CardHeader>
              <CardTitle className="text-sm">
                {r.file_path}:{r.start_line}-{r.end_line} ({r.chunk_type}) — score:{' '}
                {r.score.toFixed(3)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs">{r.content.slice(0, 500)}</pre>
            </CardContent>
          </Card>
        ))}
        {results.length === 0 && query && (
          <p className="text-muted-foreground">No results found.</p>
        )}
      </div>
    </div>
  );
}
