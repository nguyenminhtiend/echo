import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

router = APIRouter()


class TraceConnection:
    """Manages a WebSocket connection for streaming agent trace events."""

    def __init__(self, websocket: WebSocket, run_id: str):
        self.websocket = websocket
        self.run_id = run_id
        self.event_queue: asyncio.Queue = asyncio.Queue()

    async def send_event(self, event: dict) -> None:
        if self.websocket.client_state == WebSocketState.CONNECTED:
            await self.websocket.send_json(event)

    async def receive_hitl(self) -> dict:
        data = await self.websocket.receive_json()
        return data


# Active connections keyed by run_id
_connections: dict[str, TraceConnection] = {}


def get_connection(run_id: str) -> TraceConnection | None:
    return _connections.get(run_id)


@router.websocket("/ws/{run_id}")
async def agent_trace_ws(websocket: WebSocket, run_id: str):
    await websocket.accept()
    conn = TraceConnection(websocket, run_id)
    _connections[run_id] = conn

    try:
        while True:
            # Wait for events from the queue or client messages
            try:
                event = conn.event_queue.get_nowait()
                await conn.send_event(event)
            except asyncio.QueueEmpty:
                pass

            # Check for incoming HITL responses (non-blocking)
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                if data.get("type") == "hitl_response":
                    await conn.event_queue.put(data)
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        _connections.pop(run_id, None)
