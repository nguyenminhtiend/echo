from src.agents.node_tracing import (
    NodeTimer,
    agent_end_entry,
    agent_start_entry,
    llm_end_entry,
    llm_start_entry,
)
from src.agents.state import EchoState


def qa_node(state: EchoState) -> dict:
    """LangGraph node: QA/testing agent (stub — real LLM calls in Task 18)."""
    with NodeTimer("qa") as timer:
        trace = [agent_start_entry("qa", {"task": state["task"]})]
        trace.append(llm_start_entry("qa", {"prompt": "generate tests"}))
        trace.append(llm_end_entry("qa", tokens_in=0, tokens_out=0))
        trace.append(agent_end_entry("qa", timer.elapsed_ms))
    return {"current_agent": "qa", "trace": trace}
