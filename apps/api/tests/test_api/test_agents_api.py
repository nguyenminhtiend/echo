import pytest


@pytest.mark.asyncio
async def test_create_agent_run(client):
    response = await client.post("/api/agents/runs", json={"task": "Fix the login bug"})
    assert response.status_code == 201
    data = response.json()
    assert data["task"] == "Fix the login bug"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_agent_runs(client):
    response = await client.get("/api/agents/runs")
    assert response.status_code == 200
    data = response.json()
    assert "runs" in data
    assert "total" in data
