'use client';

import { apiFetch } from '@/lib/api-client';
import type { TraceEventRest, TraceTreeResponse } from '@/lib/types';
import { useCallback, useEffect, useRef, useState } from 'react';

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

const LIVE_STATUSES = new Set(['pending', 'running', 'hitl_waiting']);

function normalizeRestEvent(e: TraceEventRest): TraceEvent {
  return {
    type: e.event_type,
    agent_name: e.agent_name ?? undefined,
    data: e.data,
    duration_ms: e.duration_ms ?? undefined,
    tokens_in: e.tokens_in ?? undefined,
    tokens_out: e.tokens_out ?? undefined,
    cost: e.cost != null ? Number(e.cost) : undefined,
    created_at: e.created_at
  };
}

export function useRunConsole(runId: string | null, runStatus: string) {
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [hitlPending, setHitlPending] = useState<HITLRequest | null>(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!runId) {
      setEvents([]);
      setHitlPending(null);
      setConnected(false);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setEvents([]);
    setHitlPending(null);
    setConnected(false);

    async function init() {
      try {
        const trace = await apiFetch<TraceTreeResponse>(`/api/traces/${runId}`);
        if (cancelled) return;
        setEvents(trace.events.map(normalizeRestEvent));
      } catch {
        // REST fetch failed — still allow WS to connect for live runs
      } finally {
        if (!cancelled) setLoading(false);
      }

      if (cancelled) return;
      if (!LIVE_STATUSES.has(runStatus)) return;

      const ws = new WebSocket(`ws://localhost:8000/ws/${runId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!cancelled) setConnected(true);
      };
      ws.onclose = () => {
        if (!cancelled) setConnected(false);
      };
      ws.onmessage = (e) => {
        if (cancelled) return;
        const event = JSON.parse(e.data);
        if (event.type === 'hitl_request') {
          setHitlPending(event);
        } else if (event.type === 'stream_end') {
          ws.close();
        } else {
          setEvents((prev) => [...prev, event]);
        }
      };
    }

    init();

    return () => {
      cancelled = true;
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [runId, runStatus]);

  const respondHITL = useCallback((action: 'approve' | 'reject', feedback?: string) => {
    wsRef.current?.send(JSON.stringify({ type: 'hitl_response', action, feedback }));
    setHitlPending(null);
  }, []);

  return { events, hitlPending, respondHITL, connected, loading };
}

/** Legacy hook — kept for [id]/page.tsx backward compat */
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
