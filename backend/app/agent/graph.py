import time
from datetime import datetime
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
import logging

from backend.app.agent.state import AgentState
from backend.app.agent.planner import generate_plan
from backend.app.agent.executor import execute_task
from backend.app.agent.verifier import verify_execution
from backend.app.agent.finalizer import finalize_task
from backend.app.models.router import model_router

logger = logging.getLogger("agni.agent.graph")


def _create_trace_event(step: str, start_time: float, status: str = "completed", details: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "step": step,
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": int((time.time() - start_time) * 1000),
        "status": status,
        "details": details or {},
    }


async def planner_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    plan = await generate_plan(state["task"], state.get("files", []))
    event = _create_trace_event("planner", t0, "completed", {"plan_steps": len(plan)})
    return {
        "plan": plan,
        "current_step": "planner",
        "trace": (state.get("trace") or []) + [event],
    }


async def router_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    decision = await model_router.route_task(state["task"], state.get("files", []))
    event = _create_trace_event("router", t0, "completed", {
        "selected_model": decision.selected_model,
        "task_type": decision.task_type,
        "reason": decision.reason,
    })
    return {
        "selected_model": decision.selected_model,
        "task_type": decision.task_type,
        "routing_reason": decision.reason,
        "current_step": "router",
        "trace": (state.get("trace") or []) + [event],
    }


async def executor_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    res = await execute_task(state)
    status = "failed" if res.get("errors") else "completed"
    event = _create_trace_event("executor", t0, status, {
        "model": state.get("selected_model"),
        "errors": res.get("errors", []),
        "output_length": len(res.get("model_response", "")),
        "deliverables": len(res.get("outputs", [])),
    })
    return {
        "model_response": res.get("model_response", ""),
        "tool_results": (state.get("tool_results") or []) + res.get("tool_results", []),
        "outputs": (state.get("outputs") or []) + res.get("outputs", []),
        "errors": (state.get("errors") or []) + res.get("errors", []),
        "current_step": "executor",
        "trace": (state.get("trace") or []) + [event],
    }


async def verifier_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    verdict = await verify_execution(state)
    event = _create_trace_event("verifier", t0, verdict["status"], {
        "passed_checks": sum(1 for c in verdict["checks"] if c["passed"]),
        "total_checks": len(verdict["checks"]),
    })
    return {
        "verification": verdict,
        "current_step": "verifier",
        "trace": (state.get("trace") or []) + [event],
    }


async def finalizer_node(state: AgentState) -> Dict[str, Any]:
    t0 = time.time()
    res = await finalize_task(state)
    event = _create_trace_event("finalizer", t0, "completed", {"summary": res.get("summary")})
    return {
        "current_step": "finalized",
        "trace": (state.get("trace") or []) + [event],
    }


def should_continue_or_finalize(state: AgentState) -> str:
    """Evaluates verification verdict."""
    verdict = state.get("verification", {})
    if verdict.get("status") == "passed":
        return "finalize"
    # If failed but retries not exceeded, can correct; for now direct to finalize with failure details
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
})
workflow.add_edge("finalizer", END)

# Compiled graph runnable
agent_graph = workflow.compile()


async def run_agent(task: str, files: List[str] = None) -> Dict[str, Any]:
    """Frozen interface contract for running the AGNI-AI agent."""
    initial_state: AgentState = {
        "task": task,
        "files": files or [],
        "plan": [],
        "selected_model": None,
        "routing_reason": None,
        "task_type": None,
        "observations": [],
        "retrieved_context": [],
        "tool_results": [],
        "model_response": None,
        "verification": {},
        "outputs": [],
        "errors": [],
        "trace": [],
        "current_step": "init",
    }
    final_state = await agent_graph.ainvoke(initial_state)
    return final_state
