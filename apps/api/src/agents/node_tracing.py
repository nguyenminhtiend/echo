"""Helpers for emitting structured trace entries from agent nodes."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from contextlib import contextmanager


class NodeTimer:
    """Context manager that tracks agent node execution time."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.start: float = 0
        self.elapsed_ms: int = 0

    def __enter__(self) -> "NodeTimer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *_exc) -> None:
        self.elapsed_ms = int((time.perf_counter() - self.start) * 1000)


def agent_start_entry(agent: str, data: dict | None = None) -> dict:
    return {"agent": agent, "event_type": "agent_start", "data": data or {}}


def agent_end_entry(agent: str, duration_ms: int, data: dict | None = None) -> dict:
    return {
        "agent": agent,
        "event_type": "agent_end",
        "data": data or {},
        "duration_ms": duration_ms,
    }


def llm_start_entry(agent: str, data: dict | None = None) -> dict:
    return {"agent": agent, "event_type": "llm_start", "data": data or {}}


def llm_end_entry(
    agent: str,
    *,
    model: str = "ollama/gemma4:8b",
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost: float = 0.0,
    duration_ms: int = 0,
    data: dict | None = None,
) -> dict:
    d = {
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost": cost,
        **(data or {}),
    }
    return {"agent": agent, "event_type": "llm_end", "data": d, "duration_ms": duration_ms}
