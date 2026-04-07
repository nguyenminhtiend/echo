from src.agents.state import EchoState, TaskType

_TASK_KEYWORDS: dict[TaskType, set[str]] = {
    TaskType.BUGFIX: {"fix", "bug", "error", "crash", "broken", "issue", "patch"},
    TaskType.FEATURE: {"add", "new", "feature", "implement", "create", "build"},
    TaskType.REVIEW: {"review", "pr", "pull request", "check", "audit"},
    TaskType.TEST: {"test", "tests", "coverage", "spec", "unittest", "pytest"},
    TaskType.SECURITY: {"security", "vulnerability", "vulnerabilities", "owasp", "secret", "cve", "scan"},
    TaskType.DOCS: {"doc", "documentation", "readme", "changelog", "comment"},
    TaskType.ARCHITECTURE: {"architecture", "design", "refactor", "migrate", "dependency"},
}

_ROUTE_MAP: dict[TaskType, str] = {
    TaskType.BUGFIX: "coder",
    TaskType.FEATURE: "coder",
    TaskType.REVIEW: "reviewer",
    TaskType.TEST: "qa",
    TaskType.SECURITY: "security",
    TaskType.DOCS: "docs",
    TaskType.ARCHITECTURE: "architect",
}


def classify_task(task: str) -> TaskType:
    """Classify a task string into a TaskType using keyword matching."""
    words = set(task.lower().split())
    best_type = TaskType.FEATURE
    best_score = 0
    for task_type, keywords in _TASK_KEYWORDS.items():
        score = len(words & keywords)
        if score > best_score:
            best_score = score
            best_type = task_type
    return best_type


def route_task(task_type: TaskType) -> str:
    """Return the agent name to route to for a given task type."""
    return _ROUTE_MAP[task_type]


def supervisor_node(state: EchoState) -> dict:
    """LangGraph node: classify task and route to appropriate agent."""
    task_type = classify_task(state["task"])
    next_agent = route_task(task_type)
    return {
        "task_type": task_type,
        "current_agent": next_agent,
        "trace": [
            {
                "agent": "supervisor",
                "event_type": "classify",
                "data": {
                    "task_type": task_type.value,
                    "routed_to": next_agent,
                },
            }
        ],
    }
