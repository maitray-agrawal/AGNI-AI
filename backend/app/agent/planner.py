import re
from typing import Dict, Any, List, Optional
import logging
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("agni.agent.planner")


class PlanValidationError(ValueError):
    """Raised when generated plan violates structural or semantic schemas."""
    pass


class PlanStep(BaseModel):
    """Strongly-typed individual step within an agent execution plan."""
    step_id: int = Field(..., ge=1, description="Sequential step index")
    name: str = Field(..., min_length=3, description="Concise human-readable step title")
    description: str = Field(..., min_length=5, description="Detailed objective of this step")
    required_capability: str = Field(..., description="Required model or tool capability")
    required_tools: List[str] = Field(default_factory=list, description="Tools invoked during step")
    required_files: List[str] = Field(default_factory=list, description="Files consumed during step")
    verification_requirements: List[str] = Field(default_factory=list, description="Verification criteria for this step")


class Plan(BaseModel):
    """Complete structured execution plan with task objective."""
    objective: str = Field(..., min_length=5)
    task_type: str
    steps: List[PlanStep] = Field(..., min_length=1)


async def generate_plan(task: str, files: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Constructs a deterministic, domain-aware execution plan for the task.
    Validates every step against the PlanStep schema before returning.
    """
    task_lower = task.lower()
    files = files or []

    has_images = any(f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")) for f in files)
    has_pdfs = any(f.lower().endswith((".pdf", ".docx", ".xlsx")) for f in files)

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

    raw_steps: List[Dict[str, Any]] = []

    # 1. Pure Coding & Deterministic calculation (not coupled to a multi-page inspection report)
    if is_coding and not has_pdfs and not is_inspection_doc:
        raw_steps = [
            {
                "step_id": 1,
                "name": "Problem Formulation",
                "description": "Analyze technical calculation requirements and identify input parameters",
                "required_capability": "reasoning",
                "required_tools": [],
                "required_files": files,
                "verification_requirements": ["Parameters identified with units"],
            },
            {
                "step_id": 2,
                "name": "Code / Math Generation",
                "description": "Generate deterministic Python calculation logic via Coder model",
                "required_capability": "coding",
                "required_tools": [],
                "required_files": [],
                "verification_requirements": ["Executable Python logic generated", "Formula explicitly displayed"],
            },
            {
                "step_id": 3,
                "name": "Sandboxed Execution",
                "description": "Execute calculation in isolated environment without network egress",
                "required_capability": "sandboxed_execution",
                "required_tools": ["code_sandbox"],
                "required_files": [],
                "verification_requirements": ["Exit code 0", "Zero network egress"],
            },
            {
                "step_id": 4,
                "name": "Result Verification",
                "description": "Verify calculation accuracy and constraint compliance",
                "required_capability": "verification",
                "required_tools": [],
                "required_files": [],
                "verification_requirements": ["Quantitative metric present in response"],
            },
        ]
        task_type = "coding_calculation"

    # 2. Vision & Multimodal tasks: has image file OR visual query without document files
    elif (has_images or is_vision) and not has_pdfs and not is_inspection_doc:
        raw_steps = [
            {
                "step_id": 1,
                "name": "Visual Inspection",
                "description": "Load and inspect engineering drawing or P&ID schematic",
                "required_capability": "vision",
                "required_tools": ["vision_analyzer"],
                "required_files": files,
                "verification_requirements": ["Image loaded without corruption"],
            },
            {
                "step_id": 2,
                "name": "Component Identification",
                "description": "Identify valves, pumps, tags, line specifications, and pipe connections",
                "required_capability": "vision",
                "required_tools": ["vision_analyzer"],
                "required_files": files,
                "verification_requirements": ["Asset tags and flow lines detected"],
            },
            {
                "step_id": 3,
                "name": "Engineering Synthesis",
                "description": "Formulate structured engineering response to user query",
                "required_capability": "reasoning",
                "required_tools": [],
                "required_files": [],
                "verification_requirements": ["Valid engineering response formulated"],
            },
        ]
        task_type = "visual_inspection"

    # 3. Industrial Inspection Workflow: Multi-step document ingestion, RAG, reasoning & DOCX
    elif is_inspection_doc or (is_vision and has_pdfs):
        raw_steps = [
            {
                "step_id": 1,
                "name": "Document Inspection",
                "description": "Inspect and parse input inspection document/PDF to extract text and image layers",
                "required_capability": "document_parsing",
                "required_tools": ["document_parser"],
                "required_files": files,
                "verification_requirements": ["Input document parsed successfully", "Extracted page count > 0"],
            },
            {
                "step_id": 2,
                "name": "Multimodal Finding Extraction",
                "description": "Extract critical quantitative findings (wall thickness, vibration RMS, corrosion rate)",
                "required_capability": "vision",
                "required_tools": ["vision_analyzer"],
                "required_files": files,
                "verification_requirements": ["Equipment tag identified", "Critical measurements extracted"],
            },
            {
                "step_id": 3,
                "name": "Local RAG Retrieval",
                "description": "Query local Qdrant knowledge base for applicable industrial SOPs and API 570 / ISO 10816 criteria",
                "required_capability": "retrieval",
                "required_tools": ["qdrant_retriever"],
                "required_files": [],
                "verification_requirements": ["Local standard chunks retrieved with page numbers"],
            },
            {
                "step_id": 4,
                "name": "Engineering Reasoning",
                "description": "Synthesize findings against maintenance limits and formulate action recommendation",
                "required_capability": "reasoning",
                "required_tools": [],
                "required_files": [],
                "verification_requirements": ["Actionable disposition formulated", "Grounding citations referenced"],
            },
            {
                "step_id": 5,
                "name": "8-Point Verification",
                "description": "Validate equipment tag, dates, citations, deliverables, and air-gap telemetry integrity",
                "required_capability": "verification",
                "required_tools": [],
                "required_files": [],
                "verification_requirements": ["All 8 verification checks evaluated"],
            },
            {
                "step_id": 6,
                "name": "Deliverable Generation",
                "description": "Generate official Inspection Approval Note DOCX file",
                "required_capability": "deliverable_generation",
                "required_tools": ["docx_generator"],
                "required_files": [],
                "verification_requirements": ["DOCX file generated on disk", "Size > 5000 bytes"],
            },
        ]
        task_type = "inspection_workflow"

    # 4. General technical reasoning
    else:
        raw_steps = [
            {
                "step_id": 1,
                "name": "Task Understanding",
                "description": "Deconstruct user instruction and identify key technical parameters",
                "required_capability": "reasoning",
                "required_tools": [],
                "required_files": files,
                "verification_requirements": ["User query deconstructed"],
            },
            {
                "step_id": 2,
                "name": "Local Reasoning",
                "description": "Process query using local open-weight model",
                "required_capability": "reasoning",
                "required_tools": [],
                "required_files": [],
                "verification_requirements": ["Model response generated"],
            },
            {
                "step_id": 3,
                "name": "Quality Verification",
                "description": "Validate completeness and consistency of response",
                "required_capability": "verification",
                "required_tools": [],
                "required_files": [],
                "verification_requirements": ["Non-empty response verified"],
            },
        ]
        task_type = "general_reasoning"

    # Schema validation of the plan
    try:
        plan_obj = Plan(
            objective=task,
            task_type=task_type,
            steps=[PlanStep(**s) for s in raw_steps],
        )
        validated_steps = [s.model_dump() for s in plan_obj.steps]
        logger.info(f"Plan validated: {len(validated_steps)} steps for task_type='{task_type}'")
        return validated_steps
    except ValidationError as e:
        logger.error(f"Plan validation failed: {e}")
        raise PlanValidationError(f"Generated plan is malformed: {e}")
