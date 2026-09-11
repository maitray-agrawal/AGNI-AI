import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END
import logging

from backend.app.agent.state import AgentState
from backend.app.agent.planner import generate_plan
from backend.app.agent.executor import execute_task
from backend.app.agent.verifier import verify_execution
from backend.app.agent.finalizer import finalize_task
from backend.app.models.router import model_router

logger = logging.getLogger("agni.agent.graph")


def _create_trace_event(
    step: str,
    start_time: float,
    status: str = "completed",
    details: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None,
    capability: Optional[str] = None,
    fallback: bool = False,
) -> Dict[str, Any]:
    """Creates a standardized execution trace event with millisecond precision."""
    duration_ms = int((time.time() - start_time) * 1000)
    ev: Dict[str, Any] = {
        "step": step,
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": duration_ms,
        "status": status,
        "details": details or {},
    }
    if model:
        ev["model"] = model
    if capability:
        ev["capability"] = capability
    if fallback:
        ev["fallback"] = True
    return ev


async def planner_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    plan = await generate_plan(state["task"], state.get("files", []))
    event = _create_trace_event("planner", t0, "completed", {"plan_steps": len(plan)})
    
    latencies = state.get("latency_breakdown") or {}
    latencies["planner_ms"] = event["duration_ms"]

    return {
        "plan": plan,
        "current_step": "planner",
        "latency_breakdown": latencies,
        "trace": (state.get("trace") or []) + [event],
    }


async def router_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    decision = await model_router.route_task(state["task"], state.get("files", []))
    event = _create_trace_event(
        step="router",
        start_time=t0,
        status="completed",
        details={
            "selected_model": decision.selected_model,
            "task_type": decision.task_type,
            "reason": decision.reason,
            "candidate_scores": decision.candidate_scores,
            "fallback_chain": decision.fallback_chain,
        },
        model=decision.selected_model,
        capability=decision.task_type,
        fallback=decision.fallback_used,
    )

    latencies = state.get("latency_breakdown") or {}
    latencies["router_ms"] = event["duration_ms"]

    return {
        "selected_model": decision.selected_model,
        "actual_model": decision.selected_model,
        "task_type": decision.task_type,
        "routing_reason": decision.reason,
        "current_step": "router",
        "latency_breakdown": latencies,
        "trace": (state.get("trace") or []) + [event],
    }


async def executor_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    is_retry = (state.get("current_step") == "verifier") or (
        state.get("verification", {}).get("status") == "failed" and state.get("retry_count", 0) == 0
    )

    retry_count = state.get("retry_count", 0)
    exec_state = dict(state)
    failed_checks = []

    if is_retry:
        retry_count += 1
        failed_checks = [
            c.get("name")
            for c in state.get("verification", {}).get("checks", [])
            if not c.get("passed")
        ]
        failed_str = ", ".join(failed_checks) if failed_checks else "domain consistency checks"
        exec_state["retry_count"] = retry_count
        exec_state["task"] = (
            f"{state['task']}\n\n"
            f"[RETRY CORRECTION REQUIRED: Previous execution attempt failed the following verification check(s): {failed_str}. "
            f"Please specifically address and correct these items in your synthesis.]"
        )
        logger.info(f"Executing agent retry attempt {retry_count}/1 for failed checks: {failed_checks}")

    res = await execute_task(exec_state)
    status = "failed" if res.get("errors") else "completed"
    
    actual_model = res.get("actual_model") or state.get("selected_model")
    fallbacks = res.get("fallbacks", [])
    step_name = "executor_retry" if is_retry else "executor"
    
    event_details: Dict[str, Any] = {
        "model": actual_model,
        "errors": res.get("errors", []),
        "output_length": len(res.get("model_response", "")),
        "deliverables": len(res.get("outputs", [])),
        "fallbacks": fallbacks,
    }
    if is_retry:
        event_details["retry_attempt"] = retry_count
        event_details["failed_checks_retried"] = failed_checks

    event = _create_trace_event(
        step=step_name,
        start_time=t0,
        status=status,
        details=event_details,
        model=actual_model,
        capability=state.get("task_type"),
        fallback=len(fallbacks) > 0,
    )

    latencies = state.get("latency_breakdown") or {}
    latencies[f"{step_name}_ms"] = event["duration_ms"]

    new_outputs = res.get("outputs", []) if res.get("outputs") else (state.get("outputs") or [])

    return {
        "model_response": res.get("model_response", ""),
        "actual_model": actual_model,
        "model_metadata": res.get("model_metadata"),
        "tool_results": (state.get("tool_results") or []) + res.get("tool_results", []),
        "outputs": new_outputs,
        "deliverables": new_outputs,
        "errors": res.get("errors", []),
        "fallbacks": (state.get("fallbacks") or []) + fallbacks,
        "current_step": step_name,
        "retry_count": retry_count,
        "latency_breakdown": latencies,
        "trace": (state.get("trace") or []) + [event],
    }


async def verifier_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    verdict = await verify_execution(state)
    event = _create_trace_event(
        step="verifier",
        start_time=t0,
        status=verdict["status"],
        details={
            "passed_checks": verdict.get("passed_count", 0),
            "total_checks": verdict.get("total_count", 0),
        },
    )

    latencies = state.get("latency_breakdown") or {}
    latencies["verifier_ms"] = event["duration_ms"]

    return {
        "verification": verdict,
        "current_step": "verifier",
        "latency_breakdown": latencies,
        "trace": (state.get("trace") or []) + [event],
    }


async def finalizer_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    res = await finalize_task(state)
    event = _create_trace_event(
        step="finalizer",
        start_time=t0,
        status="completed",
        details={"summary": res.get("summary"), "status": res.get("final_status")},
    )

    latencies = state.get("latency_breakdown") or {}
    latencies["finalizer_ms"] = event["duration_ms"]
    latencies["total_workflow_ms"] = sum(latencies.values())

    return {
        "summary": res.get("summary"),
        "deliverables": res.get("deliverables", []),
        "final_status": res.get("final_status", "completed"),
        "current_step": "finalized",
        "latency_breakdown": latencies,
        "trace": (state.get("trace") or []) + [event],
    }


def should_continue_or_finalize(state: AgentState) -> str:
    """Evaluates verification verdict and routes conditionally."""
    verdict = state.get("verification", {})
    retry_count = state.get("retry_count", 0)
    if verdict.get("status") == "passed":
        return "finalize"
    if retry_count < 1:
        logger.warning(
            f"Verification gate flagged concerns ({verdict.get('passed_count')}/{verdict.get('total_count')} passed). "
            f"Routing to executor for adaptive retry (attempt {retry_count + 1}/1)."
        )
        return "retry"
    logger.warning(
        f"Verification gate flagged concerns ({verdict.get('passed_count')}/{verdict.get('total_count')} passed). "
        "Max retry cap (1) reached. Finalizing."
    )
    return "finalize"


# Build the LangGraph StateMachine
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("router", router_node)
workflow.add_node("executor", executor_node)
workflow.add_node("verifier", verifier_node)
workflow.add_node("finalizer", finalizer_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "router")
workflow.add_edge("router", "executor")
workflow.add_edge("executor", "verifier")
workflow.add_conditional_edges("verifier", should_continue_or_finalize, {
    "finalize": "finalizer",
    "retry": "executor",
})
workflow.add_edge("finalizer", END)

# Compiled graph runnable
agent_graph = workflow.compile()


async def run_agent(task: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Submission-grade entrypoint for executing the AGNI-AI LangGraph agent.
    Initializes typed state, executes state machine, and returns complete lifecycle result.
    """
    initial_state: AgentState = {
        "task": task,
        "files": files or [],
        "plan": [],
        "current_step": "init",
        "selected_model": None,
        "actual_model": None,
        "routing_reason": None,
        "task_type": None,
        "model_metadata": None,
        "observations": [],
        "retrieved_context": [],
        "tool_results": [],
        "model_response": None,
        "verification": {},
        "outputs": [],
        "deliverables": [],
        "errors": [],
        "fallbacks": [],
        "trace": [],
        "latency_breakdown": {},
        "final_status": "in_progress",
        "summary": None,
        "retry_count": 0,
    }
    final_state = await agent_graph.ainvoke(initial_state)
    return final_state
