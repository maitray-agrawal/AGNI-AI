import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from backend.app.schemas import TaskRunRequest, TaskRunResponse, VerificationResult, OutputDeliverable, TraceEvent
from backend.app.agent.graph import run_agent

router = APIRouter()

# In-memory store for task states (also written to audit db in security layer)
TASK_STORE: Dict[str, Dict[str, Any]] = {}


@router.post("/tasks/run", response_model=TaskRunResponse)
async def submit_task(req: TaskRunRequest):
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    try:
        final_state = await run_agent(task=req.task, files=req.files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

    TASK_STORE[task_id] = final_state

    # Extract tool invocations
    tools_called = [t.get("tool") for t in final_state.get("tool_results", []) if t.get("tool")]

    # Format trace events and enrich executor details with tools invoked
    trace_events = []
    for ev in final_state.get("trace", []):
        details = dict(ev.get("details") or {})
        if ev.get("step") == "executor" and tools_called and "tools_invoked" not in details:
            details["tools_invoked"] = tools_called
        trace_events.append(
            TraceEvent(
                step=ev.get("step", "unknown"),
                timestamp=ev.get("timestamp", ""),
                duration_ms=ev.get("duration_ms", 0),
                status=ev.get("status", "completed"),
                details=details,
            )
        )

    # Format verification
    raw_v = final_state.get("verification")
    verification_obj = None
    if raw_v and "checks" in raw_v:
        verification_obj = VerificationResult(
            status=raw_v.get("status", "passed"),
            checks=raw_v.get("checks", []),
        )

    # Format deliverables
    deliverables = [
        OutputDeliverable(
            type=out.get("type", "docx"),
            filename=out.get("filename", ""),
            path=out.get("path", ""),
            size_bytes=out.get("size_bytes", 0),
        )
        for out in final_state.get("outputs", [])
    ]

    summary_text = (
        final_state.get("model_response") or 
        final_state.get("summary") or 
        f"Completed via {final_state.get('selected_model')}."
    )

    total_ms = (
        final_state.get("latency_breakdown", {}).get("total_workflow_ms") or
        sum(ev.get("duration_ms", 0) for ev in final_state.get("trace", []))
    )

    citations = final_state.get("retrieved_context") or []

    return TaskRunResponse(
        task_id=task_id,
        status="completed" if not final_state.get("errors") else "completed_with_errors",
        selected_model=final_state.get("selected_model"),
        task_type=final_state.get("task_type"),
        routing_reason=final_state.get("routing_reason"),
        total_duration_ms=total_ms,
        plan=final_state.get("plan", []),
        summary=summary_text,
        verification=verification_obj,
        outputs=deliverables,
        trace_summary=trace_events,
        retrieved_citations=citations,
    )


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in TASK_STORE:
        raise HTTPException(status_code=404, detail="Task not found")
    state = TASK_STORE[task_id]
    return {
        "task_id": task_id,
        "selected_model": state.get("selected_model"),
        "task_type": state.get("task_type"),
        "summary": state.get("summary"),
        "verification": state.get("verification"),
        "errors": state.get("errors", []),
    }


@router.get("/tasks/{task_id}/trace")
async def get_task_trace(task_id: str):
    if task_id not in TASK_STORE:
        raise HTTPException(status_code=404, detail="Task not found")
    state = TASK_STORE[task_id]
    return {
        "task_id": task_id,
        "trace": state.get("trace", []),
    }
