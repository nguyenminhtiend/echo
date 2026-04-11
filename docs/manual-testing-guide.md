# E.C.H.O. Manual Testing Guide

Local manual testing procedures for verifying the current state of the E.C.H.O. platform.

**Last updated:** 2026-04-11 (post Phase 2: API ↔ DB wiring, LangGraph runner, WebSocket streaming, gateway middleware, RAG pgvector)

---

## Prerequisites

### Required Software

| Tool | Version | Install |
|------|---------|---------|
| mise | latest | `curl https://mise.run \| sh` |
| Docker + Docker Compose | v2+ | [docker.com](https://docker.com) |
| Ollama | latest | `brew install ollama` or [ollama.com](https://ollama.com) |

After installing mise, run from the project root:

```bash
mise install
```

This installs Python 3.14, Node 24, and Bun.

### Pull Ollama Models

```bash
ollama pull gemma4:e4b
ollama pull nomic-embed-text:latest
```

Verify:

```bash
ollama list
# Should show gemma4:e4b and nomic-embed-text:latest
```

### Environment Setup

```bash
cp .env.example .env
```

Check `.env` has correct DB credentials matching docker-compose defaults:

```
DATABASE_URL=postgresql+asyncpg://admin:123456@127.0.0.1:5432/echo
POSTGRES_USER=admin
POSTGRES_PASSWORD=123456
POSTGRES_DB=echo
```

> **Note:** The `docker-compose.yml` defaults to `echo:echo` credentials via `${POSTGRES_USER:-echo}`. Your `.env` overrides this to `admin:123456`. Make sure `.env` is loaded or the compose defaults match your `DATABASE_URL`.

### Optional Env Flags (new in Phase 2)

| Var | Purpose |
|-----|---------|
| `ECHO_DRY_RUN=1` | Agents and RAG indexer skip real LLM / embedding calls and emit stub artifacts. Use for fast smoke tests without Ollama. |
| `ECHO_SKIP_AGENT_RUNNER=1` | `POST /api/agents/runs` persists the run but does NOT spawn the background `AgentRunner` task. Used by unit/integration tests so DB assertions aren't racy. |
| `CODEBASE_ROOT=/path/to/repo` | Root directory the agent `read_file` tool and indexer scan. Defaults to cwd. |

---

## 1. Infrastructure Tests

### 1.1 Database Container

```bash
# Start just the DB
docker compose up -d db

# Verify it's running
docker compose ps
# Expected: db service is "running (healthy)"

# Test connection
docker compose exec db psql -U admin -d echo -c "SELECT version();"
# Expected: PostgreSQL 18.x

# Verify pgvector
docker compose exec db psql -U admin -d echo -c "CREATE EXTENSION IF NOT EXISTS vector; SELECT extversion FROM pg_extension WHERE extname = 'vector';"
# Expected: 0.8.2
```

### 1.2 Run Migrations

```bash
mise run db:migrate
# Expected: "Running upgrade -> head" with no errors
# or "INFO  [alembic.runtime.migration] Running upgrade  -> 05df721e935b, initial schema"
# or if already up-to-date: "INFO  [alembic.runtime.migration] Will assume transactional DDL."
```

Verify tables:

```bash
docker compose exec db psql -U admin -d echo -c "\dt"
```

Expected tables: `users`, `sessions`, `agent_runs`, `trace_events`, `cost_ledger`, `audit_log`, `rag_chunks`, `graph_nodes`, `graph_edges`, `alembic_version`.

### 1.3 Ollama Connectivity

```bash
curl http://localhost:11434/api/tags
# Expected: JSON with models list including gemma4:e4b

# Test embedding
curl http://localhost:11434/api/embed -d '{"model":"nomic-embed-text:latest","input":"hello world"}'
# Expected: JSON with "embeddings" array, each vector has 768 dimensions

# Test LLM (quick)
curl http://localhost:11434/api/generate -d '{"model":"gemma4:e4b","prompt":"Say hello","stream":false}'
# Expected: JSON with "response" field containing text
```

---

## 2. Backend API Tests

### 2.1 Install Dependencies

```bash
cd apps/api
uv sync
```

### 2.2 Unit Tests

```bash
cd apps/api
uv run pytest -m "not integration and not ollama" -v
```

**Expected:** All tests pass. Current test modules:
- `test_main.py` — health endpoint
- `test_models.py` — SQLAlchemy model table names, columns, indexes
- `test_gateway/test_scrubber.py` — PII detection (email, phone, AWS keys, JWT)
- `test_gateway/test_router.py` — task complexity classification
- `test_gateway/test_tracker.py` — cost tracking + `CostTracker.flush()` persists to `cost_ledger`
- `test_gateway/test_rate_limiter.py` — rate limiting logic
- `test_agents/test_state.py` — EchoState TypedDict shape
- `test_agents/test_graph.py` — LangGraph compilation, all nodes present
- `test_agents/test_supervisor.py` — task type classification (bugfix, feature, review, etc.)
- `test_api/test_agents_api.py` — create/list/get agent runs + stats (DB-backed via in-memory SQLite; `ECHO_SKIP_AGENT_RUNNER=1` in conftest)
- `test_api/test_traces_api.py` — trace 404 for unknown run, 200 for existing
- `test_api/test_rag_api.py` — RAG query happy path with mocked retriever

### 2.3 Integration Tests (requires Docker)

```bash
cd apps/api
uv run pytest -m integration -v
```

**Expected:** All pass. These use testcontainers to spin up a real Postgres with pgvector. Tests:
- `test_health_db.py` — /health with real DB, pgvector extension present, all tables created
- `test_rag_flow.py` — chunker splits fixture file, `write_chunks_to_db` writes embeddings, retriever returns ordered results via `<=>` cosine distance
- `test_agents_flow.py` — POST creates and persists run, `AgentRunner` executes graph (under `ECHO_DRY_RUN=1`), trace events and cost_ledger rows written, WebSocket receives `run_start` → `run_complete`

### 2.4 Ollama Smoke Tests (requires running Ollama)

```bash
cd apps/api
RUN_OLLAMA_TESTS=1 uv run pytest -m ollama -v
```

**Expected:** Pass if Ollama is running with both models pulled. Tests:
- Ollama tags endpoint returns model list
- Embedding call returns 768-dim vector
- Chat completion returns text

### 2.5 Start API Server Manually

```bash
mise run dev:api
# or
cd apps/api && uv run fastapi dev src/main.py --port 8000
```

Test endpoints:

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"0.1.0"}

# Create agent run (persists to DB, spawns background AgentRunner that runs the LangGraph pipeline)
curl -X POST http://localhost:8000/api/agents/runs \
  -H "Content-Type: application/json" \
  -d '{"task":"Fix the login bug in auth handler"}'
# Expected: 201 with JSON containing a real UUID, task, task_type (auto-classified),
#           status="pending". The run will flip to "running" → "completed"/"failed" in the
#           background as the graph executes. Set ECHO_SKIP_AGENT_RUNNER=1 to persist only.

# List agent runs (reads from DB, paginated)
curl "http://localhost:8000/api/agents/runs?skip=0&limit=50"
# Expected: {"runs":[{...persisted rows...}],"total":N}

# Get single run by id
curl http://localhost:8000/api/agents/runs/<run_id>
# Expected: 200 with the AgentRun JSON, 404 if not found

# Dashboard stats (new in Phase 2)
curl http://localhost:8000/api/agents/stats
# Expected: {"total_runs":N,"total_tokens":N,"total_cost":"0.000000"}

# Get trace (reads trace_events rows; 404 if run doesn't exist)
curl http://localhost:8000/api/traces/<run_id>
# Expected: {"run_id":"...","events":[{event_type, agent_name, data, tokens_in, tokens_out, cost, duration_ms, ...}]}

# RAG query (real pgvector cosine search against rag_chunks)
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"auth flow","top_k":5}'
# Expected: {"results":[{content, chunk_type, file_path, start_line, end_line, score}], "query":"auth flow"}
# Empty array if the index hasn't been populated via `mise run index` yet.
```

> **Running without Ollama:** Set `ECHO_DRY_RUN=1` before starting the API. The runner still executes the
> graph end-to-end and emits trace events, but agent nodes return stub artifacts and the RAG retriever
> returns `[]`. This is the fastest way to smoke-test the wiring without pulling models.

### 2.6 WebSocket Test

With the API server running:

```bash
# Create a run first, then connect to its WebSocket using the returned id
RUN_ID=$(curl -s -X POST http://localhost:8000/api/agents/runs \
  -H "Content-Type: application/json" \
  -d '{"task":"Write a hello world function"}' | jq -r .id)

# Using websocat (brew install websocat) or wscat (npm i -g wscat)
websocat ws://localhost:8000/ws/$RUN_ID
# or
wscat -c ws://localhost:8000/ws/$RUN_ID
```

**Expected:** A stream of JSON events arrives as the `AgentRunner` executes the graph:

1. `{"type":"run_start","run_id":"...","status":"running"}`
2. A sequence of `agent_start` / `llm_start` / `llm_end` / `agent_end` events per node
   (supervisor → coder → reviewer → qa → security → docs → architect, depending on task_type)
3. `{"type":"run_complete","run_id":"...","status":"completed","total_tokens":N,"total_cost":"...","duration_ms":N}`
4. `{"type":"stream_end","run_id":"..."}` and the server closes the push loop

If the graph interrupts for HITL, you'll see `{"type":"hitl_request",...}`; reply with
`{"type":"hitl_response","action":"approve"}` and the graph resumes (300s timeout → auto-approve).

> **Tip:** With `ECHO_DRY_RUN=1` the events stream in near-instantly without hitting Ollama. Use this
> if you only want to verify the WebSocket producer is wired correctly.

---

## 3. Frontend Tests

### 3.1 Install Dependencies

```bash
cd apps/web
bun install
```

### 3.2 Unit Tests (Vitest)

```bash
cd apps/web
bun run vitest run
```

**Expected:** All pass. Current test files:
- `tests/components/trace-viewer.test.tsx` — TraceNode renders badges, agent names, durations, tokens; TraceTree empty state
- `tests/components/agent-console.test.tsx` — AgentList empty state, renders run task/status/tokens

### 3.3 Start Frontend Manually

```bash
mise run dev:web
# or
cd apps/web && bun run dev
```

Open http://localhost:3000 in browser.

**Expected pages:**

| URL | What You Should See |
|-----|-------------------|
| `http://localhost:3000` | E.C.H.O. product landing: "Enterprise Cognitive Hub & Orchestration" headline, Sign In / Get Started buttons. Redirects to `/dashboard` if a session cookie is present. |
| `http://localhost:3000/login` | Login form with email/password fields and "Sign in to E.C.H.O." heading |
| `http://localhost:3000/register` | Registration form with name/email/password and "Create account" heading |
| `http://localhost:3000/dashboard` | Overview with sidebar nav and 3 metric cards populated from `GET /api/agents/stats` (shows `—` while loading, then real totals for runs / tokens / cost) |
| `http://localhost:3000/dashboard/agents` | Agent Console with task submission input + "Run" button, run list populated from `GET /api/agents/runs` |
| `http://localhost:3000/dashboard/rag` | RAG Explorer with search input. Calls `POST /api/rag/query`, shows scored chunks or "No results found" |
| `http://localhost:3000/dashboard/rag/graph` | Knowledge Graph placeholder: "Graph visualization will render here..." (post-MVP) |
| `http://localhost:3000/dashboard/settings` | Settings page showing model config (gemma4:e4b, nomic-embed-text) |
| `http://localhost:3000/dashboard/admin` | Admin panel with placeholder cards for Users, Cost Reports, Audit Logs |

### 3.4 Interactive Frontend Tests

With **both API (port 8000) and frontend (port 3000)** running:

1. **Agent Task Submission:**
   - Go to `/dashboard/agents`
   - Type "Fix the login bug in auth handler" in the task input
   - Click "Run"
   - **Expected:** A new run card appears immediately with task text and "pending"/"running" badge. Within a few seconds (dry-run) or tens of seconds (real Ollama), the badge flips to "completed" and `total_tokens` / `total_cost` fill in.

2. **Agent Run Detail:**
   - Click on the run card you just created
   - **Expected:** Redirects to `/dashboard/agents/[id]`. The WebSocket connects and trace events stream in as they're produced (`run_start`, `agent_start`, `llm_*`, `agent_end`, `run_complete`). The trace viewer fills with per-agent nodes showing duration and token counts. On `stream_end` the WebSocket closes cleanly.

3. **RAG Search:**
   - First populate the index: `mise run index` (or set `ECHO_DRY_RUN=1` to verify the UI path without embeddings — retriever will still return `[]`)
   - Go to `/dashboard/rag`
   - Type "authentication" and click Search
   - **Expected:** Scored chunks from `rag_chunks` ordered by cosine similarity, or "No results found" if the index is empty.

4. **Sidebar Navigation:**
   - Click "Hide sidebar" / "Show sidebar" button
   - **Expected:** Sidebar toggles visibility
   - Navigate between Overview, Agents, RAG Explorer, Settings, Admin
   - **Expected:** Active nav item is highlighted

### 3.5 Auth Flow (requires DB running + Better Auth configured)

> **Note:** Auth requires Better Auth to have initialized its tables. If you get errors, the DB may need Better Auth's auto-migration to run.

1. Go to `/register`
2. Fill in name, email, password
3. Click "Create account"
4. **Expected with working DB:** Redirect to `/dashboard`
5. **Expected without DB or with errors:** No visible error in UI (check browser console for fetch error)

---

## 4. RAG Indexing Test

### 4.1 Run Indexer

```bash
mise run index
# or
cd apps/api && uv run python -m src.rag.indexer
```

**Expected output:**

```
Found N chunks under '.'
Indexed N chunks into rag_chunks (embeddings + pgvector).
```

The indexer scans `.py`, `.ts`, `.tsx`, `.md` files, chunks them (AST-aware for Python, heading-based for Markdown), embeds each chunk via the Ollama `nomic-embed-text` model in batches of 50, **truncates `rag_chunks`**, and inserts fresh rows with 768-dim vectors.

Verify in the DB:

```bash
docker compose exec db psql -U admin -d echo -c "SELECT count(*) FROM rag_chunks;"
docker compose exec db psql -U admin -d echo -c "SELECT file_path, chunk_type, start_line, end_line FROM rag_chunks LIMIT 5;"
```

> **Dry-run mode:** With `ECHO_DRY_RUN=1` the indexer prints the first 5 chunks to stdout and skips embedding + DB writes entirely — use this if Ollama isn't running.

---

## 5. Lint & Format

### 5.1 Python

```bash
cd apps/api
uv run ruff check .      # Lint
uv run ruff format .     # Format
uv run pyright           # Type check
```

### 5.2 TypeScript

```bash
cd apps/web
bun run biome check .       # Lint
bun run biome format . --write  # Format
```

### 5.3 All at once

```bash
mise run lint     # Lint everything
mise run format   # Format everything
```

---

## 6. Full Stack (Docker Compose)

### 6.1 Start Everything

```bash
# Start DB first
docker compose up -d db
sleep 3

# Run migrations
mise run db:migrate

# Start API + Web separately (for live reload)
mise run dev:api &
mise run dev:web &
```

Or use Docker Compose for all services (no live reload for api/web code):

```bash
docker compose up --build
```

### 6.2 Verify All Services

```bash
# DB
docker compose exec db pg_isready -U admin
# Expected: accepting connections

# API
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"0.1.0"}

# Web
curl -s http://localhost:3000 | head -20
# Expected: HTML content (Next.js page)
```

### 6.3 Tear Down

```bash
docker compose down        # Stop containers
docker compose down -v     # Stop + remove volumes (reset DB data)
```

---

## 7. E2E Tests (Playwright)

### 7.1 Install Playwright Browsers

```bash
cd apps/web
bunx playwright install chromium
```

### 7.2 Run E2E

```bash
mise run test:e2e
```

All three specs now point at the correct endpoints:
- `auth.spec.ts` — `POST /api/auth/sign-up/email` against Next.js (Better Auth)
- `agent-run.spec.ts` — same auth setup, then `POST /api/agents/runs` and WebSocket trace assertions
- `rag-explorer.spec.ts` — `POST /api/rag/query`

For a fully green E2E run you need: DB migrated, API running on :8000 with `ECHO_DRY_RUN=1` (or Ollama + models pulled), and the web dev server on :3000.

---

## 8. Current Status Summary (post Phase 2)

| Feature | Status | Notes |
|---------|--------|-------|
| **DB persistence** | ✅ Wired | `agent_runs`, `trace_events`, `audit_log`, `cost_ledger`, `rag_chunks` all read/written by the API |
| **Agent execution** | ✅ Wired | `AgentRunner.execute` runs the LangGraph pipeline via `astream`, updates run status, persists traces and audit entries |
| **WebSocket** | ✅ Wired | `/ws/{run_id}` streams real events from the runner's per-run `asyncio.Queue`; closes on `stream_end` |
| **Gateway middleware** | ✅ Wired | All agent LLM calls go through `gateway_llm_call` (scrub → rate limit → LiteLLM → cost record → audit) |
| **Cost tracking** | ✅ Wired | `CostTracker.record()` accumulates in memory; `flush()` writes `cost_ledger` rows at end of each run |
| **RAG pipeline** | ✅ Wired | Indexer embeds + writes `rag_chunks`; retriever does pgvector cosine search via `<=>` |
| **Dashboard metrics** | ✅ Wired | Overview card fetches `GET /api/agents/stats` |
| **Home page** | ✅ Replaced | Product landing with redirect-if-authenticated |
| **Drizzle parity** | ✅ Complete | `sessions`, `traceEvents`, `auditLog`, `ragChunks`, `graphNodes`, `graphEdges`, `costLedger` all present |
| **E2E tests** | ✅ Endpoints fixed | All specs point at Next.js `/api/auth/*` and correct FastAPI paths |
| **Auth** | Partial | Better Auth handler + pages work; session propagation to FastAPI routes not yet enforced (all routes still accept `user_id=null`) |
| **Knowledge graph viz** | Placeholder | Canvas placeholder only (post-MVP) |
| **Real cost pricing** | Stub | `cost=0.0` always for Ollama; LiteLLM pricing not plumbed for local models |

---

## Quick Verification Checklist

Run these commands in sequence for a quick confidence check:

```bash
# 1. Start infrastructure
docker compose up -d db
mise run db:migrate

# 2. Run unit tests
cd apps/api && uv run pytest -m "not integration and not ollama" -v && cd ../..
cd apps/web && bun run vitest run && cd ../..

# 3. Run integration tests
cd apps/api && uv run pytest -m integration -v && cd ../..

# 4. Verify API
mise run dev:api &
sleep 3
curl http://localhost:8000/health

# 5. Verify frontend builds
cd apps/web && bun run build && cd ../..

# 6. Run indexer
mise run index

# 7. (Optional) Ollama smoke tests
cd apps/api && RUN_OLLAMA_TESTS=1 uv run pytest -m ollama -v && cd ../..
```

If all the above pass, Phase 1 scaffolding **and** Phase 2 wiring are verified. For an end-to-end smoke, run a task through the dashboard (or via `curl POST /api/agents/runs`) with Ollama running (or `ECHO_DRY_RUN=1`) and confirm:

- The run row appears in `agent_runs` and transitions `pending → running → completed`
- `trace_events` contains `agent_start`/`llm_*`/`agent_end` rows for the dispatched nodes
- `audit_log` has `llm_call` entries when LLM calls happen (real mode)
- `cost_ledger` has one row per LLM call after the run completes
- The `/ws/{run_id}` stream delivered `run_start` → `run_complete` → `stream_end`
