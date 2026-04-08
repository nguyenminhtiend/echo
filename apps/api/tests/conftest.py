import os

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_OLLAMA_TESTS") == "1":
        return
    skip_ollama = pytest.mark.skip(reason="set RUN_OLLAMA_TESTS=1 to run")
    for item in items:
        if "ollama" in item.keywords:
            item.add_marker(skip_ollama)
