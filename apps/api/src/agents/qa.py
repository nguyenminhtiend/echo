from src.agents.state import EchoState


def qa_node(state: EchoState) -> dict:
    """LangGraph node: QA/testing agent (stub)."""
    return {
        "current_agent": "qa",
        "trace": [
            {
                "agent": "qa",
                "event_type": "agent_start",
                "data": {"task": state["task"]},
            }
        ],
    }
