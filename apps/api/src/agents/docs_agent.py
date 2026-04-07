from src.agents.state import EchoState


def docs_node(state: EchoState) -> dict:
    """LangGraph node: documentation agent (stub)."""
    return {
        "current_agent": "docs",
        "trace": [
            {
                "agent": "docs",
                "event_type": "agent_start",
                "data": {"task": state["task"]},
            }
        ],
    }
