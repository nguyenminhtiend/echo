import os

import httpx
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.ollama]

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


async def test_ollama_tags_lists_required_models():
    async with httpx.AsyncClient(base_url=OLLAMA, timeout=10) as c:
        r = await c.get("/api/tags")
    assert r.status_code == 200
    names = {m["name"].split(":")[0] for m in r.json().get("models", [])}
    assert "gemma4" in names, f"gemma4 not pulled; got {names}"
    assert "nomic-embed-text" in names, f"nomic-embed-text not pulled; got {names}"


async def test_ollama_embed_returns_768_dim():
    async with httpx.AsyncClient(base_url=OLLAMA, timeout=60) as c:
        r = await c.post(
            "/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": "hello world"},
        )
    assert r.status_code == 200
    vec = r.json()["embedding"]
    assert len(vec) == 768


async def test_ollama_chat_responds():
    async with httpx.AsyncClient(base_url=OLLAMA, timeout=120) as c:
        r = await c.post(
            "/api/chat",
            json={
                "model": "gemma4:8b",
                "messages": [{"role": "user", "content": "Reply with the single word: pong"}],
                "stream": False,
            },
        )
    assert r.status_code == 200
    content = r.json()["message"]["content"].lower()
    assert "pong" in content
