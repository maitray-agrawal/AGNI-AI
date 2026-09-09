from fastapi import APIRouter
from datetime import datetime
from backend.app.config import settings
from backend.app.models.client import get_local_model_client

router = APIRouter()


@router.get("/health")
async def get_health():
    client = get_local_model_client()
    models = await client.list_models()
    ollama_ok = len(models) > 0

    return {
        "status": "healthy" if ollama_ok else "degraded",
        "version": settings.APP_VERSION,
        "environment": "sovereign_local",
        "ollama_connected": ollama_ok,
        "ollama_models_count": len(models),
        "qdrant_ready": settings.QDRANT_PATH.exists(),
        "timestamp": datetime.utcnow().isoformat(),
    }
