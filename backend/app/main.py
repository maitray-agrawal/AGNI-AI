from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.app.config import settings
from backend.app.models.registry import model_registry
from backend.app.api.health import router as health_router
from backend.app.api.models import router as models_router
from backend.app.api.tasks import router as tasks_router
from backend.app.api.files import router as files_router
from backend.app.api.outputs import router as outputs_router
from backend.app.api.security import router as security_router
from backend.app.api.signals import router as signals_router
from backend.app.api.events import router as events_router
from backend.app.api.regimes import router as regimes_router
from backend.app.api.scenarios import router as scenarios_router
from backend.app.api.forecasts import router as forecasts_router
from backend.app.api.graph import router as graph_router
from backend.app.api.research import router as research_router, direct_router as research_direct_router
from backend.app.api.satellite import router as satellite_router
from backend.app.api.markets import router as markets_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agni.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.APP_ENV} mode...")
    logger.info(f"Connecting to local Ollama runtime on {settings.OLLAMA_BASE_URL}...")
    models = await model_registry.refresh_available_models()
    logger.info(f"Local models detected: {models}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title="AGNI-AI Sovereign Engineering Intelligence",
    version=settings.APP_VERSION,
    description="Sovereign Agentic Intelligence for Evidence-Grounded Engineering Workflows (AstraX)",
    lifespan=lifespan,
)

# CORS configuration - strictly allows local development frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(models_router, prefix="/api", tags=["Models"])
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
app.include_router(files_router, prefix="/api", tags=["Files"])
app.include_router(outputs_router, prefix="/api", tags=["Outputs"])
app.include_router(security_router, prefix="/api", tags=["Security"])
app.include_router(signals_router, prefix="/api", tags=["Signals"])
app.include_router(events_router, prefix="/api", tags=["Events"])
app.include_router(regimes_router, prefix="/api", tags=["Regimes"])
app.include_router(scenarios_router, prefix="/api", tags=["Scenarios"])
app.include_router(forecasts_router, prefix="/api", tags=["Forecasts"])
app.include_router(graph_router, prefix="/api", tags=["Graph"])
app.include_router(research_router, prefix="/api", tags=["Research"])
app.include_router(research_direct_router, prefix="/api", tags=["Research Direct"])
app.include_router(satellite_router, prefix="/api", tags=["Earth Observation (Satellite)"])
app.include_router(markets_router, prefix="/api", tags=["Markets"])

# Direct top-level Phase 1, Phase 3 & Phase 4 routes: /health, /events, /signals, /markets, /graph, /regimes
app.include_router(health_router, tags=["Health (Root)"])
app.include_router(events_router, tags=["Events (Root)"])
app.include_router(signals_router, tags=["Signals (Root)"])
app.include_router(markets_router, tags=["Markets (Root)"])
app.include_router(graph_router, tags=["Graph (Root)"])
app.include_router(regimes_router, tags=["Regimes (Root)"])


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "SOVEREIGN_AIR_GAPPED",
        "docs": "/docs",
    }
