from src.agents.state import TaskType
from src.agents.supervisor import classify_task


def test_classify_bugfix():
    assert classify_task("fix the login bug in auth handler") == TaskType.BUGFIX


def test_classify_feature():
    assert classify_task("add a new dashboard page for metrics") == TaskType.FEATURE


def test_classify_review():
    assert classify_task("review the pull request for auth changes") == TaskType.REVIEW


def test_classify_security():
    assert classify_task("scan codebase for security vulnerabilities") == TaskType.SECURITY


def test_classify_test():
    assert classify_task("write tests for the user service") == TaskType.TEST
