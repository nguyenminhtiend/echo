# Project E.C.H.O. Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-hosted, multi-agent AI platform (E.C.H.O.) that orchestrates specialized AI agents across the SDLC, with a FastAPI backend, Next.js dashboard, LangGraph agents, LlamaIndex Graph RAG, and PostgreSQL storage — all running locally via Ollama.

**Architecture:** Monorepo with `apps/api` (Python 3.14, FastAPI, LangGraph, LlamaIndex, LiteLLM) and `apps/web` (Next.js 16.2, Bun, shadcn/ui, Better Auth). PostgreSQL 18.3 + pgvector 0.8.2 for relational, vector, and graph storage. Ollama on host for Gemma 4 8B and nomic-embed-text. Docker Compose orchestrates 3 services (db, api, web).

**Tech Stack:** Python 3.14, FastAPI ~0.135.3, LangGraph 1.1.0, LlamaIndex ~0.14.x, LiteLLM >=1.83.0, Next.js 16.2, Bun, React 19, shadcn/ui CLI v4, Tailwind 4, Better Auth 1.5.6, Drizzle ORM ~0.45.2, Zustand ~5.0.12, TanStack Query ~5.96.2, PostgreSQL 18.3, pgvector 0.8.2, Ollama (gemma4:8b, nomic-embed-text), mise, uv, ruff, pyright, Biome.

---

## File Structure

### Claude Code Configuration (Task 0)
```
echo/
├── CLAUDE.md                          # Project overview, tech stack, conventions, commands
├── CLAUDE.local.md                    # Local overrides (empty)
├── .claude/
│   ├── settings.json                  # Permissions, tool access, hooks
│   ├── settings.local.json            # Local overrides (empty)
│   ├── rules/
│   │   ├── code-style.md              # Code style rules (empty)
│   │   ├── testing.md                 # Testing rules (empty)
│   │   └── api-conventions.md         # API convention rules (empty)
│   ├── commands/
│   │   ├── review.md                  # Review slash command (empty)
│   │   └── fix-issue.md               # Fix-issue slash command (empty)
│   ├── skills/
│   │   └── deploy/
│   │       ├── SKILL.md               # Deploy skill definition (empty)
│   │       └── deploy-config.md       # Deploy configuration (empty)
│   ├── agents/
│   │   ├── code-reviewer.md           # Code reviewer agent (empty)
│   │   └── security-auditor.md        # Security auditor agent (empty)
│   └── hooks/
│       └── validate-bash.sh           # Bash validation hook script
```

### Monorepo Scaffolding (Task 1)
```
echo/
├── .gitignore
├── .mise.toml                         # Version & task management
├── .env.example                       # Environment template
├── docker-compose.yml                 # PG + FastAPI + Next.js
├── Dockerfile.api                     # Python backend container
├── Dockerfile.web                     # Next.js frontend container
```

### Python Backend (Tasks 2-8)
```
echo/apps/api/
├── pyproject.toml                     # uv managed dependencies
├── src/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app entry
│   ├── config.py                      # Settings via pydantic-settings
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py                 # Async SQLAlchemy engine + session
│   │   └── alembic/
│   │       ├── alembic.ini
│   │       ├── env.py
│   │       └── versions/              # Migration files
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                    # User + Session tables
│   │   ├── agent_run.py               # AgentRun table
│   │   ├── trace_event.py             # TraceEvent table
│   │   ├── cost_ledger.py             # CostLedger table
│   │   ├── audit_log.py               # AuditLog table
│   │   └── rag.py                     # rag_chunks, graph_nodes, graph_edges
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent request/response schemas
│   │   ├── trace.py                   # Trace event schemas
│   │   └── rag.py                     # RAG query/response schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── agents.py                  # /api/agents/* routes
│   │   ├── rag.py                     # /api/rag/* routes
│   │   ├── traces.py                  # /api/traces/* routes
│   │   └── ws.py                      # WebSocket endpoint
│   ├── gateway/
│   │   ├── __init__.py
│   │   ├── router.py                  # LiteLLM semantic routing
│   │   ├── scrubber.py                # PII/secret detection
│   │   ├── tracker.py                 # Cost/token tracking
│   │   └── rate_limiter.py            # Per-user token/minute rate limiting
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py                   # EchoState TypedDict
│   │   ├── graph.py                   # LangGraph StateGraph assembly
│   │   ├── supervisor.py              # Supervisor agent
│   │   ├── coder.py                   # Coder agent
│   │   ├── reviewer.py                # Reviewer agent
│   │   ├── qa.py                      # QA agent
│   │   ├── security.py                # Security agent
│   │   ├── docs_agent.py              # Docs agent
│   │   └── architect.py               # Architect agent
│   └── rag/
│       ├── __init__.py
│       ├── indexer.py                  # Indexing pipeline
│       ├── retriever.py               # Query/retrieval
│       ├── chunkers.py                # AST-aware + semantic chunking
│       └── graph_schema.py            # Entity/relationship definitions
└── tests/
    ├── __init__.py
    ├── conftest.py                    # Shared fixtures
    ├── test_main.py                   # Health check test
    ├── test_models.py                 # Model tests
    ├── test_gateway/
    │   ├── test_router.py
    │   ├── test_scrubber.py
    │   ├── test_tracker.py
    │   └── test_rate_limiter.py
    ├── test_agents/
    │   ├── test_state.py
    │   ├── test_graph.py
    │   └── test_supervisor.py
    └── test_api/
        ├── test_agents_api.py
        ├── test_traces_api.py
        └── test_rag_api.py
```

### Next.js Frontend (Tasks 9-13)
```
echo/apps/web/
├── package.json
├── biome.json                         # Biome linter/formatter
├── tsconfig.json
├── next.config.ts
├── src/
│   ├── app/
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing / Login
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/
│   │   │   ├── layout.tsx             # Dashboard shell
│   │   │   ├── page.tsx               # Overview
│   │   │   ├── agents/
│   │   │   │   ├── page.tsx           # Agent console
│   │   │   │   └── [id]/page.tsx      # Run detail + trace viewer
│   │   │   ├── rag/
│   │   │   │   ├── page.tsx           # RAG explorer
│   │   │   │   └── graph/page.tsx     # Knowledge graph viz
│   │   │   ├── settings/page.tsx      # User settings
│   │   │   └── admin/page.tsx         # Admin panel
│   │   └── api/                       # BFF API routes
│   │       └── auth/[...all]/route.ts # Better Auth handler
│   ├── components/
│   │   ├── ui/                        # shadcn primitives (generated)
│   │   ├── trace-viewer/
│   │   │   ├── trace-tree.tsx         # Recursive trace tree
│   │   │   ├── trace-node.tsx         # Single trace event
│   │   │   └── hitl-card.tsx          # HITL approval card
│   │   ├── agent-console/
│   │   │   ├── task-form.tsx          # Task submission form
│   │   │   └── agent-list.tsx         # Agent list view
│   │   └── graph-viz/
│   │       └── knowledge-graph.tsx    # Knowledge graph viewer
│   ├── lib/
│   │   ├── api-client.ts             # FastAPI HTTP client
│   │   ├── ws-client.ts              # WebSocket hook
│   │   ├── auth.ts                   # Better Auth config
│   │   ├── types.ts                  # Shared TypeScript interfaces
│   │   ├── query-provider.tsx        # TanStack Query provider
│   │   └── stores/
│   │       └── ui-store.ts           # Zustand UI state
│   └── db/
│       ├── schema.ts                 # Drizzle schema (read-only mirror)
│       └── drizzle.config.ts         # Drizzle config
└── tests/
    ├── setup.ts
    └── components/
        ├── trace-viewer.test.tsx
        └── agent-console.test.tsx
```

---

## Task 0: Claude Code Project Structure

**Goal:** Set up the Claude Code configuration files as the project foundation. This ensures consistent AI-assisted development from the start.

**Files:**
- Create: `CLAUDE.md`
- Create: `CLAUDE.local.md`
- Create: `.claude/settings.json`
- Create: `.claude/settings.local.json`
- Create: `.claude/rules/code-style.md`
- Create: `.claude/rules/testing.md`
- Create: `.claude/rules/api-conventions.md`
- Create: `.claude/commands/review.md`
- Create: `.claude/commands/fix-issue.md`
- Create: `.claude/skills/deploy/SKILL.md`
- Create: `.claude/skills/deploy/deploy-config.md`
- Create: `.claude/agents/code-reviewer.md`
- Create: `.claude/agents/security-auditor.md`
- Create: `.claude/hooks/validate-bash.sh`

- [ ] **Step 1: Create CLAUDE.md with full project context**

```markdown
# Project E.C.H.O. — Enterprise Cognitive Hub & Orchestration

## Overview

Self-hosted, multi-agent AI platform that orchestrates specialized AI agents across the entire SDLC. Agents autonomously generate code, review PRs, write tests, scan for security vulnerabilities, produce documentation, and analyze architecture.

**Core Principles:**
- Local-first: Runs entirely on developer machines via Ollama
- Privacy by default: Gemma 4 8B — code never leaves the machine
- Enterprise-grade patterns: Multi-agent orchestration, Graph RAG, AI gateway, PII scrubbing, audit logging, OTEL tracing
- Provider-agnostic: LiteLLM abstraction layer ready for any provider

## Tech Stack

### Backend (`apps/api/`)
- **Runtime:** Python 3.14
- **Framework:** FastAPI ~0.135.3
- **ORM:** SQLAlchemy ~2.0.49 (async) + Alembic ~1.18.4
- **Agents:** LangGraph 1.1.0 (multi-agent orchestration)
- **RAG:** LlamaIndex ~0.14.x (PropertyGraphIndex, Graph RAG)
- **AI Gateway:** LiteLLM >=1.83.0 (semantic routing, cost tracking)
- **Observability:** structlog ~25.5.0 + OpenTelemetry ~1.40.0
- **PII:** Presidio (email, phone, SSN, API key scrubbing)
- **AST Parsing:** tree-sitter ~0.25.2

### Frontend (`apps/web/`)
- **Runtime:** Bun + Node 24
- **Framework:** Next.js 16.2 (App Router)
- **UI:** React 19 + shadcn/ui CLI v4 + Tailwind 4
- **Auth:** Better Auth 1.5.6
- **ORM:** Drizzle ORM ~0.45.2 (read-only, shared PG)
- **State:** Zustand ~5.0.12 (client) + TanStack Query ~5.96.2 (server)
- **Testing:** Vitest ~4.1.2 + Playwright ~1.59.1

### Infrastructure
- **Database:** PostgreSQL 18.3 + pgvector 0.8.2
- **LLM:** Ollama — gemma4:8b (reasoning) + nomic-embed-text (embeddings, 768 dim)
- **Containers:** Docker Compose (3 services: db, api, web)
- **Version Manager:** mise (Python, Node, Bun)

## Architecture

```
Next.js 16.2 (Bun) → FastAPI (Python 3.14) → PostgreSQL 18.3 + pgvector
                            ↓
                    LiteLLM Middleware (routing, PII scrub, cost tracking)
                            ↓
                    LangGraph Orchestrator (Supervisor → Coder/Reviewer/QA/Security/Docs/Architect)
                            ↓
                    LlamaIndex Graph RAG (PropertyGraphIndex → pgvector + pg relations)
                            ↓
                    Ollama (localhost:11434) — gemma4:8b + nomic-embed-text
```

## Coding Conventions

### Python (`apps/api/`)
- Formatter/Linter: `ruff` (format + check)
- Type checker: `pyright`
- Package manager: `uv`
- Test runner: `pytest`
- Async everywhere: use `async def` for all route handlers and DB operations
- Pydantic models for all API request/response schemas
- SQLAlchemy 2.0 style (mapped_column, async session)

### TypeScript (`apps/web/`)
- Formatter/Linter: `biome` (replaces ESLint + Prettier)
- Package manager: `bun`
- Test runner: `vitest` (unit) + `playwright` (e2e)
- Server Components by default; `"use client"` only when needed
- Never store server data in Zustand — use TanStack Query for server state
- shadcn/ui components via CLI (`bunx shadcn@latest add <component>`)

### General
- No `any` types in TypeScript
- All database access through ORM (no raw SQL outside migrations)
- Environment variables via `.env` — never hardcode secrets

## Available Commands (mise)

```bash
mise run dev              # Start all services (db + api + web)
mise run dev:api          # Start FastAPI backend on :8000
mise run dev:web          # Start Next.js frontend on :3000
mise run db:migrate       # Run Alembic migrations
mise run db:reset         # Reset database (destroy + recreate + migrate)
mise run index            # Run RAG indexing pipeline on own codebase
mise run lint             # Lint all code (ruff + pyright + biome)
mise run test             # Run all tests (pytest + vitest)
mise run format           # Format all code (ruff + biome)
mise run test:e2e         # Run Playwright E2E tests
```

## Security Notes

- **LiteLLM >=1.83.0 ONLY** — versions 1.82.7 and 1.82.8 were compromised (supply chain attack, March 2026)
- **pgvector 0.8.2 ONLY** — earlier versions have CVE-2026-3172 (buffer overflow)
- PII scrubbed before any LLM call (Presidio middleware)
- Secrets never reach the LLM — regex scan for AWS keys, JWT tokens, private keys
- All LLM calls audit-logged: timestamp, user, model, token count, cost, input hash
```

- [ ] **Step 2: Create CLAUDE.local.md (empty)**

Create an empty file:

```markdown
```

This file is for local developer overrides and is gitignored.

- [ ] **Step 3: Create .claude/settings.json with practical defaults**

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "Bash(mise run *)",
      "Bash(cd apps/api && uv run *)",
      "Bash(cd apps/web && bun *)",
      "Bash(docker compose *)",
      "Bash(git *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl * | bash)",
      "Bash(wget * | bash)"
    ]
  },
  "hooks": {
    "Bash": {
      "pre": [".claude/hooks/validate-bash.sh"]
    }
  }
}
```

- [ ] **Step 4: Create .claude/settings.local.json (empty)**

```json
{}
```

- [ ] **Step 5: Create rule files in .claude/rules/**

Create `.claude/rules/code-style.md`:
```markdown
```

Create `.claude/rules/testing.md`:
```markdown
```

Create `.claude/rules/api-conventions.md`:
```markdown
```

- [ ] **Step 6: Create command files in .claude/commands/**

Create `.claude/commands/review.md`:
```markdown
```

Create `.claude/commands/fix-issue.md`:
```markdown
```

- [ ] **Step 7: Create skill files in .claude/skills/deploy/**

Create `.claude/skills/deploy/SKILL.md`:
```markdown
```

Create `.claude/skills/deploy/deploy-config.md`:
```markdown
```

- [ ] **Step 8: Create agent files in .claude/agents/**

Create `.claude/agents/code-reviewer.md`:
```markdown
```

Create `.claude/agents/security-auditor.md`:
```markdown
```

- [ ] **Step 9: Create validate-bash.sh hook script**

Create `.claude/hooks/validate-bash.sh`:

```bash
#!/usr/bin/env bash
# validate-bash.sh — Pre-hook for Bash tool calls
# Runs before any Bash command executed by Claude Code.
# Exit 0 to allow, exit non-zero to block.

set -euo pipefail

COMMAND="${CLAUDE_BASH_COMMAND:-}"

# Block dangerous patterns
if echo "$COMMAND" | grep -qE '(rm\s+-rf\s+/|mkfs\.|dd\s+if=|>\s*/dev/sd)'; then
  echo "BLOCKED: Dangerous command pattern detected: $COMMAND" >&2
  exit 1
fi

# Log all commands for audit
echo "[validate-bash] $(date -u +%Y-%m-%dT%H:%M:%SZ) — $COMMAND" >> /tmp/echo-claude-bash-audit.log

exit 0
```

- [ ] **Step 10: Make validate-bash.sh executable and verify structure**

Run:
```bash
chmod +x .claude/hooks/validate-bash.sh
```

Verify the full structure:
```bash
find .claude -type f | sort
```

Expected output:
```
.claude/agents/code-reviewer.md
.claude/agents/security-auditor.md
.claude/commands/fix-issue.md
.claude/commands/review.md
.claude/hooks/validate-bash.sh
.claude/rules/api-conventions.md
.claude/rules/code-style.md
.claude/rules/testing.md
.claude/settings.json
.claude/settings.local.json
.claude/skills/deploy/SKILL.md
.claude/skills/deploy/deploy-config.md
```

Also verify root files:
```bash
ls CLAUDE.md CLAUDE.local.md
```

Expected: both files exist.

- [ ] **Step 11: Commit Claude Code project structure**

```bash
git init
git add CLAUDE.md CLAUDE.local.md .claude/
git commit -m "chore: add Claude Code project structure

Set up CLAUDE.md with full project context (tech stack, architecture,
conventions, commands), .claude/ directory with settings, rules,
commands, skills, agents, and hooks. Foundation for AI-assisted
development workflow."
```

---

## Task 1: Monorepo Scaffolding & Infrastructure

**Goal:** Initialize the monorepo with mise, Docker Compose, Dockerfiles, and environment configuration.

**Files:**
- Create: `.gitignore`
- Create: `.mise.toml`
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `Dockerfile.api`
- Create: `Dockerfile.web`

- [ ] **Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
dist/
.ruff_cache/

# Node / Bun
node_modules/
.next/
.turbo/

# Environment
.env
.env.local
*.local.md

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Docker
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/

# Alembic
apps/api/src/db/alembic/versions/__pycache__/
```

- [ ] **Step 2: Create .mise.toml**

```toml
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

- [ ] **Step 3: Create .env.example**

```env
# Database
DATABASE_URL=postgresql://echo:echo@localhost:5432/echo
POSTGRES_USER=echo
POSTGRES_PASSWORD=echo
POSTGRES_DB=echo

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# LLM Model
ECHO_LLM_MODEL=ollama/gemma4:8b
ECHO_EMBED_MODEL=nomic-embed-text

# App
API_PORT=8000
WEB_PORT=3000
SECRET_KEY=change-me-in-production
```

- [ ] **Step 4: Create docker-compose.yml**

```yaml
services:
  db:
    image: pgvector/pgvector:0.8.2-pg18
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-echo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-echo}
      POSTGRES_DB: ${POSTGRES_DB:-echo}
    volumes:
      - echo_pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U echo"]
      interval: 5s
      timeout: 3s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      DATABASE_URL: postgresql://echo:echo@db:5432/echo
      OLLAMA_BASE_URL: http://host.docker.internal:11434
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./apps/api/src:/app/src
    command: uv run fastapi dev src/main.py --host 0.0.0.0 --port 8000

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "${WEB_PORT:-3000}:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - api
    volumes:
      - ./apps/web/src:/app/src

volumes:
  echo_pgdata:
```

- [ ] **Step 5: Create Dockerfile.api**

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY apps/api/pyproject.toml apps/api/uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync

# Copy source
COPY apps/api/src ./src

EXPOSE 8000
CMD ["uv", "run", "fastapi", "dev", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 6: Create Dockerfile.web**

```dockerfile
FROM oven/bun:latest

WORKDIR /app

# Copy dependency files
COPY apps/web/package.json apps/web/bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile 2>/dev/null || bun install

# Copy source
COPY apps/web/ ./

EXPOSE 3000
CMD ["bun", "run", "dev"]
```

- [ ] **Step 7: Create apps directory structure**

```bash
mkdir -p apps/api/src apps/api/tests apps/web/src
```

- [ ] **Step 8: Commit monorepo scaffolding**

```bash
git add .gitignore .mise.toml .env.example docker-compose.yml Dockerfile.api Dockerfile.web apps/
git commit -m "chore: scaffold monorepo with mise, Docker Compose, and Dockerfiles

Three-service Docker Compose (db: pgvector/pg18, api: Python 3.14 FastAPI,
web: Bun/Next.js). mise manages versions and task runner. Environment
template for local development."
```

---

## Task 2: Python Backend — Project Init & Database Connection

**Goal:** Initialize the Python project with uv, configure FastAPI, set up async SQLAlchemy with PostgreSQL.

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/src/__init__.py`
- Create: `apps/api/src/config.py`
- Create: `apps/api/src/main.py`
- Create: `apps/api/src/db/__init__.py`
- Create: `apps/api/src/db/session.py`
- Create: `apps/api/tests/__init__.py`
- Create: `apps/api/tests/conftest.py`
- Create: `apps/api/tests/test_main.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "echo-api"
version = "0.1.0"
description = "E.C.H.O. — Enterprise Cognitive Hub & Orchestration API"
requires-python = ">=3.14"
dependencies = [
    "fastapi~=0.135.3",
    "uvicorn",
    "pydantic~=2.12.5",
    "pydantic-settings>=2.0",
    "sqlalchemy~=2.0.49",
    "asyncpg",
    "alembic~=1.18.4",
    "structlog~=25.5.0",
    "websockets",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "httpx",
    "ruff",
    "pyright",
]

[tool.ruff]
target-version = "py314"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pyright]
pythonVersion = "3.14"
typeCheckingMode = "standard"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Install dependencies**

Run:
```bash
cd apps/api && uv sync
```

Expected: dependencies installed, `uv.lock` created.

- [ ] **Step 3: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://echo:echo@localhost:5432/echo"
    ollama_base_url: str = "http://localhost:11434"
    echo_llm_model: str = "ollama/gemma4:8b"
    echo_embed_model: str = "nomic-embed-text"
    secret_key: str = "change-me-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 4: Create db/__init__.py and db/session.py**

Create `apps/api/src/db/__init__.py` (empty).

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
```

- [ ] **Step 5: Write failing test for health endpoint**

Create `apps/api/tests/__init__.py` (empty), `apps/api/tests/conftest.py`:

```python
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

Create `apps/api/tests/test_main.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
```

- [ ] **Step 6: Run test to verify it fails**

Run:
```bash
cd apps/api && uv run pytest tests/test_main.py -v
```

Expected: FAIL — `src.main` does not exist yet or has no `/health` route.

- [ ] **Step 7: Create main.py with health endpoint**

Create `apps/api/src/__init__.py` (empty).

Create `apps/api/src/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="E.C.H.O. API", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

- [ ] **Step 8: Run test to verify it passes**

Run:
```bash
cd apps/api && uv run pytest tests/test_main.py -v
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
cd apps/api && git add pyproject.toml uv.lock src/ tests/
cd ../.. && git commit -m "feat(api): initialize FastAPI backend with health endpoint

Python 3.14 project with uv, FastAPI ~0.135.3, async SQLAlchemy,
pydantic-settings config. Health endpoint at /health with passing test."
```

---

## Task 3: Database Models & Alembic Migrations

**Goal:** Define all SQLAlchemy models matching the spec's PostgreSQL schema and set up Alembic for migrations.

**Files:**
- Create: `apps/api/src/models/__init__.py`
- Create: `apps/api/src/models/base.py`
- Create: `apps/api/src/models/user.py`
- Create: `apps/api/src/models/agent_run.py`
- Create: `apps/api/src/models/trace_event.py`
- Create: `apps/api/src/models/cost_ledger.py`
- Create: `apps/api/src/models/audit_log.py`
- Create: `apps/api/src/models/rag.py`
- Create: `apps/api/src/db/alembic/alembic.ini`
- Create: `apps/api/src/db/alembic/env.py`
- Create: `apps/api/tests/test_models.py`

- [ ] **Step 1: Create base model**

Create `apps/api/src/models/__init__.py` (empty).

Create `apps/api/src/models/base.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

- [ ] **Step 2: Create User and Session models**

Create `apps/api/src/models/user.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="user")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", onupdate="now()"
    )

    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user")


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="sessions")
```

- [ ] **Step 3: Create AgentRun model**

Create `apps/api/src/models/agent_run.py`:

```python
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class AgentRun(TimestampMixin, Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    task: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[str | None] = mapped_column(String(50))
    complexity: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    result: Mapped[dict | None] = mapped_column(JSONB)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 4: Create TraceEvent model**

Create `apps/api/src/models/trace_event.py`:

```python
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class TraceEvent(TimestampMixin, Base):
    __tablename__ = "trace_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("trace_events.id"))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_name: Mapped[str | None] = mapped_column(String(50))
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    tokens_in: Mapped[int | None] = mapped_column(Integer)
    tokens_out: Mapped[int | None] = mapped_column(Integer)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        Index("idx_trace_events_run", "run_id"),
        Index("idx_trace_events_parent", "parent_id"),
    )
```

- [ ] **Step 5: Create CostLedger model**

Create `apps/api/src/models/cost_ledger.py`:

```python
import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class CostLedger(TimestampMixin, Base):
    __tablename__ = "cost_ledger"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agent_runs.id"))
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)

    __table_args__ = (
        Index("idx_cost_ledger_user", "user_id"),
        Index("idx_cost_ledger_created", "created_at"),
    )
```

- [ ] **Step 6: Create AuditLog model**

Create `apps/api/src/models/audit_log.py`:

```python
import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str | None] = mapped_column(String(255))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    __table_args__ = (
        Index("idx_audit_log_user", "user_id"),
        Index("idx_audit_log_created", "created_at"),
    )
```

- [ ] **Step 7: Create RAG models (chunks, graph nodes, graph edges)**

Create `apps/api/src/models/rag.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class RagChunk(Base):
    __tablename__ = "rag_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # embedding column: vector(768) — created via raw SQL in migration (pgvector type)
    chunk_type: Mapped[str | None] = mapped_column(String(50))
    file_path: Mapped[str | None] = mapped_column(String(500))
    start_line: Mapped[int | None] = mapped_column(Integer)
    end_line: Mapped[int | None] = mapped_column(Integer)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    properties: Mapped[dict | None] = mapped_column(JSONB)
    # embedding column: vector(768) — created via raw SQL in migration

    __table_args__ = (Index("idx_graph_nodes_label", "label"),)


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("graph_nodes.id"), nullable=False
    )
    target_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("graph_nodes.id"), nullable=False
    )
    relation: Mapped[str] = mapped_column(String(100), nullable=False)
    properties: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("idx_graph_edges_source", "source_id"),
        Index("idx_graph_edges_target", "target_id"),
    )
```

- [ ] **Step 8: Write model tests**

Create `apps/api/tests/test_models.py`:

```python
from src.models.user import User, UserSession
from src.models.agent_run import AgentRun
from src.models.trace_event import TraceEvent
from src.models.cost_ledger import CostLedger
from src.models.audit_log import AuditLog
from src.models.rag import RagChunk, GraphNode, GraphEdge


def test_user_table_name():
    assert User.__tablename__ == "users"


def test_user_session_table_name():
    assert UserSession.__tablename__ == "sessions"


def test_agent_run_table_name():
    assert AgentRun.__tablename__ == "agent_runs"


def test_trace_event_table_name():
    assert TraceEvent.__tablename__ == "trace_events"


def test_cost_ledger_table_name():
    assert CostLedger.__tablename__ == "cost_ledger"


def test_audit_log_table_name():
    assert AuditLog.__tablename__ == "audit_log"


def test_rag_chunk_table_name():
    assert RagChunk.__tablename__ == "rag_chunks"


def test_graph_node_table_name():
    assert GraphNode.__tablename__ == "graph_nodes"


def test_graph_edge_table_name():
    assert GraphEdge.__tablename__ == "graph_edges"


def test_user_has_email_column():
    assert "email" in User.__table__.columns.keys()


def test_agent_run_has_status_column():
    assert "status" in AgentRun.__table__.columns.keys()


def test_trace_event_has_indexes():
    index_names = [idx.name for idx in TraceEvent.__table__.indexes]
    assert "idx_trace_events_run" in index_names
    assert "idx_trace_events_parent" in index_names
```

- [ ] **Step 9: Run model tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_models.py -v
```

Expected: All PASS.

- [ ] **Step 10: Initialize Alembic**

Run:
```bash
cd apps/api && uv run alembic init src/db/alembic
```

Then update `apps/api/src/db/alembic/env.py` to use async engine and import all models:

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.models.base import Base
from src.models.user import User, UserSession
from src.models.agent_run import AgentRun
from src.models.trace_event import TraceEvent
from src.models.cost_ledger import CostLedger
from src.models.audit_log import AuditLog
from src.models.rag import RagChunk, GraphNode, GraphEdge

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings.database_url, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

Update `alembic.ini` to point `script_location = src/db/alembic`.

- [ ] **Step 11: Generate initial migration**

Run:
```bash
cd apps/api && uv run alembic revision --autogenerate -m "initial schema"
```

Expected: migration file created in `src/db/alembic/versions/`.

Note: pgvector `vector(768)` columns and IVFFlat indexes must be added manually to the migration since SQLAlchemy doesn't natively support the `vector` type. Add raw SQL ops:

```python
# At top of migration upgrade():
op.execute("CREATE EXTENSION IF NOT EXISTS vector")

# After rag_chunks table creation:
op.execute("ALTER TABLE rag_chunks ADD COLUMN embedding vector(768) NOT NULL")
op.execute("""
    CREATE INDEX idx_rag_chunks_embedding ON rag_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
""")

# After graph_nodes table creation:
op.execute("ALTER TABLE graph_nodes ADD COLUMN embedding vector(768)")
```

- [ ] **Step 12: Commit**

```bash
git add apps/api/src/models/ apps/api/src/db/ apps/api/tests/test_models.py
git commit -m "feat(api): add database models and Alembic migrations

SQLAlchemy models for users, sessions, agent_runs, trace_events,
cost_ledger, audit_log, rag_chunks, graph_nodes, graph_edges.
Async Alembic config with pgvector extension support."
```

---

## Task 4: Pydantic Schemas & API Routes (Agents, Traces, RAG)

**Goal:** Define Pydantic request/response schemas and FastAPI route stubs for the three main API domains.

**Files:**
- Create: `apps/api/src/schemas/__init__.py`
- Create: `apps/api/src/schemas/agent.py`
- Create: `apps/api/src/schemas/trace.py`
- Create: `apps/api/src/schemas/rag.py`
- Create: `apps/api/src/api/__init__.py`
- Create: `apps/api/src/api/agents.py`
- Create: `apps/api/src/api/traces.py`
- Create: `apps/api/src/api/rag.py`
- Modify: `apps/api/src/main.py`
- Create: `apps/api/tests/test_api/test_agents_api.py`
- Create: `apps/api/tests/test_api/test_traces_api.py`
- Create: `apps/api/tests/test_api/test_rag_api.py`

- [ ] **Step 1: Create Pydantic schemas for agents**

Create `apps/api/src/schemas/__init__.py` (empty).

Create `apps/api/src/schemas/agent.py`:

```python
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AgentRunCreate(BaseModel):
    task: str
    task_type: str | None = None


class AgentRunResponse(BaseModel):
    id: uuid.UUID
    task: str
    task_type: str | None
    complexity: str | None
    status: str
    total_tokens: int
    total_cost: Decimal
    duration_ms: int | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class AgentRunList(BaseModel):
    runs: list[AgentRunResponse]
    total: int
```

- [ ] **Step 2: Create Pydantic schemas for traces**

Create `apps/api/src/schemas/trace.py`:

```python
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TraceEventResponse(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    parent_id: uuid.UUID | None
    event_type: str
    agent_name: str | None
    data: dict
    tokens_in: int | None
    tokens_out: int | None
    cost: Decimal | None
    duration_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TraceTree(BaseModel):
    events: list[TraceEventResponse]
    run_id: uuid.UUID
```

- [ ] **Step 3: Create Pydantic schemas for RAG**

Create `apps/api/src/schemas/rag.py`:

```python
from pydantic import BaseModel


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    include_graph: bool = True


class RAGChunkResult(BaseModel):
    content: str
    chunk_type: str | None
    file_path: str | None
    start_line: int | None
    end_line: int | None
    score: float


class RAGQueryResponse(BaseModel):
    results: list[RAGChunkResult]
    query: str
```

- [ ] **Step 4: Write failing tests for API routes**

Create `apps/api/tests/test_api/__init__.py` (empty).

Create `apps/api/tests/test_api/test_agents_api.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_create_agent_run(client):
    response = await client.post("/api/agents/runs", json={"task": "Fix the login bug"})
    assert response.status_code == 201
    data = response.json()
    assert data["task"] == "Fix the login bug"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_agent_runs(client):
    response = await client.get("/api/agents/runs")
    assert response.status_code == 200
    data = response.json()
    assert "runs" in data
    assert "total" in data
```

Create `apps/api/tests/test_api/test_traces_api.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_get_trace_returns_404_for_unknown_run(client):
    response = await client.get("/api/traces/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
```

Create `apps/api/tests/test_api/test_rag_api.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_rag_query_endpoint_exists(client):
    response = await client.post("/api/rag/query", json={"query": "auth flow"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query" in data
```

- [ ] **Step 5: Run tests to verify they fail**

Run:
```bash
cd apps/api && uv run pytest tests/test_api/ -v
```

Expected: FAIL — routes don't exist yet.

- [ ] **Step 6: Create API route modules**

Create `apps/api/src/api/__init__.py` (empty).

Create `apps/api/src/api/agents.py`:

```python
import uuid

from fastapi import APIRouter

from src.schemas.agent import AgentRunCreate, AgentRunList, AgentRunResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/runs", status_code=201, response_model=AgentRunResponse)
async def create_run(body: AgentRunCreate):
    # Stub: returns a mock response until DB integration
    return AgentRunResponse(
        id=uuid.uuid4(),
        task=body.task,
        task_type=body.task_type,
        complexity=None,
        status="pending",
        total_tokens=0,
        total_cost=0,
        duration_ms=None,
        created_at="2026-01-01T00:00:00Z",
        completed_at=None,
    )


@router.get("/runs", response_model=AgentRunList)
async def list_runs():
    return AgentRunList(runs=[], total=0)
```

Create `apps/api/src/api/traces.py`:

```python
import uuid

from fastapi import APIRouter, HTTPException

from src.schemas.trace import TraceTree

router = APIRouter(prefix="/api/traces", tags=["traces"])


@router.get("/{run_id}", response_model=TraceTree)
async def get_trace(run_id: uuid.UUID):
    # Stub: returns 404 until DB integration
    raise HTTPException(status_code=404, detail="Run not found")
```

Create `apps/api/src/api/rag.py`:

```python
from fastapi import APIRouter

from src.schemas.rag import RAGQueryRequest, RAGQueryResponse

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(body: RAGQueryRequest):
    # Stub: returns empty results until RAG pipeline integration
    return RAGQueryResponse(results=[], query=body.query)
```

- [ ] **Step 7: Register routers in main.py**

Update `apps/api/src/main.py`:

```python
from fastapi import FastAPI

from src.api.agents import router as agents_router
from src.api.traces import router as traces_router
from src.api.rag import router as rag_router

app = FastAPI(title="E.C.H.O. API", version="0.1.0")

app.include_router(agents_router)
app.include_router(traces_router)
app.include_router(rag_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

- [ ] **Step 8: Run tests to verify they pass**

Run:
```bash
cd apps/api && uv run pytest tests/ -v
```

Expected: All PASS.

- [ ] **Step 9: Commit**

```bash
git add apps/api/src/schemas/ apps/api/src/api/ apps/api/src/main.py apps/api/tests/test_api/
git commit -m "feat(api): add Pydantic schemas and API route stubs

Schemas for agent runs, trace events, and RAG queries. Route stubs
at /api/agents/runs, /api/traces/{run_id}, /api/rag/query.
All endpoints return mock/empty data until backend integration."
```

---

## Task 5: AI Gateway — LiteLLM Router, PII Scrubber, Cost Tracker

**Goal:** Implement the AI gateway layer with LiteLLM semantic routing, PII/secret scrubbing, and per-request cost tracking.

**Files:**
- Create: `apps/api/src/gateway/__init__.py`
- Create: `apps/api/src/gateway/router.py`
- Create: `apps/api/src/gateway/scrubber.py`
- Create: `apps/api/src/gateway/tracker.py`
- Create: `apps/api/src/gateway/rate_limiter.py`
- Create: `apps/api/tests/test_gateway/__init__.py`
- Create: `apps/api/tests/test_gateway/test_router.py`
- Create: `apps/api/tests/test_gateway/test_scrubber.py`
- Create: `apps/api/tests/test_gateway/test_tracker.py`
- Create: `apps/api/tests/test_gateway/test_rate_limiter.py`
- Modify: `apps/api/pyproject.toml` (add litellm, presidio-analyzer)

- [ ] **Step 1: Add gateway dependencies to pyproject.toml**

Add to the `dependencies` list in `apps/api/pyproject.toml`:

```
"litellm>=1.83.0",
"presidio-analyzer",
```

Run:
```bash
cd apps/api && uv sync
```

- [ ] **Step 2: Write failing tests for PII scrubber**

Create `apps/api/tests/test_gateway/__init__.py` (empty).

Create `apps/api/tests/test_gateway/test_scrubber.py`:

```python
from src.gateway.scrubber import scrub_pii, scrub_secrets


def test_scrub_email():
    text = "Contact john@example.com for details"
    result = scrub_pii(text)
    assert "john@example.com" not in result
    assert "<EMAIL>" in result


def test_scrub_phone():
    text = "Call me at 555-123-4567"
    result = scrub_pii(text)
    assert "555-123-4567" not in result


def test_scrub_aws_key():
    text = "key is AKIAIOSFODNN7EXAMPLE"
    result = scrub_secrets(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in result
    assert "<SECRET>" in result


def test_scrub_jwt():
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    result = scrub_secrets(f"token: {jwt}")
    assert jwt not in result
    assert "<SECRET>" in result


def test_no_false_positives():
    text = "This is a normal sentence about coding."
    assert scrub_pii(text) == text
    assert scrub_secrets(text) == text
```

- [ ] **Step 3: Run tests to verify they fail**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/test_scrubber.py -v
```

Expected: FAIL — module doesn't exist.

- [ ] **Step 4: Implement PII scrubber**

Create `apps/api/src/gateway/__init__.py` (empty).

Create `apps/api/src/gateway/scrubber.py`:

```python
import re

from presidio_analyzer import AnalyzerEngine

_analyzer = AnalyzerEngine()

# Regex patterns for secrets
_SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                          # AWS access key
    re.compile(r"(?:aws.{0,20})?['\"][0-9a-zA-Z/+]{40}['\"]"),  # AWS secret key
    re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),  # JWT
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),   # Private keys
    re.compile(r"ghp_[0-9a-zA-Z]{36}"),                       # GitHub PAT
    re.compile(r"sk-[0-9a-zA-Z]{48}"),                        # OpenAI API key
    re.compile(r"sk-ant-[0-9a-zA-Z-]{90,}"),                  # Anthropic API key
]


def scrub_pii(text: str) -> str:
    """Replace PII (emails, phones, SSNs) with placeholders using Presidio."""
    results = _analyzer.analyze(
        text=text,
        entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN"],
        language="en",
    )
    # Sort by start position descending to replace from end
    for result in sorted(results, key=lambda r: r.start, reverse=True):
        entity_tag = result.entity_type.replace("_ADDRESS", "").replace("US_", "")
        text = text[:result.start] + f"<{entity_tag}>" + text[result.end:]
    return text


def scrub_secrets(text: str) -> str:
    """Replace secret patterns (AWS keys, JWTs, private keys) with <SECRET>."""
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("<SECRET>", text)
    return text


def scrub_all(text: str) -> str:
    """Run both PII and secret scrubbing."""
    return scrub_secrets(scrub_pii(text))
```

- [ ] **Step 5: Run scrubber tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/test_scrubber.py -v
```

Expected: All PASS.

- [ ] **Step 6: Write failing tests for cost tracker**

Create `apps/api/tests/test_gateway/test_tracker.py`:

```python
from src.gateway.tracker import CostTracker, LLMUsage


def test_track_usage():
    tracker = CostTracker()
    usage = LLMUsage(
        model="ollama/gemma4:8b",
        tokens_in=100,
        tokens_out=50,
        cost=0.0,
        user_id="test-user",
        run_id="test-run",
    )
    tracker.record(usage)
    assert len(tracker.entries) == 1
    assert tracker.entries[0].model == "ollama/gemma4:8b"


def test_total_cost():
    tracker = CostTracker()
    tracker.record(LLMUsage(model="m1", tokens_in=10, tokens_out=5, cost=0.001))
    tracker.record(LLMUsage(model="m2", tokens_in=20, tokens_out=10, cost=0.002))
    assert tracker.total_cost == 0.003


def test_total_tokens():
    tracker = CostTracker()
    tracker.record(LLMUsage(model="m1", tokens_in=100, tokens_out=50, cost=0.0))
    assert tracker.total_tokens == 150
```

- [ ] **Step 7: Run to verify failure**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/test_tracker.py -v
```

Expected: FAIL.

- [ ] **Step 8: Implement cost tracker**

Create `apps/api/src/gateway/tracker.py`:

```python
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class LLMUsage:
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    user_id: str | None = None
    run_id: str | None = None


class CostTracker:
    """In-memory cost tracker. Persists to DB via flush() in production."""

    def __init__(self):
        self.entries: list[LLMUsage] = []

    def record(self, usage: LLMUsage) -> None:
        self.entries.append(usage)

    @property
    def total_cost(self) -> float:
        return sum(e.cost for e in self.entries)

    @property
    def total_tokens(self) -> int:
        return sum(e.tokens_in + e.tokens_out for e in self.entries)
```

- [ ] **Step 9: Run tracker tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/test_tracker.py -v
```

Expected: All PASS.

- [ ] **Step 10: Write failing test for LiteLLM router**

Create `apps/api/tests/test_gateway/test_router.py`:

```python
from src.agents.state import TaskComplexity
from src.gateway.router import classify_complexity


def test_simple_task():
    assert classify_complexity("fix typo in readme") == TaskComplexity.SIMPLE


def test_moderate_task():
    assert classify_complexity("add unit tests for the auth module") == TaskComplexity.MODERATE


def test_complex_task():
    assert classify_complexity("refactor the entire authentication architecture") == TaskComplexity.COMPLEX


def test_security_keyword_is_complex():
    assert classify_complexity("scan for security vulnerabilities") == TaskComplexity.COMPLEX
```

- [ ] **Step 11: Run to verify failure**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/test_router.py -v
```

Expected: FAIL.

- [ ] **Step 12: Implement LiteLLM router with complexity classifier**

Create `apps/api/src/gateway/router.py`:

```python
from litellm import Router

from src.agents.state import TaskComplexity
from src.config import settings

COMPLEX_KEYWORDS = {"refactor", "security", "architecture", "migrate", "redesign", "vulnerability"}
MODERATE_KEYWORDS = {"test", "review", "update", "add", "implement", "feature"}


def classify_complexity(task: str) -> TaskComplexity:
    """Classify task complexity using keyword heuristics."""
    words = set(task.lower().split())
    if words & COMPLEX_KEYWORDS:
        return TaskComplexity.COMPLEX
    if words & MODERATE_KEYWORDS:
        return TaskComplexity.MODERATE
    return TaskComplexity.SIMPLE


def create_llm_router() -> Router:
    """Create LiteLLM router configured for local Ollama."""
    return Router(
        model_list=[
            {
                "model_name": "echo-default",
                "litellm_params": {
                    "model": settings.echo_llm_model,
                    "api_base": settings.ollama_base_url,
                },
            },
        ],
        routing_strategy="simple-shuffle",
    )
```

- [ ] **Step 13: Run all gateway tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/ -v
```

Expected: All PASS.

- [ ] **Step 14: Write failing test for rate limiter**

Create `apps/api/tests/test_gateway/test_rate_limiter.py`:

```python
import pytest

from src.gateway.rate_limiter import RateLimiter


def test_allows_under_limit():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    assert limiter.check("user-1", tokens=100) is True


def test_blocks_over_limit():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    limiter.record("user-1", tokens=900)
    assert limiter.check("user-1", tokens=200) is False


def test_separate_users_have_separate_limits():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    limiter.record("user-1", tokens=900)
    assert limiter.check("user-2", tokens=500) is True


def test_remaining_tokens():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    limiter.record("user-1", tokens=300)
    assert limiter.remaining("user-1") == 700
```

- [ ] **Step 15: Run to verify failure**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/test_rate_limiter.py -v
```

Expected: FAIL.

- [ ] **Step 16: Implement rate limiter**

Create `apps/api/src/gateway/rate_limiter.py`:

```python
import time
from collections import defaultdict


class RateLimiter:
    """Per-user token/minute rate limiter (in-memory, single-process)."""

    def __init__(self, max_tokens_per_minute: int = 100_000):
        self.max_tokens_per_minute = max_tokens_per_minute
        self._usage: dict[str, list[tuple[float, int]]] = defaultdict(list)

    def _prune(self, user_id: str) -> None:
        """Remove entries older than 60 seconds."""
        cutoff = time.monotonic() - 60.0
        self._usage[user_id] = [
            (ts, tokens) for ts, tokens in self._usage[user_id] if ts > cutoff
        ]

    def _current_usage(self, user_id: str) -> int:
        self._prune(user_id)
        return sum(tokens for _, tokens in self._usage[user_id])

    def check(self, user_id: str, tokens: int) -> bool:
        """Return True if the request is within rate limits."""
        return self._current_usage(user_id) + tokens <= self.max_tokens_per_minute

    def record(self, user_id: str, tokens: int) -> None:
        """Record token usage for a user."""
        self._usage[user_id].append((time.monotonic(), tokens))

    def remaining(self, user_id: str) -> int:
        """Return remaining tokens in the current window."""
        return max(0, self.max_tokens_per_minute - self._current_usage(user_id))
```

- [ ] **Step 17: Run rate limiter tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/test_rate_limiter.py -v
```

Expected: All PASS.

- [ ] **Step 18: Run all gateway tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_gateway/ -v
```

Expected: All PASS.

- [ ] **Step 19: Commit**

```bash
git add apps/api/src/gateway/ apps/api/tests/test_gateway/ apps/api/pyproject.toml apps/api/uv.lock
git commit -m "feat(api): add AI gateway — LiteLLM router, PII scrubber, cost tracker, rate limiter

Complexity classifier routes tasks to LLM tiers. Presidio-based PII
scrubbing for emails, phones, SSNs. Regex secret detection for AWS keys,
JWTs, private keys. In-memory cost tracker and per-user token/minute
rate limiter."
```

---

## Task 6: LangGraph Agent System — State, Graph, Supervisor

**Goal:** Implement the multi-agent orchestration core with LangGraph: shared state, graph assembly, and the Supervisor agent.

**Files:**
- Create: `apps/api/src/agents/__init__.py`
- Create: `apps/api/src/agents/state.py`
- Create: `apps/api/src/agents/graph.py`
- Create: `apps/api/src/agents/supervisor.py`
- Create: `apps/api/src/agents/coder.py`
- Create: `apps/api/src/agents/reviewer.py`
- Create: `apps/api/src/agents/qa.py`
- Create: `apps/api/src/agents/security.py`
- Create: `apps/api/src/agents/docs_agent.py`
- Create: `apps/api/src/agents/architect.py`
- Modify: `apps/api/pyproject.toml` (add langgraph)
- Create: `apps/api/tests/test_agents/__init__.py`
- Create: `apps/api/tests/test_agents/test_state.py`
- Create: `apps/api/tests/test_agents/test_graph.py`
- Create: `apps/api/tests/test_agents/test_supervisor.py`

- [ ] **Step 1: Add langgraph dependency**

Add to `apps/api/pyproject.toml` dependencies:

```
"langgraph~=1.1.0",
```

Run:
```bash
cd apps/api && uv sync
```

- [ ] **Step 2: Write failing test for agent state**

Create `apps/api/tests/test_agents/__init__.py` (empty).

Create `apps/api/tests/test_agents/test_state.py`:

```python
from src.agents.state import EchoState, TaskType, TaskComplexity


def test_echo_state_has_required_keys():
    state: EchoState = {
        "task": "fix bug",
        "task_type": TaskType.BUGFIX,
        "complexity": TaskComplexity.SIMPLE,
        "messages": [],
        "artifacts": [],
        "reviews": [],
        "trace": [],
        "current_agent": "supervisor",
        "iteration": 0,
        "max_iterations": 10,
    }
    assert state["task"] == "fix bug"
    assert state["current_agent"] == "supervisor"


def test_task_type_values():
    assert TaskType.BUGFIX.value == "bugfix"
    assert TaskType.FEATURE.value == "feature"
    assert TaskType.REVIEW.value == "review"
    assert TaskType.TEST.value == "test"
```

- [ ] **Step 3: Run test to verify failure**

Run:
```bash
cd apps/api && uv run pytest tests/test_agents/test_state.py -v
```

Expected: FAIL.

- [ ] **Step 4: Implement agent state**

Create `apps/api/src/agents/__init__.py` (empty).

Create `apps/api/src/agents/state.py`:

```python
from enum import Enum
from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class TaskType(Enum):
    BUGFIX = "bugfix"
    FEATURE = "feature"
    REVIEW = "review"
    TEST = "test"
    SECURITY = "security"
    DOCS = "docs"
    ARCHITECTURE = "architecture"


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class CodeArtifact(TypedDict):
    file_path: str
    content: str
    action: str  # "create" | "modify" | "delete"


class ReviewFinding(TypedDict):
    severity: str  # "info" | "warning" | "critical"
    message: str
    file_path: str | None
    line: int | None


class TraceEntry(TypedDict):
    """In-memory trace entry for agent state. Not to be confused with the
    TraceEvent SQLAlchemy model in models/trace_event.py."""
    agent: str
    event_type: str
    data: dict


class EchoState(TypedDict):
    task: str
    task_type: TaskType
    complexity: TaskComplexity
    messages: Annotated[list, add_messages]
    artifacts: list[CodeArtifact]
    reviews: list[ReviewFinding]
    trace: list[TraceEntry]
    current_agent: str
    iteration: int
    max_iterations: int
```

- [ ] **Step 5: Run state tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_agents/test_state.py -v
```

Expected: All PASS.

- [ ] **Step 6: Write failing test for supervisor**

Create `apps/api/tests/test_agents/test_supervisor.py`:

```python
from src.agents.supervisor import classify_task
from src.agents.state import TaskType


def test_classify_bugfix():
    assert classify_task("fix the login bug in auth handler") == TaskType.BUGFIX


def test_classify_feature():
    assert classify_task("add a new dashboard page for metrics") == TaskType.FEATURE


def test_classify_review():
    assert classify_task("review the pull request for auth changes") == TaskType.REVIEW


def test_classify_security():
    assert classify_task("scan codebase for security vulnerabilities") == TaskType.SECURITY


def test_classify_test():
    assert classify_task("write tests for the user service") == TaskType.TEST
```

- [ ] **Step 7: Run to verify failure**

Run:
```bash
cd apps/api && uv run pytest tests/test_agents/test_supervisor.py -v
```

Expected: FAIL.

- [ ] **Step 8: Implement supervisor agent**

Create `apps/api/src/agents/supervisor.py`:

```python
from src.agents.state import EchoState, TaskType

_TASK_KEYWORDS: dict[TaskType, set[str]] = {
    TaskType.BUGFIX: {"fix", "bug", "error", "crash", "broken", "issue", "patch"},
    TaskType.FEATURE: {"add", "new", "feature", "implement", "create", "build"},
    TaskType.REVIEW: {"review", "pr", "pull request", "check", "audit"},
    TaskType.TEST: {"test", "coverage", "spec", "unittest", "pytest"},
    TaskType.SECURITY: {"security", "vulnerability", "owasp", "secret", "cve", "scan"},
    TaskType.DOCS: {"doc", "documentation", "readme", "changelog", "comment"},
    TaskType.ARCHITECTURE: {"architecture", "design", "refactor", "migrate", "dependency"},
}

_ROUTE_MAP: dict[TaskType, str] = {
    TaskType.BUGFIX: "coder",
    TaskType.FEATURE: "coder",
    TaskType.REVIEW: "reviewer",
    TaskType.TEST: "qa",
    TaskType.SECURITY: "security",
    TaskType.DOCS: "docs",
    TaskType.ARCHITECTURE: "architect",
}


def classify_task(task: str) -> TaskType:
    """Classify a task string into a TaskType using keyword matching."""
    words = set(task.lower().split())
    best_type = TaskType.FEATURE
    best_score = 0
    for task_type, keywords in _TASK_KEYWORDS.items():
        score = len(words & keywords)
        if score > best_score:
            best_score = score
            best_type = task_type
    return best_type


def route_task(task_type: TaskType) -> str:
    """Return the agent name to route to for a given task type."""
    return _ROUTE_MAP[task_type]


def supervisor_node(state: EchoState) -> dict:
    """LangGraph node: classify task and route to appropriate agent."""
    task_type = classify_task(state["task"])
    next_agent = route_task(task_type)
    return {
        "task_type": task_type,
        "current_agent": next_agent,
        "trace": [{"agent": "supervisor", "event_type": "classify", "data": {
            "task_type": task_type.value, "routed_to": next_agent,
        }}],
    }
```

- [ ] **Step 9: Run supervisor tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_agents/test_supervisor.py -v
```

Expected: All PASS.

- [ ] **Step 10: Create stub agent nodes**

Create `apps/api/src/agents/coder.py`:

```python
from src.agents.state import EchoState


def coder_node(state: EchoState) -> dict:
    """LangGraph node: code generation agent (stub)."""
    return {
        "current_agent": "coder",
        "trace": [{"agent": "coder", "event_type": "agent_start", "data": {
            "task": state["task"],
        }}],
    }
```

Create `apps/api/src/agents/reviewer.py`:

```python
from src.agents.state import EchoState


def reviewer_node(state: EchoState) -> dict:
    """LangGraph node: code review agent (stub)."""
    return {
        "current_agent": "reviewer",
        "trace": [{"agent": "reviewer", "event_type": "agent_start", "data": {
            "task": state["task"],
        }}],
    }
```

Create `apps/api/src/agents/qa.py`:

```python
from src.agents.state import EchoState


def qa_node(state: EchoState) -> dict:
    """LangGraph node: QA/testing agent (stub)."""
    return {
        "current_agent": "qa",
        "trace": [{"agent": "qa", "event_type": "agent_start", "data": {
            "task": state["task"],
        }}],
    }
```

Create `apps/api/src/agents/security.py`:

```python
from src.agents.state import EchoState


def security_node(state: EchoState) -> dict:
    """LangGraph node: security scanning agent (stub)."""
    return {
        "current_agent": "security",
        "trace": [{"agent": "security", "event_type": "agent_start", "data": {
            "task": state["task"],
        }}],
    }
```

Create `apps/api/src/agents/docs_agent.py`:

```python
from src.agents.state import EchoState


def docs_node(state: EchoState) -> dict:
    """LangGraph node: documentation agent (stub)."""
    return {
        "current_agent": "docs",
        "trace": [{"agent": "docs", "event_type": "agent_start", "data": {
            "task": state["task"],
        }}],
    }
```

Create `apps/api/src/agents/architect.py`:

```python
from src.agents.state import EchoState


def architect_node(state: EchoState) -> dict:
    """LangGraph node: architecture analysis agent (stub)."""
    return {
        "current_agent": "architect",
        "trace": [{"agent": "architect", "event_type": "agent_start", "data": {
            "task": state["task"],
        }}],
    }
```

- [ ] **Step 11: Write failing test for graph assembly**

Create `apps/api/tests/test_agents/test_graph.py`:

```python
from src.agents.graph import build_graph


def test_build_graph_returns_compiled_graph():
    graph = build_graph()
    assert graph is not None


def test_graph_has_supervisor_entry():
    graph = build_graph()
    # LangGraph compiled graphs have a .nodes dict
    assert "supervisor" in graph.nodes


def test_graph_has_all_agent_nodes():
    graph = build_graph()
    for agent in ["supervisor", "coder", "reviewer", "qa", "security", "docs", "architect"]:
        assert agent in graph.nodes
```

- [ ] **Step 12: Run to verify failure**

Run:
```bash
cd apps/api && uv run pytest tests/test_agents/test_graph.py -v
```

Expected: FAIL.

- [ ] **Step 13: Implement graph assembly**

Create `apps/api/src/agents/graph.py`:

```python
from langgraph.graph import END, StateGraph

from src.agents.architect import architect_node
from src.agents.coder import coder_node
from src.agents.docs_agent import docs_node
from src.agents.qa import qa_node
from src.agents.reviewer import reviewer_node
from src.agents.security import security_node
from src.agents.state import EchoState
from src.agents.supervisor import supervisor_node


def _route_from_supervisor(state: EchoState) -> str:
    """Conditional edge: route from supervisor to the chosen agent."""
    return state["current_agent"]


def build_graph():
    """Build and compile the E.C.H.O. multi-agent LangGraph.

    Flow: Supervisor -> Coder -> [HITL] -> Reviewer -> QA -> Security -> [HITL] -> Docs -> END
    For non-code tasks (review, security, docs, architect), Supervisor routes directly
    to the relevant agent which then goes to END.
    """
    builder = StateGraph(EchoState)

    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("coder", coder_node)
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("qa", qa_node)
    builder.add_node("security", security_node)
    builder.add_node("docs", docs_node)
    builder.add_node("architect", architect_node)

    # Entry point
    builder.set_entry_point("supervisor")

    # Supervisor routes to the first agent based on task type
    builder.add_conditional_edges("supervisor", _route_from_supervisor, {
        "coder": "coder",
        "reviewer": "reviewer",
        "qa": "qa",
        "security": "security",
        "docs": "docs",
        "architect": "architect",
    })

    # Full pipeline chain for code tasks:
    # Coder -> [HITL: review code?] -> Reviewer -> QA -> Security -> [HITL: accept?] -> Docs -> END
    builder.add_edge("coder", "reviewer")       # After coder, reviewer checks
    builder.add_edge("reviewer", "qa")           # After review, QA tests
    builder.add_edge("qa", "security")           # After QA, security scan
    builder.add_edge("security", "docs")         # After security, generate docs
    builder.add_edge("docs", END)                # Pipeline complete

    # Standalone tasks (non-code) go directly to END
    builder.add_edge("architect", END)

    # Compile with HITL interrupt points (LangGraph interrupt_after)
    # Post-coder gate: user reviews generated code before reviewer
    # Post-security gate: user reviews all findings before docs
    return builder.compile(
        interrupt_after=["coder", "security"],
    )
```

- [ ] **Step 14: Run all agent tests**

Run:
```bash
cd apps/api && uv run pytest tests/test_agents/ -v
```

Expected: All PASS.

- [ ] **Step 15: Commit**

```bash
git add apps/api/src/agents/ apps/api/tests/test_agents/ apps/api/pyproject.toml apps/api/uv.lock
git commit -m "feat(api): add LangGraph multi-agent system

EchoState with task classification, supervisor routing, and stub agent
nodes (coder, reviewer, qa, security, docs, architect). StateGraph
compiled with conditional routing from supervisor to agents."
```

---

## Task 7: WebSocket Endpoint for Agent Traces

**Goal:** Implement the WebSocket endpoint that streams trace events from agent execution to the frontend.

**Files:**
- Create: `apps/api/src/api/ws.py`
- Modify: `apps/api/src/main.py` (register WS route)

- [ ] **Step 1: Implement WebSocket endpoint**

Create `apps/api/src/api/ws.py`:

```python
import asyncio
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

router = APIRouter()


class TraceConnection:
    """Manages a WebSocket connection for streaming agent trace events."""

    def __init__(self, websocket: WebSocket, run_id: str):
        self.websocket = websocket
        self.run_id = run_id
        self.event_queue: asyncio.Queue = asyncio.Queue()

    async def send_event(self, event: dict) -> None:
        if self.websocket.client_state == WebSocketState.CONNECTED:
            await self.websocket.send_json(event)

    async def receive_hitl(self) -> dict:
        data = await self.websocket.receive_json()
        return data


# Active connections keyed by run_id
_connections: dict[str, TraceConnection] = {}


def get_connection(run_id: str) -> TraceConnection | None:
    return _connections.get(run_id)


@router.websocket("/ws/{run_id}")
async def agent_trace_ws(websocket: WebSocket, run_id: str):
    await websocket.accept()
    conn = TraceConnection(websocket, run_id)
    _connections[run_id] = conn

    try:
        while True:
            # Wait for events from the queue or client messages
            try:
                event = conn.event_queue.get_nowait()
                await conn.send_event(event)
            except asyncio.QueueEmpty:
                pass

            # Check for incoming HITL responses (non-blocking)
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                if data.get("type") == "hitl_response":
                    await conn.event_queue.put(data)
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        _connections.pop(run_id, None)
```

- [ ] **Step 2: Register WS router in main.py**

Add to `apps/api/src/main.py`:

```python
from src.api.ws import router as ws_router

app.include_router(ws_router)
```

- [ ] **Step 3: Commit**

```bash
git add apps/api/src/api/ws.py apps/api/src/main.py
git commit -m "feat(api): add WebSocket endpoint for agent trace streaming

WebSocket at /ws/{run_id} for bidirectional trace event streaming.
TraceConnection manages per-run event queue and HITL responses."
```

---

## Task 8: RAG Pipeline — LlamaIndex Graph RAG

**Goal:** Implement the indexing and retrieval pipeline using LlamaIndex PropertyGraphIndex with pgvector.

**Files:**
- Create: `apps/api/src/rag/__init__.py`
- Create: `apps/api/src/rag/graph_schema.py`
- Create: `apps/api/src/rag/chunkers.py`
- Create: `apps/api/src/rag/indexer.py`
- Create: `apps/api/src/rag/retriever.py`
- Modify: `apps/api/pyproject.toml` (add llama-index, tree-sitter)

- [ ] **Step 1: Add RAG dependencies**

Add to `apps/api/pyproject.toml` dependencies:

```
"llama-index-core~=0.14",
"llama-index-graph-stores-postgres",
"llama-index-vector-stores-postgres",
"llama-index-embeddings-ollama",
"tree-sitter~=0.25.2",
"tree-sitter-python~=0.25.0",
```

Run:
```bash
cd apps/api && uv sync
```

- [ ] **Step 2: Create graph schema definitions**

Create `apps/api/src/rag/__init__.py` (empty).

Create `apps/api/src/rag/graph_schema.py`:

```python
from enum import Enum


class EntityType(Enum):
    MODULE = "Module"
    CLASS = "Class"
    FUNCTION = "Function"
    FILE = "File"
    CONFIG = "Config"
    TEST = "Test"
    CONCEPT = "Concept"


class RelationType(Enum):
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    INHERITS = "INHERITS"
    DEFINES = "DEFINES"
    TESTS = "TESTS"
    DEPENDS_ON = "DEPENDS_ON"
    DOCUMENTS = "DOCUMENTS"
```

- [ ] **Step 3: Implement AST-aware chunker**

Create `apps/api/src/rag/chunkers.py`:

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser


PY_LANGUAGE = Language(tspython.language())


def chunk_python_file(source: str, file_path: str) -> list[dict]:
    """Parse Python source and return chunks per function/class."""
    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(source.encode())
    chunks = []

    for node in tree.root_node.children:
        if node.type in ("function_definition", "class_definition"):
            chunk_text = source[node.start_byte:node.end_byte]
            chunks.append({
                "content": chunk_text,
                "chunk_type": "function" if node.type == "function_definition" else "class",
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
            })

    # If no functions/classes found, chunk the whole file
    if not chunks:
        chunks.append({
            "content": source,
            "chunk_type": "module",
            "file_path": file_path,
            "start_line": 1,
            "end_line": source.count("\n") + 1,
        })

    return chunks


def chunk_markdown(content: str, file_path: str) -> list[dict]:
    """Split markdown by headings into semantic chunks."""
    chunks = []
    current_chunk = []
    current_start = 1

    for i, line in enumerate(content.split("\n"), 1):
        if line.startswith("#") and current_chunk:
            chunks.append({
                "content": "\n".join(current_chunk),
                "chunk_type": "doc_section",
                "file_path": file_path,
                "start_line": current_start,
                "end_line": i - 1,
            })
            current_chunk = [line]
            current_start = i
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append({
            "content": "\n".join(current_chunk),
            "chunk_type": "doc_section",
            "file_path": file_path,
            "start_line": current_start,
            "end_line": current_start + len(current_chunk) - 1,
        })

    return chunks
```

- [ ] **Step 4: Implement indexer pipeline**

Create `apps/api/src/rag/indexer.py`:

```python
import os
from pathlib import Path

from llama_index.embeddings.ollama import OllamaEmbedding

from src.config import settings
from src.rag.chunkers import chunk_markdown, chunk_python_file


def get_embed_model() -> OllamaEmbedding:
    return OllamaEmbedding(
        model_name=settings.echo_embed_model,
        base_url=settings.ollama_base_url,
    )


def scan_files(root: str, extensions: set[str] = {".py", ".ts", ".tsx", ".md"}) -> list[Path]:
    """Recursively find files with matching extensions, skipping hidden dirs and node_modules."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "node_modules" and d != "__pycache__"]
        for f in filenames:
            if Path(f).suffix in extensions:
                files.append(Path(dirpath) / f)
    return files


def chunk_file(file_path: Path) -> list[dict]:
    """Chunk a file based on its extension."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    if not content.strip():
        return []

    suffix = file_path.suffix
    if suffix == ".py":
        return chunk_python_file(content, str(file_path))
    elif suffix == ".md":
        return chunk_markdown(content, str(file_path))
    else:
        # Whole-file chunk for other types
        return [{
            "content": content,
            "chunk_type": "file",
            "file_path": str(file_path),
            "start_line": 1,
            "end_line": content.count("\n") + 1,
        }]


def run_indexing(root: str = ".") -> list[dict]:
    """Run the full indexing pipeline on the given root directory."""
    files = scan_files(root)
    all_chunks = []
    for f in files:
        all_chunks.extend(chunk_file(f))
    return all_chunks


if __name__ == "__main__":
    chunks = run_indexing(".")
    print(f"Indexed {len(chunks)} chunks from codebase")
    for chunk in chunks[:5]:
        print(f"  - {chunk['file_path']}:{chunk['start_line']}-{chunk['end_line']} ({chunk['chunk_type']})")
```

- [ ] **Step 5: Implement retriever**

Create `apps/api/src/rag/retriever.py`:

```python
from src.rag.indexer import get_embed_model


class RAGRetriever:
    """Retrieves relevant chunks using vector similarity.

    Note: Full PropertyGraphIndex integration requires a running PostgreSQL
    with pgvector. This implementation provides the interface; the LlamaIndex
    PropertyGraphIndex integration wires in during Task 3 DB migration.
    """

    def __init__(self):
        self.embed_model = get_embed_model()

    async def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        """Query the RAG index for relevant chunks.

        Returns list of dicts with: content, chunk_type, file_path,
        start_line, end_line, score.
        """
        # Stub: returns empty until PropertyGraphIndex is connected to PG
        return []
```

- [ ] **Step 6: Commit**

```bash
git add apps/api/src/rag/ apps/api/pyproject.toml apps/api/uv.lock
git commit -m "feat(api): add Graph RAG pipeline with LlamaIndex

AST-aware Python chunking via tree-sitter, semantic markdown chunking,
file scanner, indexing pipeline, and retriever stub. Graph schema
defines entity types (Module, Class, Function, etc.) and relationship
types (IMPORTS, CALLS, INHERITS, etc.)."
```

---

## Task 9: Next.js Frontend — Project Init & Auth

**Goal:** Initialize the Next.js 16.2 project with Bun, configure Better Auth, set up shadcn/ui and Tailwind 4.

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/biome.json`
- Create: `apps/web/src/app/layout.tsx`
- Create: `apps/web/src/app/page.tsx`
- Create: `apps/web/src/lib/auth.ts`
- Create: `apps/web/src/lib/types.ts`
- Create: `apps/web/src/lib/query-provider.tsx`
- Create: `apps/web/src/app/api/auth/[...all]/route.ts`
- Create: `apps/web/src/app/(auth)/login/page.tsx`
- Create: `apps/web/src/app/(auth)/register/page.tsx`

- [ ] **Step 1: Initialize Next.js project with Bun**

Run:
```bash
cd apps/web && bun create next-app . --typescript --tailwind --app --src-dir --no-eslint --import-alias "@/*"
```

If the directory is not empty, adjust as needed. The key is getting a Next.js 16.2 app with App Router + TypeScript + Tailwind.

- [ ] **Step 2: Install dependencies**

Run:
```bash
cd apps/web && bun add better-auth@~1.5.6 drizzle-orm@~0.45.2 zustand@~5.0.12 @tanstack/react-query@~5.96.2
bun add -d drizzle-kit vitest@~4.1.2 @vitejs/plugin-react playwright@~1.59.1
```

- [ ] **Step 3: Configure Biome**

Create `apps/web/biome.json`:

```json
{
  "$schema": "https://biomejs.dev/schemas/2.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2
  }
}
```

Run:
```bash
cd apps/web && bun add -d @biomejs/biome
```

- [ ] **Step 4: Initialize shadcn/ui**

Run:
```bash
cd apps/web && bunx shadcn@latest init
```

Follow prompts: pick default style, CSS variables, base color. Then add commonly needed components:

```bash
cd apps/web && bunx shadcn@latest add button card input label form collapsible badge
```

- [ ] **Step 5: Create Better Auth configuration**

Create `apps/web/src/lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    type: "postgres",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
});
```

- [ ] **Step 6: Create auth API route**

Create `apps/web/src/app/api/auth/[...all]/route.ts`:

```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

- [ ] **Step 7: Create login page**

Create `apps/web/src/app/(auth)/login/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/auth/sign-in/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      window.location.href = "/dashboard";
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Sign in to E.C.H.O.</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <Button type="submit" className="w-full">Sign in</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 8: Create register page**

Create `apps/web/src/app/(auth)/register/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/auth/sign-up/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    if (res.ok) {
      window.location.href = "/dashboard";
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create account</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <Button type="submit" className="w-full">Create account</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 9: Create shared types**

Create `apps/web/src/lib/types.ts`:

```typescript
export interface AgentRun {
  id: string;
  task: string;
  task_type: string | null;
  complexity: string | null;
  status: string;
  total_tokens: number;
  total_cost: number;
  duration_ms: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface AgentRunList {
  runs: AgentRun[];
  total: number;
}

export interface RAGResult {
  content: string;
  chunk_type: string | null;
  file_path: string | null;
  start_line: number | null;
  end_line: number | null;
  score: number;
}

export interface RAGQueryResponse {
  results: RAGResult[];
  query: string;
}
```

- [ ] **Step 10: Create TanStack Query provider**

Create `apps/web/src/lib/query-provider.tsx`:

```tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30 * 1000, // 30 seconds
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

Update `apps/web/src/app/layout.tsx` to wrap children with the provider. Add inside the `<body>` tag:

```tsx
import { QueryProvider } from "@/lib/query-provider";

// In the layout return:
<body>
  <QueryProvider>
    {children}
  </QueryProvider>
</body>
```

- [ ] **Step 11: Commit**

```bash
git add apps/web/
git commit -m "feat(web): initialize Next.js 16.2 with Better Auth, shadcn/ui, Tailwind 4

Bun-managed Next.js app with App Router, Better Auth email/password,
shadcn/ui components, Biome linter, login and register pages. Shared
types for AgentRun and RAG. TanStack Query provider in root layout."
```

---

## Task 10: Dashboard Layout & Overview Page

**Goal:** Create the dashboard shell layout and overview page with placeholders for agent activity, costs, and recent runs.

**Files:**
- Create: `apps/web/src/app/dashboard/layout.tsx`
- Create: `apps/web/src/app/dashboard/page.tsx`
- Create: `apps/web/src/lib/api-client.ts`
- Create: `apps/web/src/lib/stores/ui-store.ts`

- [ ] **Step 1: Create API client**

Create `apps/web/src/lib/api-client.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}
```

- [ ] **Step 2: Create Zustand UI store**

Create `apps/web/src/lib/stores/ui-store.ts`:

```typescript
import { create } from "zustand";

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
```

- [ ] **Step 3: Create dashboard layout**

Create `apps/web/src/app/dashboard/layout.tsx`:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUIStore } from "@/lib/stores/ui-store";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/agents", label: "Agents" },
  { href: "/dashboard/rag", label: "RAG Explorer" },
  { href: "/dashboard/settings", label: "Settings" },
  { href: "/dashboard/admin", label: "Admin" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <div className="flex h-screen">
      {sidebarOpen && (
        <aside className="w-64 border-r bg-muted/40 p-4">
          <h2 className="mb-6 text-lg font-bold">E.C.H.O.</h2>
          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm ${
                  pathname === item.href ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>
      )}
      <main className="flex-1 overflow-auto p-6">
        <button onClick={toggleSidebar} className="mb-4 text-sm text-muted-foreground">
          {sidebarOpen ? "Hide sidebar" : "Show sidebar"}
        </button>
        {children}
      </main>
    </div>
  );
}
```

- [ ] **Step 4: Create dashboard overview page**

Create `apps/web/src/app/dashboard/page.tsx`:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Runs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">0</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">0</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">$0.00</p>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Recent Runs</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No agent runs yet. Submit a task from the Agent Console.</p>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/app/dashboard/ apps/web/src/lib/
git commit -m "feat(web): add dashboard layout with sidebar and overview page

Dashboard shell with collapsible sidebar nav, overview page with
metric cards (runs, tokens, cost) and recent runs list. API client
utility and Zustand UI store for sidebar state."
```

---

## Task 11: Agent Console — Task Submission & Run List

**Goal:** Build the agent console page where users submit tasks and view agent run history.

**Files:**
- Create: `apps/web/src/app/dashboard/agents/page.tsx`
- Create: `apps/web/src/components/agent-console/task-form.tsx`
- Create: `apps/web/src/components/agent-console/agent-list.tsx`

- [ ] **Step 1: Create task submission form**

Create `apps/web/src/components/agent-console/task-form.tsx`:

```tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiFetch } from "@/lib/api-client";
import type { AgentRun } from "@/lib/types";

export function TaskForm({ onSubmit }: { onSubmit: (run: AgentRun) => void }) {
  const [task, setTask] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!task.trim()) return;
    setSubmitting(true);
    try {
      const run = await apiFetch<AgentRun>("/api/agents/runs", {
        method: "POST",
        body: JSON.stringify({ task }),
      });
      onSubmit(run);
      setTask("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit Task</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="task" className="sr-only">Task</Label>
            <Input
              id="task"
              placeholder="Describe the task (e.g., 'Fix the login bug in auth handler')"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={submitting}>
            {submitting ? "Submitting..." : "Run"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Create agent run list**

Create `apps/web/src/components/agent-console/agent-list.tsx`:

```tsx
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentRun } from "@/lib/types";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-500",
  running: "bg-blue-500",
  hitl_waiting: "bg-purple-500",
  completed: "bg-green-500",
  failed: "bg-red-500",
};

export function AgentList({ runs }: { runs: AgentRun[] }) {
  if (runs.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No agent runs yet. Submit a task above to get started.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      {runs.map((run) => (
        <Link key={run.id} href={`/dashboard/agents/${run.id}`}>
          <Card className="cursor-pointer transition-colors hover:bg-muted/50">
            <CardContent className="flex items-center justify-between py-4">
              <div>
                <p className="font-medium">{run.task}</p>
                <p className="text-sm text-muted-foreground">
                  {run.task_type ?? "unclassified"} &middot; {run.total_tokens} tokens &middot; ${run.total_cost.toFixed(4)}
                </p>
              </div>
              <Badge className={STATUS_COLORS[run.status] ?? "bg-gray-500"}>
                {run.status}
              </Badge>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Create agents page**

Create `apps/web/src/app/dashboard/agents/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { TaskForm } from "@/components/agent-console/task-form";
import { AgentList } from "@/components/agent-console/agent-list";
import { apiFetch } from "@/lib/api-client";
import type { AgentRun, AgentRunList } from "@/lib/types";

export default function AgentsPage() {
  const [runs, setRuns] = useState<AgentRun[]>([]);

  useEffect(() => {
    apiFetch<AgentRunList>("/api/agents/runs").then((data) => setRuns(data.runs));
  }, []);

  function handleNewRun(run: AgentRun) {
    setRuns((prev) => [run, ...prev]);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Agent Console</h1>
      <TaskForm onSubmit={handleNewRun} />
      <AgentList runs={runs} />
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/app/dashboard/agents/ apps/web/src/components/agent-console/
git commit -m "feat(web): add agent console with task form and run list

Task submission form posts to /api/agents/runs. Agent list shows
run history with status badges, token counts, and costs. Links
to individual run detail pages."
```

---

## Task 12: Trace Viewer — LangSmith-style Execution Traces

**Goal:** Build the recursive trace tree viewer with HITL approval cards.

**Files:**
- Create: `apps/web/src/app/dashboard/agents/[id]/page.tsx`
- Create: `apps/web/src/components/trace-viewer/trace-tree.tsx`
- Create: `apps/web/src/components/trace-viewer/trace-node.tsx`
- Create: `apps/web/src/components/trace-viewer/hitl-card.tsx`
- Create: `apps/web/src/lib/ws-client.ts`

- [ ] **Step 1: Create WebSocket hook**

Create `apps/web/src/lib/ws-client.ts`:

```typescript
"use client";

import { useEffect, useRef, useState } from "react";

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
  type: "hitl_request";
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
      if (event.type === "hitl_request") {
        setHitlPending(event);
      } else {
        setEvents((prev) => [...prev, event]);
      }
    };

    wsRef.current = ws;
    return () => ws.close();
  }, [runId]);

  function respondHITL(action: "approve" | "reject", feedback?: string) {
    wsRef.current?.send(JSON.stringify({ type: "hitl_response", action, feedback }));
    setHitlPending(null);
  }

  return { events, hitlPending, respondHITL, connected };
}
```

- [ ] **Step 2: Create trace node component**

Create `apps/web/src/components/trace-viewer/trace-node.tsx`:

```tsx
import { Badge } from "@/components/ui/badge";
import type { TraceEvent } from "@/lib/ws-client";

const TYPE_COLORS: Record<string, string> = {
  agent_start: "bg-blue-500",
  agent_end: "bg-blue-700",
  tool_call: "bg-amber-500",
  tool_result: "bg-amber-700",
  llm_start: "bg-purple-500",
  llm_end: "bg-purple-700",
};

export function TraceNode({ event }: { event: TraceEvent }) {
  return (
    <div className="flex items-start gap-3 rounded-md border p-3">
      <Badge className={TYPE_COLORS[event.type] ?? "bg-gray-500"}>
        {event.type}
      </Badge>
      <div className="flex-1">
        {event.agent_name && (
          <p className="text-sm font-medium">{event.agent_name}</p>
        )}
        <pre className="mt-1 text-xs text-muted-foreground">
          {JSON.stringify(event.data, null, 2)}
        </pre>
        <div className="mt-1 flex gap-4 text-xs text-muted-foreground">
          {event.duration_ms != null && <span>{event.duration_ms}ms</span>}
          {event.tokens_in != null && <span>{event.tokens_in} tok in</span>}
          {event.tokens_out != null && <span>{event.tokens_out} tok out</span>}
          {event.cost != null && <span>${event.cost.toFixed(4)}</span>}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create HITL card component**

Create `apps/web/src/components/trace-viewer/hitl-card.tsx`:

```tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { HITLRequest } from "@/lib/ws-client";

interface Props {
  request: HITLRequest;
  onRespond: (action: "approve" | "reject", feedback?: string) => void;
}

export function HITLCard({ request, onRespond }: Props) {
  const [feedback, setFeedback] = useState("");

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
          <Button onClick={() => onRespond("approve", feedback)} variant="default">
            Approve
          </Button>
          <Button onClick={() => onRespond("reject", feedback)} variant="destructive">
            Reject
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 4: Create trace tree component**

Create `apps/web/src/components/trace-viewer/trace-tree.tsx`:

```tsx
import type { TraceEvent } from "@/lib/ws-client";
import { TraceNode } from "./trace-node";

export function TraceTree({ events }: { events: TraceEvent[] }) {
  if (events.length === 0) {
    return <p className="text-muted-foreground">Waiting for trace events...</p>;
  }

  return (
    <div className="space-y-2">
      {events.map((event, i) => (
        <TraceNode key={i} event={event} />
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Create agent run detail page**

Create `apps/web/src/app/dashboard/agents/[id]/page.tsx`:

```tsx
"use client";

import { use } from "react";
import { Badge } from "@/components/ui/badge";
import { TraceTree } from "@/components/trace-viewer/trace-tree";
import { HITLCard } from "@/components/trace-viewer/hitl-card";
import { useAgentTrace } from "@/lib/ws-client";

export default function AgentRunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { events, hitlPending, respondHITL, connected } = useAgentTrace(id);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">Run {id.slice(0, 8)}...</h1>
        <Badge className={connected ? "bg-green-500" : "bg-red-500"}>
          {connected ? "Connected" : "Disconnected"}
        </Badge>
      </div>

      {hitlPending && (
        <HITLCard request={hitlPending} onRespond={respondHITL} />
      )}

      <TraceTree events={events} />
    </div>
  );
}
```

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/app/dashboard/agents/\[id\]/ apps/web/src/components/trace-viewer/ apps/web/src/lib/ws-client.ts
git commit -m "feat(web): add LangSmith-style trace viewer with HITL cards

WebSocket hook streams trace events in real-time. TraceTree renders
events with type badges, token counts, costs. HITLCard shows
interactive approval/rejection UI for human-in-the-loop checkpoints."
```

---

## Task 13: Remaining Dashboard Pages (RAG Explorer, Settings, Admin)

**Goal:** Create the remaining dashboard pages as functional shells.

**Files:**
- Create: `apps/web/src/app/dashboard/rag/page.tsx`
- Create: `apps/web/src/app/dashboard/rag/graph/page.tsx`
- Create: `apps/web/src/app/dashboard/settings/page.tsx`
- Create: `apps/web/src/app/dashboard/admin/page.tsx`
- Create: `apps/web/src/db/schema.ts`
- Create: `apps/web/src/db/drizzle.config.ts`

- [ ] **Step 1: Create RAG explorer page**

Create `apps/web/src/app/dashboard/rag/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiFetch } from "@/lib/api-client";
import type { RAGResult, RAGQueryResponse } from "@/lib/types";

export default function RAGPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<RAGResult[]>([]);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const data = await apiFetch<{ results: RAGResult[] }>("/api/rag/query", {
      method: "POST",
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
                {r.file_path}:{r.start_line}-{r.end_line} ({r.chunk_type}) — score: {r.score.toFixed(3)}
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
```

- [ ] **Step 2: Create knowledge graph page**

Create `apps/web/src/app/dashboard/rag/graph/page.tsx`:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function GraphPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Knowledge Graph</h1>
      <Card>
        <CardHeader>
          <CardTitle>Graph Visualization</CardTitle>
        </CardHeader>
        <CardContent className="flex h-96 items-center justify-center text-muted-foreground">
          Graph visualization will render here once the RAG indexing pipeline has run.
          Use `mise run index` to index the codebase.
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 3: Create settings page**

Create `apps/web/src/app/dashboard/settings/page.tsx`:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>Model Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><strong>LLM:</strong> gemma4:8b (Ollama local)</p>
          <p><strong>Embeddings:</strong> nomic-embed-text (768 dimensions)</p>
          <p><strong>Ollama URL:</strong> http://localhost:11434</p>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 4: Create admin page**

Create `apps/web/src/app/dashboard/admin/page.tsx`:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin Panel</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            User management will be available once Better Auth is fully integrated.
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Cost Reports</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            Aggregated cost data from the cost_ledger table will appear here.
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Audit Logs</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground">
            All LLM calls and agent actions are logged for compliance review.
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Create Drizzle schema (read-only mirror)**

Create `apps/web/src/db/schema.ts`:

```typescript
import { pgTable, uuid, varchar, text, integer, decimal, timestamp, jsonb } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: varchar("email", { length: 255 }).unique().notNull(),
  name: varchar("name", { length: 255 }),
  role: varchar("role", { length: 50 }).default("user"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});

export const agentRuns = pgTable("agent_runs", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id").references(() => users.id),
  task: text("task").notNull(),
  taskType: varchar("task_type", { length: 50 }),
  complexity: varchar("complexity", { length: 20 }),
  status: varchar("status", { length: 20 }).default("pending"),
  result: jsonb("result"),
  totalTokens: integer("total_tokens").default(0),
  totalCost: decimal("total_cost", { precision: 10, scale: 6 }).default("0"),
  durationMs: integer("duration_ms"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  completedAt: timestamp("completed_at", { withTimezone: true }),
});

export const costLedger = pgTable("cost_ledger", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: uuid("user_id").references(() => users.id),
  runId: uuid("run_id").references(() => agentRuns.id),
  model: varchar("model", { length: 100 }).notNull(),
  tokensIn: integer("tokens_in").notNull(),
  tokensOut: integer("tokens_out").notNull(),
  cost: decimal("cost", { precision: 10, scale: 6 }).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});
```

- [ ] **Step 6: Create Drizzle config**

Create `apps/web/src/db/drizzle.config.ts`:

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

- [ ] **Step 7: Commit**

```bash
git add apps/web/src/app/dashboard/rag/ apps/web/src/app/dashboard/settings/ apps/web/src/app/dashboard/admin/ apps/web/src/db/
git commit -m "feat(web): add RAG explorer, settings, admin pages, Drizzle schema

RAG search page queries /api/rag/query. Graph visualization placeholder.
Settings shows model config. Admin shows user/cost/audit sections.
Drizzle schema mirrors PostgreSQL tables for type-safe reads."
```

---

## Task 14: Observability — structlog + OpenTelemetry

**Goal:** Add structured logging and distributed tracing to the backend.

**Files:**
- Modify: `apps/api/pyproject.toml` (add structlog, opentelemetry)
- Modify: `apps/api/src/main.py` (add logging + OTEL middleware)

- [ ] **Step 1: Add observability dependencies**

Add to `apps/api/pyproject.toml` dependencies:

```
"structlog~=25.5.0",
"opentelemetry-sdk~=1.40.0",
"opentelemetry-api~=1.40.0",
"opentelemetry-instrumentation-fastapi",
```

Run:
```bash
cd apps/api && uv sync
```

- [ ] **Step 2: Configure structlog and OTEL in main.py**

Update `apps/api/src/main.py`:

```python
import structlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider

from src.api.agents import router as agents_router
from src.api.rag import router as rag_router
from src.api.traces import router as traces_router
from src.api.ws import router as ws_router

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
)

# Configure OpenTelemetry
provider = TracerProvider()
trace.set_tracer_provider(provider)

app = FastAPI(title="E.C.H.O. API", version="0.1.0")

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

app.include_router(agents_router)
app.include_router(traces_router)
app.include_router(rag_router)
app.include_router(ws_router)

log = structlog.get_logger()


@app.get("/health")
async def health():
    log.info("health_check")
    return {"status": "ok", "version": "0.1.0"}
```

- [ ] **Step 3: Run existing tests to ensure nothing broke**

Run:
```bash
cd apps/api && uv run pytest tests/ -v
```

Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add apps/api/pyproject.toml apps/api/uv.lock apps/api/src/main.py
git commit -m "feat(api): add structlog + OpenTelemetry observability

Structured logging with structlog, distributed tracing with
OpenTelemetry SDK, FastAPI auto-instrumentation for all endpoints."
```

---

## Summary

| Task | Description | Key Deliverable |
|------|-------------|-----------------|
| 0 | Claude Code Project Structure | CLAUDE.md, .claude/ config, rules, hooks |
| 1 | Monorepo Scaffolding | .mise.toml, docker-compose.yml, Dockerfiles |
| 2 | Python Backend Init | FastAPI + health endpoint + tests |
| 3 | Database Models | SQLAlchemy models + Alembic migrations |
| 4 | API Routes | Pydantic schemas + route stubs |
| 5 | AI Gateway | LiteLLM router + PII scrubber + cost tracker |
| 6 | Agent System | LangGraph state + graph + supervisor + agent stubs |
| 7 | WebSocket | Real-time trace streaming |
| 8 | RAG Pipeline | LlamaIndex indexer + chunkers + retriever |
| 9 | Frontend Init | Next.js + Better Auth + shadcn/ui |
| 10 | Dashboard | Layout + overview page |
| 11 | Agent Console | Task form + run list |
| 12 | Trace Viewer | LangSmith-style traces + HITL cards |
| 13 | Dashboard Pages | RAG explorer + settings + admin + Drizzle |
| 14 | Observability | structlog + OpenTelemetry |
