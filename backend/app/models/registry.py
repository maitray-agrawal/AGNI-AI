from typing import Dict, List, Any, Optional
import logging
from backend.app.config import settings
from backend.app.models.client import LocalModelClient, get_local_model_client

logger = logging.getLogger("agni.models.registry")


class ModelRegistry:
    """Capability-based model registry with dynamic discovery of local open-weight models."""

    def __init__(self, client: Optional[LocalModelClient] = None):
        self.client = client or get_local_model_client()
        # Default capability definition mapping
        self._capability_profiles = {
            "reasoning": {
                "preferred": settings.REASONING_MODEL,
                "fallbacks": ["llama3.1:8b", "llama3.1:latest", "mistral:latest"],
                "capabilities": ["reasoning", "planning", "summarization", "analysis", "report_generation"],
            },
            "coding": {
                "preferred": settings.CODING_MODEL,
                "fallbacks": ["qwen2.5-coder:7b", "llama3.1:8b"],
                "capabilities": ["coding", "python", "mathematics", "calculation", "data_analysis"],
            },
            "vision": {
                "preferred": settings.VISION_MODEL,
                "fallbacks": ["moondream", "llava", "llama3.2-vision"],
                "capabilities": ["vision", "scanned_document", "image", "diagram", "pid", "visual_analysis"],
            },
            "general": {
                "preferred": settings.GENERAL_MODEL,
                "fallbacks": ["mistral:latest", "llama3.1:8b"],
                "capabilities": ["general", "instruction", "qa"],
            },
        }
        self._cached_available_models: List[str] = []

    async def refresh_available_models(self) -> List[str]:
        """Queries local runtime to determine which model weights are actually installed."""
        try:
            models_meta = await self.client.list_models()
            self._cached_available_models = [m.get("name", "") for m in models_meta if m.get("name")]
            logger.info(f"Discovered {len(self._cached_available_models)} local models: {self._cached_available_models}")
        except Exception as e:
            logger.warning(f"Could not query local models, using defaults: {e}")
        return self._cached_available_models

    async def get_model_for_capabilities(self, required_capabilities: List[str]) -> str:
        """Finds the best local model matching the required capabilities."""
        if not self._cached_available_models:
            await self.refresh_available_models()

        req_set = set(c.lower() for c in required_capabilities)

        # Check vision first if requested
        if req_set.intersection({"vision", "scanned_document", "image", "diagram", "pid", "visual_analysis"}):
            return self._resolve_model("vision")

        # Check coding / calculation next
        if req_set.intersection({"coding", "python", "mathematics", "calculation"}):
            return self._resolve_model("coding")

        # Default to reasoning
        return self._resolve_model("reasoning")

    def _resolve_model(self, profile_name: str) -> str:
        profile = self._capability_profiles.get(profile_name, self._capability_profiles["reasoning"])
        preferred = profile["preferred"]

        # Check if preferred is in cached available models
        if preferred in self._cached_available_models or any(preferred in m for m in self._cached_available_models):
            return preferred

        # Try fallbacks
        for fb in profile["fallbacks"]:
            if fb in self._cached_available_models or any(fb in m for m in self._cached_available_models):
                return fb

        # If nothing matches or cache was empty, return preferred
        return preferred

    async def get_registry_info(self) -> List[Dict[str, Any]]:
        """Returns structured metadata for UI and /api/models."""
        await self.refresh_available_models()
        info = []
        for role, profile in self._capability_profiles.items():
            resolved = self._resolve_model(role)
            is_present = resolved in self._cached_available_models or any(resolved in m for m in self._cached_available_models)
            info.append({
                "id": resolved,
                "role": role,
                "name": resolved.split(":")[0].upper(),
                "capabilities": profile["capabilities"],
                "status": "available" if is_present else "configured",
            })
        return info


# Global registry singleton
model_registry = ModelRegistry()
