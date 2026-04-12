import uuid

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


async def test_create_run_returns_payload(client: AsyncClient):
    payload = {"task": "write a hello world function", "task_type": "code"}
    r = await client.post("/api/agents/runs", json=payload)
    assert r.status_code in (200, 201), r.text
    body = r.json()
    assert body["task"] == payload["task"]
    assert body["task_type"] == payload["task_type"]
    assert body["status"] == "pending"
    assert "id" in body


async def test_list_runs_returns_shape(client: AsyncClient):
    r = await client.get("/api/agents/runs")
    assert r.status_code == 200
    body = r.json()
    assert "runs" in body and "total" in body
    assert isinstance(body["runs"], list)


async def test_get_trace_for_unknown_run_returns_404(client: AsyncClient):
    unknown_id = uuid.uuid4()
    r = await client.get(f"/api/traces/{unknown_id}")
    assert r.status_code == 404


async def test_get_trace_for_existing_run_returns_empty_tree(client: AsyncClient):
    # With ECHO_SKIP_AGENT_RUNNER=1 the runner doesn't execute, so the run
    # exists but no trace_events rows have been written. The endpoint should
    # still return 200 with an empty events list.
    r = await client.post("/api/agents/runs", json={"task": "noop"})
    run_id = r.json()["id"]
    r2 = await client.get(f"/api/traces/{run_id}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["run_id"] == run_id
    assert body["events"] == []
