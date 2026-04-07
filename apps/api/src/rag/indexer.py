import os
from pathlib import Path

from llama_index.embeddings.ollama import OllamaEmbedding

from src.config import settings
from src.rag.chunkers import chunk_markdown, chunk_python_file


def get_embed_model() -> OllamaEmbedding:
    return OllamaEmbedding(
        model_name=settings.echo_embed_model,
        base_url=settings.ollama_base_url,
    )


def scan_files(
    root: str, extensions: set[str] | None = None
) -> list[Path]:
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


if __name__ == "__main__":
    chunks = run_indexing(".")
    print(f"Indexed {len(chunks)} chunks from codebase")  # noqa: T201
    for chunk in chunks[:5]:
        loc = f"{chunk['file_path']}:{chunk['start_line']}-{chunk['end_line']}"
        print(f"  - {loc} ({chunk['chunk_type']})")  # noqa: T201
