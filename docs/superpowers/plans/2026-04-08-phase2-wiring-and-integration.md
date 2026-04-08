# Phase 2: Wiring & Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect all the scaffolded Phase 1 components into a working end-to-end system. After this phase, a user can: submit a task via the dashboard, have agents process it through Ollama, see real-time trace events over WebSocket, query the RAG index, and view persisted data — all running locally.

**Prerequisite:** Phase 1 (Tasks 0–15 from `2026-04-05-project-echo-implementation.md`) is fully scaffolded. The verification plan (`2026-04-08-echo-integration-e2e-verification.md`) adds integration/E2E test infrastructure.

---

## Gap Analysis: Spec vs Plan vs Current Code

### Status Summary

| Area | Spec Requirement | Plan Coverage | Current Code | Gap |
|------|-----------------|---------------|--------------|-----|
| **API ↔ DB** | All routes persist to PostgreSQL | Plan creates stubs only | `get_db()` exists but unused by routes | **Critical** |
| **LangGraph invocation** | POST /runs triggers agent pipeline | Not in plan | `build_graph()` exists but never called from API | **Critical** |
| **Real agent nodes** | Agents call LLM via LiteLLM | Plan creates stubs | All agents except supervisor return static trace | **Critical** |
| **Gateway middleware** | PII scrub + rate limit on every LLM call | Plan builds libraries | Not wired into request path | **Major** |
| **RAG ↔ DB** | Indexer writes embeddings, retriever queries pgvector | Plan creates interface | Indexer doesn't write to DB, retriever returns `[]` | **Critical** |
| **WebSocket ↔ LangGraph** | WS streams real trace events from runs | Plan creates WS shell | No producer pushes events from agent runs | **Critical** |
| **Cost tracker persistence** | Per-request cost logged to `cost_ledger` | In-memory only | `flush()` not implemented | **Major** |
| **Audit logging** | Every LLM call audit-logged | Spec requires it | `audit_log` table exists, no writes | **Major** |
| **Dashboard real data** | Overview shows live metrics | Plan creates static UI | Hardcoded zeros | **Moderate** |
| **Landing page** | Product landing / login | Spec defines it | Still CNA template | **Moderate** |
| **E2E tests** | Test full user flows | Tests exist | Target wrong API endpoints (`:8000/auth/*` instead of Next.js) | **Major** |
| **Knowledge graph viz** | d3-force or similar | Spec mentions it | Canvas placeholder showing counts | **Minor (post-MVP)** |
| **Drizzle schema parity** | Mirror all Alembic tables | Plan creates partial | Missing `sessions`, `trace_events`, `audit_log`, `graph_*` | **Moderate** |
| **Home page** | Landing / Login redirect | Spec Section 6 | Default Next.js template | **Moderate** |

### What's Working (Phase 1 Complete)

- Infrastructure: Docker Compose, Dockerfiles, mise, .env ✅
- DB: SQLAlchemy models, Alembic migration, pgvector extension ✅
- API: FastAPI app with CORS, OTEL, structlog, 4 routers mounted ✅
- Gateway: LiteLLM router, Presidio scrubber, rate limiter, cost tracker (as libraries) ✅
- Agents: LangGraph state, graph compilation, supervisor routing, agent stubs ✅
- RAG: tree-sitter chunker, markdown chunker, file scanner, indexer (no DB) ✅
- Frontend: Next.js + shadcn + Better Auth + all dashboard pages + components ✅
- Tests: Unit tests (pytest + vitest), integration tests (testcontainers), E2E shell ✅

---

## Task 16: Wire API Routes to Database

**Goal:** Replace all API route stubs with real DB operations using async SQLAlchemy sessions.

**Files:**
- Modify: `apps/api/src/api/agents.py`
- Modify: `apps/api/src/api/traces.py`
- Modify: `apps/api/src/api/rag.py`
- Modify: `apps/api/src/main.py` (add lifespan for DB engine disposal)

- [ ] **Step 1: Add lifespan handler to main.py for DB connection management**

Add a `lifespan` context manager to `main.py` that ensures `engine.dispose()` on shutdown. Import `get_db` from `src.db.session`.

- [ ] **Step 2: Wire POST /api/agents/runs to create AgentRun in DB**

Inject `db: AsyncSession = Depends(get_db)` into `create_run`. Create an `AgentRun` row with the submitted task, commit, return the persisted object. Classify task_type via `classify_task()` from supervisor. Set `status="pending"`.

- [ ] **Step 3: Wire GET /api/agents/runs to read from DB**

Query `AgentRun` table ordered by `created_at` desc, return paginated list.

- [ ] **Step 4: Wire GET /api/agents/runs/{id} to return single run**

Add a new endpoint to fetch a single run by UUID.

- [ ] **Step 5: Wire GET /api/traces/{run_id} to read TraceEvent rows**

Query `trace_events` table for the given `run_id`, return as `TraceTree`. Return 404 if run doesn't exist.

- [ ] **Step 6: Update tests to account for DB-backed responses**

Unit tests should still work (using mock/in-memory). Integration tests already cover real DB.

- [ ] **Step 7: Commit**

---

## Task 17: Invoke LangGraph from API + Stream Traces via WebSocket

**Goal:** When a run is created, execute the LangGraph agent pipeline asynchronously. Stream trace events to connected WebSocket clients in real-time.

**Files:**
- Create: `apps/api/src/agents/runner.py` (orchestrates graph execution + trace emission)
- Modify: `apps/api/src/api/agents.py` (trigger async run after creating DB row)
- Modify: `apps/api/src/api/ws.py` (connect to runner's trace stream)
- Modify: `apps/api/src/agents/graph.py` (add trace callback hooks)

- [ ] **Step 1: Create agent runner module**

`AgentRunner` class that:
- Takes a `run_id` and initial state
- Invokes `build_graph().astream()` or `.ainvoke()`
- Emits trace events to an `asyncio.Queue` per run
- Updates `AgentRun.status` in DB as it progresses (`running` → `completed`/`failed`)
- Persists `TraceEvent` rows to DB as they occur

- [ ] **Step 2: Update POST /api/agents/runs to trigger agent execution**

After creating the `AgentRun` row, spawn an `asyncio.Task` that runs `AgentRunner.execute(run_id)`. Return the run immediately with `status="running"`.

- [ ] **Step 3: Wire WebSocket to receive events from AgentRunner**

When a WS connects for a `run_id`, subscribe to that run's trace queue. Push events as they arrive. Handle HITL by pausing execution via LangGraph's interrupt mechanism.

- [ ] **Step 4: Update agent nodes to emit structured trace events**

Each agent node should emit `agent_start`/`agent_end` events with timing, plus any `tool_call`/`tool_result` and `llm_start`/`llm_end` events.

- [ ] **Step 5: Persist trace events and update run totals**

After each LLM call, write a `TraceEvent` row and a `CostLedger` row. On run completion, update `AgentRun.total_tokens`, `total_cost`, `duration_ms`, `completed_at`.

- [ ] **Step 6: Write audit log entries**

Each LLM call writes to `audit_log` with action `llm_call`, model, token count, cost, input hash.

- [ ] **Step 7: Test with integration test**

- [ ] **Step 8: Commit**

---

## Task 18: Implement Real Agent Nodes (LLM-backed)

**Goal:** Replace stub agent nodes with real Ollama calls via the gateway.

**Files:**
- Modify: `apps/api/src/agents/coder.py`
- Modify: `apps/api/src/agents/reviewer.py`
- Modify: `apps/api/src/agents/qa.py`
- Modify: `apps/api/src/agents/security.py`
- Modify: `apps/api/src/agents/docs_agent.py`
- Modify: `apps/api/src/agents/architect.py`
- Create: `apps/api/src/agents/prompts.py` (agent prompt templates)
- Create: `apps/api/src/agents/tools.py` (shared agent tools: file read, RAG query)

- [ ] **Step 1: Create prompt templates for each agent**

Define system prompts that set agent role, constraints, and output format. Use structured JSON output where possible.

- [ ] **Step 2: Create shared agent tools**

Tools that agents can use:
- `read_file(path)` — read a file from the indexed codebase
- `rag_query(query)` — query the RAG index
- `write_artifact(file_path, content)` — produce a code artifact

- [ ] **Step 3: Implement coder agent with LLM call**

Use `gateway.router` to call Ollama. Scrub input via `gateway.scrubber`. Track cost via `gateway.tracker`. Return code artifacts in state.

- [ ] **Step 4: Implement reviewer agent**

Reads generated artifacts, calls LLM for review, returns `ReviewFinding` entries.

- [ ] **Step 5: Implement QA agent**

Generates test suggestions for produced code.

- [ ] **Step 6: Implement security agent**

Scans code artifacts for OWASP patterns, secret leaks.

- [ ] **Step 7: Implement docs agent**

Generates documentation for code changes.

- [ ] **Step 8: Implement architect agent**

Analyzes architecture impact, uses Graph RAG for dependency analysis.

- [ ] **Step 9: Commit**

---

## Task 19: Wire Gateway Middleware into Request Pipeline

**Goal:** Integrate PII scrubber, rate limiter, and cost tracker as actual middleware in the LLM call path.

**Files:**
- Create: `apps/api/src/gateway/middleware.py` (unified gateway middleware)
- Modify: `apps/api/src/gateway/tracker.py` (add `flush()` to persist to DB)
- Modify: `apps/api/src/agents/runner.py` (use gateway for all LLM calls)

- [ ] **Step 1: Create gateway call function**

A single `gateway_llm_call(prompt, model_tier, user_id, run_id)` function that:
1. Scrubs PII/secrets from prompt
2. Checks rate limit for user
3. Calls LiteLLM router
4. Records cost/tokens
5. Writes audit log entry
6. Returns response

- [ ] **Step 2: Wire all agent LLM calls through gateway**

Replace direct LiteLLM calls in agents with `gateway_llm_call()`.

- [ ] **Step 3: Implement `CostTracker.flush()` to persist to cost_ledger**

Write accumulated entries to `cost_ledger` table in a batch.

- [ ] **Step 4: Add rate limit middleware to FastAPI**

Optional: Add a FastAPI middleware that checks rate limits before processing agent run requests.

- [ ] **Step 5: Commit**

---

## Task 20: Wire RAG Pipeline to Database

**Goal:** Connect the RAG indexer to write embeddings to pgvector and the retriever to query them.

**Files:**
- Modify: `apps/api/src/rag/indexer.py` (write chunks + embeddings to DB)
- Modify: `apps/api/src/rag/retriever.py` (query pgvector for similar chunks)
- Modify: `apps/api/src/api/rag.py` (use real retriever)

- [ ] **Step 1: Update indexer to write to rag_chunks table**

After chunking files, call Ollama embedding model for each chunk. Insert rows into `rag_chunks` with content, embedding vector, chunk_type, file_path, line numbers.

- [ ] **Step 2: Implement retriever with pgvector similarity search**

Query `rag_chunks` using `embedding <=> query_embedding` (cosine distance) with `ORDER BY` and `LIMIT top_k`. Return scored results.

- [ ] **Step 3: Wire `/api/rag/query` to use real retriever**

Inject DB session, create `RAGRetriever` with session, call `query()`, return results.

- [ ] **Step 4: Update `mise run index` to use DB**

Ensure the indexer CLI entry point connects to the database and writes chunks.

- [ ] **Step 5: Test indexing + retrieval integration**

- [ ] **Step 6: Commit**

---

## Task 21: Fix Frontend Issues

**Goal:** Fix the landing page, E2E tests, Drizzle schema parity, and dashboard data binding.

**Files:**
- Modify: `apps/web/src/app/page.tsx` (replace CNA template with product landing)
- Modify: `apps/web/src/app/dashboard/page.tsx` (fetch real metrics from API)
- Modify: `apps/web/src/db/schema.ts` (add missing tables)
- Modify: `apps/web/e2e/auth.spec.ts` (fix endpoint URLs)
- Modify: `apps/web/e2e/agent-run.spec.ts` (fix endpoint URLs)
- Modify: `apps/web/e2e/rag-explorer.spec.ts` (fix endpoint URLs)

- [ ] **Step 1: Replace home page with product landing**

Show E.C.H.O. branding, login/register links. Redirect to `/dashboard` if already authenticated.

- [ ] **Step 2: Wire dashboard overview to real API data**

Add `GET /api/agents/stats` endpoint on backend returning `{total_runs, total_tokens, total_cost}`. Fetch in dashboard overview page.

- [ ] **Step 3: Complete Drizzle schema**

Add `sessions`, `traceEvents`, `auditLog`, `ragChunks`, `graphNodes`, `graphEdges` tables to match Alembic migration.

- [ ] **Step 4: Fix E2E auth test**

Auth is via Next.js `/api/auth/*` (Better Auth), not FastAPI `:8000/auth/*`. Fix `beforeEach` setup in all E2E specs.

- [ ] **Step 5: Fix E2E RAG test**

RAG endpoint is `POST /api/rag/query`, not `POST /rag/chunks`. Fix endpoint path.

- [ ] **Step 6: Fix E2E agent run test**

Ensure agent-run spec creates a run via the correct API path and waits for WebSocket trace events.

- [ ] **Step 7: Commit**

---

## Task 22: End-to-End Smoke Test

**Goal:** Verify the full stack works together locally.

- [ ] **Step 1: Run `mise run db:reset` and `mise run db:migrate`**
- [ ] **Step 2: Start all services with `mise run dev`**
- [ ] **Step 3: Run `mise run index` to index the codebase**
- [ ] **Step 4: Submit a task via dashboard, verify agent execution**
- [ ] **Step 5: Verify trace events stream over WebSocket**
- [ ] **Step 6: Query RAG and verify results**
- [ ] **Step 7: Run `mise run test` (all unit tests pass)**
- [ ] **Step 8: Run `mise run test:integration` (integration tests pass)**
- [ ] **Step 9: Run `mise run test:e2e` (E2E tests pass)**

---

## Summary

| Task | Description | Priority | Effort |
|------|-------------|----------|--------|
| 16 | Wire API routes to DB | Critical | Medium |
| 17 | LangGraph invocation + WebSocket streaming | Critical | Large |
| 18 | Real LLM-backed agent nodes | Critical | Large |
| 19 | Gateway middleware wiring | Major | Medium |
| 20 | RAG pipeline to DB | Critical | Medium |
| 21 | Fix frontend issues | Major | Medium |
| 22 | End-to-end smoke test | Validation | Small |

**Estimated total effort:** ~3-4 focused implementation sessions.

**After Phase 2:** The system is fully functional for local demo. A user can submit tasks, agents process them through Ollama, traces stream in real-time, RAG queries return real results, and all data is persisted.
