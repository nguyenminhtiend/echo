from src.agents.state import TaskComplexity
from src.gateway.router import classify_complexity


def test_simple_task():
    assert classify_complexity("fix typo in readme") == TaskComplexity.SIMPLE


def test_moderate_task():
    assert classify_complexity("add unit tests for the auth module") == TaskComplexity.MODERATE


def test_complex_task():
    assert (
        classify_complexity("refactor the entire authentication architecture")
        == TaskComplexity.COMPLEX
    )


def test_security_keyword_is_complex():
    assert classify_complexity("scan for security vulnerabilities") == TaskComplexity.COMPLEX
