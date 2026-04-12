from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select, text

from src.models.rag import RagChunk
from src.rag.chunkers import chunk_python_file

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.integration

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_repo" / "sample.py"


def test_chunker_splits_by_function():
    chunks = chunk_python_file(FIXTURE.read_text(), str(FIXTURE))
    assert len(chunks) >= 2
    texts = [c["content"] for c in chunks]
    assert any("def add" in t for t in texts)
    assert any("def multiply" in t for t in texts)
    assert all(c["chunk_type"] == "function" for c in chunks)


async def test_rag_chunk_roundtrip(session: AsyncSession):
    # embedding is NOT NULL and not mapped on the ORM model; insert via SQL.
    zeros = "[" + ",".join(["0"] * 768) + "]"
    rid = (
        await session.execute(
            text(
                """
                INSERT INTO rag_chunks (
                    id, content, embedding, chunk_type, file_path, start_line, end_line, metadata
                )
                VALUES (
                    gen_random_uuid(),
                    :content,
                    CAST(:emb AS vector),
                    :chunk_type,
                    :file_path,
                    :start_line,
                    :end_line,
                    NULL
                )
                RETURNING id
                """
            ),
            {
                "content": "def add(a, b): return a + b",
                "emb": zeros,
                "chunk_type": "function",
                "file_path": str(FIXTURE),
                "start_line": 1,
                "end_line": 1,
            },
        )
    ).scalar_one()

    await session.commit()

    got = (await session.execute(select(RagChunk).where(RagChunk.id == rid))).scalar_one()
    assert got.file_path == str(FIXTURE)
    assert got.chunk_type == "function"


async def test_rag_chunks_embedding_column_is_vector_768(session: AsyncSession):
    # embedding column is raw pgvector (not mapped); verify the column exists
    # at the expected dimension via information_schema/pg_catalog.
    r = await session.execute(
        text(
            "SELECT format_type(a.atttypid, a.atttypmod) "
            "FROM pg_attribute a "
            "JOIN pg_class c ON a.attrelid = c.oid "
            "WHERE c.relname = 'rag_chunks' AND a.attname = 'embedding'"
        )
    )
    col_type = r.scalar_one_or_none()
    assert col_type is not None, "rag_chunks.embedding column missing"
    assert "vector" in col_type
