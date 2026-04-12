from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from src.db.session import get_db
from src.rag.retriever import RAGRetriever
from src.schemas.rag import RAGChunkResult, RAGQueryRequest, RAGQueryResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(
    body: RAGQueryRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    retriever = RAGRetriever(db)
    rows = await retriever.query(body.query, top_k=body.top_k)
    results = [
        RAGChunkResult(
            content=r["content"],
            chunk_type=r["chunk_type"],
            file_path=r["file_path"],
            start_line=r["start_line"],
            end_line=r["end_line"],
            score=r["score"],
        )
        for r in rows
    ]
    return RAGQueryResponse(results=results, query=body.query)
