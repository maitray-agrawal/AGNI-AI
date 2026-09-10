from abc import ABC, abstractmethod
from enum import Enum
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import httpx
import logging
from pydantic import BaseModel, Field
from backend.app.config import settings

logger = logging.getLogger("agni.models.client")


class ModelFailureType(str, Enum):
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    EXECUTION_ERROR = "EXECUTION_ERROR"


class ModelInferenceError(RuntimeError):
    """Base exception for local model inference failures."""
    def __init__(self, message: str, failure_type: ModelFailureType = ModelFailureType.EXECUTION_ERROR):
        super().__init__(message)
        self.failure_type = failure_type


class ModelTimeoutError(ModelInferenceError):
    """Raised when local inference times out."""
    def __init__(self, message: str):
        super().__init__(message, failure_type=ModelFailureType.TIMEOUT)


class ModelConnectionError(ModelInferenceError):
    """Raised when connection to local model runtime (Ollama) fails."""
    def __init__(self, message: str):
        super().__init__(message, failure_type=ModelFailureType.CONNECTION_ERROR)


class ModelNotFoundError(ModelInferenceError):
    """Raised when the requested model is not installed or available locally."""
    def __init__(self, message: str):
        super().__init__(message, failure_type=ModelFailureType.MODEL_NOT_FOUND)


class ModelInvocationMetadata(BaseModel):
    """Structured telemetry captured for every local model invocation."""
    request_id: Optional[str] = None
    step_id: Optional[str] = None
    requested_model: str
    actual_model: str
    capability: Optional[str] = None
    success: bool = True
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    attempt: int = 1
    retry_count: int = 0
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_ms: int = 0
    timeout_seconds: int = 120
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    provider: str = "ollama"
    local_endpoint: str = "http://127.0.0.1:11434"


class LocalModelClient(ABC):
    """Abstract interface for local on-premise model runtimes."""

    @abstractmethod
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Backwards-compatible generation returning pure text."""
        pass

    @abstractmethod
    @abstractmethod
    async def generate_with_meta(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> Tuple[str, ModelInvocationMetadata]:
        """Generation returning both text and structured execution telemetry."""
        pass

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Backwards-compatible chat returning message content."""
        pass

    @abstractmethod
    async def chat_with_meta(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> Tuple[str, ModelInvocationMetadata]:
        """Chat returning content and structured telemetry."""
        pass

    @abstractmethod
    async def vision(
        self,
        model: str,
        prompt: str,
        images_base64: List[str],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Backwards-compatible vision inference returning analysis text."""
        pass

    @abstractmethod
    async def vision_with_meta(
        self,
        model: str,
        prompt: str,
        images_base64: List[str],
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> Tuple[str, ModelInvocationMetadata]:
        """Vision returning text and structured execution telemetry."""
        pass

    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        pass


class OllamaProvider(LocalModelClient):
    """Hardened provider for local Ollama runtime on 127.0.0.1:11434."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 180, max_retries: int = 1):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def _classify_exception(self, e: Exception) -> Tuple[ModelFailureType, str]:
        """Classify exceptions into deterministic failure categories."""
        msg = str(e)
        if isinstance(e, (httpx.TimeoutException, TimeoutError)):
            return ModelFailureType.TIMEOUT, f"Inference timed out after {self.timeout}s: {msg}"
        if isinstance(e, (httpx.ConnectError, httpx.NetworkError)):
            return ModelFailureType.CONNECTION_ERROR, f"Cannot connect to local Ollama runtime on {self.base_url}: {msg}"
        if isinstance(e, httpx.HTTPStatusError):
            if e.response.status_code == 404:
                return ModelFailureType.MODEL_NOT_FOUND, f"Model not found in local Ollama: {msg}"
            return ModelFailureType.INVALID_RESPONSE, f"Ollama HTTP error {e.response.status_code}: {msg}"
        return ModelFailureType.EXECUTION_ERROR, f"Inference execution error: {msg}"

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

    async def check_health(self) -> Dict[str, Any]:
        """Check runtime connectivity and latency."""
        t0 = time.time()
        models = await self.list_models()
        latency_ms = int((time.time() - t0) * 1000)
        return {
            "reachable": len(models) > 0,
            "endpoint": self.base_url,
            "models_count": len(models),
            "latency_ms": latency_ms,
        }

    async def generate_with_meta(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> Tuple[str, ModelInvocationMetadata]:
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

        started_at = datetime.utcnow().isoformat()
        t0 = time.time()
        last_err: Optional[Exception] = None

        # Bounded retry for transient connection/network errors only
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    response_text = data.get("response", "").strip()

                    completed_at = datetime.utcnow().isoformat()
                    duration_ms = int((time.time() - t0) * 1000)

                    meta = ModelInvocationMetadata(
                        request_id=request_id,
                        step_id=step_id,
                        requested_model=model,
                        actual_model=model,
                        success=True,
                        attempt=attempt + 1,
                        retry_count=attempt,
                        started_at=started_at,
                        completed_at=completed_at,
                        duration_ms=duration_ms,
                        timeout_seconds=self.timeout,
                        provider="ollama",
                        local_endpoint=self.base_url,
                    )
                    return response_text, meta

            except Exception as e:
                last_err = e
                fail_type, fail_msg = self._classify_exception(e)
                # Only retry on transient connection error on first attempt
                if attempt < self.max_retries and fail_type in (ModelFailureType.CONNECTION_ERROR, ModelFailureType.TIMEOUT):
                    logger.warning(f"Transient Ollama error on attempt {attempt + 1}, retrying after 0.5s: {fail_msg}")
                    time.sleep(0.5)
                    continue
                break

        completed_at = datetime.utcnow().isoformat()
        duration_ms = int((time.time() - t0) * 1000)
        fail_type, fail_msg = self._classify_exception(last_err)

        meta = ModelInvocationMetadata(
            request_id=request_id,
            step_id=step_id,
            requested_model=model,
            actual_model=model,
            success=False,
            attempt=self.max_retries + 1,
            retry_count=self.max_retries,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            timeout_seconds=self.timeout,
            error_type=fail_type.value,
            error_message=fail_msg,
            provider="ollama",
            local_endpoint=self.base_url,
        )
        logger.error(f"Ollama generate failed ({model}) [{fail_type.value}]: {fail_msg}")
        return "", meta

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        text, meta = await self.generate_with_meta(model, prompt, system=system, options=options)
        if not meta.success:
            if meta.error_type == ModelFailureType.TIMEOUT.value:
                raise ModelTimeoutError(meta.error_message or "Model generation timed out")
            elif meta.error_type == ModelFailureType.CONNECTION_ERROR.value:
                raise ModelConnectionError(meta.error_message or "Connection failed")
            elif meta.error_type == ModelFailureType.MODEL_NOT_FOUND.value:
                raise ModelNotFoundError(meta.error_message or "Model not found")
            raise ModelInferenceError(meta.error_message or f"Inference failed for {model}")
        return text

    async def chat_with_meta(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> Tuple[str, ModelInvocationMetadata]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": "5m",
        }
        if options:
            payload["options"] = options

        started_at = datetime.utcnow().isoformat()
        t0 = time.time()
        last_err: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data.get("message", {}).get("content", "").strip()

                    completed_at = datetime.utcnow().isoformat()
                    duration_ms = int((time.time() - t0) * 1000)

                    meta = ModelInvocationMetadata(
                        request_id=request_id,
                        step_id=step_id,
                        requested_model=model,
                        actual_model=model,
                        success=True,
                        attempt=attempt + 1,
                        retry_count=attempt,
                        started_at=started_at,
                        completed_at=completed_at,
                        duration_ms=duration_ms,
                        timeout_seconds=self.timeout,
                        provider="ollama",
                        local_endpoint=self.base_url,
                    )
                    return content, meta

            except Exception as e:
                last_err = e
                fail_type, fail_msg = self._classify_exception(e)
                if attempt < self.max_retries and fail_type in (ModelFailureType.CONNECTION_ERROR, ModelFailureType.TIMEOUT):
                    logger.warning(f"Transient Ollama chat error on attempt {attempt + 1}, retrying after 0.5s: {fail_msg}")
                    time.sleep(0.5)
                    continue
                break

        completed_at = datetime.utcnow().isoformat()
        duration_ms = int((time.time() - t0) * 1000)
        fail_type, fail_msg = self._classify_exception(last_err)

        meta = ModelInvocationMetadata(
            request_id=request_id,
            step_id=step_id,
            requested_model=model,
            actual_model=model,
            success=False,
            attempt=self.max_retries + 1,
            retry_count=self.max_retries,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            timeout_seconds=self.timeout,
            error_type=fail_type.value,
            error_message=fail_msg,
            provider="ollama",
            local_endpoint=self.base_url,
        )
        logger.error(f"Ollama chat failed ({model}) [{fail_type.value}]: {fail_msg}")
        return "", meta

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        content, meta = await self.chat_with_meta(model, messages, options=options)
        if not meta.success:
            if meta.error_type == ModelFailureType.TIMEOUT.value:
                raise ModelTimeoutError(meta.error_message or "Model chat timed out")
            elif meta.error_type == ModelFailureType.CONNECTION_ERROR.value:
                raise ModelConnectionError(meta.error_message or "Connection failed")
            elif meta.error_type == ModelFailureType.MODEL_NOT_FOUND.value:
                raise ModelNotFoundError(meta.error_message or "Model not found")
            raise ModelInferenceError(meta.error_message or f"Chat failed for {model}")
        return content

    async def vision_with_meta(
        self,
        model: str,
        prompt: str,
        images_base64: List[str],
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> Tuple[str, ModelInvocationMetadata]:
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

        started_at = datetime.utcnow().isoformat()
        t0 = time.time()
        last_err: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    response_text = data.get("response", "").strip()

                    completed_at = datetime.utcnow().isoformat()
                    duration_ms = int((time.time() - t0) * 1000)

                    meta = ModelInvocationMetadata(
                        request_id=request_id,
                        step_id=step_id,
                        requested_model=model,
                        actual_model=model,
                        capability="vision",
                        success=True,
                        attempt=attempt + 1,
                        retry_count=attempt,
                        started_at=started_at,
                        completed_at=completed_at,
                        duration_ms=duration_ms,
                        timeout_seconds=self.timeout,
                        provider="ollama",
                        local_endpoint=self.base_url,
                    )
                    return response_text, meta

            except Exception as e:
                last_err = e
                fail_type, fail_msg = self._classify_exception(e)
                if attempt < self.max_retries and fail_type in (ModelFailureType.CONNECTION_ERROR, ModelFailureType.TIMEOUT):
                    logger.warning(f"Transient Ollama vision error on attempt {attempt + 1}, retrying after 0.5s: {fail_msg}")
                    time.sleep(0.5)
                    continue
                break

        completed_at = datetime.utcnow().isoformat()
        duration_ms = int((time.time() - t0) * 1000)
        fail_type, fail_msg = self._classify_exception(last_err)

        meta = ModelInvocationMetadata(
            request_id=request_id,
            step_id=step_id,
            requested_model=model,
            actual_model=model,
            capability="vision",
            success=False,
            attempt=self.max_retries + 1,
            retry_count=self.max_retries,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            timeout_seconds=self.timeout,
            error_type=fail_type.value,
            error_message=fail_msg,
            provider="ollama",
            local_endpoint=self.base_url,
        )
        logger.error(f"Ollama vision failed ({model}) [{fail_type.value}]: {fail_msg}")
        return "", meta

    async def vision(
        self,
        model: str,
        prompt: str,
        images_base64: List[str],
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        text, meta = await self.vision_with_meta(model, prompt, images_base64, options=options)
        if not meta.success:
            if meta.error_type == ModelFailureType.TIMEOUT.value:
                raise ModelTimeoutError(meta.error_message or "Vision inference timed out")
            elif meta.error_type == ModelFailureType.CONNECTION_ERROR.value:
                raise ModelConnectionError(meta.error_message or "Connection failed")
            elif meta.error_type == ModelFailureType.MODEL_NOT_FOUND.value:
                raise ModelNotFoundError(meta.error_message or "Model not found")
            raise ModelInferenceError(meta.error_message or f"Vision failed for {model}")
        return text


def get_local_model_client() -> LocalModelClient:
    """Factory function returning configured local inference client."""
    return OllamaProvider(base_url=settings.OLLAMA_BASE_URL, timeout=settings.DEFAULT_TIMEOUT_SECONDS)
