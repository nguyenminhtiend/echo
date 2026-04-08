from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider

from src.api.agents import router as agents_router
from src.api.rag import router as rag_router
from src.api.traces import router as traces_router
from src.api.ws import router as ws_router
from src.db.session import engine, get_db  # noqa: F401

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
)

# Configure OpenTelemetry
provider = TracerProvider()
trace.set_tracer_provider(provider)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="E.C.H.O. API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

app.include_router(agents_router)
app.include_router(traces_router)
app.include_router(rag_router)
app.include_router(ws_router)

log = structlog.get_logger()


@app.get("/health")
async def health():
    log.info("health_check")
    return {"status": "ok", "version": "0.1.0"}
