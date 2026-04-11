"""Unified LLM gateway: PII scrubbing, rate limits, cost tracking, audit logging."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

import litellm
import structlog

from src.config import settings
from src.gateway.rate_limiter import RateLimiter
from src.gateway.scrubber import scrub_all
from src.gateway.tracker import LLMUsage, get_cost_tracker

log = structlog.get_logger()

_rate_limiter = RateLimiter()


def _estimate_tokens(text: str) -> int:
    return max(128, len(text) // 4)


def _scrub_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in messages:
        m2 = dict(m)
        c = m2.get("content")
        if isinstance(c, str):
            m2["content"] = scrub_all(c)
        out.append(m2)
    return out


def _content_from_choice(resp: Any) -> str:
    choice = resp.choices[0]
    msg = getattr(choice, "message", None)
    if msg is not None:
        c = getattr(msg, "content", None)
        if isinstance(c, str):
            return c
    return ""


def _usage_from_response(resp: Any) -> tuple[int, int]:
    usage = getattr(resp, "usage", None)
    if usage is None:
        return 0, 0
    tin = getattr(usage, "prompt_tokens", None)
    tout = getattr(usage, "completion_tokens", None)
    if tin is None and isinstance(usage, dict):
        tin = usage.get("prompt_tokens")
    if tout is None and isinstance(usage, dict):
        tout = usage.get("completion_tokens")
    return int(tin or 0), int(tout or 0)


@dataclass
class GatewayLLMResult:
    content: str
    tokens_in: int
    tokens_out: int
    cost: float
    model: str
    duration_ms: int = 0
    error: str | None = None
    input_hash: str | None = None


async def gateway_llm_call(
    messages: list[dict[str, Any]],
    *,
    user_id: str | None = None,
    run_id: str | None = None,
    max_tokens: int | None = None,
    temperature: float = 0.2,
) -> GatewayLLMResult:
    """Scrub prompts, enforce rate limits, call LiteLLM, record usage and audit."""
    scrubbed = _scrub_messages(messages)
    raw_for_hash = "\n".join(
        str(m.get("content", "")) for m in scrubbed if isinstance(m.get("content"), str)
    )
    input_hash = hashlib.sha256(raw_for_hash.encode()).hexdigest()[:16]

    uid = user_id or "anonymous"
    est = _estimate_tokens(raw_for_hash)
    if not _rate_limiter.check(uid, est):
        log.warning("gateway_rate_limited", user_id=uid, estimated_tokens=est)
        return GatewayLLMResult(
            content="Rate limit exceeded. Try again in a minute.",
            tokens_in=0,
            tokens_out=0,
            cost=0.0,
            model=settings.echo_llm_model,
            error="rate_limited",
            input_hash=input_hash,
        )

    model = settings.echo_llm_model
    t0 = time.perf_counter()
    try:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": scrubbed,
            "api_key": settings.openrouter_api_key.get_secret_value(),
            "extra_headers": {
                "HTTP-Referer": "https://github.com/echo-platform/echo",
                "X-Title": settings.echo_llm_app_name,
            },
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        resp = await litellm.acompletion(**kwargs)
        content = _content_from_choice(resp)
        tokens_in, tokens_out = _usage_from_response(resp)
        duration_ms = int((time.perf_counter() - t0) * 1000)

        cost = float(
            getattr(resp, "_hidden_params", {}).get("response_cost")
            or litellm.completion_cost(completion_response=resp)
            or 0.0
        )
        get_cost_tracker().record(
            LLMUsage(
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost,
                user_id=uid,
                run_id=run_id,
            )
        )
        _rate_limiter.record(uid, tokens_in + tokens_out)

        log.info(
            "llm_call",
            user_id=uid,
            run_id=run_id,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            input_hash=input_hash,
            duration_ms=duration_ms,
        )

        return GatewayLLMResult(
            content=content,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            model=model,
            duration_ms=duration_ms,
            input_hash=input_hash,
        )
    except Exception:
        log.exception("gateway_llm_call_failed", user_id=uid, run_id=run_id, model=model)
        duration_ms = int((time.perf_counter() - t0) * 1000)
        return GatewayLLMResult(
            content=(
                "[LLM unavailable] The model could not be reached. "
                "Check OPENROUTER_API_KEY and network connectivity, or set ECHO_DRY_RUN=1."
            ),
            tokens_in=0,
            tokens_out=0,
            cost=0.0,
            model=model,
            duration_ms=duration_ms,
            error="llm_error",
            input_hash=input_hash,
        )
