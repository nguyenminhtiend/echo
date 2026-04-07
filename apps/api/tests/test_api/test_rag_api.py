import pytest


@pytest.mark.asyncio
async def test_rag_query_endpoint_exists(client):
    response = await client.post("/api/rag/query", json={"query": "auth flow"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query" in data
