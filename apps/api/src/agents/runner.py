"""Orchestrates LangGraph execution, trace emission, and DB persistence."""

from __future__ import annotations

import asyncio
import hashlib
import time
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import structlog
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import select

from src.agents.graph import build_graph
from src.agents.state import EchoState, TaskComplexity, TaskType
from src.agents.supervisor import classify_task
from src.db.session import async_session
from src.models.agent_run import AgentRun
from src.models.audit_log import AuditLog
from src.models.cost_ledger import CostLedger
from src.models.trace_event import TraceEvent

log = structlog.get_logger()

_trace_queues: dict[str, asyncio.Queue[dict]] = {}
_hitl_queues: dict[str, asyncio.Queue[dict]] = {}


def ensure_queues(run_id: str) -> tuple[asyncio.Queue[dict], asyncio.Queue[dict]]:
    if run_id not in _trace_queues:
        _trace_queues[run_id] = asyncio.Queue()
    if run_id not in _hitl_queues:
        _hitl_queues[run_id] = asyncio.Queue()
    return _trace_queues[run_id], _hitl_queues[run_id]


def get_trace_queue(run_id: str) -> asyncio.Queue[dict] | None:
    return _trace_queues.get(run_id)


def get_hitl_queue(run_id: str) -> asyncio.Queue[dict] | None:
    return _hitl_queues.get(run_id)


def cleanup_queues(run_id: str) -> None:
    _trace_queues.pop(run_id, None)
    _hitl_queues.pop(run_id, None)


async def _emit(run_id: str, event: dict) -> None:
    q = _trace_queues.get(run_id)
    if q is not None:
        await q.put(event)


async def _persist_trace(
    db_session,
    *,
    run_id: uuid.UUID,
    event_type: str,
    agent_name: str | None = None,
    data: dict | None = None,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    cost: Decimal | None = None,
    duration_ms: int | None = None,
) -> TraceEvent:
    te = TraceEvent(
        id=uuid.uuid4(),
        run_id=run_id,
        event_type=event_type,
        agent_name=agent_name,
        data=data or {},
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost=cost,
        duration_ms=duration_ms,
    )
    db_session.add(te)
    return te


async def _persist_cost(
    db_session,
    *,
    run_id: uuid.UUID,
    model: str,
    tokens_in: int,
    tokens_out: int,
    cost: Decimal,
) -> None:
    db_session.add(
        CostLedger(
            id=uuid.uuid4(),
            run_id=run_id,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
        )
    )


async def _persist_audit(
    db_session,
    *,
    action: str,
    resource: str | None = None,
    metadata: dict | None = None,
) -> None:
    db_session.add(
        AuditLog(
            id=uuid.uuid4(),
            action=action,
            resource=resource,
            metadata_=metadata,
        )
    )


class AgentRunner:
    @staticmethod
    async def execute(run_id: uuid.UUID) -> None:  # noqa: C901
        rid = str(run_id)
        trace_q, hitl_q = ensure_queues(rid)
        start = time.perf_counter()
        total_tokens_in = 0
        total_tokens_out = 0
        total_cost = Decimal("0")

        try:
            async with async_session() as db:
                run = (await db.execute(select(AgentRun).where(AgentRun.id == run_id))).scalar_one()

                run.status = "running"
                await db.commit()

                await _emit(rid, {"type": "run_start", "run_id": rid, "status": "running"})

                task_type = classify_task(run.task)
                initial_state: EchoState = {
                    "task": run.task,
                    "task_type": task_type,
                    "complexity": TaskComplexity.SIMPLE,
                    "messages": [],
                    "artifacts": [],
                    "reviews": [],
                    "trace": [],
                    "current_agent": "supervisor",
                    "iteration": 0,
                    "max_iterations": 10,
                }

                checkpointer = MemorySaver()
                graph = build_graph(checkpointer=checkpointer)
                config = {"configurable": {"thread_id": rid}}

                async for chunk in graph.astream(initial_state, config=config):
                    for node_name, node_output in chunk.items():
                        if node_name == "__interrupt__":
                            event = {
                                "type": "hitl_request",
                                "run_id": rid,
                                "data": node_output,
                            }
                            await _emit(rid, event)
                            await _persist_trace(
                                db,
                                run_id=run_id,
                                event_type="hitl_request",
                                data={"interrupt": str(node_output)},
                            )

                            run.status = "hitl_waiting"
                            await db.commit()

                            try:
                                hitl_resp = await asyncio.wait_for(hitl_q.get(), timeout=300)
                            except asyncio.TimeoutError:
                                hitl_resp = {"action": "approve"}

                            await _emit(rid, {"type": "hitl_response", "data": hitl_resp})

                            from langgraph.types import Command

                            async for resume_chunk in graph.astream(
                                Command(resume=True), config=config
                            ):
                                for rn, ro in resume_chunk.items():
                                    if rn != "__interrupt__":
                                        await _process_node_output(db, run_id, rid, rn, ro)
                            continue

                        tok_in, tok_out, c = await _process_node_output(
                            db, run_id, rid, node_name, node_output
                        )
                        total_tokens_in += tok_in
                        total_tokens_out += tok_out
                        total_cost += c

                elapsed_ms = int((time.perf_counter() - start) * 1000)
                run.status = "completed"
                run.total_tokens = total_tokens_in + total_tokens_out
                run.total_cost = total_cost
                run.duration_ms = elapsed_ms
                run.completed_at = datetime.now(UTC)
                await db.commit()

                await _emit(
                    rid,
                    {
                        "type": "run_complete",
                        "run_id": rid,
                        "status": "completed",
                        "total_tokens": run.total_tokens,
                        "total_cost": str(run.total_cost),
                        "duration_ms": elapsed_ms,
                    },
                )

        except Exception:
            log.exception("agent_run_failed", run_id=rid)
            try:
                async with async_session() as db:
                    run = (
                        await db.execute(select(AgentRun).where(AgentRun.id == run_id))
                    ).scalar_one()
                    run.status = "failed"
                    run.duration_ms = int((time.perf_counter() - start) * 1000)
                    run.completed_at = datetime.now(UTC)
                    await db.commit()
            except Exception:
                log.exception("failed_to_update_run_status", run_id=rid)

            await _emit(rid, {"type": "run_failed", "run_id": rid, "status": "failed"})
        finally:
            await _emit(rid, {"type": "stream_end", "run_id": rid})


async def _process_node_output(
    db, run_id: uuid.UUID, rid: str, node_name: str, node_output: dict
) -> tuple[int, int, Decimal]:
    tok_in = 0
    tok_out = 0
    cost = Decimal("0")

    trace_entries = node_output.get("trace", [])
    for entry in trace_entries:
        event_type = entry.get("event_type", "unknown")
        agent = entry.get("agent", node_name)
        data = entry.get("data", {})
        duration_ms = entry.get("duration_ms")
        e_tok_in = data.get("tokens_in", 0) or 0
        e_tok_out = data.get("tokens_out", 0) or 0
        e_cost = Decimal(str(data.get("cost", 0) or 0))

        tok_in += e_tok_in
        tok_out += e_tok_out
        cost += e_cost

        te = await _persist_trace(
            db,
            run_id=run_id,
            event_type=event_type,
            agent_name=agent,
            data=data,
            tokens_in=e_tok_in or None,
            tokens_out=e_tok_out or None,
            cost=e_cost or None,
            duration_ms=duration_ms,
        )

        ws_event = {
            "type": event_type,
            "agent_name": agent,
            "data": data,
            "duration_ms": duration_ms,
            "tokens_in": e_tok_in,
            "tokens_out": e_tok_out,
            "cost": str(e_cost),
            "created_at": te.created_at.isoformat() if te.created_at else None,
        }
        await _emit(rid, ws_event)

        if event_type == "llm_end" and e_tok_in + e_tok_out > 0:
            model = data.get("model", "ollama/gemma4:8b")
            await _persist_cost(
                db,
                run_id=run_id,
                model=model,
                tokens_in=e_tok_in,
                tokens_out=e_tok_out,
                cost=e_cost,
            )
            input_hash = hashlib.sha256(str(data.get("input", "")).encode()).hexdigest()[:16]
            await _persist_audit(
                db,
                action="llm_call",
                resource=model,
                metadata={
                    "run_id": rid,
                    "agent": agent,
                    "tokens_in": e_tok_in,
                    "tokens_out": e_tok_out,
                    "cost": str(e_cost),
                    "input_hash": input_hash,
                },
            )

    await db.commit()
    return tok_in, tok_out, cost
