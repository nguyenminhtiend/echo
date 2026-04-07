'use client';

import { useEffect, useRef, useState } from 'react';

export interface TraceEvent {
  type: string;
  agent_name?: string;
  data: Record<string, unknown>;
  duration_ms?: number;
  tokens_in?: number;
  tokens_out?: number;
  cost?: number;
  created_at: string;
}

export interface HITLRequest {
  type: 'hitl_request';
  checkpoint: string;
  data: Record<string, unknown>;
}

export function useAgentTrace(runId: string) {
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [hitlPending, setHitlPending] = useState<HITLRequest | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${runId}`);

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    ws.onmessage = (e) => {
      const event = JSON.parse(e.data);
      if (event.type === 'hitl_request') {
        setHitlPending(event);
      } else {
        setEvents((prev) => [...prev, event]);
      }
    };

    wsRef.current = ws;
    return () => ws.close();
  }, [runId]);

  function respondHITL(action: 'approve' | 'reject', feedback?: string) {
    wsRef.current?.send(JSON.stringify({ type: 'hitl_response', action, feedback }));
    setHitlPending(null);
  }

  return { events, hitlPending, respondHITL, connected };
}
