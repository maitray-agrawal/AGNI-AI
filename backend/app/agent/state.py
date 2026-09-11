from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    """
    Centralized execution state for the AGNI-AI LangGraph state machine.
    Captures complete end-to-end lifecycle provenance without global mutable state.
    """
    task: str
    files: List[str]
    plan: List[Dict[str, Any]]
    current_step: str
    selected_model: Optional[str]
    actual_model: Optional[str]
    routing_reason: Optional[str]
    task_type: Optional[str]
    model_metadata: Optional[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    retrieved_context: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    model_response: Optional[str]
    verification: Dict[str, Any]
    outputs: List[Dict[str, Any]]
    deliverables: List[Dict[str, Any]]
    errors: List[str]
    fallbacks: List[Dict[str, Any]]
    trace: List[Dict[str, Any]]
    latency_breakdown: Dict[str, int]
    final_status: str
    summary: Optional[str]
    retry_count: int
