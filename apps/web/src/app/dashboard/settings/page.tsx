import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>Model Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>LLM:</strong> gemma4:8b (Ollama local)
          </p>
          <p>
            <strong>Embeddings:</strong> nomic-embed-text (768 dimensions)
          </p>
          <p>
            <strong>Ollama URL:</strong> http://localhost:11434
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
