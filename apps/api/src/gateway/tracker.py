import uuid
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cost_ledger import CostLedger


@dataclass
class LLMUsage:
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    user_id: str | None = None
    run_id: str | None = None


def _parse_uuid(value: str | None) -> uuid.UUID | None:
    if not value or value in ("anonymous", "unknown"):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


class CostTracker:
    """In-memory cost tracker. Persists to DB via flush() in production."""

    def __init__(self) -> None:
        self.entries: list[LLMUsage] = []

    def record(self, usage: LLMUsage) -> None:
        self.entries.append(usage)

    async def flush(
        self,
        session: AsyncSession,
        *,
        user_id: uuid.UUID | None = None,
        run_id: uuid.UUID | None = None,
    ) -> int:
        """Write accumulated usage rows to ``cost_ledger`` and clear the buffer."""
        if not self.entries:
            return 0
        for e in self.entries:
            uid = _parse_uuid(e.user_id) if e.user_id else user_id
            rid = _parse_uuid(e.run_id) if e.run_id else run_id
            session.add(
                CostLedger(
                    id=uuid.uuid4(),
                    user_id=uid,
                    run_id=rid,
                    model=e.model,
                    tokens_in=e.tokens_in,
                    tokens_out=e.tokens_out,
                    cost=Decimal(str(e.cost)),
                )
            )
        count = len(self.entries)
        self.entries.clear()
        return count

    @property
    def total_cost(self) -> float:
        return sum(e.cost for e in self.entries)

    @property
    def total_tokens(self) -> int:
        return sum(e.tokens_in + e.tokens_out for e in self.entries)


cost_tracker = CostTracker()


def get_cost_tracker() -> CostTracker:
    return cost_tracker


def reset_cost_tracker() -> None:
    """Clear in-memory entries (e.g. at the start of a new agent run)."""
    cost_tracker.entries.clear()
