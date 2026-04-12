from src.models.agent_run import AgentRun
from src.models.audit_log import AuditLog
from src.models.cost_ledger import CostLedger
from src.models.rag import GraphEdge, GraphNode, RagChunk
from src.models.trace_event import TraceEvent


def test_agent_run_table_name():
    assert AgentRun.__tablename__ == "agent_runs"


def test_trace_event_table_name():
    assert TraceEvent.__tablename__ == "trace_events"


def test_cost_ledger_table_name():
    assert CostLedger.__tablename__ == "cost_ledger"


def test_audit_log_table_name():
    assert AuditLog.__tablename__ == "audit_log"


def test_rag_chunk_table_name():
    assert RagChunk.__tablename__ == "rag_chunks"


def test_graph_node_table_name():
    assert GraphNode.__tablename__ == "graph_nodes"


def test_graph_edge_table_name():
    assert GraphEdge.__tablename__ == "graph_edges"


def test_agent_run_has_status_column():
    assert "status" in AgentRun.__table__.columns


def test_agent_run_user_id_is_text():
    # Better Auth owns identity; user_id must be text (cuid2), not uuid.
    assert str(AgentRun.__table__.columns["user_id"].type).upper() == "TEXT"


def test_trace_event_has_indexes():
    index_names = [idx.name for idx in TraceEvent.__table__.indexes]
    assert "idx_trace_events_run" in index_names
    assert "idx_trace_events_parent" in index_names
