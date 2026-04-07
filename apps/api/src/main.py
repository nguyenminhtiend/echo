from fastapi import FastAPI

from src.api.agents import router as agents_router
from src.api.rag import router as rag_router
from src.api.traces import router as traces_router
from src.api.ws import router as ws_router

app = FastAPI(title="E.C.H.O. API", version="0.1.0")

app.include_router(agents_router)
app.include_router(traces_router)
app.include_router(rag_router)
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
