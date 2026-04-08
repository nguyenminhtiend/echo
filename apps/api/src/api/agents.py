import asyncio
import os
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.runner import AgentRunner
from src.agents.supervisor import classify_task
from src.db.session import get_db
from src.models.agent_run import AgentRun
from src.schemas.agent import (
    AgentRunCreate,
    AgentRunList,
    AgentRunResponse,
    AgentStatsResponse,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/runs", status_code=201, response_model=AgentRunResponse)
async def create_run(body: AgentRunCreate, db: AsyncSession = Depends(get_db)):
    classified = classify_task(body.task)
    task_type = body.task_type if body.task_type is not None else classified.value
    run = AgentRun(
        id=uuid.uuid4(),
        task=body.task,
        task_type=task_type,
        status="pending",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    if not os.environ.get("ECHO_SKIP_AGENT_RUNNER"):
        asyncio.create_task(AgentRunner.execute(run.id))

    return AgentRunResponse.model_validate(run)


@router.get("/runs", response_model=AgentRunList)
async def list_runs(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    count_stmt = select(func.count()).select_from(AgentRun)
    total = (await db.execute(count_stmt)).scalar_one()
    stmt = select(AgentRun).order_by(AgentRun.created_at.desc()).offset(skip).limit(limit)
    runs = (await db.execute(stmt)).scalars().all()
    return AgentRunList(
        runs=[AgentRunResponse.model_validate(r) for r in runs],
        total=total,
    )


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(AgentRun).where(AgentRun.id == run_id)
    run = (await db.execute(stmt)).scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return AgentRunResponse.model_validate(run)


@router.get("/stats", response_model=AgentStatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    stmt = select(
        func.count(AgentRun.id),
        func.coalesce(func.sum(AgentRun.total_tokens), 0),
        func.coalesce(func.sum(AgentRun.total_cost), 0),
    )
    row = (await db.execute(stmt)).one()
    total_runs, total_tokens, total_cost = row
    return AgentStatsResponse(
        total_runs=int(total_runs),
        total_tokens=int(total_tokens),
        total_cost=Decimal(str(total_cost)),
    )
