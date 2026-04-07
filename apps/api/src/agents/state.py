from enum import Enum
from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class TaskType(Enum):
    BUGFIX = "bugfix"
    FEATURE = "feature"
    REVIEW = "review"
    TEST = "test"
    SECURITY = "security"
    DOCS = "docs"
    ARCHITECTURE = "architecture"


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class CodeArtifact(TypedDict):
    file_path: str
    content: str
    action: str  # "create" | "modify" | "delete"


class ReviewFinding(TypedDict):
    severity: str  # "info" | "warning" | "critical"
    message: str
    file_path: str | None
    line: int | None


class TraceEntry(TypedDict):
    """In-memory trace entry for agent state. Not to be confused with the
    TraceEvent SQLAlchemy model in models/trace_event.py."""

    agent: str
    event_type: str
    data: dict


class EchoState(TypedDict):
    task: str
    task_type: TaskType
    complexity: TaskComplexity
    messages: Annotated[list, add_messages]
    artifacts: list[CodeArtifact]
    reviews: list[ReviewFinding]
    trace: list[TraceEntry]
    current_agent: str
    iteration: int
    max_iterations: int
