from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
import logging
from backend.app.config import settings

logger = logging.getLogger("agni.models.client")


class LocalModelClient(ABC):
    """Abstract interface for local on-premise model runtimes (Ollama, LM Studio, vLLM)."""

    @abstractmethod
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        pass

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        pass

    @abstractmethod
    async def vision(
        self,
        model: str,
        prompt: str,
        images_base64: List[str],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        pass

    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        pass


class OllamaProvider(LocalModelClient):
    """Concrete provider for local Ollama runtime on 127.0.0.1:11434."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 120):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout = timeout

    async def list_models(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("models", [])
        except Exception as e:
            logger.warning(f"Ollama list_models failed on {url}: {e}")
        return []

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "5m",
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama generate failed ({model}): {e}")
            raise RuntimeError(f"Local Ollama inference failed for model '{model}': {e}")

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": "5m",
        }
        if options:
            payload["options"] = options

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.error(f"Ollama chat failed ({model}): {e}")
            raise RuntimeError(f"Local Ollama chat failed for model '{model}': {e}")

    async def vision(
        self,
        model: str,
        prompt: str,
        images_base64: List[str],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "images": images_base64,
            "stream": False,
            "keep_alive": "5m",
        }
        if options:
            payload["options"] = options

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama vision inference failed ({model}): {e}")
            raise RuntimeError(f"Local Ollama vision failed for model '{model}': {e}")


def get_local_model_client() -> LocalModelClient:
    """Factory function returning configured local inference client."""
    return OllamaProvider(base_url=settings.OLLAMA_BASE_URL, timeout=settings.DEFAULT_TIMEOUT_SECONDS)
