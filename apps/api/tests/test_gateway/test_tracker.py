import uuid

import pytest

from src.gateway.tracker import CostTracker, LLMUsage


def test_track_usage():
    tracker = CostTracker()
    usage = LLMUsage(
        model="ollama/gemma4:8b",
        tokens_in=100,
        tokens_out=50,
        cost=0.0,
        user_id="test-user",
        run_id="test-run",
    )
    tracker.record(usage)
    assert len(tracker.entries) == 1
    assert tracker.entries[0].model == "ollama/gemma4:8b"


def test_total_cost():
    tracker = CostTracker()
    tracker.record(LLMUsage(model="m1", tokens_in=10, tokens_out=5, cost=0.001))
    tracker.record(LLMUsage(model="m2", tokens_in=20, tokens_out=10, cost=0.002))
    assert tracker.total_cost == 0.003


def test_total_tokens():
    tracker = CostTracker()
    tracker.record(LLMUsage(model="m1", tokens_in=100, tokens_out=50, cost=0.0))
    assert tracker.total_tokens == 150


@pytest.mark.asyncio
async def test_flush_writes_rows_and_clears():
    from unittest.mock import MagicMock

    from sqlalchemy.ext.asyncio import AsyncSession

    tracker = CostTracker()
    rid = uuid.uuid4()
    uid = uuid.uuid4()
    tracker.record(
        LLMUsage(
            model="ollama/gemma4:8b",
            tokens_in=10,
            tokens_out=5,
            cost=0.0,
            user_id=str(uid),
            run_id=str(rid),
        )
    )
    session = MagicMock(spec=AsyncSession)
    session.add = MagicMock()
    n = await tracker.flush(session, user_id=uid, run_id=rid)
    assert n == 1
    assert tracker.entries == []
    session.add.assert_called_once()
