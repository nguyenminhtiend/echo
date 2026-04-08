import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AgentRunCreate(BaseModel):
    task: str
    task_type: str | None = None


class AgentRunResponse(BaseModel):
    id: uuid.UUID
    task: str
    task_type: str | None
    complexity: str | None
    status: str
    total_tokens: int
    total_cost: Decimal
    duration_ms: int | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class AgentRunList(BaseModel):
    runs: list[AgentRunResponse]
    total: int


class AgentStatsResponse(BaseModel):
    total_runs: int
    total_tokens: int
    total_cost: Decimal
