import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.agent_run import AgentRun
from src.models.trace_event import TraceEvent
from src.schemas.trace import TraceEventResponse, TraceTree

router = APIRouter(prefix="/api/traces", tags=["traces"])


@router.get("/{run_id}", response_model=TraceTree)
async def get_trace(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    run_stmt = select(AgentRun).where(AgentRun.id == run_id)
    run = (await db.execute(run_stmt)).scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    events_stmt = select(TraceEvent).where(TraceEvent.run_id == run_id)
    events = (await db.execute(events_stmt)).scalars().all()
    return TraceTree(
        run_id=run_id,
        events=[TraceEventResponse.model_validate(e) for e in events],
    )
