import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


async def test_create_run_returns_payload(client: AsyncClient):
    # NOTE: /api/agents endpoint is currently a stub (no DB persistence).
    # This test locks in the current contract; once persistence lands,
    # extend it to assert the row exists in agent_runs and that list/get surface it.
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


async def test_get_trace_missing_returns_404(client: AsyncClient):
    r = await client.post("/api/agents/runs", json={"task": "noop"})
    run_id = r.json()["id"]
    r2 = await client.get(f"/api/traces/{run_id}")
    # Stub currently 404s; update once traces are persisted.
    assert r2.status_code == 404
