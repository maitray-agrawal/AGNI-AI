import asyncio
import pytest
from backend.app.models.router import model_router
from backend.app.agent.graph import run_agent


@pytest.mark.asyncio
async def test_vertical_slice_reasoning():
    """Test A: Summarize industrial report -> reasoning model routed and executed."""
    task = "Summarize this industrial report for Crude Distillation Unit pump maintenance."
    decision = await model_router.route_task(task)
    
    # Assert router mapped to reasoning capability
    assert "reasoning" in decision.required_capabilities or decision.task_type in ["general_reasoning", "inspection_workflow"]
    print(f"\n[Test A Routing] Model: {decision.selected_model}, Type: {decision.task_type}")

    # Run LangGraph agent
    result = await run_agent(task)
    assert result is not None
    assert result.get("current_step") == "finalized"
    assert len(result.get("plan", [])) > 0
    assert result.get("selected_model") is not None
    assert result.get("model_response") is not None
    assert len(result.get("model_response")) > 10
    assert result.get("verification", {}).get("status") == "passed"
    assert len(result.get("trace", [])) >= 4
    print(f"[Test A Result] Generated length: {len(result.get('model_response'))} chars")
    print(f"[Test A Trace Steps]: {[t['step'] for t in result.get('trace', [])]}")


@pytest.mark.asyncio
async def test_vertical_slice_coding():
    """Test B: Calculate percentage reduction from 8.2 mm to 7.4 mm -> coder model routed and executed."""
    task = "Calculate the percentage reduction from 8.2 mm to 7.4 mm wall thickness."
    decision = await model_router.route_task(task)
    
    # Assert router mapped to coding capability
    assert "coding" in decision.required_capabilities or decision.task_type == "coding_calculation"
    assert "coder" in decision.selected_model.lower() or "qwen" in decision.selected_model.lower()
    print(f"\n[Test B Routing] Model: {decision.selected_model}, Type: {decision.task_type}")

    # Run LangGraph agent
    result = await run_agent(task)
    assert result is not None
    assert result.get("current_step") == "finalized"
    assert len(result.get("plan", [])) > 0
    assert result.get("selected_model") is not None
    assert result.get("model_response") is not None
    assert len(result.get("model_response")) > 10
    assert result.get("verification", {}).get("status") == "passed"
    assert len(result.get("trace", [])) >= 4
    print(f"[Test B Result]:\n{result.get('model_response')[:250]}...")
    print(f"[Test B Trace Steps]: {[t['step'] for t in result.get('trace', [])]}")
