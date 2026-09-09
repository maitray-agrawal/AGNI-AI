# AGNI-AI Three-Developer Modular Ownership Plan

To guarantee rapid parallel development over the 48-hour MVP window without code collisions, the repository is split into three strictly bounded modules with frozen interface contracts.

---

## Developer 1: Agent Core & Model Orchestration

### Ownership Paths
- `backend/app/agent/` (LangGraph state machine, planner, router, executor, verifier, finalizer)
- `backend/app/models/` (LocalModelClient, OllamaProvider, model registry, capability router)
- `backend/tests/test_agent.py`, `backend/tests/test_models.py`

### Key Responsibilities
1. State management (`AgentState` TypedDict).
2. LangGraph DAG compilation and conditional correction loop.
3. Capability-based model routing (matching tasks to `llama3.1:8b`, `qwen2.5-coder:7b`, `moondream`).
4. Hardware-aware sequential model execution (memory guard for 16GB RAM).
5. Verification node logic enforcing 8-point domain validation.

### Frozen Interface Contract
```python
async def run_agent(task: str, files: list[str] = []) -> AgentResult:
    """Executes stateful LangGraph agent and returns verified outputs + trace."""
    ...
```

---

## Developer 2: RAG & Multimodal Document Pipeline

### Ownership Paths
- `backend/app/rag/` (Embeddings, Qdrant client, ingestion, hybrid retrieval, citation formatter)
- `backend/app/tools/document.py` (PyMuPDF inspection and text/table extractor)
- `backend/app/tools/vision.py` (Multimodal vision caller, P&ID and inspection schema extractor)
- `data/` (MRPL manuals, inspection reports, P&ID benchmarks, embedded Qdrant storage)
- `backend/tests/test_rag.py`, `backend/tests/test_vision.py`

### Key Responsibilities
1. Document ingestion and metadata preservation (`document`, `page`, `section`, `equipment_id`).
2. Embedded Qdrant disk storage setup (`path="./data/qdrant_storage"`).
3. Hybrid semantic retrieval with citation grounding.
4. Rendering PDF pages to high-res images for local vision model.
5. Structured JSON extraction for inspection findings.

### Frozen Interface Contracts
```python
def retrieve(query: str, top_k: int = 5, filters: dict | None = None) -> list[DocumentChunk]:
    """Retrieves top-k chunks with document and page provenance."""
    ...

def analyze_document(file_path: str) -> InspectionResult:
    """Parses PDF/image, invokes vision if needed, and returns structured findings."""
    ...
```

---

## Developer 3: Platform, UI, Security & Deliverables

### Ownership Paths
- `frontend/` (React 19, TypeScript, Tailwind CSS, workbench UI, trace viewer, telemetry panel)
- `backend/app/api/` (FastAPI route controllers, file upload, stream handlers)
- `backend/app/tools/code.py` (Code execution sandbox)
- `backend/app/tools/docx.py`, `backend/app/tools/xlsx.py` (Report generation)
- `backend/app/security/` (Network telemetry monitor, SQLite audit ledger)
- `infra/` (Docker compose, environment config)
- `backend/tests/test_security.py`, `backend/tests/test_docx.py`

### Key Responsibilities
1. Enterprise workbench interface (high-contrast dark mode, visual execution trace, sovereignty status).
2. Professional DOCX generator for MRPL Inspection Approval Note.
3. Code sandbox with `network=none` Docker container and isolated process fallback.
4. Socket-level network monitor verifying zero external outbound connections.
5. SQLite audit ledger capturing run history and deliverable hashes.

### Frozen Interface Contracts
```python
def execute_code(code: str, timeout: int = 10) -> SandboxResult:
    """Executes Python code in isolated sandbox without network access."""
    ...

def generate_docx(data: dict) -> FileResult:
    """Generates formatted MRPL Inspection Approval Note DOCX file."""
    ...
```
