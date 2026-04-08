from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.state import EchoState


def security_node(state: EchoState) -> dict:
    """LangGraph node: security scanning agent (stub — real LLM calls in Task 18)."""
    with NodeTimer("security") as timer:
        trace = [agent_start_entry("security", {"task": state["task"]})]
        trace.append(llm_start_entry("security", {"prompt": "scan for vulnerabilities"}))
        trace.append(llm_end_entry("security", tokens_in=0, tokens_out=0))
        trace.append(agent_end_entry("security", timer.elapsed_ms))
    return {"current_agent": "security", "trace": trace}
