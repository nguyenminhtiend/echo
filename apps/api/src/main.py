import structlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider

from src.api.agents import router as agents_router
from src.api.rag import router as rag_router
from src.api.traces import router as traces_router
from src.api.ws import router as ws_router

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

app = FastAPI(title="E.C.H.O. API", version="0.1.0")

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
