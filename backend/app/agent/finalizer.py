from typing import Dict, Any
import logging

logger = logging.getLogger("agni.agent.finalizer")


async def finalize_task(state: Dict[str, Any]) -> Dict[str, Any]:
    """Compiles outputs, trace, and summary for the completed task."""
    model_response = state.get("model_response", "")
    verification = state.get("verification", {})
    task_type = state.get("task_type", "general_reasoning")

    # Generate summary line
    v_status = verification.get("status", "passed")
    summary = f"Task completed via {state.get('selected_model')} (Verification: {v_status.upper()})."

    return {
        "summary": summary,
        "current_step": "finalized",
    }
