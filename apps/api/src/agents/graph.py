from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.agents.architect import architect_node
from src.agents.coder import coder_node
from src.agents.docs_agent import docs_node
from src.agents.qa import qa_node
from src.agents.reviewer import reviewer_node
from src.agents.security import security_node
from src.agents.state import EchoState
from src.agents.supervisor import supervisor_node


def _route_from_supervisor(state: EchoState) -> str:
    """Conditional edge: route from supervisor to the chosen agent."""
    return state["current_agent"]


def build_graph(checkpointer=None):
    """Build and compile the E.C.H.O. multi-agent LangGraph.

    Flow: Supervisor -> Coder -> [HITL] -> Reviewer -> QA -> Security -> [HITL] -> Docs -> END
    For non-code tasks (review, security, docs, architect), Supervisor routes directly
    to the relevant agent which then goes to END.
    """
    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(EchoState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("coder", coder_node)
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("qa", qa_node)
    builder.add_node("security", security_node)
    builder.add_node("docs", docs_node)
    builder.add_node("architect", architect_node)

    builder.set_entry_point("supervisor")

    builder.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {
            "coder": "coder",
            "reviewer": "reviewer",
            "qa": "qa",
            "security": "security",
            "docs": "docs",
            "architect": "architect",
        },
    )

    builder.add_edge("coder", "reviewer")
    builder.add_edge("reviewer", "qa")
    builder.add_edge("qa", "security")
    builder.add_edge("security", "docs")
    builder.add_edge("docs", END)

    builder.add_edge("architect", END)

    return builder.compile(checkpointer=checkpointer, interrupt_after=["coder", "security"])
