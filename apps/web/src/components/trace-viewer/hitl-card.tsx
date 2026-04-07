'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import type { HITLRequest } from '@/lib/ws-client';

interface Props {
  request: HITLRequest;
  onRespond: (action: 'approve' | 'reject', feedback?: string) => void;
}

export function HITLCard({ request, onRespond }: Props) {
  const [feedback, setFeedback] = useState('');

  return (
    <Card className="border-purple-500">
      <CardHeader>
        <CardTitle className="text-sm">Human Review Required: {request.checkpoint}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <pre className="text-xs">{JSON.stringify(request.data, null, 2)}</pre>
        <Input
          placeholder="Optional feedback..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
        />
        <div className="flex gap-2">
          <Button onClick={() => onRespond('approve', feedback)} variant="default">
            Approve
          </Button>
          <Button onClick={() => onRespond('reject', feedback)} variant="destructive">
            Reject
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
