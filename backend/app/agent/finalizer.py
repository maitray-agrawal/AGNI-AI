from typing import Dict, Any
import logging

logger = logging.getLogger("agni.agent.finalizer")


async def finalize_task(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compiles final outputs, evidence citations, deliverable references,
    and verification results into a coherent summary.
    Does NOT hardcode outputs; derives strictly from actual execution state.
    """
    selected_model = state.get("selected_model", "unknown")
    actual_model = state.get("actual_model", selected_model)
    task_type = state.get("task_type", "general_reasoning")
    verification = state.get("verification", {})
    outputs = state.get("outputs", [])
    errors = state.get("errors", [])
    fallbacks = state.get("fallbacks", [])

    v_status = verification.get("status", "unknown")
    passed_checks = verification.get("passed_count", 0)
    total_checks = verification.get("total_count", len(verification.get("checks", [])))

    # Construct descriptive summary
    if v_status == "passed":
        summary = (
            f"Task successfully completed and verified ({passed_checks}/{total_checks} domain checks passed). "
            f"Executed via '{actual_model}'."
        )
        if fallbacks:
            summary += f" (Fallback note: Primary '{selected_model}' fell back to '{actual_model}')."
        if outputs:
            deliverable_names = ", ".join(o.get("filename", "") for o in outputs)
            summary += f" Deliverable generated: {deliverable_names}."
    else:
        summary = (
            f"Task execution completed with verification concerns ({passed_checks}/{total_checks} checks passed). "
            f"Executed via '{actual_model}'."
        )
        if errors:
            summary += f" Errors encountered: {len(errors)}."

    return {
        "summary": summary,
        "deliverables": outputs,
        "current_step": "finalized",
        "final_status": "completed" if v_status == "passed" and not errors else "completed_with_warnings",
    }
