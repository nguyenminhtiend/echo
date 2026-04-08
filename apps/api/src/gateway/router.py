from litellm.router import Router

from src.agents.state import TaskComplexity
from src.config import settings

COMPLEX_KEYWORDS = {"refactor", "security", "architecture", "migrate", "redesign", "vulnerability"}
MODERATE_KEYWORDS = {"test", "review", "update", "add", "implement", "feature"}


def classify_complexity(task: str) -> TaskComplexity:
    """Classify task complexity using keyword heuristics."""
    words = set(task.lower().split())
    if words & COMPLEX_KEYWORDS:
        return TaskComplexity.COMPLEX
    if words & MODERATE_KEYWORDS:
        return TaskComplexity.MODERATE
    return TaskComplexity.SIMPLE


def create_llm_router() -> Router:
    """Create LiteLLM router configured for local Ollama."""
    return Router(
        model_list=[
            {
                "model_name": "echo-default",
                "litellm_params": {
                    "model": settings.echo_llm_model,
                    "api_base": settings.ollama_base_url,
                },
            },
        ],
        routing_strategy="simple-shuffle",
    )
