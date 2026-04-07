from fastapi import APIRouter

from src.schemas.rag import RAGQueryRequest, RAGQueryResponse

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(body: RAGQueryRequest):
    # Stub: returns empty results until RAG pipeline integration
    return RAGQueryResponse(results=[], query=body.query)
