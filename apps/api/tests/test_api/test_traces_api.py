import pytest


@pytest.mark.asyncio
async def test_get_trace_returns_404_for_unknown_run(client):
    response = await client.get("/api/traces/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
