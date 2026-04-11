# Project E.C.H.O. — Enterprise Cognitive Hub & Orchestration

## Overview

Self-hosted, multi-agent AI platform that orchestrates specialized AI agents across the entire SDLC. Agents autonomously generate code, review PRs, write tests, scan for security vulnerabilities, produce documentation, and analyze architecture.

**Core Principles:**
- Provider-agnostic LiteLLM gateway: chat via OpenRouter (Claude Sonnet 4.5), embeddings via local Ollama (nomic-embed-text)
- Enterprise-grade patterns: Multi-agent orchestration, Graph RAG, AI gateway, PII scrubbing, audit logging, OTEL tracing

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
- **LLM:** OpenRouter (chat: anthropic/claude-sonnet-4.5) + Ollama (embeddings only: nomic-embed-text, 768 dim)
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
                    OpenRouter API (chat: anthropic/claude-sonnet-4.5)
                    Ollama (embeddings only: nomic-embed-text, localhost:11434)
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
mise run test:integration # Backend integration tests (docker required)
mise run test:e2e         # Full-stack Playwright E2E
mise run test:ollama      # Ollama-gated smoke tests (requires local ollama)
```

## Security Notes

- **LiteLLM >=1.83.0 ONLY** — versions 1.82.7 and 1.82.8 were compromised (supply chain attack, March 2026)
- **pgvector 0.8.2 ONLY** — earlier versions have CVE-2026-3172 (buffer overflow)
- PII scrubbed before any LLM call (Presidio middleware)
- Secrets never reach the LLM — regex scan for AWS keys, JWT tokens, private keys
- All LLM calls audit-logged: timestamp, user, model, token count, cost, input hash
