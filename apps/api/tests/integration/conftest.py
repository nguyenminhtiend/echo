import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.db import session as db_session
from src.main import app

PG_IMAGE = "pgvector/pgvector:pg18"  # pg18 + pgvector 0.8.2


def _local_test_db_url() -> str | None:
    """Return an explicit test DB URL if the user provided one.

    Set ECHO_TEST_DATABASE_URL when running integration tests against a locally
    running Postgres (e.g. Homebrew) to avoid the testcontainers/Docker path.
    The URL must point at an EMPTY database — migrations will be applied to it.
    """
    return os.environ.get("ECHO_TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def pg_container():
    if _local_test_db_url():
        yield None
        return
    # Lazy import so unit-test collection doesn't require the testcontainers
    # extra or a running Docker daemon.
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer(PG_IMAGE, driver="asyncpg") as pg:
        yield pg


@pytest.fixture(scope="session")
def db_url(pg_container) -> str:
    local = _local_test_db_url()
    if local:
        # Normalise to the asyncpg driver the app expects.
        if local.startswith("postgresql://"):
            local = local.replace("postgresql://", "postgresql+asyncpg://", 1)
        os.environ["DATABASE_URL"] = local
        return local
    url = pg_container.get_connection_url()
    os.environ["DATABASE_URL"] = url
    return url


@pytest.fixture(scope="session", autouse=True)
def run_migrations(db_url: str):
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url.replace("+asyncpg", ""))
    command.upgrade(cfg, "head")


@pytest.fixture(scope="session", autouse=True)
def _rebind_app_engine(db_url: str, run_migrations: None):
    """Point the app's DB engine at the test database.

    `src.db.session` creates its engine at import time using settings.database_url
    (which comes from .env). We swap it out here so FastAPI routes hit the test
    DB instead of the developer's dev DB.
    """
    original_engine = db_session.engine
    original_sessionmaker = db_session.async_session

    # NullPool: never cache connections across requests. Each request opens
    # and closes its own asyncpg connection. This sidesteps the
    # "another operation is in progress" errors that happen when a pooled
    # connection is reused across pytest-asyncio's per-test event loops.
    test_engine = create_async_engine(db_url, future=True, echo=False, poolclass=NullPool)
    test_sessionmaker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    db_session.engine = test_engine
    db_session.async_session = test_sessionmaker

    yield

    db_session.engine = original_engine
    db_session.async_session = original_sessionmaker


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
