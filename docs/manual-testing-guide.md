# E.C.H.O. Manual Testing Guide

Local manual testing procedures for verifying the current state of the E.C.H.O. platform.

**Last updated:** 2026-04-08

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
- `test_gateway/test_tracker.py` — cost tracking
- `test_gateway/test_rate_limiter.py` — rate limiting logic
- `test_agents/test_state.py` — EchoState TypedDict shape
- `test_agents/test_graph.py` — LangGraph compilation, all nodes present
- `test_agents/test_supervisor.py` — task type classification (bugfix, feature, review, etc.)
- `test_api/test_agents_api.py` — create/list agent runs (stub responses)
- `test_api/test_traces_api.py` — trace 404 for unknown run
- `test_api/test_rag_api.py` — RAG query returns empty results

### 2.3 Integration Tests (requires Docker)

```bash
cd apps/api
uv run pytest -m integration -v
```

**Expected:** All pass. These use testcontainers to spin up a real Postgres with pgvector. Tests:
- `test_health_db.py` — /health with real DB, pgvector extension present, all tables created
- `test_rag_flow.py` — chunker splits fixture file, RagChunk insert/select, vector column type verification
- `test_agents_flow.py` — POST creates run (stub), trace returns 404 (expected with current stubs)

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

# Create agent run (stub - returns fake UUID, no DB persistence)
curl -X POST http://localhost:8000/api/agents/runs \
  -H "Content-Type: application/json" \
  -d '{"task":"Fix the login bug in auth handler"}'
# Expected: 201 with JSON containing id, task, status="pending"

# List agent runs (stub - always empty)
curl http://localhost:8000/api/agents/runs
# Expected: {"runs":[],"total":0}

# Get trace (stub - always 404)
curl http://localhost:8000/api/traces/00000000-0000-0000-0000-000000000000
# Expected: 404 {"detail":"Run not found"}

# RAG query (stub - always empty)
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"auth flow","top_k":5}'
# Expected: {"results":[],"query":"auth flow"}
```

### 2.6 WebSocket Test

With the API server running:

```bash
# Using websocat (brew install websocat) or wscat (npm i -g wscat)
websocat ws://localhost:8000/ws/test-run-id
# or
wscat -c ws://localhost:8000/ws/test-run-id
```

**Expected:** Connection establishes. No events are pushed (no producer wired yet). Sending a JSON message like `{"type":"hitl_response","action":"approve"}` is accepted silently.

> **Current limitation:** WebSocket connects but no trace events are ever pushed because agent execution is not wired to the WS endpoint yet (Phase 2, Task 17).

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
| `http://localhost:3000` | Default Next.js template page (not yet replaced with product landing) |
| `http://localhost:3000/login` | Login form with email/password fields and "Sign in to E.C.H.O." heading |
| `http://localhost:3000/register` | Registration form with name/email/password and "Create account" heading |
| `http://localhost:3000/dashboard` | Dashboard overview with sidebar nav, 3 metric cards (all showing 0), "Recent Runs" section |
| `http://localhost:3000/dashboard/agents` | Agent Console with task submission input + "Run" button, empty run list |
| `http://localhost:3000/dashboard/rag` | RAG Explorer with search input, returns "No results found" on any query |
| `http://localhost:3000/dashboard/rag/graph` | Knowledge Graph placeholder: "Graph visualization will render here..." |
| `http://localhost:3000/dashboard/settings` | Settings page showing model config (gemma4:8b, nomic-embed-text) |
| `http://localhost:3000/dashboard/admin` | Admin panel with placeholder cards for Users, Cost Reports, Audit Logs |

### 3.4 Interactive Frontend Tests

With **both API (port 8000) and frontend (port 3000)** running:

1. **Agent Task Submission:**
   - Go to `/dashboard/agents`
   - Type "Fix the login bug in auth handler" in the task input
   - Click "Run"
   - **Expected:** A new run card appears in the list with task text, "pending" badge, "0 tokens", "$0.0000"
   - **Note:** Run won't progress (agent execution not wired yet)

2. **Agent Run Detail:**
   - Click on the run card you just created
   - **Expected:** Redirects to `/dashboard/agents/[id]`, shows "Run [8chars]..." heading, "Disconnected" badge (WebSocket connects then closes because no events), "Waiting for trace events..."

3. **RAG Search:**
   - Go to `/dashboard/rag`
   - Type "authentication" and click Search
   - **Expected:** "No results found." (RAG retriever returns empty)

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
Indexed N chunks from codebase
  - ./apps/api/src/main.py:1-52 (function)
  - ./apps/api/src/config.py:1-12 (class)
  - ...
```

The indexer scans `.py`, `.ts`, `.tsx`, `.md` files, chunks them (AST-aware for Python, heading-based for Markdown), and reports the count.

> **Current limitation:** Chunks are generated but NOT written to the database. They're only printed to stdout. Full DB integration is Phase 2, Task 20.

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

> **Known issues:** E2E tests currently have endpoint mismatches:
> - `auth.spec.ts` hits `http://localhost:8000/auth/register` — should be `http://localhost:3000/api/auth/sign-up/email`
> - `agent-run.spec.ts` has the same auth issue in `beforeEach`
> - `rag-explorer.spec.ts` hits `POST http://localhost:8000/rag/chunks` — should be `POST http://localhost:8000/api/rag/query`
>
> These will be fixed in Phase 2, Task 21.

---

## 8. Current Limitations Summary

| Feature | Status | What Works | What Doesn't |
|---------|--------|------------|--------------|
| **DB persistence** | Stub | Tables exist, models defined | API routes don't read/write DB |
| **Agent execution** | Stub | LangGraph compiles, supervisor classifies | Agents don't call LLM, runs don't execute |
| **WebSocket** | Shell | Connects, accepts messages | No trace events pushed from runs |
| **RAG** | Partial | Chunking + scanning works | No DB storage, no vector search |
| **PII scrubbing** | Library | Works standalone in tests | Not wired into request pipeline |
| **Cost tracking** | In-memory | Tracks in-memory correctly | Not persisted to cost_ledger table |
| **Auth** | Partial | Better Auth handler exists, login/register pages render | Full E2E auth flow untested |
| **Dashboard** | Static | All pages render, navigation works | Shows hardcoded zeros, no real data |
| **Home page** | Placeholder | Loads | Shows default Next.js CNA template |

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

If all the above pass, Phase 1 scaffolding is verified. Phase 2 (wiring + integration) is needed to make the system functional end-to-end.
