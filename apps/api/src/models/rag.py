import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class RagChunk(Base):
    __tablename__ = "rag_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # embedding column: vector(768) — created via raw SQL in migration (pgvector type)
    chunk_type: Mapped[str | None] = mapped_column(String(50))
    file_path: Mapped[str | None] = mapped_column(String(500))
    start_line: Mapped[int | None] = mapped_column(Integer)
    end_line: Mapped[int | None] = mapped_column(Integer)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    properties: Mapped[dict | None] = mapped_column(JSONB)
    # embedding column: vector(768) — created via raw SQL in migration

    __table_args__ = (Index("idx_graph_nodes_label", "label"),)


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("graph_nodes.id"), nullable=False
    )
    target_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("graph_nodes.id"), nullable=False
    )
    relation: Mapped[str] = mapped_column(String(100), nullable=False)
    properties: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("idx_graph_edges_source", "source_id"),
        Index("idx_graph_edges_target", "target_id"),
    )
