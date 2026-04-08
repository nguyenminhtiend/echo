import time
from collections import defaultdict


class RateLimiter:
    """Per-user token/minute rate limiter (in-memory, single-process)."""

    def __init__(self, max_tokens_per_minute: int = 100_000):
        self.max_tokens_per_minute = max_tokens_per_minute
        self._usage: dict[str, list[tuple[float, int]]] = defaultdict(list)

    def _prune(self, user_id: str) -> None:
        """Remove entries older than 60 seconds."""
        cutoff = time.monotonic() - 60.0
        self._usage[user_id] = [(ts, tokens) for ts, tokens in self._usage[user_id] if ts > cutoff]

    def _current_usage(self, user_id: str) -> int:
        self._prune(user_id)
        return sum(tokens for _, tokens in self._usage[user_id])

    def check(self, user_id: str, tokens: int) -> bool:
        """Return True if the request is within rate limits."""
        return self._current_usage(user_id) + tokens <= self.max_tokens_per_minute

    def record(self, user_id: str, tokens: int) -> None:
        """Record token usage for a user."""
        self._usage[user_id].append((time.monotonic(), tokens))

    def remaining(self, user_id: str) -> int:
        """Return remaining tokens in the current window."""
        return max(0, self.max_tokens_per_minute - self._current_usage(user_id))
