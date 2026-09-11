import pytest
from unittest.mock import AsyncMock, patch
from backend.app.agent.graph import run_agent


@pytest.mark.asyncio
async def test_agent_retries_on_verification_failure_and_recovers(monkeypatch):
    """
    Validates P0-1:
    1. Verifier failure on pass 1 triggers adaptive retry back to executor.
    2. Retry prompt injects failed check names.
    3. Trace contains distinct 'executor_retry' event.
    4. Successful verification on pass 2 finalizes with completed status.
    """
    call_count = 0
    executed_tasks = []

    async def mock_execute_task(state):
        nonlocal call_count
        executed_tasks.append(state.get("task", ""))
        return {
            "model_response": "Valid response text after correction",
            "actual_model": "llama3.1:8b",
            "model_metadata": None,
            "tool_results": [{"tool": "mock_tool", "output": "ok"}],
            "outputs": [{"type": "docx", "filename": "test.docx", "path": "outputs/test.docx", "size_bytes": 12000}],
            "errors": [],
            "fallbacks": [],
            "duration_ms": 100,
        }

    async def mock_verify_execution(state):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return {
                "status": "failed",
                "passed_count": 7,
                "total_count": 8,
                "checks": [
                    {"name": "critical_findings_identified", "passed": False, "details": "Missing measurement"},
                    {"name": "equipment_tag_identified", "passed": True, "details": "Tag found"},
                ],
            }
        else:
            return {
                "status": "passed",
                "passed_count": 8,
                "total_count": 8,
                "checks": [
                    {"name": "critical_findings_identified", "passed": True, "details": "Corrected on retry"},
                    {"name": "equipment_tag_identified", "passed": True, "details": "Tag found"},
                ],
            }

    monkeypatch.setattr("backend.app.agent.graph.execute_task", mock_execute_task)
    monkeypatch.setattr("backend.app.agent.graph.verify_execution", mock_verify_execution)

    result = await run_agent("Analyze pump P-204 inspection report")

    assert result is not None
    assert result.get("retry_count") == 1
    assert result.get("verification", {}).get("status") == "passed"
    assert result.get("final_status") == "completed"

    # Assert trace progression
    trace_steps = [t["step"] for t in result.get("trace", [])]
    print(f"\n[Trace Steps with Recovery]: {trace_steps}")
    assert "planner" in trace_steps
    assert "router" in trace_steps
    assert "executor" in trace_steps
    assert "verifier" in trace_steps
    assert "executor_retry" in trace_steps
    assert trace_steps.count("verifier") == 2
    assert "finalizer" in trace_steps

    # Assert retry trace event details
    retry_events = [t for t in result.get("trace", []) if t["step"] == "executor_retry"]
    assert len(retry_events) == 1
    details = retry_events[0].get("details", {})
    assert details.get("retry_attempt") == 1
    assert "critical_findings_identified" in details.get("failed_checks_retried", [])

    # Assert corrective instruction was injected into prompt for the retry execution
    assert len(executed_tasks) == 2
    assert "critical_findings_identified" in executed_tasks[1]
    assert "[RETRY CORRECTION REQUIRED" in executed_tasks[1]


@pytest.mark.asyncio
async def test_agent_retry_capped_at_one_attempt(monkeypatch):
    """
    Validates P0-1:
    Even if verifier continues to fail on retry, agent terminates after exactly 1 retry
    and does not loop infinitely.
    """
    verify_call_count = 0

    async def mock_execute_task(state):
        return {
            "model_response": "Still failing response",
            "actual_model": "llama3.1:8b",
            "errors": ["Persistent execution error"],
            "tool_results": [],
            "outputs": [],
            "fallbacks": [],
            "duration_ms": 50,
        }

    async def mock_verify_always_fail(state):
        nonlocal verify_call_count
        verify_call_count += 1
        return {
            "status": "failed",
            "passed_count": 5,
            "total_count": 8,
            "checks": [{"name": "zero_execution_errors", "passed": False, "details": "Persistent error"}],
        }

    monkeypatch.setattr("backend.app.agent.graph.execute_task", mock_execute_task)
    monkeypatch.setattr("backend.app.agent.graph.verify_execution", mock_verify_always_fail)

    result = await run_agent("Unrecoverable test task")

    assert result is not None
    assert result.get("retry_count") == 1
    assert verify_call_count == 2
    assert result.get("verification", {}).get("status") == "failed"
    assert result.get("final_status") in ["completed_with_warnings", "failed"]

    # Ensure it finalized and didn't execute beyond 1 retry
    trace_steps = [t["step"] for t in result.get("trace", [])]
    print(f"\n[Trace Steps with Max Retry Cap]: {trace_steps}")
    assert trace_steps.count("executor_retry") == 1
    assert trace_steps.count("verifier") == 2
    assert trace_steps[-1] == "finalizer"
