from dataclasses import dataclass


@dataclass
class LLMUsage:
    model: str
    tokens_in: int
    tokens_out: int
    cost: float
    user_id: str | None = None
    run_id: str | None = None


class CostTracker:
    """In-memory cost tracker. Persists to DB via flush() in production."""

    def __init__(self):
        self.entries: list[LLMUsage] = []

    def record(self, usage: LLMUsage) -> None:
        self.entries.append(usage)

    @property
    def total_cost(self) -> float:
        return sum(e.cost for e in self.entries)

    @property
    def total_tokens(self) -> int:
        return sum(e.tokens_in + e.tokens_out for e in self.entries)
