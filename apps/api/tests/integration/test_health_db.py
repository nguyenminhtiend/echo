import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.integration


async def test_health_ok(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_pgvector_extension_present(session: AsyncSession):
    row = await session.execute(text("SELECT extname FROM pg_extension WHERE extname='vector'"))
    assert row.scalar_one() == "vector"


async def test_core_tables_exist(session: AsyncSession):
    rows = await session.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    )
    names = {r[0] for r in rows}
    # Identity tables (``user``/``session``/etc.) are owned by Better Auth and
    # are NOT created by Alembic, so we only assert the Alembic-managed set.
    for expected in ("agent_runs", "trace_events", "rag_chunks", "audit_log", "cost_ledger"):
        assert expected in names, f"missing table {expected}"
