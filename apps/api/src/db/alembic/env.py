import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.models.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# pgvector's ``vector`` type isn't mapped in the SQLAlchemy ORM, so
# autogenerate otherwise thinks the ``embedding`` columns are drift and
# produces spurious "Detected removed column" diffs. Filter them out.
_PGVECTOR_COLUMNS = {
    ("rag_chunks", "embedding"),
    ("graph_nodes", "embedding"),
}


def _include_object(object_, name, type_, reflected, compare_to):  # type: ignore[no-untyped-def]
    if type_ == "column" and (object_.table.name, name) in _PGVECTOR_COLUMNS:
        return False
    return not (type_ == "index" and name == "idx_rag_chunks_embedding")


def _resolved_url() -> str:
    """Use the sqlalchemy.url alembic main option if it was set by the caller
    (e.g. the integration-test conftest), otherwise fall back to the app
    settings. This lets tests point alembic at a throwaway DB without touching
    the developer's .env-configured DATABASE_URL.
    """
    override = config.get_main_option("sqlalchemy.url")
    return override or settings.database_url


def run_migrations_offline():
    context.configure(
        url=_resolved_url(),
        target_metadata=target_metadata,
        include_object=_include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=_include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    url = _resolved_url()
    if "+asyncpg" not in url and url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    connectable = create_async_engine(url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
