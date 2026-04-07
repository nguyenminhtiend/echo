from src.agents.state import EchoState


def architect_node(state: EchoState) -> dict:
    """LangGraph node: architecture analysis agent (stub)."""
    return {
        "current_agent": "architect",
        "trace": [
            {
                "agent": "architect",
                "event_type": "agent_start",
                "data": {"task": state["task"]},
            }
        ],
    }
