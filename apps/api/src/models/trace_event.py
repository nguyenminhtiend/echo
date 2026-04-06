import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class TraceEvent(TimestampMixin, Base):
    __tablename__ = "trace_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("trace_events.id"))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_name: Mapped[str | None] = mapped_column(String(50))
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    tokens_in: Mapped[int | None] = mapped_column(Integer)
    tokens_out: Mapped[int | None] = mapped_column(Integer)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        Index("idx_trace_events_run", "run_id"),
        Index("idx_trace_events_parent", "parent_id"),
    )
