import time
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from backend.app.models.registry import model_registry, ModelRegistry, CAPABILITY_FALLBACK_RULES

logger = logging.getLogger("agni.models.router")


class TaskProfile(BaseModel):
    """Detailed profile of incoming task characteristics."""
    capability: str  # "reasoning", "coding", "vision", "general"
    modality: str = "text"  # "text" or "multimodal"
    task_type: str  # "inspection_workflow", "coding_calculation", "visual_inspection", "general_reasoning"
    complexity: str = "medium"  # "low", "medium", "high"
    latency_preference: str = "normal"  # "low", "normal"
    tool_required: List[str] = Field(default_factory=list)
    file_required: bool = False
    has_images: bool = False
    has_documents: bool = False


class RoutingDecision(BaseModel):
    """Strongly-typed, observable routing decision containing selection rationale."""
    task_type: str
    required_capabilities: List[str]
    selected_model: str
    reason: str
    fallback_chain: List[str] = Field(default_factory=list)
    fallback_used: bool = False
    task_profile: Optional[Dict[str, Any]] = None
    candidate_scores: Dict[str, float] = Field(default_factory=dict)
    decision_latency_ms: int = 0


# Deterministic scoring weights for model selection
SCORING_WEIGHTS = {
    "capability_match": 50.0,
    "modality_match": 30.0,
    "availability_gate": 15.0,
    "priority_rank": 5.0,
}


class CapabilityRouter:
    """Deterministic, capability-aware router assigning optimal local model to task."""

    def __init__(self, registry: ModelRegistry = model_registry):
        self.registry = registry

    def profile_task(self, task: str, files: Optional[List[str]] = None) -> TaskProfile:
        """Extracts task profile from user prompt and file inputs using word-boundary matching."""
        task_lower = task.lower()
        files = files or []

        has_images = any(f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")) for f in files)
        has_pdfs = any(f.lower().endswith((".pdf", ".docx", ".xlsx")) for f in files)

        # Regex whole-word patterns to prevent partial substring matches (e.g. "formulate" matching "formula")
        coding_pattern = re.compile(
            r"\b(calculate|percentage|formula|python|script|code|reduction|algorithm|anomaly\s+statistics|"
            r"compute|math|equation|simulation|numpy|pandas|algebra|derivative|integral|convert\s+units|arithmetic)\b"
        )
        vision_pattern = re.compile(
            r"\b(p&id|pid|drawing|schematic|diagram|image|visual|scanned|isometric|layout|photo|thermogram|defect\s+photo)\b"
        )
        inspection_doc_pattern = re.compile(
            r"\b(inspection\s+report|report|sop|procedure|approval\s+note|ndt\s+report|fmea|clearance|audit)\b"
        )

        is_coding = bool(coding_pattern.search(task_lower))
        is_vision = bool(vision_pattern.search(task_lower)) or has_images
        is_inspection_doc = bool(inspection_doc_pattern.search(task_lower)) or has_pdfs

        # Classification precedence:
        # 1. Vision & Multimodal tasks: has image file OR visual query without document files
        if (has_images or is_vision) and not has_pdfs and not is_inspection_doc:
            return TaskProfile(
                capability="vision",
                modality="multimodal",
                task_type="visual_inspection",
                complexity="high",
                tool_required=["vision_analyzer"],
                file_required=bool(files),
                has_images=has_images,
                has_documents=has_pdfs,
            )

        # 2. Pure Coding & Deterministic calculation (not coupled to a multi-page inspection report)
        if is_coding and not has_pdfs:
            return TaskProfile(
                capability="coding",
                modality="text",
                task_type="coding_calculation",
                complexity="medium",
                tool_required=["code_sandbox"],
                file_required=bool(files),
                has_images=has_images,
                has_documents=has_pdfs,
            )

        # 3. Industrial Inspection Workflow: Multi-step document ingestion, RAG, reasoning & DOCX
        if is_inspection_doc or (is_vision and has_pdfs):
            return TaskProfile(
                capability="reasoning",
                modality="text",  # Reasoning model orchestrates, vision model invoked via tool
                task_type="inspection_workflow",
                complexity="high",
                tool_required=["document_parser", "vision_analyzer", "qdrant_retriever", "docx_generator"],
                file_required=True,
                has_images=has_images,
                has_documents=has_pdfs,
            )

        # 4. General technical reasoning
        return TaskProfile(
            capability="reasoning",
            modality="text",
            task_type="general_reasoning",
            complexity="low",
            tool_required=[],
            file_required=bool(files),
            has_images=has_images,
            has_documents=has_pdfs,
        )

    def _score_candidates(self, profile: TaskProfile, available_models: List[str]) -> Dict[str, float]:
        """Calculates deterministic capability alignment scores for candidate models."""
        scores: Dict[str, float] = {}

        for name, spec in self.registry.specs.items():
            score = 0.0

            # 1. Capability match
            if profile.capability in spec.capabilities or profile.capability == spec.role:
                score += SCORING_WEIGHTS["capability_match"]
            elif any(c in spec.capabilities for c in [profile.capability, profile.task_type]):
                score += SCORING_WEIGHTS["capability_match"] * 0.5

            # 2. Modality match (Mandatory gate for multimodal tasks)
            if profile.modality == "multimodal":
                if spec.modality == "multimodal":
                    score += SCORING_WEIGHTS["modality_match"]
                else:
                    # Text models cannot fulfill multimodal tasks directly
                    score = 0.0
                    scores[name] = 0.0
                    continue
            else:
                score += SCORING_WEIGHTS["modality_match"]

            # 3. Availability gate
            is_avail = self.registry.is_model_available(name)
            if is_avail:
                score += SCORING_WEIGHTS["availability_gate"]

            # 4. Priority rank
            score += (spec.priority / 100.0) * SCORING_WEIGHTS["priority_rank"]

            scores[name] = round(score, 2)

        return scores

    async def route_task(self, task: str, files: Optional[List[str]] = None) -> RoutingDecision:
        """
        Main routing function: Profile -> Candidate Evaluation -> Capability Resolution -> Decision.
        """
        t0 = time.time()
        files = files or []
        profile = self.profile_task(task, files)

        # Ensure local registry availability is known
        available = await self.registry.refresh_available_models()

        # Score candidate models
        scores = self._score_candidates(profile, available)

        # Resolve primary model and fallback chain from registry
        role = profile.capability
        selected_model, fallback_chain, is_fallback, reason_text = await self.registry.resolve_model_for_role(role)

        # Construct required capabilities list
        if profile.task_type == "coding_calculation":
            required_caps = ["coding", "python", "mathematics", "calculation"]
            base_reason = f"Task requires deterministic calculation and code execution. Routed to '{selected_model}'."
        elif profile.task_type == "visual_inspection":
            required_caps = ["vision", "scanned_document", "visual_analysis"]
            base_reason = f"Task requires multimodal analysis of visual diagram/drawing. Routed to '{selected_model}'."
        elif profile.task_type == "inspection_workflow":
            required_caps = ["reasoning", "planning", "analysis", "report_generation"]
            base_reason = f"Task is industrial inspection analysis and approval synthesis. Routed to '{selected_model}'."
        else:
            required_caps = ["reasoning", "instruction"]
            base_reason = f"General technical reasoning task. Routed to '{selected_model}'."

        if is_fallback:
            reason = f"{base_reason} (Fallback Notice: {reason_text})"
        else:
            reason = base_reason

        decision_latency_ms = int((time.time() - t0) * 1000)

        decision = RoutingDecision(
            task_type=profile.task_type,
            required_capabilities=required_caps,
            selected_model=selected_model,
            reason=reason,
            fallback_chain=fallback_chain,
            fallback_used=is_fallback,
            task_profile=profile.model_dump(),
            candidate_scores=scores,
            decision_latency_ms=decision_latency_ms,
        )

        logger.info(
            f"Routing decision: task_type='{decision.task_type}', "
            f"model='{decision.selected_model}', fallback={decision.fallback_used}, "
            f"latency={decision.decision_latency_ms}ms"
        )
        return decision


# Global router singleton
model_router = CapabilityRouter()
