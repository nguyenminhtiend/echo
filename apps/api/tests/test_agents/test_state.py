from src.agents.state import EchoState, TaskComplexity, TaskType


def test_echo_state_has_required_keys():
    state: EchoState = {
        "task": "fix bug",
        "task_type": TaskType.BUGFIX,
        "complexity": TaskComplexity.SIMPLE,
        "messages": [],
        "artifacts": [],
        "reviews": [],
        "trace": [],
        "current_agent": "supervisor",
        "iteration": 0,
        "max_iterations": 10,
    }
    assert state["task"] == "fix bug"
    assert state["current_agent"] == "supervisor"


def test_task_type_values():
    assert TaskType.BUGFIX.value == "bugfix"
    assert TaskType.FEATURE.value == "feature"
    assert TaskType.REVIEW.value == "review"
    assert TaskType.TEST.value == "test"
