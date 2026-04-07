from src.gateway.rate_limiter import RateLimiter


def test_allows_under_limit():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    assert limiter.check("user-1", tokens=100) is True


def test_blocks_over_limit():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    limiter.record("user-1", tokens=900)
    assert limiter.check("user-1", tokens=200) is False


def test_separate_users_have_separate_limits():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    limiter.record("user-1", tokens=900)
    assert limiter.check("user-2", tokens=500) is True


def test_remaining_tokens():
    limiter = RateLimiter(max_tokens_per_minute=1000)
    limiter.record("user-1", tokens=300)
    assert limiter.remaining("user-1") == 700
