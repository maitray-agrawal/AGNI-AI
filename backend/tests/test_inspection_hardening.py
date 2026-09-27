import pytest
from typing import Dict, Any, List

from backend.app.agent.executor import execute_task
from backend.app.agent.finalizer import finalize_task
from backend.app.agent.graph import run_agent
from backend.app.models.client import OllamaProvider, ModelInvocationMetadata


@pytest.mark.asyncio
async def test_retry_correction_reaches_real_inspection_workflow_prompt(monkeypatch):
    """
    CRITICAL VERIFICATION (Section 11):
    1. Calls the real execute_task() without mocking it.
    2. Uses task_type="inspection_workflow".
    3. Supplies retry_correction="critical_findings_identified".
    4. Monkeypatches/spies on client.generate_with_meta on OllamaProvider.
    5. Captures the actual prompt argument.
    6. Asserts that the actual prompt contains 'critical_findings_identified'.
    7. Asserts that the correction block occurs BEFORE the final recommendation instruction.
    """
    captured_prompts: List[str] = []

    async def spy_generate_with_meta(self, model, prompt, system=None, options=None, request_id=None, step_id=None):
        captured_prompts.append(prompt)
        meta = ModelInvocationMetadata(
            requested_model=model,
            actual_model=model,
            success=True,
            duration_ms=50,
        )
        fake_response = (
            "1. MANDATORY SPOOL REPLACEMENT: Wall thickness near retirement limit.\n"
            "2. VIBRATION MITIGATION: Overhaul bearings per ISO 10816-3.\n"
            "3. FOLLOW-UP MONITORING: Schedule bi-weekly thickness inspection."
        )
        return fake_response, meta

    monkeypatch.setattr(OllamaProvider, "generate_with_meta", spy_generate_with_meta)

    state: Dict[str, Any] = {
        "task_id": "test_prompt_capture_001",
        "task": "Perform inspection evaluation on pump P-204",
        "task_type": "inspection_workflow",
        "selected_model": "llama3.1:8b",
        "retry_correction": "critical_findings_identified",
        "files": ["data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf"],
    }

    result = await execute_task(state)

    assert result is not None
    assert len(captured_prompts) >= 1, "Expected client.generate_with_meta to be called"

    actual_prompt = captured_prompts[0]
    print("\n" + "=" * 40 + " CAPTURED REASONING PROMPT " + "=" * 40)
    print(actual_prompt)
    print("=" * 105)

    # Assert failed check name is in prompt
    assert "critical_findings_identified" in actual_prompt
    assert "[CORRECTION REQUIRED FROM PRIOR ATTEMPT]" in actual_prompt

    # Assert correction block occurs BEFORE final engineering recommendation instruction
    recommendation_instruction = "Provide clear, numbered engineering recommendations and clearance disposition."
    assert recommendation_instruction in actual_prompt

    correction_idx = actual_prompt.index("[CORRECTION REQUIRED FROM PRIOR ATTEMPT]")
    instruction_idx = actual_prompt.index(recommendation_instruction)
    assert correction_idx < instruction_idx, (
        f"Correction block index ({correction_idx}) must precede final instruction index ({instruction_idx})"
    )


@pytest.mark.asyncio
async def test_live_end_to_end_retry_verification(monkeypatch):
    """
    LIVE END-TO-END RETRY VERIFICATION (Section 12):
    1. Real flow: run_agent -> executor -> verifier (FAIL) -> retry -> executor -> verifier (PASS) -> finalize
    2. Does NOT mock execute_task.
    3. Prints literal retry prompt visibly.
    4. Proves retry prompt contains [CORRECTION REQUIRED FROM PRIOR ATTEMPT] and failed check names.
    """
    captured_prompts: List[str] = []

    async def spy_generate_with_meta(self, model, prompt, system=None, options=None, request_id=None, step_id=None):
        captured_prompts.append(prompt)
        meta = ModelInvocationMetadata(
            requested_model=model,
            actual_model=model,
            success=True,
            duration_ms=45,
        )
        fake_response = (
            "1. MANDATORY SPOOL REPLACEMENT: Wall thickness near retirement limit.\n"
            "2. VIBRATION MITIGATION: Overhaul bearings per ISO 10816-3.\n"
            "3. FOLLOW-UP MONITORING: Schedule bi-weekly thickness inspection."
        )
        return fake_response, meta

    monkeypatch.setattr(OllamaProvider, "generate_with_meta", spy_generate_with_meta)

    # Controlled verifier failure on attempt 1, pass on attempt 2
    verify_call_count = 0

    async def mock_verify_execution(state):
        nonlocal verify_call_count
        verify_call_count += 1
        if verify_call_count == 1:
            return {
                "status": "failed",
                "passed_count": 6,
                "total_count": 8,
                "checks": [
                    {"name": "critical_findings_identified", "passed": False, "details": "Wall thickness not highlighted"},
                    {"name": "rag_evidence_cited", "passed": False, "details": "API 570 citation missing"},
                    {"name": "equipment_tag_identified", "passed": True, "details": "P-204 identified"},
                ],
            }
        else:
            return {
                "status": "passed",
                "passed_count": 8,
                "total_count": 8,
                "checks": [
                    {"name": "critical_findings_identified", "passed": True, "details": "Resolved on retry"},
                    {"name": "rag_evidence_cited", "passed": True, "details": "Resolved on retry"},
                    {"name": "equipment_tag_identified", "passed": True, "details": "P-204 identified"},
                ],
            }

    monkeypatch.setattr("backend.app.agent.graph.verify_execution", mock_verify_execution)

    result = await run_agent(
        task="Analyze this inspection report, identify critical findings, consult relevant local procedures, determine the recommended action, verify the result and generate an approval note.",
        files=["data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf"],
    )

    assert result is not None
    assert result.get("retry_count") == 1
    assert result.get("verification", {}).get("status") == "passed"
    assert verify_call_count == 2

    # Verify that client.generate_with_meta was called twice (initial + retry)
    assert len(captured_prompts) == 2, f"Expected 2 reasoning calls, got {len(captured_prompts)}"

    initial_prompt = captured_prompts[0]
    retry_prompt = captured_prompts[1]

    # Print the LITERAL retry prompt as required by Section 12
    print("\n" + "=" * 35 + " LITERAL RETRY PROMPT SENT TO MODEL " + "=" * 35)
    print(retry_prompt)
    print("=" * 105)

    assert "[CORRECTION REQUIRED FROM PRIOR ATTEMPT]" not in initial_prompt
    assert "[CORRECTION REQUIRED FROM PRIOR ATTEMPT]" in retry_prompt
    assert "critical_findings_identified" in retry_prompt
    assert "rag_evidence_cited" in retry_prompt


@pytest.mark.asyncio
async def test_degraded_mode_surfaced_in_tool_result_and_summary(monkeypatch):
    """
    DEGRADED MODE TEST (Section 16):
    1. Force document_parser.parse_pdf to raise an exception.
    2. Run real execute_task() and real finalize_task().
    3. Assert 'DEGRADED MODE' exists in the returned summary.
    4. Assert degraded_mode == True exists in the corresponding tool result.
    """
    from backend.app.tools.document import document_parser

    def mock_broken_parse_pdf(file_path):
        raise FileNotFoundError("Simulated corrupted inspection PDF file")

    monkeypatch.setattr(document_parser, "parse_pdf", mock_broken_parse_pdf)

    # Spy client to avoid slow model inference during tool-level test
    async def fast_generate(self, *args, **kwargs):
        meta = ModelInvocationMetadata(
            requested_model="llama3.1:8b",
            actual_model="llama3.1:8b",
            success=True,
            duration_ms=10,
        )
        return "1. Action: spool replacement required.", meta

    monkeypatch.setattr(OllamaProvider, "generate_with_meta", fast_generate)

    state: Dict[str, Any] = {
        "task_id": "test_degraded_001",
        "task": "Inspect pump P-204",
        "task_type": "inspection_workflow",
        "selected_model": "llama3.1:8b",
        "files": ["corrupted_file.pdf"],
    }

    # Execute real execute_task
    exec_result = await execute_task(state)

    # Find the document_parser tool result
    tool_results = exec_result.get("tool_results", [])
    doc_tool = next((t for t in tool_results if t.get("tool") == "document_parser"), None)
    assert doc_tool is not None, "document_parser tool result missing"
    assert doc_tool.get("success") is False
    assert doc_tool.get("degraded_mode") is True
    assert "Simulated corrupted inspection PDF file" in doc_tool.get("degraded_reason", "")

    # Now pass state with tool_results to real finalize_task
    state_to_finalize = dict(state)
    state_to_finalize["tool_results"] = tool_results
    state_to_finalize["outputs"] = exec_result.get("outputs", [])
    state_to_finalize["verification"] = {"status": "passed", "passed_count": 8, "total_count": 8}

    final_result = await finalize_task(state_to_finalize)
    summary = final_result.get("summary", "")

    print("\n" + "=" * 35 + " FINALIZER SUMMARY WITH DEGRADED WARNING " + "=" * 35)
    print(summary.encode("ascii", errors="backslashreplace").decode("ascii"))
    print("=" * 105)

    assert "⚠ DEGRADED MODE:" in summary
    assert "document_parser" in summary
    assert "Simulated corrupted inspection PDF file" in summary
