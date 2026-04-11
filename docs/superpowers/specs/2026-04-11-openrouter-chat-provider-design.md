# OpenRouter Chat Provider Refactor

**Date:** 2026-04-11
**Status:** Design
**Owner:** Tien Nguyen

## Problem

Local chat inference via Ollama (`gemma4:8b`) has become too slow for day-to-day multi-agent runs. The LangGraph orchestrator spawns coder/reviewer/qa/security/docs/architect nodes that each make LLM calls, and waiting on a local 8B model for each one makes the feedback loop unusable.

The user has signed up for OpenRouter and wants chat generation to move to a hosted provider while keeping the rest of the gateway (PII scrubbing, rate limiting, cost tracking, audit logging) unchanged.

## Goals

1. Replace Ollama chat inference with OpenRouter via the existing LiteLLM gateway.
2. Default to `openrouter/free` as the single model for all agents.
3. Record real cost per call (currently hardcoded to `0.0`).
4. Keep the `GatewayLLMResult` surface and the rate limiter/scrubber/audit pipeline unchanged so agent nodes need no edits.
5. Fail fast at startup if the API key is missing, except in `ECHO_DRY_RUN` mode.

## Non-Goals

- Per-agent model routing. Config shape allows it later; no code in this refactor.
- Streaming responses (`litellm.acompletion_stream`). Still using `acompletion`.
- Multi-provider fallback (Ollama-as-backup-for-OpenRouter).
- A live integration test that calls real OpenRouter in CI.
- Replacing Ollama for embeddings — see "Design Decision: Embeddings" below.

## Design Decision: Embeddings stay on Ollama

OpenRouter exposes chat/completion models only — no embeddings endpoint. The RAG pipeline (`src/rag/indexer.py`) depends on a 768-dim embedding vector from `nomic-embed-text`, and the `rag_chunks.embedding` column is `vector(768)`.

Options considered:
- **Switch embeddings to a cloud provider (OpenAI/Voyage/Cohere):** requires a second API key, per-index-run costs, and a database migration to change the vector dimension.
- **Drop RAG:** breaks the retriever.
- **Keep Ollama for embeddings only (chosen):** the slowness complaint is about chat inference, not embeddings. Embeddings are fast on CPU, free, and require no migration.

Consequence: the `ollama_base_url` and `echo_embed_model` settings remain. The `llama-index-embeddings-ollama` dependency stays in `pyproject.toml`. This is a deliberate narrow scope — we are replacing chat, not Ollama wholesale.

## Design Decision: Single default model

`echo_llm_model` is one string. All agents use the same model for now.

Rationale:
- Simpler config, traces, and cost attribution.
- No real-workload data yet on which agents actually need cheaper tiers.
- The config key is already set up so adding per-agent overrides later (e.g. `ECHO_LLM_MODEL_CODER=...`) is a code change of <10 lines if/when needed.

Chosen default: `openrouter/free`. Sweet spot for code agents, well-supported by LiteLLM, OpenRouter returns real cost in the response, cost is reasonable (~$3/M in, $15/M out).

## Tech Approach

OpenRouter is natively supported by LiteLLM via the `openrouter/` model prefix. The existing gateway (`src/gateway/middleware.py`) already uses `litellm.acompletion`, so the core change is:

1. Remove the `_normalize_ollama_model()` prefix hack and the `api_base` override — LiteLLM resolves OpenRouter from the model string and the `api_key` kwarg.
2. Inject the API key and OpenRouter analytics headers.
3. Extract real cost from `resp._hidden_params["response_cost"]` (or `litellm.completion_cost(resp)` as a fallback).

The rate limiter, PII scrubber, audit logging, and `GatewayLLMResult` dataclass do not change. Agent nodes (`coder.py`, `reviewer.py`, etc.) do not change — they already call `gateway_llm_call()` and read from the result.

## File-Level Changes

### `apps/api/src/config.py`

Add `openrouter_api_key: SecretStr` (required, no default — fails fast on startup if missing). Add `echo_llm_app_name: str = "echo"` for the OpenRouter `X-Title` header. Change `echo_llm_model` default to `"openrouter/free"`. Add defaults for `ollama_base_url` and `echo_embed_model` so only `DATABASE_URL`, `SECRET_KEY`, and `OPENROUTER_API_KEY` are strictly required.

### `apps/api/src/gateway/router.py`

In `create_llm_router()`, drop the `api_base` param from `litellm_params`. Add `api_key=settings.openrouter_api_key.get_secret_value()`.

### `apps/api/src/gateway/middleware.py`

- **Delete** `_normalize_ollama_model()` and all call sites.
- In `gateway_llm_call()`:
  - `model = settings.echo_llm_model` (no prefix massaging).
  - Replace `api_base` kwarg with `api_key` + `extra_headers` (`HTTP-Referer`, `X-Title`).
  - Replace `cost = 0.0` with real extraction:
    ```python
    cost = float(
        getattr(resp, "_hidden_params", {}).get("response_cost")
        or litellm.completion_cost(completion_response=resp)
        or 0.0
    )
    ```
- Update the error-path fallback message from "Check Ollama or set ECHO_DRY_RUN=1" to "Check OPENROUTER_API_KEY and network connectivity, or set ECHO_DRY_RUN=1."

### `apps/api/src/rag/indexer.py`

**No functional changes.** `OllamaEmbedding` continues pointing at `settings.ollama_base_url` and `settings.echo_embed_model`. Documented here as a deliberate non-change for the reviewer.

### `apps/api/src/agents/node_tracing.py`

Change the hardcoded `model: str = "ollama/gemma4:8b"` default in `llm_end_entry()` to `model: str | None = None`, and in the body use `model or settings.echo_llm_model`. All real call sites pass `model=` explicitly, so this is a safety net only.

### `apps/api/src/agents/runner.py`

Line ~273: change `data.get("model", "ollama/gemma4:8b")` to `data.get("model", settings.echo_llm_model)`. Import `settings` if not already imported.

### Sweep for stray hardcoded model strings

During implementation, run `grep -rn 'ollama/gemma4:8b' apps/api/src apps/api/tests` and fix any remaining hits not listed above.

### `.env.example`

Split the env file into clearly labeled sections. Replace the current single "Ollama" section with:

```
# Chat LLM (OpenRouter)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
ECHO_LLM_MODEL=openrouter/free

# Embeddings (local Ollama)
OLLAMA_BASE_URL=http://localhost:11434
ECHO_EMBED_MODEL=nomic-embed-text:latest
```

### `apps/api/tests/conftest.py`

Set env defaults for the new variables:
```python
os.environ.setdefault("OPENROUTER_API_KEY", "sk-or-test-key-not-real")
os.environ.setdefault("ECHO_LLM_MODEL", "openrouter/free")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ.setdefault("ECHO_EMBED_MODEL", "nomic-embed-text:latest")
```
`ECHO_DRY_RUN=1` is already set, so no real network calls occur.

### `apps/api/tests/test_gateway/test_tracker.py`

Replace the two `"ollama/gemma4:8b"` string literals with `"openrouter/free"`. No logic change.

### `apps/api/tests/integration/test_ollama_smoke.py` → rename to `test_ollama_embed_smoke.py`

- `test_ollama_tags_lists_required_models`: remove the `"gemma4" in names` assertion; keep `"nomic-embed-text" in names`.
- `test_ollama_embed_returns_768_dim`: unchanged.
- `test_ollama_chat_responds`: **delete**.

### `CLAUDE.md`

Three edits:
1. **Core Principles** — remove "Local-first: Runs entirely on developer machines via Ollama" and "Privacy by default: Gemma 4 8B — code never leaves the machine". Replace with "Provider-agnostic LiteLLM gateway: chat via OpenRouter (Claude Sonnet 4.5), embeddings via local Ollama (nomic-embed-text)".
2. **Tech Stack → Infrastructure → LLM line** — change to: "OpenRouter (chat: anthropic/claude-sonnet-4.5) + Ollama (embeddings only: nomic-embed-text, 768 dim)".
3. **Architecture diagram** — change the bottom `Ollama (localhost:11434)` box to two boxes: `OpenRouter API (chat)` and `Ollama (embeddings only)`.

## Error Handling

- **Missing `OPENROUTER_API_KEY` at startup:** Pydantic raises `ValidationError` on import of `src.config`. Uvicorn exits with a clear error. Acceptable — the app cannot function without it.
- **Missing key in `ECHO_DRY_RUN=1` mode:** `conftest.py` sets a dummy key; tests never reach `litellm.acompletion`. Real dry-run runs would also set a dummy key via `.env`.
- **OpenRouter 401/403/429/5xx or network error:** caught by the existing `try/except Exception` in `gateway_llm_call()`. Returns a `GatewayLLMResult` with `error="llm_error"` and the updated human-readable fallback content. Same behavior as today, different error message.
- **`response_cost` missing from response:** `litellm.completion_cost(resp)` computes from the usage × pricing table. If that also fails, cost records as `0.0` — same as today, never raises.

## Testing Strategy

- **Unit tests** (`apps/api/tests/`): all pass with the new defaults via `conftest.py` and `ECHO_DRY_RUN=1`. No real network calls.
- **`test_tracker.py`**: updated to assert the new model string.
- **Integration tests** (`test_ollama_embed_smoke.py`): verifies the embeddings path still works end-to-end against local Ollama. Gated by `RUN_OLLAMA_TESTS=1` as today.
- **Manual smoke test before merging:**
  1. Set `OPENROUTER_API_KEY` in `.env`.
  2. `mise run dev` — verify API boots without errors.
  3. Kick off one agent run from the web UI or via `POST /api/agents/runs`.
  4. Verify the run completes, traces show `model=openrouter/free`, and `total_cost > 0`.
  5. Check OpenRouter dashboard shows the request under the `echo` app name.
- **No live OpenRouter CI test** — would require a real key in CI. Out of scope.

## Rollout

Single commit / single PR. No feature flag, no gradual rollout — this is a solo project and the Ollama chat path is being removed outright. Anyone who pulls needs to add `OPENROUTER_API_KEY` to their `.env`; `.env.example` documents it.

## Open Questions

None. All decisions resolved during brainstorming:
- Scope: full replacement of Ollama chat (embeddings stay).
- Embeddings: stay on Ollama.
- Default model: `openrouter/free`, single model for all agents.
- Cost tracking: real extraction via LiteLLM.
- API key: `SecretStr` in Settings, fail-fast at startup.
