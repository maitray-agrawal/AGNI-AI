import pytest
from pathlib import Path
from backend.app.agent.graph import run_agent


@pytest.mark.asyncio
async def test_flagship_inspection_workflow():
    """Flagship Workflow: Scanned Inspection Report -> Vision -> RAG -> Reasoning -> Verifier -> DOCX."""
    pdf_path = "data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf"
    assert Path(pdf_path).exists(), f"Sample inspection report missing: {pdf_path}"

    task = (
        "Analyze this inspection report, identify critical findings, consult relevant local procedures, "
        "determine the recommended action, verify the result and generate an approval note."
    )

    print(f"\n[FLAGSHIP WORKFLOW TEST] Starting autonomous execution...")
    result = await run_agent(task=task, files=[pdf_path])

    assert result is not None
    assert result.get("current_step") == "finalized"
    assert result.get("task_type") == "inspection_workflow"

    # Verify tool executions
    tools_called = [t.get("tool") for t in result.get("tool_results", [])]
    print(f"[Tools Executed]: {tools_called}")
    assert "document_parser" in tools_called
    assert "vision_analyzer" in tools_called
    assert "qdrant_retriever" in tools_called
    assert "docx_generator" in tools_called

    # Verify deliverable generated
    outputs = result.get("outputs", [])
    print(f"[Deliverables Generated]: {outputs}")
    assert len(outputs) > 0
    docx_file = outputs[0]
    assert docx_file["type"] == "docx"
    assert Path(docx_file["path"]).exists()
    assert docx_file["size_bytes"] > 5000

    # Verify 7-point Domain Verification
    verification = result.get("verification", {})
    print(f"\n[7-Point Domain Verification Summary]:")
    for chk in verification.get("checks", []):
        mark = "[PASS]" if chk["passed"] else "[FAIL]"
        print(f"  {mark} {chk['name']}: {chk.get('details')}")

    assert verification.get("status") == "passed"
    assert len(verification.get("checks", [])) >= 5

    # Verify Trace Sequence
    trace_steps = [t["step"] for t in result.get("trace", [])]
    print(f"\n[Agent Execution Trace]: {trace_steps}")
    assert "planner" in trace_steps
    assert "router" in trace_steps
    assert "executor" in trace_steps
    assert "verifier" in trace_steps
    assert "finalizer" in trace_steps
