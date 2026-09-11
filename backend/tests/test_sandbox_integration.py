import pytest
from backend.app.agent.graph import run_agent
from backend.app.models.client import ModelInvocationMetadata


@pytest.mark.asyncio
async def test_sandbox_integration_live_agent():
    """
    Validates P0-2:
    Submits a calculation task through the full run_agent() pipeline with live local model inference.
    Asserts that:
    1. The model router classifies it as coding_calculation and routes to qwen2.5-coder:7b.
    2. The model generates executable Python code.
    3. The agent extracts and executes the code via backend.app.security.sandbox.
    4. tool_results contains 'code_sandbox' with success == True.
    5. The sandbox stdout contains the correct numeric computation (approx 48.78% or 48.8%).
    6. The 8-point verifier's critical_findings_identified check passes based on verified sandbox output.
    """
    task = "Calculate the percentage reduction from 8.2 mm to 4.2 mm wall thickness."
    print(f"\n[SANDBOX INTEGRATION TEST] Submitting task: {task}")

    result = await run_agent(task=task)

    assert result is not None
    assert result.get("task_type") == "coding_calculation"
    assert result.get("selected_model") in ["qwen2.5-coder:7b", "llama3.1:8b"]

    # Assert tool_results contains code_sandbox
    tool_results = result.get("tool_results", [])
    sandbox_tools = [t for t in tool_results if t.get("tool") == "code_sandbox"]
    assert len(sandbox_tools) >= 1, f"Expected code_sandbox in tool_results, got: {tool_results}"

    sb_tool = sandbox_tools[0]
    print(f"\n[Sandbox Tool Result]: {sb_tool}")
    assert sb_tool.get("success") is True
    assert "output" in sb_tool
    stdout = sb_tool["output"].get("stdout", "")
    print(f"\n[Sandbox Live stdout]:\n{stdout}")

    # The exact reduction from 8.2 to 4.2 is (8.2 - 4.2) / 8.2 * 100 = 48.78048...%
    assert any(expected in stdout for expected in ["48.78", "48.8", "48.79", "48.7"]), (
        f"Expected ~48.78% in sandbox stdout, got:\n{stdout}"
    )

    # Assert authoritative sandbox output was appended to model_response
    model_response = result.get("model_response", "")
    assert "[Deterministic Sandbox Execution Result]:" in model_response
    assert stdout in model_response

    # Assert 8-point verifier evaluated the sandbox tool execution
    verification = result.get("verification", {})
    checks = {c["name"]: c for c in verification.get("checks", [])}
    assert "critical_findings_identified" in checks
    assert checks["critical_findings_identified"]["passed"] is True
    assert "code sandbox" in checks["critical_findings_identified"]["details"]

    assert checks["zero_execution_errors"]["passed"] is True
    assert verification.get("status") == "passed"
    assert result.get("final_status") == "completed"


@pytest.mark.asyncio
async def test_sandbox_integration_extraction_failure_propagation(monkeypatch):
    """
    Validates P0-2:
    If the model outputs unverified prose without code blocks, the agent must NOT
    silently pretend it was sandbox-verified. It must record an error and fail the verifier gate.
    """
    async def mock_generate_prose(*args, **kwargs):
        meta = ModelInvocationMetadata(
            requested_model="qwen2.5-coder:7b",
            actual_model="qwen2.5-coder:7b",
            success=True,
            provider="ollama",
            local_endpoint="http://127.0.0.1:11434",
            duration_ms=10,
        )
        return "I calculated the value manually without any code block: 48.8% reduction.", meta

    # Monkeypatch OllamaProvider.generate_with_meta to return un-fenced prose
    monkeypatch.setattr(
        "backend.app.models.client.OllamaProvider.generate_with_meta",
        mock_generate_prose,
    )

    task = "Calculate reduction from 8.2mm to 4.2mm without code."
    result = await run_agent(task=task)

    tool_results = result.get("tool_results", [])
    sandbox_tools = [t for t in tool_results if t.get("tool") == "code_sandbox"]
    assert len(sandbox_tools) >= 1
    assert sandbox_tools[0].get("success") is False

    # Verifier must reject unverified calculation
    verification = result.get("verification", {})
    checks = {c["name"]: c for c in verification.get("checks", [])}
    assert checks["critical_findings_identified"]["passed"] is False
    assert "Missing verified code sandbox" in checks["critical_findings_identified"]["details"]
