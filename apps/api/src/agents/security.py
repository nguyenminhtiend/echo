import time

from langchain_core.runnables import RunnableConfig

from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.prompts import SECURITY_SYSTEM
from src.agents.state import EchoState, ReviewFinding
from src.agents.tools import (
    configurable_ids,
    is_dry_run,
    max_tokens_for_complexity,
    parse_json_loose,
    user_block,
)
from src.gateway.middleware import gateway_llm_call


async def security_node(state: EchoState, config: RunnableConfig | None = None) -> dict:
    """LangGraph node: security review via gateway LLM."""
    user_id, run_id = configurable_ids(config)
    with NodeTimer("security") as timer:
        trace = [agent_start_entry("security", {"task": state["task"]})]
        if is_dry_run():
            reviews: list[ReviewFinding] = [
                {
                    "severity": "info",
                    "message": "ECHO_DRY_RUN: security scan skipped",
                    "file_path": None,
                    "line": None,
                }
            ]
            trace.append(llm_start_entry("security", {"dry_run": True}))
            trace.append(
                llm_end_entry("security", tokens_in=0, tokens_out=0, data={"dry_run": True})
            )
            trace.append(agent_end_entry("security", timer.elapsed_ms))
            return {"current_agent": "security", "trace": trace, "reviews": reviews}

        user_prompt = user_block(state["task"])
        trace.append(llm_start_entry("security", {"prompt": user_prompt[:2000]}))
        t_llm = time.perf_counter()
        result = await gateway_llm_call(
            [
                {"role": "system", "content": SECURITY_SYSTEM},
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
                sev = str(item.get("severity", "warning"))
                if sev not in ("info", "warning", "critical"):
                    sev = "warning"
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

        prior = list(state.get("reviews") or [])
        reviews_out = prior + reviews_out

        trace.append(
            llm_end_entry(
                "security",
                model=result.model,
                tokens_in=result.tokens_in,
                tokens_out=result.tokens_out,
                cost=result.cost,
                duration_ms=llm_duration,
                data={"input_hash": result.input_hash, "error": result.error},
            )
        )
        trace.append(agent_end_entry("security", timer.elapsed_ms))
    return {"current_agent": "security", "trace": trace, "reviews": reviews_out}
