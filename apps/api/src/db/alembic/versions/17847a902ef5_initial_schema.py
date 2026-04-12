"""initial schema

Revision ID: 17847a902ef5
Revises:
Create Date: 2026-04-12 08:56:24.521467

Single consolidated baseline for the Alembic-managed portion of the ECHO
schema. Identity tables (``user``/``session``/``account``/``verification``)
are **not** tracked here — they are owned by Better Auth's autoMigrate in
``apps/web/src/lib/auth.ts``. ``agent_runs``/``audit_log``/``cost_ledger``
each carry a plain ``user_id text`` column with no DB-level FK, since the
referenced table lives outside Alembic's control.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "17847a902ef5"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=True),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("task_type", sa.String(length=50), nullable=True),
        sa.Column("complexity", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("total_cost", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource", sa.String(length=255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_log_created", "audit_log", ["created_at"], unique=False)
    op.create_index("idx_audit_log_user", "audit_log", ["user_id"], unique=False)

    op.create_table(
        "graph_nodes",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_graph_nodes_label", "graph_nodes", ["label"], unique=False)
    # pgvector column — Drizzle/SQLAlchemy don't model ``vector`` natively, so we add it in raw SQL.
    op.execute("ALTER TABLE graph_nodes ADD COLUMN embedding vector(768)")

    op.create_table(
        "rag_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_type", sa.String(length=50), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=True),
        sa.Column("end_line", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "indexed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("ALTER TABLE rag_chunks ADD COLUMN embedding vector(768) NOT NULL")
    op.execute(
        """
        CREATE INDEX idx_rag_chunks_embedding ON rag_chunks
        USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
        """
    )

    op.create_table(
        "cost_ledger",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=True),
        sa.Column("run_id", sa.Uuid(), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=False),
        sa.Column("tokens_out", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cost_ledger_created", "cost_ledger", ["created_at"], unique=False)
    op.create_index("idx_cost_ledger_user", "cost_ledger", ["user_id"], unique=False)

    op.create_table(
        "graph_edges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("target_id", sa.String(length=255), nullable=False),
        sa.Column("relation", sa.String(length=100), nullable=False),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["graph_nodes.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["graph_nodes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_graph_edges_source", "graph_edges", ["source_id"], unique=False)
    op.create_index("idx_graph_edges_target", "graph_edges", ["target_id"], unique=False)

    op.create_table(
        "trace_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("agent_name", sa.String(length=50), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=True),
        sa.Column("tokens_out", sa.Integer(), nullable=True),
        sa.Column("cost", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["trace_events.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_trace_events_parent", "trace_events", ["parent_id"], unique=False)
    op.create_index("idx_trace_events_run", "trace_events", ["run_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_trace_events_run", table_name="trace_events")
    op.drop_index("idx_trace_events_parent", table_name="trace_events")
    op.drop_table("trace_events")
    op.drop_index("idx_graph_edges_target", table_name="graph_edges")
    op.drop_index("idx_graph_edges_source", table_name="graph_edges")
    op.drop_table("graph_edges")
    op.drop_index("idx_cost_ledger_user", table_name="cost_ledger")
    op.drop_index("idx_cost_ledger_created", table_name="cost_ledger")
    op.drop_table("cost_ledger")
    op.execute("DROP INDEX IF EXISTS idx_rag_chunks_embedding")
    op.drop_table("rag_chunks")
    op.drop_index("idx_graph_nodes_label", table_name="graph_nodes")
    op.drop_table("graph_nodes")
    op.drop_index("idx_audit_log_user", table_name="audit_log")
    op.drop_index("idx_audit_log_created", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_table("agent_runs")
    op.execute("DROP EXTENSION IF EXISTS vector")
