import time
from typing import Dict, Any, List
import logging

logger = logging.getLogger("agni.agent.planner")


async def generate_plan(task: str, files: List[str]) -> List[Dict[str, Any]]:
    """Constructs a deterministic, domain-aware execution plan for the task."""
    task_lower = task.lower()
    files = files or []

    if any(k in task_lower for k in ["inspection", "report", "p-204", "pump", "valve", "approval note"]):
        return [
            {"step_id": 1, "name": "Document Inspection", "description": "Inspect and parse input inspection document/PDF"},
            {"step_id": 2, "name": "Multimodal Finding Extraction", "description": "Extract critical quantitative findings (wall thickness, vibration, anomaly)"},
            {"step_id": 3, "name": "Local RAG Retrieval", "description": "Query local Qdrant knowledge base for applicable industrial SOPs / API 570 criteria"},
            {"step_id": 4, "name": "Engineering Reasoning", "description": "Synthesize findings against maintenance limits and formulate action recommendation"},
            {"step_id": 5, "name": "8-Point Verification", "description": "Validate equipment tag, dates, citations, and air-gap integrity"},
            {"step_id": 6, "name": "Deliverable Generation", "description": "Generate official Inspection Approval Note DOCX file"},
        ]
    elif any(k in task_lower for k in ["calculate", "percentage", "python", "code", "reduction", "wall thickness"]):
        return [
            {"step_id": 1, "name": "Problem Formulation", "description": "Analyze technical calculation requirements and identify parameters"},
            {"step_id": 2, "name": "Code / Math Generation", "description": "Generate deterministic Python calculation logic via Coder model"},
            {"step_id": 3, "name": "Sandboxed Execution", "description": "Execute calculation in isolated environment without network egress"},
            {"step_id": 4, "name": "Result Verification", "description": "Verify calculation accuracy and constraint compliance"},
        ]
    elif any(k in task_lower for k in ["p&id", "pid", "drawing", "diagram", "image"]):
        return [
            {"step_id": 1, "name": "Visual Inspection", "description": "Load and inspect engineering drawing"},
            {"step_id": 2, "name": "Component Identification", "description": "Identify valves, pumps, tags, and pipe connections"},
            {"step_id": 3, "name": "Engineering Synthesis", "description": "Formulate structured response to user question"},
        ]
    else:
        return [
            {"step_id": 1, "name": "Task Understanding", "description": "Deconstruct user instruction and identify key parameters"},
            {"step_id": 2, "name": "Local Reasoning", "description": "Process query using local open-weight model"},
            {"step_id": 3, "name": "Quality Verification", "description": "Validate completeness and consistency of response"},
        ]
