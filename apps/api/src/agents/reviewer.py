from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.state import EchoState


def reviewer_node(state: EchoState) -> dict:
    """LangGraph node: code review agent (stub — real LLM calls in Task 18)."""
    with NodeTimer("reviewer") as timer:
        trace = [agent_start_entry("reviewer", {"task": state["task"]})]
        trace.append(llm_start_entry("reviewer", {"prompt": "review code"}))
        trace.append(llm_end_entry("reviewer", tokens_in=0, tokens_out=0))
        trace.append(agent_end_entry("reviewer", timer.elapsed_ms))
    return {"current_agent": "reviewer", "trace": trace}
