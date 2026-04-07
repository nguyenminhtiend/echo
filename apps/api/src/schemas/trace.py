import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TraceEventResponse(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    parent_id: uuid.UUID | None
    event_type: str
    agent_name: str | None
    data: dict
    tokens_in: int | None
    tokens_out: int | None
    cost: Decimal | None
    duration_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TraceTree(BaseModel):
    events: list[TraceEventResponse]
    run_id: uuid.UUID
