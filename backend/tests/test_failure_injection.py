import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from backend.app.models.client import (
    OllamaProvider,
    ModelFailureType,
    ModelTimeoutError,
    ModelConnectionError,
    ModelNotFoundError,
    ModelInferenceError,
)
from backend.app.models.registry import ModelRegistry, ModelSpec, CAPABILITY_FALLBACK_RULES
from backend.app.models.router import CapabilityRouter
from backend.app.agent.planner import generate_plan, PlanValidationError
from backend.app.agent.verifier import verify_execution
from backend.app.agent.executor import execute_task


@pytest.mark.asyncio
async def test_failure_ollama_connection_error():
    """Validates that a connection failure to Ollama is explicitly classified as CONNECTION_ERROR."""
    provider = OllamaProvider(base_url="http://127.0.0.1:99999", timeout=1, max_retries=0)
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        text, meta = await provider.generate_with_meta(model="llama3.1:8b", prompt="Hello")
        assert meta.success is False
        assert meta.error_type == ModelFailureType.CONNECTION_ERROR.value
        assert "Cannot connect to local Ollama" in meta.error_message


@pytest.mark.asyncio
async def test_failure_model_timeout():
    """Validates that an inference timeout is explicitly classified as TIMEOUT."""
    provider = OllamaProvider(base_url="http://127.0.0.1:11434", timeout=1, max_retries=0)
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Read timed out")):
        text, meta = await provider.generate_with_meta(model="llama3.1:8b", prompt="Hello")
        assert meta.success is False
        assert meta.error_type == ModelFailureType.TIMEOUT.value
        assert "timed out" in meta.error_message


@pytest.mark.asyncio
async def test_failure_model_not_found():
    """Validates HTTP 404 from Ollama is classified as MODEL_NOT_FOUND."""
    provider = OllamaProvider(base_url="http://127.0.0.1:11434", timeout=1, max_retries=0)
    mock_resp = MagicMock(status_code=404)
    with patch("httpx.AsyncClient.post", side_effect=httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_resp)):
        text, meta = await provider.generate_with_meta(model="non_existent_model:99b", prompt="Hello")
        assert meta.success is False
        assert meta.error_type == ModelFailureType.MODEL_NOT_FOUND.value


@pytest.mark.asyncio
async def test_failure_vision_fallback_to_text_strictly_blocked():
    """CRITICAL SECURITY GATE: Vision tasks must NEVER silently fall back to text models."""
    mock_client = AsyncMock()
    # List models returns only text models
    mock_client.list_models.return_value = [{"name": "llama3.1:8b"}, {"name": "mistral:latest"}]

    reg = ModelRegistry(client=mock_client)
    await reg.refresh_available_models(force=True)

    # Resolve model for vision role
    selected_model, chain, is_fb, reason = await reg.resolve_model_for_role("vision")
    
    # Must NOT select llama3.1:8b or mistral as vision fallback
    assert "moondream" in selected_model or "vision" in selected_model
    assert "llama3.1:8b" not in chain
    assert "mistral:latest" not in chain
    print(f"\n[Vision Fallback Isolation Verified]: {selected_model} (Chain: {chain})")


@pytest.mark.asyncio
async def test_failure_verifier_rejects_empty_output():
    """Verifier must reject empty model outputs and fail Check 1."""
    state = {
        "task_type": "general_reasoning",
        "model_response": "",
        "errors": [],
        "tool_results": [],
        "outputs": [],
    }
    verdict = await verify_execution(state)
    assert verdict["status"] == "failed"
    check1 = next(c for c in verdict["checks"] if c["name"] == "model_output_valid")
    assert check1["passed"] is False


@pytest.mark.asyncio
async def test_failure_verifier_rejects_error_response():
    """Verifier must reject outputs that are execution error messages."""
    state = {
        "task_type": "general_reasoning",
        "model_response": "Inference failed on model llama3.1:8b: All connection attempts failed",
        "errors": ["Inference failed on model llama3.1:8b"],
        "tool_results": [],
        "outputs": [],
    }
    verdict = await verify_execution(state)
    assert verdict["status"] == "failed"
    check1 = next(c for c in verdict["checks"] if c["name"] == "model_output_valid")
    check2 = next(c for c in verdict["checks"] if c["name"] == "zero_execution_errors")
    assert check1["passed"] is False
    assert check2["passed"] is False


@pytest.mark.asyncio
async def test_failure_verifier_rejects_missing_equipment_tag():
    """Verifier must reject inspection workflows that fail to identify an asset tag."""
    state = {
        "task_type": "inspection_workflow",
        "model_response": "The pump has wall thickness 4.2 mm and vibration 7.8 mm/s. We recommend replacement.",
        "errors": [],
        "tool_results": [{"tool": "qdrant_retriever", "success": True}],
        "outputs": [{"type": "docx", "filename": "test.docx", "path": "test.docx", "size_bytes": 10000}],
    }
    # Notice: No tag like P-204 in response
    verdict = await verify_execution(state)
    assert verdict["status"] == "failed"
    tag_check = next(c for c in verdict["checks"] if c["name"] == "equipment_tag_identified")
    assert tag_check["passed"] is False


@pytest.mark.asyncio
async def test_failure_verifier_rejects_missing_docx():
    """Verifier must reject inspection workflow if deliverable DOCX is absent."""
    state = {
        "task_type": "inspection_workflow",
        "model_response": "Asset P-204 evaluated. Wall thickness 4.2 mm, vibration 7.8 mm/s. Mandatory replacement recommended.",
        "errors": [],
        "tool_results": [{"tool": "qdrant_retriever", "success": True}],
        "outputs": [],  # Missing outputs
    }
    verdict = await verify_execution(state)
    assert verdict["status"] == "failed"
    docx_check = next(c for c in verdict["checks"] if c["name"] == "deliverable_generated")
    assert docx_check["passed"] is False
