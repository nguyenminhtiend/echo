# E.C.H.O. Integration & E2E Verification Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add end-to-end and integration verification on top of the existing unit tests so the E.C.H.O. stack can be validated without manual inspection — real Postgres+pgvector, real Ollama, real FastAPI↔Next.js, Playwright browser flow, and a CI pipeline that runs it all.

**Architecture:**
- Backend integration tests use a real Postgres 18.3 + pgvector 0.8.2 container via `testcontainers-python`, running Alembic migrations against it. Ollama calls are gated behind a `RUN_OLLAMA_TESTS=1` env flag and use `gemma4:8b` + `nomic-embed-text` on `localhost:11434`.
- Frontend E2E tests use Playwright against `next start` (built app) talking to a real FastAPI instance on a test database. A single `scripts/e2e-up.sh` orchestrates db + api + web for the E2E run.
- CI runs in GitHub Actions: a `unit` job (pytest + vitest, fast), an `integration` job (pytest integration markers with testcontainers), and an `e2e` job (Playwright). Ollama-gated tests run only on a nightly schedule.

**Tech Stack:** pytest + pytest-asyncio + testcontainers-python, httpx.AsyncClient, Playwright 1.59.1, GitHub Actions, Docker, existing stack (FastAPI, Next.js 16.2, Postgres 18.3 + pgvector 0.8.2, Ollama gemma4:8b).

---

## File Structure

**Create:**
- `apps/api/tests/integration/__init__.py`
- `apps/api/tests/integration/conftest.py` — session-scoped Postgres container + migrated async engine + httpx AsyncClient
- `apps/api/tests/integration/test_health_db.py` — `/health` with real DB
- `apps/api/tests/integration/test_agents_flow.py` — POST `/agents/runs` → persisted row → GET trace events
- `apps/api/tests/integration/test_rag_flow.py` — index a tiny fixture dir → query retriever → assert chunks
- `apps/api/tests/integration/test_ollama_smoke.py` — gated Ollama embed + chat call
- `apps/api/tests/integration/fixtures/tiny_repo/sample.py` — fixture source file for RAG
- `apps/web/playwright.config.ts`
- `apps/web/e2e/auth.spec.ts` — register → login → dashboard
- `apps/web/e2e/agent-run.spec.ts` — submit task → run appears → trace stream renders
- `apps/web/e2e/rag-explorer.spec.ts` — search returns chunks
- `apps/web/e2e/fixtures/api.ts` — helper that seeds a user via API before the test
- `scripts/e2e-up.sh` — boots db+api+web for local E2E
- `scripts/e2e-down.sh`
- `.github/workflows/ci.yml`
- `.github/workflows/nightly.yml` — Ollama-gated tests

**Modify:**
- `apps/api/pyproject.toml` — add `testcontainers[postgres]`, `pytest-xdist`, register `integration` + `ollama` markers
- `apps/api/tests/conftest.py` — add `pytest_collection_modifyitems` to skip `ollama` marker unless `RUN_OLLAMA_TESTS=1`
- `apps/web/package.json` — add `test:e2e`, `test:e2e:ui` scripts; add `@playwright/test`
- `.mise.toml` — add `test:integration` and `test:e2e` tasks
- `CLAUDE.md` — document the new test commands under "Available Commands"

---

## Task 1: Backend integration test harness (Postgres + migrations)

**Files:**
- Modify: `apps/api/pyproject.toml`
- Create: `apps/api/tests/integration/__init__.py`
- Create: `apps/api/tests/integration/conftest.py`
- Create: `apps/api/tests/integration/test_health_db.py`
- Modify: `apps/api/tests/conftest.py`

- [ ] **Step 1: Add integration test dependencies**

Edit `apps/api/pyproject.toml` `[project.optional-dependencies].dev` list — add:

```toml
    "testcontainers[postgres]>=4.8",
    "pytest-xdist",
```

And under `[tool.pytest.ini_options]` add:

```toml
markers = [
  "integration: requires docker (real postgres via testcontainers)",
  "ollama: requires local ollama server with gemma4:8b + nomic-embed-text",
]
```

- [ ] **Step 2: Install**

Run: `cd apps/api && uv sync --extra dev`
Expected: resolves; `testcontainers` installed.

- [ ] **Step 3: Add marker gating to root conftest**

Edit `apps/api/tests/conftest.py` — append:

```python
import os
import pytest

def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_OLLAMA_TESTS") == "1":
        return
    skip_ollama = pytest.mark.skip(reason="set RUN_OLLAMA_TESTS=1 to run")
    for item in items:
        if "ollama" in item.keywords:
            item.add_marker(skip_ollama)
```

- [ ] **Step 4: Write the integration conftest**

Create `apps/api/tests/integration/__init__.py` (empty) and `apps/api/tests/integration/conftest.py`:

```python
import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.main import app

PG_IMAGE = "pgvector/pgvector:pg18"  # pg18 + pgvector 0.8.2

@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer(PG_IMAGE, driver="asyncpg") as pg:
        yield pg

@pytest.fixture(scope="session")
def db_url(pg_container: PostgresContainer) -> str:
    url = pg_container.get_connection_url()
    os.environ["DATABASE_URL"] = url
    return url

@pytest.fixture(scope="session", autouse=True)
def run_migrations(db_url: str):
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url.replace("+asyncpg", ""))
    command.upgrade(cfg, "head")

@pytest_asyncio.fixture
async def session(db_url: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(db_url, future=True)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()

@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

- [ ] **Step 5: Write the failing health+DB integration test**

Create `apps/api/tests/integration/test_health_db.py`:

```python
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

pytestmark = pytest.mark.integration

async def test_health_ok(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

async def test_pgvector_extension_present(session: AsyncSession):
    row = await session.execute(text("SELECT extname FROM pg_extension WHERE extname='vector'"))
    assert row.scalar_one() == "vector"

async def test_core_tables_exist(session: AsyncSession):
    rows = await session.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
    ))
    names = {r[0] for r in rows}
    for expected in ("users", "agent_runs", "trace_events", "rag_chunks"):
        assert expected in names, f"missing table {expected}"
```

- [ ] **Step 6: Run it and verify it passes**

Run: `cd apps/api && uv run pytest tests/integration/test_health_db.py -v -m integration`
Expected: 3 passed. If `pgvector` extension isn't auto-created by the migration, fix the migration (it should already `CREATE EXTENSION IF NOT EXISTS vector;` per Task 3 Step 11 of the main plan) rather than the test.

- [ ] **Step 7: Commit**

```bash
git add apps/api/pyproject.toml apps/api/tests/conftest.py apps/api/tests/integration
git commit -m "test(api): add integration harness with testcontainers postgres+pgvector"
```

---

## Task 2: Backend integration — agents flow

**Files:**
- Create: `apps/api/tests/integration/test_agents_flow.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.agent_run import AgentRun

pytestmark = pytest.mark.integration

async def test_create_run_persists_and_lists(client: AsyncClient, session: AsyncSession):
    payload = {"task": "write a hello world function", "repo_path": "/tmp/x"}
    r = await client.post("/agents/runs", json=payload)
    assert r.status_code in (200, 201), r.text
    run_id = r.json()["id"]

    # DB persisted
    row = (await session.execute(select(AgentRun).where(AgentRun.id == run_id))).scalar_one()
    assert row.task == payload["task"]

    # List endpoint surfaces it
    r2 = await client.get("/agents/runs")
    assert r2.status_code == 200
    assert any(item["id"] == run_id for item in r2.json())

async def test_get_run_traces_returns_list(client: AsyncClient):
    r = await client.post("/agents/runs", json={"task": "noop", "repo_path": "/tmp/x"})
    run_id = r.json()["id"]
    r2 = await client.get(f"/traces/{run_id}")
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)
```

- [ ] **Step 2: Run**

Run: `cd apps/api && uv run pytest tests/integration/test_agents_flow.py -v -m integration`
Expected: 2 passed. If POST shape differs from the implemented schema, read `src/schemas/agents.py` and `src/api/agents.py` and update the payload/assertions to match — do **not** change the API.

- [ ] **Step 3: Commit**

```bash
git add apps/api/tests/integration/test_agents_flow.py
git commit -m "test(api): integration test for agent run create+list+traces"
```

---

## Task 3: Backend integration — RAG indexing & retrieval

**Files:**
- Create: `apps/api/tests/integration/fixtures/tiny_repo/sample.py`
- Create: `apps/api/tests/integration/test_rag_flow.py`

- [ ] **Step 1: Create a tiny fixture repo**

`apps/api/tests/integration/fixtures/tiny_repo/sample.py`:

```python
def add(a: int, b: int) -> int:
    """Add two integers and return the sum."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the product."""
    return a * b
```

- [ ] **Step 2: Write the failing test (mock embeddings, real DB)**

`apps/api/tests/integration/test_rag_flow.py`:

```python
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.rag import RagChunk
from src.rag.chunkers import chunk_file  # adjust import if different

pytestmark = pytest.mark.integration

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_repo" / "sample.py"

async def test_chunker_splits_by_function():
    chunks = list(chunk_file(FIXTURE))
    assert len(chunks) >= 2
    texts = [c.text for c in chunks]
    assert any("def add" in t for t in texts)
    assert any("def multiply" in t for t in texts)

async def test_rag_chunks_writable(session: AsyncSession):
    row = RagChunk(
        source_path=str(FIXTURE),
        text="def add(a, b): return a + b",
        embedding=[0.0] * 768,
    )
    session.add(row)
    await session.commit()

    got = (await session.execute(select(RagChunk).where(RagChunk.id == row.id))).scalar_one()
    assert got.source_path == str(FIXTURE)
    assert len(got.embedding) == 768
```

- [ ] **Step 3: Run**

Run: `cd apps/api && uv run pytest tests/integration/test_rag_flow.py -v -m integration`
Expected: 2 passed. If `chunk_file` has a different signature, read `src/rag/chunkers.py` and adapt the test call (not the source). If `RagChunk` field names differ, read `src/models/rag.py` and match them exactly.

- [ ] **Step 4: Commit**

```bash
git add apps/api/tests/integration/fixtures apps/api/tests/integration/test_rag_flow.py
git commit -m "test(api): integration tests for RAG chunker and pgvector storage"
```

---

## Task 4: Backend integration — Ollama smoke (gated)

**Files:**
- Create: `apps/api/tests/integration/test_ollama_smoke.py`

- [ ] **Step 1: Write the failing (gated) test**

```python
import os

import httpx
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.ollama]

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

async def test_ollama_tags_lists_required_models():
    async with httpx.AsyncClient(base_url=OLLAMA, timeout=10) as c:
        r = await c.get("/api/tags")
    assert r.status_code == 200
    names = {m["name"].split(":")[0] for m in r.json().get("models", [])}
    assert "gemma4" in names, f"gemma4 not pulled; got {names}"
    assert "nomic-embed-text" in names, f"nomic-embed-text not pulled; got {names}"

async def test_ollama_embed_returns_768_dim():
    async with httpx.AsyncClient(base_url=OLLAMA, timeout=60) as c:
        r = await c.post("/api/embeddings", json={
            "model": "nomic-embed-text",
            "prompt": "hello world",
        })
    assert r.status_code == 200
    vec = r.json()["embedding"]
    assert len(vec) == 768

async def test_ollama_chat_responds():
    async with httpx.AsyncClient(base_url=OLLAMA, timeout=120) as c:
        r = await c.post("/api/chat", json={
            "model": "gemma4:8b",
            "messages": [{"role": "user", "content": "Reply with the single word: pong"}],
            "stream": False,
        })
    assert r.status_code == 200
    content = r.json()["message"]["content"].lower()
    assert "pong" in content
```

- [ ] **Step 2: Verify it's skipped by default**

Run: `cd apps/api && uv run pytest tests/integration/test_ollama_smoke.py -v`
Expected: 3 skipped ("set RUN_OLLAMA_TESTS=1 to run").

- [ ] **Step 3: Optionally verify it passes locally if Ollama is running**

Run: `RUN_OLLAMA_TESTS=1 uv run pytest tests/integration/test_ollama_smoke.py -v`
Expected (if Ollama up): 3 passed. Do not block on this in CI.

- [ ] **Step 4: Commit**

```bash
git add apps/api/tests/integration/test_ollama_smoke.py
git commit -m "test(api): add gated ollama smoke tests (models, embed, chat)"
```

---

## Task 5: Playwright E2E harness

**Files:**
- Modify: `apps/web/package.json`
- Create: `apps/web/playwright.config.ts`
- Create: `apps/web/e2e/fixtures/api.ts`
- Create: `scripts/e2e-up.sh`
- Create: `scripts/e2e-down.sh`

- [ ] **Step 1: Add playwright to web deps**

Edit `apps/web/package.json` — `devDependencies` add `"@playwright/test": "~1.59.1"`, `scripts` add:

```json
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
```

Run: `cd apps/web && bun install && bunx playwright install --with-deps chromium`
Expected: chromium downloaded.

- [ ] **Step 2: Create the Playwright config**

`apps/web/playwright.config.ts`:

```ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    trace: "retain-on-failure",
    video: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
```

Note: do NOT add a `webServer:` block — the stack is orchestrated by `scripts/e2e-up.sh` so all three services (db, api, web) come up together.

- [ ] **Step 3: Create API helper fixture**

`apps/web/e2e/fixtures/api.ts`:

```ts
const API = process.env.E2E_API_URL ?? "http://localhost:8000";

export async function seedUser(email: string, password: string) {
  const r = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email, password, name: "E2E" }),
  });
  if (!r.ok && r.status !== 409) throw new Error(`seedUser failed: ${r.status}`);
}

export async function apiHealthy(): Promise<boolean> {
  try {
    const r = await fetch(`${API}/health`);
    return r.ok;
  } catch {
    return false;
  }
}
```

- [ ] **Step 4: Create e2e-up / e2e-down scripts**

`scripts/e2e-up.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker compose up -d db
echo "waiting for postgres..."
for i in {1..30}; do
  if docker compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then break; fi
  sleep 1
done

(cd apps/api && uv run alembic upgrade head)
(cd apps/api && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 >/tmp/echo-api.log 2>&1 &)
echo $! > /tmp/echo-api.pid

echo "waiting for api..."
for i in {1..30}; do
  if curl -sf http://localhost:8000/health >/dev/null; then break; fi
  sleep 1
done

(cd apps/web && bun run build && bun run start >/tmp/echo-web.log 2>&1 &)
echo $! > /tmp/echo-web.pid

echo "waiting for web..."
for i in {1..60}; do
  if curl -sf http://localhost:3000 >/dev/null; then break; fi
  sleep 1
done
echo "stack up"
```

`scripts/e2e-down.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
[ -f /tmp/echo-web.pid ] && kill "$(cat /tmp/echo-web.pid)" 2>/dev/null || true
[ -f /tmp/echo-api.pid ] && kill "$(cat /tmp/echo-api.pid)" 2>/dev/null || true
rm -f /tmp/echo-web.pid /tmp/echo-api.pid
docker compose down
```

Run: `chmod +x scripts/e2e-up.sh scripts/e2e-down.sh`

- [ ] **Step 5: Smoke-test the scripts locally**

Run: `./scripts/e2e-up.sh && curl -sf http://localhost:3000 >/dev/null && echo OK && ./scripts/e2e-down.sh`
Expected: prints `OK`. If `next start` fails because of the Next.js 16.2 breaking changes, read `apps/web/node_modules/next/dist/docs/` per `apps/web/AGENTS.md` before fixing — do not guess.

- [ ] **Step 6: Commit**

```bash
git add apps/web/package.json apps/web/playwright.config.ts apps/web/e2e/fixtures/api.ts scripts/e2e-up.sh scripts/e2e-down.sh
git commit -m "test(web): add playwright harness and e2e stack scripts"
```

---

## Task 6: E2E — auth flow

**Files:**
- Create: `apps/web/e2e/auth.spec.ts`

- [ ] **Step 1: Write the failing spec**

```ts
import { test, expect } from "@playwright/test";

const email = `e2e+${Date.now()}@example.com`;
const password = "Password123!";

test("register -> login -> dashboard", async ({ page }) => {
  await page.goto("/register");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /sign up|register/i }).click();

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByRole("heading", { name: /dashboard|overview/i })).toBeVisible();
});

test("login existing user lands on dashboard", async ({ page, request }) => {
  const existing = `seeded+${Date.now()}@example.com`;
  await request.post("http://localhost:8000/auth/register", {
    data: { email: existing, password, name: "Seed" },
  });

  await page.goto("/login");
  await page.getByLabel(/email/i).fill(existing);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /sign in|log in/i }).click();

  await expect(page).toHaveURL(/\/dashboard/);
});
```

- [ ] **Step 2: Run with the stack up**

Run: `./scripts/e2e-up.sh && (cd apps/web && bun run test:e2e e2e/auth.spec.ts); ./scripts/e2e-down.sh`
Expected: 2 passed. If selectors don't match the actual form labels, read `apps/web/src/app/(auth)/login/page.tsx` and `register/page.tsx` and update the selectors (not the pages).

- [ ] **Step 3: Commit**

```bash
git add apps/web/e2e/auth.spec.ts
git commit -m "test(web): e2e register+login happy path"
```

---

## Task 7: E2E — agent run submission + trace stream

**Files:**
- Create: `apps/web/e2e/agent-run.spec.ts`

- [ ] **Step 1: Write the spec**

```ts
import { test, expect } from "@playwright/test";

const email = `runner+${Date.now()}@example.com`;
const password = "Password123!";

test.beforeEach(async ({ page, request }) => {
  await request.post("http://localhost:8000/auth/register", {
    data: { email, password, name: "Runner" },
  });
  await page.goto("/login");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /sign in|log in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
});

test("submit agent task -> run appears -> trace viewer opens", async ({ page }) => {
  await page.goto("/dashboard/agents");
  await page.getByLabel(/task/i).fill("Write a hello world function");
  await page.getByRole("button", { name: /submit|run|start/i }).click();

  const runRow = page.getByRole("row").filter({ hasText: /hello world/i }).first();
  await expect(runRow).toBeVisible({ timeout: 15_000 });

  await runRow.click();
  await expect(page.getByText(/trace|supervisor|coder/i).first()).toBeVisible({ timeout: 15_000 });
});
```

- [ ] **Step 2: Run**

Run: `./scripts/e2e-up.sh && (cd apps/web && bun run test:e2e e2e/agent-run.spec.ts); ./scripts/e2e-down.sh`
Expected: 1 passed. The WS stream does NOT require Ollama — the supervisor stubs in `src/agents/*.py` should emit trace events without calling the model. If they don't, fix the stub to emit a synthetic trace event when `ECHO_STUB_AGENTS=1` rather than shipping Ollama as a test dependency.

- [ ] **Step 3: Commit**

```bash
git add apps/web/e2e/agent-run.spec.ts
git commit -m "test(web): e2e agent run submission and trace rendering"
```

---

## Task 8: E2E — RAG explorer

**Files:**
- Create: `apps/web/e2e/rag-explorer.spec.ts`

- [ ] **Step 1: Write the spec**

```ts
import { test, expect } from "@playwright/test";

test("rag explorer search returns results", async ({ page, request }) => {
  // seed a chunk directly via API
  await request.post("http://localhost:8000/rag/chunks", {
    data: {
      source_path: "e2e/sample.py",
      text: "def greet(name): return f'hello {name}'",
    },
  });

  await page.goto("/dashboard/rag");
  await page.getByPlaceholder(/search|query/i).fill("greet");
  await page.getByRole("button", { name: /search/i }).click();

  await expect(page.getByText(/greet/)).toBeVisible({ timeout: 10_000 });
});
```

- [ ] **Step 2: Run**

Run: `./scripts/e2e-up.sh && (cd apps/web && bun run test:e2e e2e/rag-explorer.spec.ts); ./scripts/e2e-down.sh`
Expected: 1 passed. If `POST /rag/chunks` doesn't exist, read `src/api/rag.py` and use whatever seed-admission endpoint does; if none exists, insert directly via `psql` in `scripts/e2e-up.sh` using a small SQL seed file `scripts/e2e-seed.sql`.

- [ ] **Step 3: Commit**

```bash
git add apps/web/e2e/rag-explorer.spec.ts
git commit -m "test(web): e2e rag explorer search"
```

---

## Task 9: mise tasks + CLAUDE.md docs

**Files:**
- Modify: `.mise.toml`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add mise tasks**

Append to `.mise.toml`:

```toml
[tasks."test:integration"]
description = "Backend integration tests (needs docker)"
run = "cd apps/api && uv run pytest -m integration -v"

[tasks."test:e2e"]
description = "Full-stack Playwright E2E"
run = [
  "./scripts/e2e-up.sh",
  "cd apps/web && bun run test:e2e",
  "./scripts/e2e-down.sh",
]

[tasks."test:ollama"]
description = "Ollama-gated smoke tests"
run = "cd apps/api && RUN_OLLAMA_TESTS=1 uv run pytest -m ollama -v"
```

- [ ] **Step 2: Document in CLAUDE.md**

In `CLAUDE.md` under `## Available Commands (mise)`, add three lines matching the existing style:

```
mise run test:integration # Backend integration tests (docker required)
mise run test:e2e         # Full-stack Playwright E2E
mise run test:ollama      # Ollama-gated smoke tests (requires local ollama)
```

- [ ] **Step 3: Sanity-run**

Run: `mise run test:integration`
Expected: collects and runs the integration suite (passes if Docker is running).

- [ ] **Step 4: Commit**

```bash
git add .mise.toml CLAUDE.md
git commit -m "chore: add mise tasks for integration/e2e/ollama tests"
```

---

## Task 10: CI — GitHub Actions

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/nightly.yml`

- [ ] **Step 1: Create `ci.yml`**

```yaml
name: ci
on:
  push: { branches: [master] }
  pull_request:

jobs:
  unit-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.14" }
      - run: pip install uv
      - run: cd apps/api && uv sync --extra dev
      - run: cd apps/api && uv run ruff check .
      - run: cd apps/api && uv run pyright
      - run: cd apps/api && uv run pytest -v -m "not integration and not ollama"

  unit-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: cd apps/web && bun install
      - run: cd apps/web && bunx biome check .
      - run: cd apps/web && bunx vitest run

  integration-api:
    runs-on: ubuntu-latest
    needs: unit-api
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.14" }
      - run: pip install uv
      - run: cd apps/api && uv sync --extra dev
      - run: cd apps/api && uv run pytest -m integration -v

  e2e:
    runs-on: ubuntu-latest
    needs: [unit-api, unit-web]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.14" }
      - uses: oven-sh/setup-bun@v2
      - run: pip install uv
      - run: cd apps/api && uv sync --extra dev
      - run: cd apps/web && bun install
      - run: cd apps/web && bunx playwright install --with-deps chromium
      - run: ./scripts/e2e-up.sh
      - run: cd apps/web && bun run test:e2e
      - if: always()
        run: ./scripts/e2e-down.sh
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: apps/web/playwright-report
```

- [ ] **Step 2: Create `nightly.yml` (Ollama-gated)**

```yaml
name: nightly-ollama
on:
  schedule: [{ cron: "0 6 * * *" }]
  workflow_dispatch:

jobs:
  ollama-smoke:
    runs-on: self-hosted  # needs a runner with ollama installed
    steps:
      - uses: actions/checkout@v4
      - run: ollama pull gemma4:8b
      - run: ollama pull nomic-embed-text
      - run: pip install uv && cd apps/api && uv sync --extra dev
      - env: { RUN_OLLAMA_TESTS: "1" }
        run: cd apps/api && uv run pytest -m ollama -v
```

- [ ] **Step 3: Validate workflow YAML locally**

Run: `python -c "import yaml,sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]" .github/workflows/ci.yml .github/workflows/nightly.yml && echo OK`
Expected: prints `OK`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml .github/workflows/nightly.yml
git commit -m "ci: add unit+integration+e2e pipeline and nightly ollama job"
```

---

## Task 11: Final verification

- [ ] **Step 1: Run the whole local pipeline**

Run:

```bash
mise run lint
mise run test
mise run test:integration
mise run test:e2e
```

Expected: all four green. If any step fails, fix the root cause (not the test) and re-run before continuing.

- [ ] **Step 2: Confirm the gate works**

Run: `cd apps/api && uv run pytest -m ollama -v`
Expected: all `ollama`-marked tests **skipped** (not failed).

- [ ] **Step 3: Commit any fixups**

```bash
git add -A
git commit -m "test: verification pass for integration+e2e plan" || echo "nothing to commit"
```
