"""Eagerly import every model so SQLAlchemy's declarative registry is fully
populated before any route tries to resolve ForeignKey targets.

Without this, importing only `AgentRun` leaves `users` out of the metadata, and
the first INSERT into `agent_runs` fails with NoReferencedTableError because
the FK `agent_runs.user_id → users.id` cannot be resolved.
"""

from src.models.agent_run import AgentRun
from src.models.audit_log import AuditLog
from src.models.base import Base
from src.models.cost_ledger import CostLedger
from src.models.rag import GraphEdge, GraphNode, RagChunk
from src.models.trace_event import TraceEvent
from src.models.user import User, UserSession

__all__ = [
    "AgentRun",
    "AuditLog",
    "Base",
    "CostLedger",
    "GraphEdge",
    "GraphNode",
    "RagChunk",
    "TraceEvent",
    "User",
    "UserSession",
]
