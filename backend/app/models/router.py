from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
from backend.app.models.registry import model_registry

logger = logging.getLogger("agni.models.router")


class RoutingDecision(BaseModel):
    task_type: str
    required_capabilities: List[str]
    selected_model: str
    reason: str


class CapabilityRouter:
    """Semantic & capability-aware router that assigns optimal local model to task."""

    def __init__(self, registry=model_registry):
        self.registry = registry

    async def route_task(self, task: str, files: Optional[List[str]] = None) -> RoutingDecision:
        task_lower = task.lower()
        files = files or []

        has_images = any(f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")) for f in files)
        has_pdfs = any(f.lower().endswith(".pdf") for f in files)

        # Heuristic capability extraction
        is_coding_or_math = any(
            w in task_lower for w in [
                "calculate", "percentage", "formula", "python", "script", "code", 
                "reduction", "wall thickness calculation", "algorithm", "anomaly statistics"
            ]
        )
        is_inspection = any(
            w in task_lower for w in [
                "inspection", "report", "finding", "procedure", "sop", "approval note", 
                "p-204", "pump", "valve", "corrosion", "thickness", "vibration", "ndt"
            ]
        )
        is_vision_diagram = any(
            w in task_lower for w in [
                "p&id", "pid", "drawing", "schematic", "diagram", "image", "visual", "scanned"
            ]
        ) or has_images

        # Capability prioritization:
        # If task explicitly asks to calculate, compute, or write code, route to coding/calculation
        if is_coding_or_math:
            task_type = "coding_calculation"
            required_caps = ["coding", "python", "mathematics", "calculation"]
            selected_model = await self.registry.get_model_for_capabilities(required_caps)
            reason = f"Task requires deterministic calculation and code execution. Routed to '{selected_model}'."
        elif is_vision_diagram:
            task_type = "visual_inspection"
            required_caps = ["vision", "scanned_document", "visual_analysis"]
            selected_model = await self.registry.get_model_for_capabilities(required_caps)
            reason = f"Task requires visual/multimodal analysis for engineering drawing or scanned document. Routed to '{selected_model}'."
        elif is_inspection:
            task_type = "inspection_workflow"
            # Flagship inspection workflow uses reasoning model for orchestration & synthesis
            required_caps = ["reasoning", "planning", "analysis", "report_generation"]
            selected_model = await self.registry.get_model_for_capabilities(required_caps)
            reason = f"Task is industrial inspection analysis and approval synthesis. Routed to '{selected_model}'."
        else:
            task_type = "general_reasoning"
            required_caps = ["reasoning", "instruction"]
            selected_model = await self.registry.get_model_for_capabilities(required_caps)
            reason = f"General technical reasoning task. Routed to '{selected_model}'."

        decision = RoutingDecision(
            task_type=task_type,
            required_capabilities=required_caps,
            selected_model=selected_model,
            reason=reason,
        )
        logger.info(f"Routing decision: {decision.model_dump()}")
        return decision


# Global router singleton
model_router = CapabilityRouter()
