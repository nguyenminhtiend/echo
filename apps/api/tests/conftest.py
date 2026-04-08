import os
from datetime import UTC, datetime
from decimal import Decimal

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/echo_test")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ.setdefault("ECHO_LLM_MODEL", "gemma4:8b")
os.environ.setdefault("ECHO_EMBED_MODEL", "nomic-embed-text")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests")
os.environ["ECHO_SKIP_AGENT_RUNNER"] = "1"

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.main import app


async def _refresh_like_db(obj):
    """Populate columns a real DB refresh would load (defaults + timestamps)."""
    if getattr(obj, "total_tokens", None) is None:
        obj.total_tokens = 0
    if getattr(obj, "total_cost", None) is None:
        obj.total_cost = Decimal("0")
    if getattr(obj, "created_at", None) is None:
        obj.created_at = datetime.now(UTC)


async def _mock_get_db():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=_refresh_like_db)

    async def execute(_stmt):
        r = MagicMock()
        r.scalar_one.return_value = 0
        r.scalar_one_or_none.return_value = None
        r.scalars.return_value.all.return_value = []
        r.one.return_value = (0, 0, 0)
        return r

    session.execute = AsyncMock(side_effect=execute)
    yield session


@pytest.fixture
async def client():
    app.dependency_overrides[get_db] = _mock_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_OLLAMA_TESTS") == "1":
        return
    skip_ollama = pytest.mark.skip(reason="set RUN_OLLAMA_TESTS=1 to run")
    for item in items:
        if "ollama" in item.keywords:
            item.add_marker(skip_ollama)
