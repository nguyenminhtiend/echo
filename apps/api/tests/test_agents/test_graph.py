from src.agents.graph import build_graph


def test_build_graph_returns_compiled_graph():
    graph = build_graph()
    assert graph is not None


def test_graph_has_supervisor_entry():
    graph = build_graph()
    assert "supervisor" in graph.nodes


def test_graph_has_all_agent_nodes():
    graph = build_graph()
    for agent in ["supervisor", "coder", "reviewer", "qa", "security", "docs", "architect"]:
        assert agent in graph.nodes
