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
