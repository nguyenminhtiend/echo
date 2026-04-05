# Project E.C.H.O. Design Specification

**Enterprise Cognitive Hub & Orchestration**

**Date:** 2026-04-05
**Status:** Approved
**Author:** Design collaboration session

---

## 1. Executive Summary

Project E.C.H.O. is a self-hosted, multi-agent AI platform that orchestrates specialized AI agents across the entire SDLC. It demonstrates the paradigm shift from "AI as a tool" to "AI as a systemic cognitive pipeline" — where agents autonomously generate code, review PRs, write tests, scan for security vulnerabilities, produce documentation, and analyze architecture.

The platform serves a dual purpose:
1. **Working software** — a production-grade, containerized platform built with modern polyglot architecture
2. **Interview mastery** — building it deeply internalizes all 50 sections of the AI tools interview knowledge base, enabling confident, authoritative answers grounded in hands-on experience

### Core Principles

- **Local-first**: Runs entirely on developer machines. No cloud API keys required for MVP
- **Privacy by default**: Gemma 4 8B via Ollama — code never leaves the machine
- **Enterprise-grade patterns**: Multi-agent orchestration, Graph RAG, AI gateway, PII scrubbing, audit logging, OTEL tracing
- **Provider-agnostic**: LiteLLM abstraction layer ready for Claude, OpenAI, or any provider when needed

---

## 2. Architecture Overview

### High-Level Architecture

```
+-------------------------------------------------------------+
|                    Next.js 16.2 Dashboard (Bun)              |
|  +----------+ +----------+ +----------+ +-----------+       |
|  | Better   | | Agent    | | RAG      | | Trace     |       |
|  | Auth     | | Console  | | Explorer | | Viewer    |       |
|  +----------+ +----------+ +----------+ +-----------+       |
|         shadcn/ui CLI v4 + Tailwind 4                        |
+--------------------------+----------------------------------+
                           | HTTP (internal)
+--------------------------v----------------------------------+
|              FastAPI ~0.135.3 Backend (Python 3.14)          |
|  +------------------------------------------------------+   |
|  |         LiteLLM >=1.83.0 Middleware                   |   |
|  |  (semantic routing, cost tracking, PII scrub)         |   |
|  +------------------------------------------------------+   |
|  +------------------------------------------------------+   |
|  |         LangGraph 1.1.0 Orchestrator                  |   |
|  |  +----------+ +----------+ +----------+               |   |
|  |  |Supervisor|>|  Coder   | | Reviewer |               |   |
|  |  |  Agent   |>|  Agent   | |  Agent   |               |   |
|  |  |          |>| QA Agent | | Security |               |   |
|  |  |          |>| Arch.    | | Docs     |               |   |
|  |  +----------+ +----------+ +----------+               |   |
|  +------------------------------------------------------+   |
|  +------------------------------------------------------+   |
|  |     LlamaIndex ~0.14.x Graph RAG Pipeline             |   |
|  |  (PropertyGraphIndex -> pgvector + pg relations)      |   |
|  |  Chunking: AST-aware code + semantic docs             |   |
|  |  Embeddings: nomic-embed-text (Ollama local)          |   |
|  +------------------------------------------------------+   |
+--------------------------+----------------------------------+
                           |
+--------------------------v----------------------------------+
|            PostgreSQL 18.3 + pgvector 0.8.2                  |
|  +------------+ +------------+ +------------------+         |
|  | Relational | | Vector     | | Property Graph   |         |
|  | (users,    | | Store      | | (entities,       |         |
|  |  sessions, | | (embeddings| |  relationships,  |         |
|  |  traces)   | | + chunks)  | |  code graph)     |         |
|  +------------+ +------------+ +------------------+         |
+--------------------------+----------------------------------+
                           |
          Ollama API (localhost:11434)
+--------------------------+----------------------------------+
|  Ollama (runs on host, not in Docker)                        |
|  - gemma4:8b          (LLM - reasoning)                     |
|  - nomic-embed-text   (embeddings - 768 dim)                |
+-------------------------------------------------------------+
```

### Docker Compose Services (3 services)

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| `db` | postgres:18 + pgvector | 5432 | PostgreSQL 18.3 with pgvector 0.8.2 |
| `api` | Custom (Python 3.14) | 8000 | FastAPI backend with agents + RAG + gateway |
| `web` | Custom (Bun + Node 24) | 3000 | Next.js 16.2 dashboard |

Ollama runs on the host machine (not containerized) for GPU access.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Monorepo | Yes | Single source of truth, shared DB schema, easier dev |
| Graph DB | PostgreSQL (LlamaIndex PropertyGraphIndex) | No extra service, stores graph as relational tables |
| LLM runtime | Ollama (Gemma 4 8B) local | Zero cost, full privacy, no API keys for MVP |
| Embeddings | nomic-embed-text (Ollama) | Local, free, 768-dim, good code understanding |
| Agent framework | LangGraph 1.1.0 | Stateful graphs, checkpointing, HITL built-in |
| RAG framework | LlamaIndex ~0.14.x | PropertyGraphIndex for Graph RAG |
| Frontend | Next.js 16.2 + shadcn CLI v4 + Bun | Modern stack, great DX |
| Auth | Better Auth 1.5.6 | Active development, native Drizzle support |
| AI Gateway | LiteLLM as FastAPI middleware | Provider-agnostic routing, cost tracking |
| Task queue | asyncio.Queue (in-process) | No Redis needed, simplest for MVP |
| Observability | structlog + OpenTelemetry | Production-grade tracing for trace viewer |
| Version mgmt | mise | Manages Python, Node, Bun versions + task runner |
| Python tooling | uv + ruff + pyright | Modern, fast Python development |
| JS/TS tooling | Biome | Fast linter + formatter, replaces ESLint + Prettier |
| CI/CD | GitHub Actions (deferred) | Designed for but skipped in MVP |

---

## 3. Multi-Agent System (LangGraph)

### Agent Topology

```
                    +--Supervisor--+
         task ----->|    Agent     |
                    +------+-------+
                           | routes to
          +--------+-------+--------+----------+
          v        v       v        v          v
     +--------++--------++----++--------++--------+
     | Coder  || Review || QA || Secur. || Docs   |
     | Agent  || Agent  ||Agnt|| Agent  || Agent  |
     +--------++--------++----++--------++--------+
          |        |       |        |          |
          +--------+-------+--------+----------+
                           |
                    +------v-------+
                    |  Architect   |
                    |   Agent      | (advisory, cross-cutting)
                    +--------------+
```

### Agent Definitions

| Agent | Responsibility | LLM Tier | Tools |
|-------|---------------|----------|-------|
| **Supervisor** | Task classification, delegation, aggregation | Complex | All agent invocations |
| **Coder** | Code generation, refactoring, bug fixes | Complex | File read/write, AST parse, Git |
| **Reviewer** | Code review, style checks, best practices | Moderate | File read, Diff analysis, RAG |
| **QA** | Test generation, coverage analysis, mutation testing | Moderate | File read/write, Test runner, RAG |
| **Security** | OWASP scanning, secret detection, dependency audit | Complex | File read, SAST tools, RAG |
| **Docs** | Documentation generation, changelog | Simple | File read/write, RAG |
| **Architect** | System design analysis, dependency mapping, ADRs | Complex | Graph RAG, File read, codebase analysis |

### Complexity Classifier (Semantic Routing)

Routes tasks to appropriate LLM tiers via LiteLLM:

```python
class TaskComplexity(Enum):
    SIMPLE = "simple"      # -> Gemma 4 8B (local) or future Haiku-tier
    MODERATE = "moderate"  # -> Gemma 4 8B (local) or future Sonnet-tier
    COMPLEX = "complex"    # -> Gemma 4 8B (local) or future Opus-tier

# For MVP with only Gemma 4 local, all routes go to the same model.
# The routing infrastructure is in place for when cloud providers are added.
```

Classification uses a lightweight heuristic:
- Token count of input
- Presence of keywords (refactor, security, architecture = complex)
- Number of files referenced
- Task type from supervisor classification

### LangGraph State Schema

```python
class EchoState(TypedDict):
    task: str                          # Original user request
    task_type: TaskType                # Classified task type
    complexity: TaskComplexity         # Routed complexity
    messages: Annotated[list, add_messages]  # Agent conversation
    artifacts: list[CodeArtifact]      # Generated code/docs
    reviews: list[ReviewFinding]       # Review results
    trace: list[TraceEvent]            # Execution trace for UI
    current_agent: str                 # Active agent name
    iteration: int                     # Loop counter (safety)
    max_iterations: int                # Budget guard
```

### Human-in-the-Loop (HITL) Checkpoints

Using LangGraph's built-in `interrupt_before` / `interrupt_after`:

1. **Post-generation gate** — after Coder produces code, user can review/edit before Reviewer
2. **Pre-deployment gate** — after all agents finish, user reviews aggregated output before any file write/commit
3. **Escalation gate** — Security or Architect agents can flag critical findings that force a human pause

Flow:
```
Supervisor -> Coder -> [HITL: Review code?] -> Reviewer
                              |
                        User approves/rejects/edits
                              |
                        -> QA -> Security -> [HITL: Accept output?]
                                                    |
                                              User accepts/requests changes
                                                    |
                                              -> Docs -> Done
```

Dashboard renders these as interactive approval cards in the trace viewer.

---

## 4. Graph RAG Pipeline (LlamaIndex)

### Indexing Pipeline (offline)

```
Git Repo -> File Scanner -> Chunker -> Embedder -> PostgreSQL
                 |              |          |
           +-----+-----+  +---+----+     |
           | AST Parser |  |Semantic|     |
           | (code)     |  |Splitter|     |
           | tree-sitter|  | (docs) |     |
           +------------+  +--------+     |
                                          |
Entity Extractor -> Relationship Builder -> PropertyGraphIndex
(classes, funcs,    (imports, calls,          (stored in PG)
 modules, files)     inherits, depends_on)
```

### Retrieval Pipeline (online)

```
Query -> Query Router -> +- Vector Search (similarity)
                         +- Graph Traversal (relationships)
                         +- Keyword Search (exact match)
              |
        Reranker -> Context Assembly -> Agent
```

### Graph Schema

**Entity Types (Nodes):**
- `Module` — Python/TypeScript modules
- `Class` — class definitions
- `Function` — function/method definitions
- `File` — source files
- `Config` — configuration files
- `Test` — test files/functions
- `Concept` — abstract domain concepts from docs/comments

**Relationship Types (Edges):**
- `IMPORTS` — module/file imports another
- `CALLS` — function calls another function
- `INHERITS` — class extends another
- `DEFINES` — file defines a class/function
- `TESTS` — test file tests a module/function
- `DEPENDS_ON` — module depends on another (package-level)
- `DOCUMENTS` — doc chunk documents a code entity

### Chunking Strategy

| Content Type | Chunker | Chunk Size | Overlap |
|-------------|---------|------------|---------|
| Python code | AST-aware (tree-sitter) | Per function/class | Include imports + docstring |
| TypeScript code | AST-aware (tree-sitter) | Per function/class/component | Include imports + JSDoc |
| Markdown docs | Semantic (by heading) | ~512 tokens | 50 tokens |
| Config files | Whole file | Entire file | None |

### LlamaIndex Integration

```python
from llama_index.graph_stores.postgres import PGPropertyGraphStore
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding

graph_store = PGPropertyGraphStore(connection_string=PG_URL)
vector_store = PGVectorStore(connection_string=PG_URL)
embed_model = OllamaEmbedding(model_name="nomic-embed-text")

index = PropertyGraphIndex(
    graph_store=graph_store,
    vector_store=vector_store,
    embed_model=embed_model,
)
```

The platform indexes **its own codebase** (self-referential) for demo purposes.

---

## 5. Security, Governance & AI Gateway

### LiteLLM as FastAPI Middleware

```python
from litellm import Router

router = Router(
    model_list=[
        {"model_name": "echo-fast", "litellm_params": {
            "model": "ollama/gemma4:8b",
            "api_base": "http://localhost:11434",
        }},
        # Future cloud providers:
        # {"model_name": "echo-deep", "litellm_params": {
        #     "model": "claude-sonnet-4-6", "api_key": os.getenv("ANTHROPIC_API_KEY")
        # }},
    ],
    routing_strategy="simple-shuffle",
)
```

### Security Layers

| Layer | Implementation | KB Sections |
|-------|---------------|------------|
| **PII Scrubbing** | Pre-request middleware with Presidio (email, phone, SSN, API key patterns) | 11.2, 11.4 |
| **Secret Detection** | Regex scan for AWS keys, JWT tokens, private keys, `.env` patterns | 11.5 |
| **Audit Logging** | Every LLM call logged: timestamp, user, model, token count, cost, input hash | 20.1 |
| **Rate Limiting** | Per-user token/minute limits in middleware | 34.1 |
| **Cost Tracking** | LiteLLM per-request cost, aggregated by user/session/agent in PostgreSQL | 9.1, 42.3 |
| **Input Validation** | Pydantic models validate all API inputs | 36.1 |

### Enterprise Boundary Rules

```
+-------------------------------------------+
|  Trust Boundary: E.C.H.O. Platform        |
|                                            |
|  +------------------------------------+   |
|  |  Inner Zone: Agent Execution        |   |
|  |  - No raw user data in prompts      |   |
|  |  - PII scrubbed before LLM call     |   |
|  |  - Secrets never reach LLM          |   |
|  +------------------------------------+   |
|                                            |
|  +------------------------------------+   |
|  |  Outer Zone: User Interface         |   |
|  |  - Better Auth session validation   |   |
|  |  - RBAC per-feature                 |   |
|  |  - CSRF + rate limiting             |   |
|  +------------------------------------+   |
+-------------------------------------------+
         |
         | (Ollama runs locally)
         v
   LLM: Gemma 4 8B (localhost:11434)
```

---

## 6. Dashboard & Trace Viewer (Next.js)

### Page Structure

| Route | Purpose |
|-------|---------|
| `/` | Landing / Login |
| `/dashboard` | Overview (agent activity, costs, recent runs) |
| `/dashboard/agents` | Agent console (submit tasks, view agent list) |
| `/dashboard/agents/[id]` | Single agent run detail + trace viewer |
| `/dashboard/rag` | RAG explorer (search index, view graph) |
| `/dashboard/rag/graph` | Knowledge graph visualization |
| `/dashboard/settings` | User settings, model config |
| `/dashboard/admin` | Admin panel (users, cost reports, audit logs) |

### Trace Viewer (LangSmith-style)

Rendered using a recursive tree component with shadcn `Collapsible` + custom styling.

Each trace node displays:
- Agent name and duration
- Tool calls with inputs/outputs
- LLM calls with model, token counts, cost
- HITL checkpoints as interactive approval cards
- Expandable raw LLM input/output

Example trace structure:
```
v Supervisor (2.1s)
  +- classify_task -> {type: "bugfix", complexity: "moderate"}
  +- route -> Coder Agent
  |
  v Coder Agent (18.3s)
    +- tool: read_file("src/auth/handler.ts")
    +- tool: graph_rag_query("auth flow dependencies")
    +- llm_call (Gemma 4 8B) -> 3,200 tokens
    +- tool: write_file("src/auth/handler.ts")
    +- result: {files_changed: 1, lines: +12/-3}
  |
  [HITL] Review generated code -> User approved (10.2s)
  |
  v Reviewer Agent (8.4s)
    +- tool: read_diff()
    +- llm_call (Gemma 4 8B) -> 2,100 tokens
    +- result: {findings: 1 warning, 0 critical}
  |
  v QA Agent (12.1s)
    +- tool: generate_test("src/auth/handler.test.ts")
    +- tool: run_tests() -> 5/5 passed
    +- result: {tests_added: 3, coverage: +4.2%}
```

### State Management

- **Zustand ~5.0.12** for client state (UI toggles, form state, active filters)
- **TanStack Query ~5.96.2** for server state (agent runs, traces, RAG results, cost data)
- Never store server data in Zustand — TanStack Query handles caching/refetching

---

## 7. WebSocket Architecture

### Connection Flow

```
Browser (Next.js) <--WebSocket--> FastAPI <--> LangGraph Agent Loop
```

1. Client connects: `ws://localhost:8000/ws/{run_id}`
2. Server streams trace events as JSON messages
3. Client sends HITL responses when checkpoints are reached
4. Server resumes agent execution and continues streaming

### Event Types

| Event Type | Direction | Payload |
|-----------|-----------|---------|
| `agent_start` | Server -> Client | agent name, timestamp |
| `agent_end` | Server -> Client | agent name, duration, result summary |
| `tool_call` | Server -> Client | tool name, input args |
| `tool_result` | Server -> Client | output, duration_ms |
| `llm_start` | Server -> Client | model, tokens_in |
| `llm_end` | Server -> Client | tokens_out, duration_ms, cost |
| `hitl_request` | Server -> Client | checkpoint name, data for review |
| `hitl_response` | Client -> Server | action (approve/reject), feedback |
| `run_complete` | Server -> Client | final summary, total cost, total tokens |

### FastAPI WebSocket Endpoint

```python
@router.websocket("/ws/{run_id}")
async def agent_trace_ws(websocket: WebSocket, run_id: str):
    await websocket.accept()
    event_queue: asyncio.Queue[TraceEvent] = asyncio.Queue()
    agent_runner.register_trace_listener(run_id, event_queue)
    try:
        async for event in dual_channel(websocket, event_queue):
            if isinstance(event, TraceEvent):
                await websocket.send_json(event.model_dump())
            elif isinstance(event, HITLResponse):
                agent_runner.resume_checkpoint(run_id, event)
    finally:
        agent_runner.unregister_trace_listener(run_id)
```

### Next.js Client Hook

```typescript
export const useAgentTrace = (runId: string) => {
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [hitlPending, setHitlPending] = useState<HITLRequest | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${runId}`);
    ws.onmessage = (e) => {
      const event = JSON.parse(e.data);
      if (event.type === "hitl_request") setHitlPending(event);
      else setEvents(prev => [...prev, event]);
    };
    wsRef.current = ws;
    return () => ws.close();
  }, [runId]);

  const respondHITL = (action: "approve" | "reject", feedback?: string) => {
    wsRef.current?.send(JSON.stringify({ type: "hitl_response", action, feedback }));
    setHitlPending(null);
  };

  return { events, hitlPending, respondHITL };
};
```

---

## 8. Database Schema

### PostgreSQL Tables

Both SQLAlchemy (Python) and Drizzle (Next.js) share the same physical tables. SQLAlchemy owns migrations via Alembic. Drizzle provides type-safe reads on the Next.js side.

#### Users & Auth

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(255),
    password_hash VARCHAR(255),
    role          VARCHAR(50) DEFAULT 'user',  -- 'user' | 'admin'
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sessions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at    TIMESTAMPTZ NOT NULL
);
```

Note: Better Auth may auto-create additional tables (accounts, verification_tokens). The schema above shows the core tables; Better Auth's Drizzle adapter will manage its own schema.

#### Agent Runs

```sql
CREATE TABLE agent_runs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id),
    task          TEXT NOT NULL,
    task_type     VARCHAR(50),          -- 'bugfix','feature','review','test',...
    complexity    VARCHAR(20),          -- 'simple','moderate','complex'
    status        VARCHAR(20) DEFAULT 'pending',
                  -- 'pending','running','hitl_waiting','completed','failed'
    result        JSONB,                -- Final aggregated result
    total_tokens  INTEGER DEFAULT 0,
    total_cost    DECIMAL(10,6) DEFAULT 0,
    duration_ms   INTEGER,
    created_at    TIMESTAMPTZ DEFAULT now(),
    completed_at  TIMESTAMPTZ
);
```

#### Trace Events

```sql
CREATE TABLE trace_events (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id        UUID REFERENCES agent_runs(id) ON DELETE CASCADE,
    parent_id     UUID REFERENCES trace_events(id),  -- Tree structure
    event_type    VARCHAR(50) NOT NULL,
                  -- 'agent_start','agent_end','tool_call','tool_result',
                  -- 'llm_start','llm_end','hitl_request','hitl_response'
    agent_name    VARCHAR(50),
    data          JSONB NOT NULL,        -- Event-specific payload
    tokens_in     INTEGER,
    tokens_out    INTEGER,
    cost          DECIMAL(10,6),
    duration_ms   INTEGER,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_trace_events_run ON trace_events(run_id);
CREATE INDEX idx_trace_events_parent ON trace_events(parent_id);
```

#### Cost Tracking

```sql
CREATE TABLE cost_ledger (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id),
    run_id        UUID REFERENCES agent_runs(id),
    model         VARCHAR(100) NOT NULL,
    tokens_in     INTEGER NOT NULL,
    tokens_out    INTEGER NOT NULL,
    cost          DECIMAL(10,6) NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_cost_ledger_user ON cost_ledger(user_id);
CREATE INDEX idx_cost_ledger_created ON cost_ledger(created_at);
```

#### Audit Log

```sql
CREATE TABLE audit_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id),
    action        VARCHAR(100) NOT NULL,
                  -- 'agent_run','llm_call','file_write','config_change'
    resource      VARCHAR(255),
    metadata      JSONB,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);
```

#### RAG: Vector Store (pgvector)

```sql
CREATE TABLE rag_chunks (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content       TEXT NOT NULL,
    embedding     vector(768) NOT NULL,  -- nomic-embed-text = 768 dims
    chunk_type    VARCHAR(50),           -- 'function','class','doc_section','config'
    file_path     VARCHAR(500),
    start_line    INTEGER,
    end_line      INTEGER,
    metadata      JSONB,                 -- Language, module, etc.
    indexed_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_rag_chunks_embedding ON rag_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### RAG: Property Graph (LlamaIndex-managed)

```sql
-- Auto-created by LlamaIndex PropertyGraphIndex, shown for reference
CREATE TABLE graph_nodes (
    id            VARCHAR(255) PRIMARY KEY,
    label         VARCHAR(100) NOT NULL,  -- 'Module','Class','Function','File',...
    properties    JSONB,
    embedding     vector(768)
);

CREATE TABLE graph_edges (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id     VARCHAR(255) REFERENCES graph_nodes(id),
    target_id     VARCHAR(255) REFERENCES graph_nodes(id),
    relation      VARCHAR(100) NOT NULL,  -- 'IMPORTS','CALLS','INHERITS',...
    properties    JSONB
);

CREATE INDEX idx_graph_edges_source ON graph_edges(source_id);
CREATE INDEX idx_graph_edges_target ON graph_edges(target_id);
CREATE INDEX idx_graph_nodes_label ON graph_nodes(label);
```

---

## 9. Monorepo Structure

```
echo/
|-- .mise.toml                       # Version & task management
|-- docker-compose.yml               # PG + FastAPI + Next.js
|-- Dockerfile.api                   # Python backend
|-- Dockerfile.web                   # Next.js frontend
|-- .env.example                     # Environment template
|-- apps/
|   |-- api/                         # Python FastAPI backend
|   |   |-- pyproject.toml           # uv managed
|   |   |-- src/
|   |   |   |-- main.py              # FastAPI app entry
|   |   |   |-- agents/              # LangGraph agent definitions
|   |   |   |   |-- supervisor.py
|   |   |   |   |-- coder.py
|   |   |   |   |-- reviewer.py
|   |   |   |   |-- qa.py
|   |   |   |   |-- security.py
|   |   |   |   |-- docs_agent.py
|   |   |   |   |-- architect.py
|   |   |   |   |-- state.py         # EchoState TypedDict
|   |   |   |   +-- graph.py         # LangGraph StateGraph assembly
|   |   |   |-- rag/                 # LlamaIndex Graph RAG
|   |   |   |   |-- indexer.py       # Indexing pipeline
|   |   |   |   |-- retriever.py     # Query/retrieval
|   |   |   |   |-- chunkers.py      # AST-aware + semantic
|   |   |   |   +-- graph_schema.py  # Entity/relationship defs
|   |   |   |-- gateway/             # AI Gateway / LiteLLM
|   |   |   |   |-- router.py        # Semantic routing
|   |   |   |   |-- scrubber.py      # PII/secret detection
|   |   |   |   +-- tracker.py       # Cost/token tracking
|   |   |   |-- api/                 # FastAPI routes
|   |   |   |   |-- agents.py        # /api/agents/*
|   |   |   |   |-- rag.py           # /api/rag/*
|   |   |   |   |-- traces.py        # /api/traces/*
|   |   |   |   +-- ws.py            # WebSocket endpoint
|   |   |   |-- models/              # SQLAlchemy models
|   |   |   |-- schemas/             # Pydantic schemas
|   |   |   +-- db/                  # Database config + migrations
|   |   |       +-- alembic/
|   |   +-- tests/
|   |
|   +-- web/                         # Next.js 16.2 dashboard (Bun)
|       |-- package.json
|       |-- biome.json               # Biome linter/formatter
|       |-- src/
|       |   |-- app/                 # App Router pages
|       |   |   |-- (auth)/          # Login/register
|       |   |   |-- dashboard/       # Dashboard pages
|       |   |   +-- api/             # API routes (BFF)
|       |   |-- components/          # shadcn/ui + custom
|       |   |   |-- ui/              # shadcn primitives
|       |   |   |-- trace-viewer/    # LangSmith-style traces
|       |   |   |-- agent-console/   # Agent task submission
|       |   |   +-- graph-viz/       # Knowledge graph viewer
|       |   |-- lib/                 # Utilities
|       |   |   |-- api-client.ts    # FastAPI client
|       |   |   |-- auth.ts          # Better Auth config
|       |   |   +-- stores/          # Zustand stores
|       |   +-- db/                  # Drizzle schema + config
|       +-- tests/
|
|-- docs/
|   +-- superpowers/
|       +-- specs/                   # Design docs
+-- ai-tools-interview-kb.md        # Reference KB (50 sections)
```

---

## 10. mise Configuration

```toml
# .mise.toml (project root)
[tools]
python = "3.14"
node = "24"
bun = "latest"

[env]
DATABASE_URL = "postgresql://echo:echo@localhost:5432/echo"
OLLAMA_BASE_URL = "http://localhost:11434"

[tasks.dev]
description = "Start all services for development"
run = "docker compose up -d db && mise run dev:api & mise run dev:web"

[tasks."dev:api"]
description = "Start FastAPI backend"
dir = "apps/api"
run = "uv run fastapi dev src/main.py --port 8000"

[tasks."dev:web"]
description = "Start Next.js frontend"
dir = "apps/web"
run = "bun run dev"

[tasks."db:migrate"]
description = "Run Alembic migrations"
dir = "apps/api"
run = "uv run alembic upgrade head"

[tasks."db:reset"]
description = "Reset database"
run = "docker compose down db -v && docker compose up -d db && sleep 2 && mise run db:migrate"

[tasks.index]
description = "Run RAG indexing pipeline on own codebase"
dir = "apps/api"
run = "uv run python -m src.rag.indexer"

[tasks.lint]
description = "Lint all code"
run = """
cd apps/api && uv run ruff check . && uv run pyright
cd ../web && bun run biome check .
"""

[tasks.test]
description = "Run all tests"
run = """
cd apps/api && uv run pytest
cd ../web && bun run vitest run
"""

[tasks.format]
description = "Format all code"
run = """
cd apps/api && uv run ruff format .
cd ../web && bun run biome format . --write
"""

[tasks."test:e2e"]
description = "Run Playwright E2E tests"
dir = "apps/web"
run = "bunx playwright test"
```

---

## 11. Version Manifest

### Runtime & Tooling

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.14 | Backend runtime |
| Node.js | 24.x | Next.js build tooling |
| Bun | latest | Next.js runtime, package manager |
| mise | latest | Version & task management |
| uv | latest | Python package manager |
| ruff | latest | Python linter + formatter |
| pyright | latest | Python type checker |
| Biome | latest | JS/TS linter + formatter |

### Infrastructure

| Component | Version | Notes |
|-----------|---------|-------|
| PostgreSQL | 18.3 | uuidv7(), virtual generated columns |
| pgvector | 0.8.2 | 768-dim vectors, IVFFlat index |
| Docker | latest | Container runtime |
| Docker Compose | v2 | 3-service orchestration |
| Ollama | latest | Local LLM runtime (host-installed) |

### Python Backend (apps/api)

| Package | Pin | Purpose |
|---------|-----|---------|
| fastapi | ~=0.135.3 | Web framework |
| pydantic | ~=2.12.5 | Data validation/schemas |
| sqlalchemy | ~=2.0.49 | Async ORM |
| alembic | ~=1.18.4 | Database migrations |
| langgraph | ~=1.1.0 | Multi-agent orchestration |
| llama-index-core | ~=0.14 | RAG framework |
| llama-index-graph-stores-postgres | latest | PropertyGraphIndex in PG |
| llama-index-vector-stores-postgres | latest | pgvector integration |
| llama-index-embeddings-ollama | latest | Local embeddings |
| litellm | >=1.83.0 | AI gateway (**NOT 1.82.7-8: supply chain attack**) |
| structlog | ~=25.5.0 | Structured logging |
| opentelemetry-sdk | ~=1.40.0 | Distributed tracing |
| opentelemetry-api | ~=1.40.0 | OTEL API |
| tree-sitter | ~=0.25.2 | AST-aware code chunking |
| tree-sitter-python | ~=0.25.0 | Python grammar |
| tree-sitter-typescript | latest | TypeScript grammar |
| asyncpg | latest | Async PostgreSQL driver |
| uvicorn | latest | ASGI server |
| websockets | latest | WebSocket support |
| presidio-analyzer | latest | PII detection/scrubbing |
| pytest | latest | Testing |

### Next.js Frontend (apps/web)

| Package | Pin | Purpose |
|---------|-----|---------|
| next | ~=16.2 | React framework (Bun runtime) |
| react | 19.x | UI library |
| better-auth | ~=1.5.6 | Authentication |
| drizzle-orm | ~=0.45.2 | Type-safe PostgreSQL ORM |
| drizzle-kit | latest | Drizzle migrations/studio |
| shadcn/ui | CLI v4 | Component library |
| tailwindcss | 4.x | Styling |
| zustand | ~=5.0.12 | Client state management |
| @tanstack/react-query | ~=5.96.2 | Server state/caching |
| vitest | ~=4.1.2 | Unit/integration testing |
| playwright | ~=1.59.1 | E2E testing |

### LLM Models (Ollama)

| Model | Size | Purpose |
|-------|------|---------|
| gemma4:8b | ~5GB | Primary reasoning LLM |
| nomic-embed-text | ~274MB | Embedding model (768 dimensions) |

### Security Notes

- **LiteLLM 1.82.7 and 1.82.8 were compromised** in a supply chain attack (March 24, 2026). Always pin >=1.83.0.
- **pgvector 0.8.2** fixes CVE-2026-3172 (buffer overflow in parallel HNSW builds). Do not use earlier versions.

---

## 12. Interview Knowledge Coverage

Building this project provides hands-on experience with all 50 KB sections:

| KB Section | E.C.H.O. Component |
|-----------|-------------------|
| 1. Foundations | Overall architecture demonstrates AI-native SDLC |
| 2. AI-Assisted Dev | Coder/Reviewer agents implement assisted development |
| 3. Claude Code Deep Dive | Platform concepts mirror Claude Code's architecture |
| 4. MCP | LiteLLM acts as the tool-connection layer |
| 5. Hooks System | PreToolUse-style validation in gateway middleware |
| 6. Skills & CLAUDE.md | Agent instructions parallel CLAUDE.md patterns |
| 7. Sub-Agents | LangGraph multi-agent = sub-agent orchestration |
| 8. Prompt Engineering | Agent prompt design for each role |
| 9. Token Usage & Cost | Cost tracking dashboard, semantic routing |
| 10. Memory & Compaction | Agent state management across turns |
| 11. Security & DLP | PII scrubbing, secret detection, audit logging |
| 12. Automation & CI/CD | Designed for GitHub Actions (deferred) |
| 13. Workflow Design | Supervisor + fan-out + HITL patterns |
| 14-18. Role-Specific | Each agent maps to a role workflow |
| 19. RAG & Embeddings | Full Graph RAG pipeline with LlamaIndex |
| 20. Governance | Audit log, RBAC, enterprise boundary rules |
| 21. Advanced Topics | Graph RAG, hybrid execution, OTEL |
| 22-23. Scenarios | Real implementation of scenario patterns |
| 24. Permissions | RBAC, tool-level permissions per agent |
| 25. Extended Thinking | Complexity classifier maps to reasoning effort |
| 26. Platforms & IDE | Dashboard as the platform UI |
| 27. Worktrees | Agent isolation via state boundaries |
| 28. Structured Output | JSON schema for agent communication |
| 29. OAuth & API Security | Better Auth, API security patterns |
| 30. Agent SDK | LangGraph = custom agent building |
| 31. Batch API | Batch indexing pipeline |
| 32. Multi-Modal | Trace viewer renders visual data |
| 33. Code Attribution | Agent output attribution tracking |
| 34. Rate Limiting | LiteLLM rate limiting middleware |
| 35. Incident Response | Security agent pattern |
| 36. Guardrails | Input/output validation, PII scrubbing |
| 37. Model Selection | Semantic routing across providers |
| 38. Additional Scenarios | Real-world patterns implemented |
| 39. Memory System | Agent state persistence |
| 40. Remote Agents | Designed for remote agent extension |
| 41. Evals | Trace data enables quality measurement |
| 42. Developer Metrics | Cost dashboard, token tracking |
| 43. IaC | Docker Compose infrastructure |
| 44. Docker & Sandboxing | Containerized agent execution |
| 45. Prompt Libraries | Agent prompt templates |
| 46. AI Code Debt | Reviewer agent checks for debt patterns |
| 47. Context Window | Agent context management |
| 48. API Deep Dive | Tool use, streaming, WebSocket |
| 49. Database Ops | Alembic migrations, schema design |
| 50. Edge AI | Ollama local-first execution |

---

## 13. Future Extensions (Post-MVP)

- **GitHub Actions CI/CD**: Automated PR review pipeline with agents
- **Cloud LLM providers**: Add Claude, OpenAI, Gemini via LiteLLM config
- **Redis + ARQ**: Production task queue for agent execution
- **Neo4j**: Dedicated graph database for larger codebases
- **Ollama in Docker**: Fully containerized stack (needs GPU passthrough)
- **MCP servers**: Connect agents to external tools (Jira, Slack, GitHub)
- **Computer Use**: Browser-based UI testing agent
- **Batch API integration**: Nightly codebase audits
- **Remote agents**: Scheduled triggers for automated maintenance
