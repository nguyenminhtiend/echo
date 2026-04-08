import time

from langchain_core.runnables import RunnableConfig

from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.prompts import ARCHITECT_SYSTEM
from src.agents.state import EchoState
from src.agents.tools import (
    configurable_ids,
    is_dry_run,
    max_tokens_for_complexity,
    parse_json_loose,
    user_block,
)
from src.gateway.middleware import gateway_llm_call


async def architect_node(state: EchoState, config: RunnableConfig | None = None) -> dict:
    """LangGraph node: architecture analysis via gateway LLM."""
    user_id, run_id = configurable_ids(config)
    with NodeTimer("architect") as timer:
        trace = [agent_start_entry("architect", {"task": state["task"]})]
        if is_dry_run():
            trace.append(llm_start_entry("architect", {"dry_run": True}))
            trace.append(
                llm_end_entry(
                    "architect",
                    tokens_in=0,
                    tokens_out=0,
                    data={"dry_run": True, "summary": "ECHO_DRY_RUN stub"},
                )
            )
            trace.append(agent_end_entry("architect", timer.elapsed_ms))
            return {"current_agent": "architect", "trace": trace}

        user_prompt = user_block(state["task"])
        trace.append(llm_start_entry("architect", {"prompt": user_prompt[:2000]}))
        t_llm = time.perf_counter()
        result = await gateway_llm_call(
            [
                {"role": "system", "content": ARCHITECT_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            user_id=user_id,
            run_id=run_id,
            max_tokens=max_tokens_for_complexity(state["complexity"]),
        )
        llm_duration = int((time.perf_counter() - t_llm) * 1000)
        parsed = parse_json_loose(result.content)
        payload: dict = {}
        if isinstance(parsed, dict):
            for k in ("summary", "components", "risks", "recommendations"):
                if k in parsed:
                    payload[k] = parsed[k]
        if not payload:
            payload = {"analysis": result.content}

        trace.append(
            llm_end_entry(
                "architect",
                model=result.model,
                tokens_in=result.tokens_in,
                tokens_out=result.tokens_out,
                cost=result.cost,
                duration_ms=llm_duration,
                data={
                    "input_hash": result.input_hash,
                    "error": result.error,
                    **payload,
                },
            )
        )
        trace.append(agent_end_entry("architect", timer.elapsed_ms))
    return {"current_agent": "architect", "trace": trace}
