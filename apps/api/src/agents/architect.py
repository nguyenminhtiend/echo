from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.state import EchoState


def architect_node(state: EchoState) -> dict:
    """LangGraph node: architecture analysis agent (stub — real LLM calls in Task 18)."""
    with NodeTimer("architect") as timer:
        trace = [agent_start_entry("architect", {"task": state["task"]})]
        trace.append(llm_start_entry("architect", {"prompt": "analyze architecture"}))
        trace.append(llm_end_entry("architect", tokens_in=0, tokens_out=0))
        trace.append(agent_end_entry("architect", timer.elapsed_ms))
    return {"current_agent": "architect", "trace": trace}
