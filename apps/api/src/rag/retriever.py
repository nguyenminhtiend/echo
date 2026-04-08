from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import text

from src.config import settings
from src.rag.indexer import get_embed_model

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in embedding) + "]"


class RAGRetriever:
    """Retrieves relevant chunks using pgvector cosine distance."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self.embed_model = get_embed_model()

    async def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        """Return chunks scored by ``1 - cosine_distance`` (higher is more similar)."""
        if settings.echo_dry_run:
            return []

        q_emb = await self.embed_model.aget_query_embedding(query_text)
        emb_lit = _vector_literal(q_emb)
        stmt = text(
            """
            SELECT
                content,
                chunk_type,
                file_path,
                start_line,
                end_line,
                embedding <=> CAST(:q AS vector) AS distance
            FROM rag_chunks
            ORDER BY distance
            LIMIT :top_k
            """
        )
        result = await self._session.execute(stmt, {"q": emb_lit, "top_k": top_k})
        out: list[dict] = []
        for row in result.mappings():
            dist = float(row["distance"])
            out.append(
                {
                    "content": row["content"],
                    "chunk_type": row["chunk_type"],
                    "file_path": row["file_path"],
                    "start_line": row["start_line"],
                    "end_line": row["end_line"],
                    "score": 1.0 - dist,
                }
            )
        return out
