import pytest
from unittest.mock import AsyncMock
from backend.app.models.registry import ModelRegistry, ModelSpec
from backend.app.models.router import CapabilityRouter, TaskProfile
from backend.app.agent.planner import generate_plan, PlanStep
from backend.app.agent.state import AgentState
from backend.app.agent.verifier import verify_execution


@pytest.mark.asyncio
async def test_registry_specs_and_fallback_chains():
    """Validates ModelRegistry specifications and capability constraints."""
    mock_client = AsyncMock()
    mock_client.list_models.return_value = [
        {"name": "llama3.1:8b"},
        {"name": "qwen2.5-coder:7b"},
        {"name": "moondream"},
        {"name": "mistral:latest"},
    ]
    registry = ModelRegistry(client=mock_client)
    models = await registry.refresh_available_models(force=True)
    assert len(models) == 4

    # Verify specs
    reasoning_spec = registry.get_spec("llama3.1:8b")
    assert reasoning_spec is not None
    assert reasoning_spec.role == "reasoning"
    assert "reasoning" in reasoning_spec.capabilities

    coding_spec = registry.get_spec("qwen2.5-coder:7b")
    assert coding_spec is not None
    assert coding_spec.role == "coding"

    vision_spec = registry.get_spec("moondream")
    assert vision_spec is not None
    assert vision_spec.modality == "multimodal"

    # Fallback chain check
    reasoning_chain = registry.get_fallback_chain("reasoning")
    assert "llama3.1:8b" in reasoning_chain
    assert "mistral:latest" in reasoning_chain


@pytest.mark.asyncio
async def test_router_profiling_and_scoring():
    """Validates deterministic task profiling and capability assignment."""
    router = CapabilityRouter()

    # 1. Coding task profiling
    code_task = "Calculate the percentage reduction from 8.2 mm to 4.2 mm."
    profile_c = router.profile_task(code_task)
    assert profile_c.capability == "coding"
    assert profile_c.task_type == "coding_calculation"

    # 2. Vision task profiling
    vision_task = "Analyze the components in this P&ID drawing."
    profile_v = router.profile_task(vision_task, files=["drawing.png"])
    assert profile_v.capability == "vision"
    assert profile_v.modality == "multimodal"
    assert profile_v.task_type == "visual_inspection"

    # 3. Inspection task profiling
    insp_task = "Analyze inspection report for CDU pump P-204."
    profile_i = router.profile_task(insp_task, files=["report.pdf"])
    assert profile_i.capability == "reasoning"
    assert profile_i.task_type == "inspection_workflow"


@pytest.mark.asyncio
async def test_planner_schema_conformity():
    """Validates that generate_plan outputs strictly validated PlanStep dictionaries."""
    # Inspection plan
    plan_insp = await generate_plan("Analyze inspection report for P-204", files=["report.pdf"])
    assert len(plan_insp) == 6
    for step in plan_insp:
        assert "step_id" in step
        assert "name" in step
        assert "description" in step
        assert "required_capability" in step
        assert "verification_requirements" in step

    # Calculation plan
    plan_calc = await generate_plan("Calculate percentage reduction in wall thickness")
    assert len(plan_calc) == 4
    assert any(s["name"] == "Sandboxed Execution" for s in plan_calc)


@pytest.mark.asyncio
async def test_agent_state_keys():
    """Validates AgentState structure and lifecycle fields."""
    state: AgentState = {
        "task": "Test task",
        "files": [],
        "plan": [],
        "current_step": "init",
        "selected_model": "llama3.1:8b",
        "actual_model": "llama3.1:8b",
        "routing_reason": "Test",
        "task_type": "general_reasoning",
        "model_metadata": None,
        "observations": [],
        "retrieved_context": [],
        "tool_results": [],
        "model_response": "Valid response",
        "verification": {},
        "outputs": [],
        "deliverables": [],
        "errors": [],
        "fallbacks": [],
        "trace": [],
        "latency_breakdown": {},
        "final_status": "in_progress",
        "summary": None,
    }
    assert state["current_step"] == "init"
    assert state["final_status"] == "in_progress"
