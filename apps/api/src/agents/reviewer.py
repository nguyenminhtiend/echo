import time

from langchain_core.runnables import RunnableConfig

from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.prompts import REVIEWER_SYSTEM
from src.agents.state import EchoState, ReviewFinding
from src.agents.tools import (
    configurable_ids,
    is_dry_run,
    max_tokens_for_complexity,
    parse_json_loose,
    user_block,
)
from src.gateway.middleware import gateway_llm_call


def _artifacts_excerpt(state: EchoState) -> str | None:
    arts = state.get("artifacts") or []
    if not arts:
        return None
    lines: list[str] = []
    for a in arts[:5]:
        fp = a.get("file_path", "")
        content = (a.get("content") or "")[:1200]
        lines.append(f"--- {fp} ---\n{content}")
    return "\n\n".join(lines)


async def reviewer_node(state: EchoState, config: RunnableConfig | None = None) -> dict:
    """LangGraph node: code review via gateway LLM."""
    user_id, run_id = configurable_ids(config)
    with NodeTimer("reviewer") as timer:
        trace = [agent_start_entry("reviewer", {"task": state["task"]})]
        if is_dry_run():
            reviews: list[ReviewFinding] = [
                {
                    "severity": "info",
                    "message": "ECHO_DRY_RUN: no model output",
                    "file_path": None,
                    "line": None,
                }
            ]
            trace.append(llm_start_entry("reviewer", {"dry_run": True}))
            trace.append(
                llm_end_entry("reviewer", tokens_in=0, tokens_out=0, data={"dry_run": True})
            )
            trace.append(agent_end_entry("reviewer", timer.elapsed_ms))
            return {"current_agent": "reviewer", "trace": trace, "reviews": reviews}

        extra = _artifacts_excerpt(state)
        user_prompt = user_block(state["task"], extra)
        trace.append(llm_start_entry("reviewer", {"prompt": user_prompt[:2000]}))
        t_llm = time.perf_counter()
        result = await gateway_llm_call(
            [
                {"role": "system", "content": REVIEWER_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            user_id=user_id,
            run_id=run_id,
            max_tokens=max_tokens_for_complexity(state["complexity"]),
        )
        llm_duration = int((time.perf_counter() - t_llm) * 1000)

        parsed = parse_json_loose(result.content)
        reviews_out: list[ReviewFinding] = []
        raw = parsed.get("reviews") if isinstance(parsed, dict) else None
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                sev = str(item.get("severity", "info"))
                if sev not in ("info", "warning", "critical"):
                    sev = "info"
                line = item.get("line")
                reviews_out.append(
                    ReviewFinding(
                        severity=sev,
                        message=str(item.get("message", "")),
                        file_path=item.get("file_path"),
                        line=int(line) if isinstance(line, int) else None,
                    )
                )
        if not reviews_out:
            reviews_out = [
                ReviewFinding(
                    severity="info",
                    message=result.content[:2000] if result.content else "No structured findings.",
                    file_path=None,
                    line=None,
                )
            ]

        trace.append(
            llm_end_entry(
                "reviewer",
                model=result.model,
                tokens_in=result.tokens_in,
                tokens_out=result.tokens_out,
                cost=result.cost,
                duration_ms=llm_duration,
                data={"input_hash": result.input_hash, "error": result.error},
            )
        )
        trace.append(agent_end_entry("reviewer", timer.elapsed_ms))
    return {"current_agent": "reviewer", "trace": trace, "reviews": reviews_out}
