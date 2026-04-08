"""Shared helpers for agent nodes: config, dry-run, file/RAG tools, JSON parsing."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from langchain_core.runnables import RunnableConfig

from src.agents.state import CodeArtifact, TaskComplexity
from src.config import settings
from src.rag.retriever import RAGRetriever


def is_dry_run() -> bool:
    """True when LLM calls should be skipped (unit tests / CI)."""
    env = os.environ.get("ECHO_DRY_RUN", "").lower()
    if env in ("1", "true", "yes"):
        return True
    return bool(settings.echo_dry_run)


def configurable_ids(config: RunnableConfig | None) -> tuple[str | None, str | None]:
    """Return (user_id, run_id) strings from LangGraph RunnableConfig."""
    if not config:
        return None, None
    c = config.get("configurable") or {}
    uid = c.get("user_id")
    rid = c.get("thread_id") or c.get("run_id")
    return (str(uid) if uid is not None else None, str(rid) if rid is not None else None)


def max_tokens_for_complexity(complexity: TaskComplexity) -> int:
    if complexity == TaskComplexity.COMPLEX:
        return 4096
    if complexity == TaskComplexity.MODERATE:
        return 2048
    return 1536


def _safe_resolve_path(rel: str) -> Path:
    root = Path(settings.codebase_root or Path.cwd()).resolve()
    target = (root / rel).resolve()
    if not str(target).startswith(str(root)):
        msg = f"path escapes codebase root: {rel}"
        raise ValueError(msg)
    return target


def read_file_tool(path: str) -> str:
    """Read a UTF-8 text file from under the configured codebase root."""
    try:
        p = _safe_resolve_path(path)
        if not p.is_file():
            return f"[read_file] Not found: {path}"
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[read_file] Error: {e}"


async def rag_query_tool(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Query the RAG index (vector / graph retrieval)."""
    retriever = RAGRetriever()
    return await retriever.query(query_text=query, top_k=top_k)


def write_artifact_tool(file_path: str, content: str, action: str) -> CodeArtifact:
    """Build a CodeArtifact dict for graph state (does not write to disk)."""
    a = action.lower().strip()
    if a not in ("create", "modify", "delete"):
        a = "modify"
    return CodeArtifact(file_path=file_path, content=content, action=a)


def parse_json_loose(text: str) -> Any:
    """Parse JSON from model output, stripping optional ```json fences."""
    raw = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if m:
        raw = m.group(1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def user_block(task: str, extra: str | None = None) -> str:
    parts = [f"Task:\n{task}"]
    if extra:
        parts.append(extra)
    return "\n\n".join(parts)
