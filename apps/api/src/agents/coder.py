import time

from langchain_core.runnables import RunnableConfig

from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.prompts import CODER_SYSTEM
from src.agents.state import CodeArtifact, EchoState
from src.agents.tools import (
    configurable_ids,
    is_dry_run,
    max_tokens_for_complexity,
    parse_json_loose,
    user_block,
)
from src.gateway.middleware import gateway_llm_call


async def coder_node(state: EchoState, config: RunnableConfig | None = None) -> dict:
    """LangGraph node: code generation via gateway LLM."""
    user_id, run_id = configurable_ids(config)
    with NodeTimer("coder") as timer:
        trace = [agent_start_entry("coder", {"task": state["task"]})]
        if is_dry_run():
            artifact: CodeArtifact = {
                "file_path": "stub.py",
                "content": "# ECHO_DRY_RUN: stub artifact\npass\n",
                "action": "create",
            }
            trace.append(llm_start_entry("coder", {"prompt": "dry_run", "dry_run": True}))
            trace.append(
                llm_end_entry(
                    "coder",
                    tokens_in=0,
                    tokens_out=0,
                    data={"dry_run": True},
                )
            )
            trace.append(agent_end_entry("coder", timer.elapsed_ms))
            return {
                "current_agent": "coder",
                "trace": trace,
                "artifacts": [artifact],
            }

        user_prompt = user_block(state["task"])
        trace.append(llm_start_entry("coder", {"prompt": user_prompt[:2000]}))
        t_llm = time.perf_counter()
        result = await gateway_llm_call(
            [
                {"role": "system", "content": CODER_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            user_id=user_id,
            run_id=run_id,
            max_tokens=max_tokens_for_complexity(state["complexity"]),
        )
        llm_duration = int((time.perf_counter() - t_llm) * 1000)

        parsed = parse_json_loose(result.content)
        artifacts: list[CodeArtifact] = []
        raw_list = parsed.get("artifacts") if isinstance(parsed, dict) else None
        if isinstance(raw_list, list):
            for item in raw_list:
                if not isinstance(item, dict):
                    continue
                fp = str(item.get("file_path", "generated.py"))
                content = str(item.get("content", ""))
                act = str(item.get("action", "create"))
                artifacts.append(CodeArtifact(file_path=fp, content=content, action=act.lower()))
        if not artifacts:
            artifacts = [
                CodeArtifact(
                    file_path="generated.py",
                    content=result.content or "# (empty model output)",
                    action="create",
                )
            ]

        trace.append(
            llm_end_entry(
                "coder",
                model=result.model,
                tokens_in=result.tokens_in,
                tokens_out=result.tokens_out,
                cost=result.cost,
                duration_ms=llm_duration,
                data={
                    "input_hash": result.input_hash,
                    "error": result.error,
                },
            )
        )
        trace.append(agent_end_entry("coder", timer.elapsed_ms))
    return {"current_agent": "coder", "trace": trace, "artifacts": artifacts}
