# Agent Console Redesign — Split-Panel Layout with Live Streaming

**Date:** 2026-04-12  
**Route:** `/dashboard/agents`

## Overview

Redesign the Agent Console page from a stacked list-then-navigate pattern into a persistent split-panel layout. The main area shows a live-streaming or historically-replayed trace for the active run; the right sidebar shows run history. Users can submit new tasks or click past runs to inspect them — all on a single page, without navigation.

---

## Goals

- Submit a task and see every API event stream into the main panel in real time via WebSocket.
- Click any past run in the sidebar and replay its saved trace (fetched from `GET /api/traces/{id}`).
- For a run still in `running` or `hitl_waiting` status, the sidebar click also opens the WebSocket so live events append after the historical ones.
- HITL approval/rejection works the same as today, surfaced inside the main panel.
- No new API routes or backend changes needed.

---

## Data Flow

### New run (submitted by user)

1. `POST /api/agents/runs` → receive `AgentRun` with `id` and `status: pending`
2. Auto-select the new run (`selectedRunId = run.id`)
3. Backend fires `AgentRunner.execute(run.id)` in background; emits events to `asyncio.Queue`
4. Frontend connects `ws://localhost:8000/ws/{id}`
5. WS events arrive and are appended to `events[]` in the console
6. `stream_end` event closes the WS; run transitions to `completed` or `failed`

### Past run (clicked from sidebar)

1. `GET /api/traces/{id}` → receive `TraceTree` with `events[]`
2. Normalize `TraceEventResponse[]` → `TraceEvent[]`: REST uses `event_type`, WS uses `type` — the hook maps `event_type → type` during normalization. Other fields (`agent_name`, `data`, `tokens_in`, `tokens_out`, `cost`, `duration_ms`, `created_at`) are identical.
3. If `run.status` is `running` or `hitl_waiting`: also open WS and append live events after the REST-loaded ones
4. If `run.status` is `completed` or `failed`: no WS connection; REST events are the full picture

### Composite hook: `useRunConsole(runId, runStatus)`

```
state: events[], hitlPending, connected, loading

on mount / runId change:
  1. reset state
  2. fetch GET /api/traces/{runId} → seed events[]
  3. if runStatus in [pending, running, hitl_waiting]:
       open WS → append events as they arrive
       on stream_end → close WS
  4. if runStatus in [completed, failed]:
       skip WS

respondHITL(action, feedback):
  send via WS, clear hitlPending
```

---

## Component Structure

### `apps/web/src/app/dashboard/agents/page.tsx`

Owns top-level state:
- `runs: AgentRun[]` — full history list, refreshed on new submission
- `selectedRun: AgentRun | null` — currently viewed run

Layout: `flex flex-row h-full gap-0`
- `<RunConsole>` (`flex-1`, min-h-0, overflow scroll inside)
- `<AgentHistory>` (`w-72`, border-left, scrollable)

### `apps/web/src/components/agent-console/run-console.tsx` (new)

Props: `{ selectedRun: AgentRun | null, onNewRun: (run: AgentRun) => void }`

Structure:
- Task form pinned at top (always visible)
- If no `selectedRun`: empty state — "Submit a task to get started"
- If `selectedRun`:
  - Run header: `Run {id.slice(0,8)}...` + connection badge (`● Connected` / `○ Disconnected` / `— Historical`)
  - HITL card (when `hitlPending !== null`)
  - `<TraceTree events={events} />` — scrollable event list

Calls `useRunConsole(selectedRun?.id ?? null, selectedRun?.status ?? '')` unconditionally (hooks must not be called conditionally). The hook returns empty state when `runId` is `null`.

### `apps/web/src/components/agent-console/agent-history.tsx` (new)

Props: `{ runs: AgentRun[], selectedId: string | null, onSelect: (run: AgentRun) => void }`

Structure:
- "Run History" heading
- Scrollable list of runs, each showing:
  - Status dot (color-coded: yellow=pending, blue=running, purple=hitl_waiting, green=completed, red=failed)
  - Task text (truncated to one line)
  - Relative timestamp
- Selected run highlighted
- Empty state: "No runs yet"

### `apps/web/src/lib/ws-client.ts`

Add `useRunConsole` hook alongside the existing `useAgentTrace`. The existing hook stays to avoid breaking `[id]/page.tsx`.

`useRunConsole`:
- Accepts `runId: string | null` and `runStatus: string`
- Fetches REST trace on mount/runId change
- Opens WS only for live statuses
- Returns `{ events, hitlPending, respondHITL, connected, loading }`

### Unchanged files

- `apps/web/src/components/trace-viewer/trace-tree.tsx` — reused as-is
- `apps/web/src/components/trace-viewer/trace-node.tsx` — reused as-is
- `apps/web/src/components/trace-viewer/hitl-card.tsx` — reused as-is
- `apps/web/src/components/agent-console/task-form.tsx` — reused as-is
- `apps/web/src/app/dashboard/agents/[id]/page.tsx` — kept for direct URL access
- All API/backend files — no changes

---

## Type Changes

`apps/web/src/lib/types.ts` — add REST trace types:

```ts
export interface TraceEventRest {
  id: string;
  run_id: string;
  event_type: string;
  agent_name: string | null;
  data: Record<string, unknown>;
  tokens_in: number | null;
  tokens_out: number | null;
  cost: string | null;
  duration_ms: number | null;
  created_at: string;
}

export interface TraceTreeResponse {
  run_id: string;
  events: TraceEventRest[];
}
```

`TraceEventRest` maps to `TraceEvent` from `ws-client.ts` (REST uses `event_type`; WS uses `type` — normalize in the hook by mapping `event_type → type`).

---

## Error Handling

- REST fetch failure: show error message in console panel, allow retry
- WS connection failure: show `● Disconnected` badge; no retry loop (user can re-select run)
- `POST /api/agents/runs` failure: surface inline error in the task form, keep form value

---

## Out of Scope

- Pagination of run history (sidebar shows latest 50, matching existing API default)
- "Continue" as in resuming a completed LangGraph run (no API support exists today)
- Real-time sidebar status updates without a full page re-fetch
