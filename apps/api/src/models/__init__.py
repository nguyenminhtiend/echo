"""Eagerly import every model so SQLAlchemy's declarative registry is fully
populated before any route tries to resolve ForeignKey targets.

Without this, importing only `AgentRun` can leave sibling tables out of the
metadata and cause NoReferencedTableError at the first INSERT.

Note: identity (users/sessions) is owned by Better Auth in the web app — see
``apps/web/src/lib/auth.ts``. The API references Better Auth's ``"user".id``
via plain text columns; there is no ``User`` ORM model on this side.
"""

from src.models.agent_run import AgentRun
from src.models.audit_log import AuditLog
from src.models.base import Base
from src.models.cost_ledger import CostLedger
from src.models.rag import GraphEdge, GraphNode, RagChunk
from src.models.trace_event import TraceEvent

__all__ = [
    "AgentRun",
    "AuditLog",
    "Base",
    "CostLedger",
    "GraphEdge",
    "GraphNode",
    "RagChunk",
    "TraceEvent",
]
