from src.agents.state import EchoState


def coder_node(state: EchoState) -> dict:
    """LangGraph node: code generation agent (stub)."""
    return {
        "current_agent": "coder",
        "trace": [
            {
                "agent": "coder",
                "event_type": "agent_start",
                "data": {"task": state["task"]},
            }
        ],
    }
