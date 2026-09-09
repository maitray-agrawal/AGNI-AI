from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    task: str
    files: List[str]
    plan: List[Dict[str, Any]]
    selected_model: Optional[str]
    routing_reason: Optional[str]
    task_type: Optional[str]
    observations: List[Dict[str, Any]]
    retrieved_context: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    model_response: Optional[str]
    verification: Dict[str, Any]
    outputs: List[Dict[str, Any]]
    errors: List[str]
    trace: List[Dict[str, Any]]
    current_step: str
