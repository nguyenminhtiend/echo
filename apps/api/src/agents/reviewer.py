from src.agents.state import EchoState


def reviewer_node(state: EchoState) -> dict:
    """LangGraph node: code review agent (stub)."""
    return {
        "current_agent": "reviewer",
        "trace": [
            {
                "agent": "reviewer",
                "event_type": "agent_start",
                "data": {"task": state["task"]},
            }
        ],
    }
