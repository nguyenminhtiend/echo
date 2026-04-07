from src.agents.state import EchoState


def security_node(state: EchoState) -> dict:
    """LangGraph node: security scanning agent (stub)."""
    return {
        "current_agent": "security",
        "trace": [
            {
                "agent": "security",
                "event_type": "agent_start",
                "data": {"task": state["task"]},
            }
        ],
    }
