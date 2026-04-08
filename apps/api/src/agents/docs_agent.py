from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.state import EchoState


def docs_node(state: EchoState) -> dict:
    """LangGraph node: documentation agent (stub — real LLM calls in Task 18)."""
    with NodeTimer("docs") as timer:
        trace = [agent_start_entry("docs", {"task": state["task"]})]
        trace.append(llm_start_entry("docs", {"prompt": "generate documentation"}))
        trace.append(llm_end_entry("docs", tokens_in=0, tokens_out=0))
        trace.append(agent_end_entry("docs", timer.elapsed_ms))
    return {"current_agent": "docs", "trace": trace}
