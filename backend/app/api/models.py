from fastapi import APIRouter
from backend.app.config import settings
from backend.app.models.registry import model_registry

router = APIRouter()


@router.get("/models")
async def get_models():
    reg_info = await model_registry.get_registry_info()
    return {
        "provider": settings.MODEL_PROVIDER,
        "endpoint": settings.OLLAMA_BASE_URL,
        "models": reg_info,
    }
