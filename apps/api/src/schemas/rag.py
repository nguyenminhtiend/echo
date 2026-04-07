from pydantic import BaseModel


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    include_graph: bool = True


class RAGChunkResult(BaseModel):
    content: str
    chunk_type: str | None
    file_path: str | None
    start_line: int | None
    end_line: int | None
    score: float


class RAGQueryResponse(BaseModel):
    results: list[RAGChunkResult]
    query: str
