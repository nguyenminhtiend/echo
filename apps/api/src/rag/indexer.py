from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from llama_index.embeddings.ollama import OllamaEmbedding
from sqlalchemy import text

from src.config import settings
from src.db.session import async_session
from src.rag.chunkers import chunk_markdown, chunk_python_file

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

EMBED_BATCH_SIZE = 50


def get_embed_model() -> OllamaEmbedding:
    return OllamaEmbedding(
        model_name=settings.echo_embed_model,
        base_url=settings.ollama_base_url,
        embed_batch_size=EMBED_BATCH_SIZE,
    )


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in embedding) + "]"


async def write_chunks_to_db(
    session: AsyncSession,
    chunks: list[dict],
    embed_model: OllamaEmbedding,
) -> int:
    """Clear ``rag_chunks``, embed chunk texts, and insert rows with vectors."""
    await session.execute(text("DELETE FROM rag_chunks"))
    usable = [c for c in chunks if c.get("content", "").strip()]
    if not usable:
        return 0

    inserted = 0
    for i in range(0, len(usable), EMBED_BATCH_SIZE):
        batch = usable[i : i + EMBED_BATCH_SIZE]
        texts = [c["content"] for c in batch]
        embeddings = await embed_model.aget_text_embedding_batch(texts)
        for chunk, emb in zip(batch, embeddings, strict=True):
            meta = chunk.get("metadata")
            meta_json: str | None = None if meta is None else json.dumps(meta)
            await session.execute(
                text(
                    """
                    INSERT INTO rag_chunks (
                        id, content, embedding,
                        chunk_type, file_path, start_line, end_line, metadata
                    )
                    VALUES (
                        CAST(:id AS uuid),
                        :content,
                        CAST(:embedding AS vector),
                        :chunk_type,
                        :file_path,
                        :start_line,
                        :end_line,
                        CAST(:metadata AS jsonb)
                    )
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "content": chunk["content"],
                    "embedding": _vector_literal(emb),
                    "chunk_type": chunk.get("chunk_type"),
                    "file_path": chunk.get("file_path"),
                    "start_line": chunk.get("start_line"),
                    "end_line": chunk.get("end_line"),
                    "metadata": meta_json,
                },
            )
            inserted += 1
    return inserted


def scan_files(root: str, extensions: set[str] | None = None) -> list[Path]:
    """Recursively find files with matching extensions, skipping hidden dirs and node_modules."""
    if extensions is None:
        extensions = {".py", ".ts", ".tsx", ".md"}
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".") and d != "node_modules" and d != "__pycache__"
        ]
        files.extend(Path(dirpath) / f for f in filenames if Path(f).suffix in extensions)
    return files


def chunk_file(file_path: Path) -> list[dict]:
    """Chunk a file based on its extension."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    if not content.strip():
        return []

    suffix = file_path.suffix
    if suffix == ".py":
        return chunk_python_file(content, str(file_path))
    if suffix == ".md":
        return chunk_markdown(content, str(file_path))
    return [
        {
            "content": content,
            "chunk_type": "file",
            "file_path": str(file_path),
            "start_line": 1,
            "end_line": content.count("\n") + 1,
        }
    ]


def run_indexing(root: str = ".") -> list[dict]:
    """Run the full indexing pipeline on the given root directory."""
    files = scan_files(root)
    all_chunks = []
    for f in files:
        all_chunks.extend(chunk_file(f))
    return all_chunks


async def _run_index_cli_async() -> None:
    root = settings.codebase_root or "."
    chunks = run_indexing(root)
    print(f"Found {len(chunks)} chunks under {root!r}")  # noqa: T201

    if settings.echo_dry_run:
        for chunk in chunks[:5]:
            loc = f"{chunk['file_path']}:{chunk['start_line']}-{chunk['end_line']}"
            print(f"  - {loc} ({chunk['chunk_type']})")  # noqa: T201
        print("ECHO_DRY_RUN=1: skipping embeddings and database write.")  # noqa: T201
        return

    embed_model = get_embed_model()
    async with async_session() as session:
        n = await write_chunks_to_db(session, chunks, embed_model)
        await session.commit()
    print(f"Indexed {n} chunks into rag_chunks (embeddings + pgvector).")  # noqa: T201


def main() -> None:
    asyncio.run(_run_index_cli_async())


if __name__ == "__main__":
    main()
