from src.rag.indexer import get_embed_model


class RAGRetriever:
    """Retrieves relevant chunks using vector similarity.

    Note: Full PropertyGraphIndex integration requires a running PostgreSQL
    with pgvector. This implementation provides the interface; the LlamaIndex
    PropertyGraphIndex integration wires in during Task 3 DB migration.
    """

    def __init__(self):
        self.embed_model = get_embed_model()

    async def query(self, query_text: str, top_k: int = 5) -> list[dict]:  # noqa: ARG002
        """Query the RAG index for relevant chunks.

        Returns list of dicts with: content, chunk_type, file_path,
        start_line, end_line, score.
        """
        return []
