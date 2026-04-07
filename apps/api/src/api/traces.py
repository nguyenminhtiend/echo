import uuid

from fastapi import APIRouter, HTTPException

from src.schemas.trace import TraceTree

router = APIRouter(prefix="/api/traces", tags=["traces"])


@router.get("/{run_id}", response_model=TraceTree)
async def get_trace(run_id: uuid.UUID):
    # Stub: returns 404 until DB integration
    raise HTTPException(status_code=404, detail="Run not found")
