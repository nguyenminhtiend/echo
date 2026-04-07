import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter

from src.schemas.agent import AgentRunCreate, AgentRunList, AgentRunResponse

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/runs", status_code=201, response_model=AgentRunResponse)
async def create_run(body: AgentRunCreate):
    # Stub: returns a mock response until DB integration
    return AgentRunResponse(
        id=uuid.uuid4(),
        task=body.task,
        task_type=body.task_type,
        complexity=None,
        status="pending",
        total_tokens=0,
        total_cost=Decimal("0"),
        duration_ms=None,
        created_at=datetime.now(timezone.utc),
        completed_at=None,
    )


@router.get("/runs", response_model=AgentRunList)
async def list_runs():
    return AgentRunList(runs=[], total=0)
