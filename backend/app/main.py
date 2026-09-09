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
    title="AGNI-AI Sovereign Industrial Workbench",
    version=settings.APP_VERSION,
    description="Air-gapped, sovereign multimodal agentic AI workbench for MRPL (SIH 2026 PS 26117)",
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

# Mount API routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(models_router, prefix="/api", tags=["Models"])
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
app.include_router(files_router, prefix="/api", tags=["Files"])
app.include_router(outputs_router, prefix="/api", tags=["Outputs"])
app.include_router(security_router, prefix="/api", tags=["Security"])


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "SOVEREIGN_AIR_GAPPED",
        "docs": "/docs",
    }
