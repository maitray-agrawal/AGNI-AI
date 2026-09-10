from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class TaskRunRequest(BaseModel):
    task: str = Field(..., description="User's task prompt or instruction")
    files: List[str] = Field(default_factory=list, description="List of local file paths")
    stream: bool = Field(default=False, description="Whether to stream trace events")


class VerificationCheck(BaseModel):
    name: str
    passed: bool
    details: Optional[str] = None


class VerificationResult(BaseModel):
    status: str = Field(..., description="'passed' or 'failed'")
    checks: List[VerificationCheck] = Field(default_factory=list)


class OutputDeliverable(BaseModel):
    type: str = Field(..., description="docx, xlsx, pptx, json, or text")
    filename: str
    path: str
    size_bytes: int


class TraceEvent(BaseModel):
    step: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_ms: int = 0
    status: str = "completed"
    details: Optional[Dict[str, Any]] = None


class TaskRunResponse(BaseModel):
    task_id: str
    status: str
    selected_model: Optional[str] = None
    task_type: Optional[str] = None
    routing_reason: Optional[str] = None
    total_duration_ms: Optional[int] = None
    plan: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str
    verification: Optional[VerificationResult] = None
    outputs: List[OutputDeliverable] = Field(default_factory=list)
    trace_summary: List[TraceEvent] = Field(default_factory=list)
    retrieved_citations: List[Dict[str, Any]] = Field(default_factory=list)


class ModelInfo(BaseModel):
    id: str
    name: str
    capabilities: List[str]
    status: str = "available"


class ModelListResponse(BaseModel):
    provider: str
    endpoint: str
    models: List[ModelInfo]


class SecurityStatusResponse(BaseModel):
    air_gapped: bool = True
    inference_runtime: str = "local_ollama"
    inference_endpoint: str
    vector_db: str = "embedded_qdrant_disk"
    active_sockets: List[Dict[str, Any]] = Field(default_factory=list)
    external_ai_api_calls: int = 0
    external_network_connections: int = 0
    sandbox_network_isolated: bool = True
