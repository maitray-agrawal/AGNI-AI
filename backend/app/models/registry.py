import time
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from pydantic import BaseModel, Field
from backend.app.config import settings
from backend.app.models.client import LocalModelClient, get_local_model_client

logger = logging.getLogger("agni.models.registry")


class ModelSpec(BaseModel):
    """Strongly-typed specification for a locally hosted model."""
    name: str
    capabilities: List[str]
    modality: str = "text"  # "text" or "multimodal"
    role: str  # "reasoning", "coding", "vision", "general"
    priority: int = 1
    enabled: bool = True
    fallback_rank: int = 1
    timeout_seconds: int = 180
    description: str = ""


# Centralized single source of truth for model specifications
DEFAULT_MODEL_SPECS: List[ModelSpec] = [
    ModelSpec(
        name=settings.REASONING_MODEL,  # "llama3.1:8b"
        capabilities=["reasoning", "planning", "summarization", "analysis", "report_generation", "industrial_synthesis"],
        modality="text",
        role="reasoning",
        priority=100,
        enabled=True,
        fallback_rank=1,
        timeout_seconds=180,
        description="Primary reasoning, planning, and industrial approval synthesis engine (Llama 3.1 8B).",
    ),
    ModelSpec(
        name=settings.CODING_MODEL,  # "qwen2.5-coder:7b"
        capabilities=["coding", "python", "mathematics", "calculation", "data_analysis", "scripting"],
        modality="text",
        role="coding",
        priority=90,
        enabled=True,
        fallback_rank=1,
        timeout_seconds=180,
        description="Technical coding, engineering formulas, and deterministic calculations (Qwen 2.5 Coder 7B).",
    ),
    ModelSpec(
        name=settings.VISION_MODEL,  # "moondream"
        capabilities=["vision", "scanned_document", "image", "diagram", "pid", "visual_analysis"],
        modality="multimodal",
        role="vision",
        priority=80,
        enabled=True,
        fallback_rank=1,
        timeout_seconds=120,
        description="Multimodal vision inspection for scanned reports and P&ID diagrams (Moondream).",
    ),
    ModelSpec(
        name=settings.GENERAL_MODEL,  # "mistral:latest"
        capabilities=["general", "instruction", "qa", "fallback_reasoning"],
        modality="text",
        role="general",
        priority=70,
        enabled=True,
        fallback_rank=2,
        timeout_seconds=120,
        description="General instruction following and fast local fallback (Mistral 7B).",
    ),
]

# Strict capability fallback rules:
# Vision tasks MUST NOT fallback to text models (strict capability isolation)
CAPABILITY_FALLBACK_RULES: Dict[str, List[str]] = {
    "vision": ["moondream", "moondream:latest", "llava", "llama3.2-vision"],
    "coding": ["qwen2.5-coder:7b", "qwen2.5-coder:latest", "llama3.1:8b"],
    "reasoning": ["llama3.1:8b", "llama3.1:latest", "mistral:latest"],
    "general": ["mistral:latest", "llama3.1:8b"],
}


class ModelRegistry:
    """Capability-based local model registry with availability caching and explicit fallback policies."""

    def __init__(
        self,
        client: Optional[LocalModelClient] = None,
        specs: Optional[List[ModelSpec]] = None,
        cache_ttl_seconds: float = 60.0,
    ):
        self.client = client or get_local_model_client()
        self._specs: Dict[str, ModelSpec] = {s.name: s for s in (specs or DEFAULT_MODEL_SPECS)}
        self._cache_ttl = cache_ttl_seconds
        self._last_refresh_time: float = 0.0
        self._cached_available_models: List[str] = []

    @property
    def specs(self) -> Dict[str, ModelSpec]:
        return self._specs

    async def refresh_available_models(self, force: bool = False) -> List[str]:
        """Queries local Ollama runtime with lightweight caching (TTL 60s)."""
        now = time.time()
        if not force and self._cached_available_models and (now - self._last_refresh_time < self._cache_ttl):
            return self._cached_available_models

        try:
            models_meta = await self.client.list_models()
            self._cached_available_models = [m.get("name", "") for m in models_meta if m.get("name")]
            self._last_refresh_time = now
            logger.info(f"Registry refreshed: {len(self._cached_available_models)} local model(s) available: {self._cached_available_models}")
        except Exception as e:
            logger.warning(f"Could not refresh local model availability from client: {e}")
            if not self._cached_available_models:
                # Fallback to configured names in specs
                self._cached_available_models = list(self._specs.keys())
        return self._cached_available_models

    def is_model_available(self, model_name: str) -> bool:
        """Determines if a model is currently available locally."""
        if not self._cached_available_models:
            return True  # If not yet refreshed, assume present pending first refresh
        norm = model_name.lower()
        return any(norm == m.lower() or norm in m.lower() or m.lower() in norm for m in self._cached_available_models)

    def get_spec(self, model_name: str) -> Optional[ModelSpec]:
        """Look up specification for a model name."""
        if model_name in self._specs:
            return self._specs[model_name]
        norm = model_name.lower()
        for k, v in self._specs.items():
            if norm == k.lower() or norm in k.lower():
                return v
        return None

    def get_fallback_chain(self, role: str) -> List[str]:
        """Returns the ordered fallback candidate models for a given capability role."""
        candidates = CAPABILITY_FALLBACK_RULES.get(role, [])
        return candidates

    async def resolve_model_for_role(self, role: str) -> Tuple[str, List[str], bool, str]:
        """
        Resolves the best available local model for a capability role.
        Returns: (selected_model, fallback_chain, is_fallback, reason)
        """
        await self.refresh_available_models()
        fallback_chain = self.get_fallback_chain(role)

        if not fallback_chain:
            # Default to reasoning model
            return settings.REASONING_MODEL, [], False, f"Defaulted to primary model {settings.REASONING_MODEL}"

        primary_model = fallback_chain[0]
        if self.is_model_available(primary_model):
            return primary_model, fallback_chain, False, f"Primary model '{primary_model}' available for {role}."

        # Primary not available: look for permitted fallback
        for fb in fallback_chain[1:]:
            if self.is_model_available(fb):
                logger.info(f"Fallback active for role '{role}': '{primary_model}' unavailable, using '{fb}'")
                return fb, fallback_chain, True, f"Primary model '{primary_model}' unavailable; fell back to permitted '{fb}' for {role}."

        # If vision, do NOT fallback to text model
        if role == "vision":
            logger.error("Vision task has no available multimodal model locally. Text models strictly prohibited as vision fallback.")
            return primary_model, fallback_chain, False, f"Vision model '{primary_model}' configured; no vision fallback installed."

        # If all else fails, return primary model
        return primary_model, fallback_chain, False, f"Selected configured primary '{primary_model}' for {role}."

    async def get_model_for_capabilities(self, required_capabilities: List[str]) -> str:
        """Backwards-compatible resolution of best local model matching capabilities."""
        req_set = set(c.lower() for c in required_capabilities)

        if req_set.intersection({"vision", "scanned_document", "image", "diagram", "pid", "visual_analysis"}):
            model, _, _, _ = await self.resolve_model_for_role("vision")
            return model

        if req_set.intersection({"coding", "python", "mathematics", "calculation"}):
            model, _, _, _ = await self.resolve_model_for_role("coding")
            return model

        model, _, _, _ = await self.resolve_model_for_role("reasoning")
        return model

    async def get_registry_info(self) -> List[Dict[str, Any]]:
        """Returns structured metadata for UI and /api/models."""
        await self.refresh_available_models()
        info = []
        for role, chain in CAPABILITY_FALLBACK_RULES.items():
            primary = chain[0]
            spec = self.get_spec(primary)
            is_present = self.is_model_available(primary)
            caps = spec.capabilities if spec else [role]
            desc = spec.description if spec else f"{role.capitalize()} capability"
            info.append({
                "id": primary,
                "role": role,
                "name": primary.split(":")[0].upper(),
                "capabilities": caps,
                "modality": spec.modality if spec else "text",
                "status": "available" if is_present else "configured",
                "fallback_chain": chain[1:],
                "description": desc,
            })
        return info


# Global registry singleton
model_registry = ModelRegistry()
