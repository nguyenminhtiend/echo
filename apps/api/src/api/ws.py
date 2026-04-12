import asyncio
import contextlib

import structlog
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketState

from src.agents.runner import ensure_queues, get_hitl_queue

router = APIRouter()
log = structlog.get_logger()


@router.websocket("/ws/{run_id}")
async def agent_trace_ws(websocket: WebSocket, run_id: str):
    await websocket.accept()
    trace_q, _hitl_q = ensure_queues(run_id)

    async def _push_events():
        try:
            while True:
                event = await trace_q.get()
                if websocket.client_state != WebSocketState.CONNECTED:
                    break
                await websocket.send_json(event)
                if event.get("type") == "stream_end":
                    break
        except Exception:  # noqa: BLE001
            log.debug("ws_push_events_ended", run_id=run_id)

    async def _receive_hitl():
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "hitl_response":
                    hq = get_hitl_queue(run_id)
                    if hq is not None:
                        await hq.put(data)
        except Exception:  # noqa: BLE001
            log.debug("ws_receive_ended", run_id=run_id)

    push_task = asyncio.create_task(_push_events())
    recv_task = asyncio.create_task(_receive_hitl())

    try:
        await push_task
    finally:
        recv_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await recv_task
