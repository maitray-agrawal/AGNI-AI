# AGNI-AI System Architecture

## 1. Overview & Problem Statement
**AGNI-AI** (**A**gentic **G**overnment **N**eural **I**ntelligence) is a sovereign, air-gapped, on-premise multimodal agentic AI workbench engineered for **Mangalore Refinery and Petrochemicals Limited (MRPL)** under **SIH 2026 Problem Statement 26117**.
The system is built to process confidential industrial engineering assets—including scanned non-destructive testing (NDT) inspection reports, Piping & Instrumentation Diagrams (P&IDs), operating manuals, and standard operating procedures (SOPs)—completely within on-premise infrastructure without external network egress.

---

## 2. Logical Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGNI-AI WORKBENCH                             │
│                  React 19 + TypeScript + Tailwind CSS                   │
│                                                                         │
│  Inspection Hub  │  Coding Sandbox  │  Execution Trace  │  Sovereignty  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     │ REST / JSON (127.0.0.1:8000)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND                              │
│                                                                         │
│  /api/tasks   /api/files   /api/knowledge   /api/outputs   /api/security│
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         LANGGRAPH AGENT ENGINE                          │
│                                                                         │
│  START ──► Planner ──► Router ──► Executor ──► Verifier ──► Finalize    │
│                                                     │ (Fail Report)     │
│                                                     └──► Finalize (Err) │
└───────────────────────┬───────────────────────────────┬─────────────────┘
                        │                               │
                        ▼                               ▼
       ┌────────────────────────────────┐     ┌───────────────────────────┐
       │      MODEL RUNTIME LAYER       │     │      KNOWLEDGE LAYER      │
       │                                │     │                           │
       │  LocalModelClient (Interface)  │     │  Local SOP Ingestion      │
       │  └── OllamaProvider (Active)   │     │  384-dim Dense Embeddings │
       │                                │     │  Embedded Qdrant Storage  │
       │                                │     │  Exact Citation Provenance│
       │                                │     └───────────────────────────┘
       │  Local Open-Weight Models:     │
       │  • llama3.1:8b (Reasoning)     │
       │  • qwen2.5-coder:7b (Coding)   │
       │  • moondream (Vision/Diagrams) │
       │  • mistral:latest (General)    │
       └────────────────┬───────────────┘
                        │
                        ▼
       ┌────────────────────────────────┐
       │        LOCAL TOOL LAYER        │
       │                                │
       │  • document_parser (PyMuPDF)   │
       │  • vision_analyzer (Moondream) │
       │  • rag_retriever (Qdrant)      │
       │  • code_sandbox (Isolated)     │
       │  • docx_generator (python-docx)│
       │  • xlsx_generator (openpyxl)   │
       └────────────────┬───────────────┘
                        │
                        ▼
       ┌────────────────────────────────┐
       │   SECURITY & SOVEREIGNTY       │
       │                                │
       │  • Loopback Binding (127.0.0.1)│
       │  • Docker network=none Sandbox │
       │  • Local Process Resource Guard│
       │  • Socket-level Audit Monitor  │
       │  • SQLite Audit Ledger         │
       └────────────────────────────────┘
```

---

## 3. Core Component Design

### 3.1 Model Abstraction & Capability Router
Rather than coupling agent code to concrete model names, AGNI-AI introduces a unified provider contract:
- `LocalModelClient`: Abstract base class providing `chat()`, `generate()`, and `vision()`.
- `OllamaProvider`: Concrete implementation calling `http://127.0.0.1:11434`.
- `ModelRegistry`: Maintains capabilities (`reasoning`, `planning`, `coding`, `mathematics`, `vision`, `multimodal`).
- `ModelRouter`: Inspects incoming tasks and selects the model with exact matching capabilities.
- **Hardware-Aware Loading**: Invocations execute sequentially to prevent OOM on machines with 16 GB RAM and shared Intel Arc graphics.

### 3.2 LangGraph Agent State Machine
The core execution engine is stateful and modeled as a directed graph:
```python
class AgentState(TypedDict):
    task: str
    files: list[str]
    plan: list[dict]
    selected_model: str | None
    observations: list[dict]
    retrieved_context: list[dict]
    tool_results: list[dict]
    verification: dict
    outputs: list[dict]
    errors: list[str]
    trace: list[dict]
```
Nodes:
1. **Planner**: Breaks user request into structured milestone subtasks.
2. **Router**: Maps subtasks to required capabilities and active local models.
3. **Executor**: Invokes local tools (document parser, vision analyzer, RAG retriever, code sandbox, document generator).
4. **Verifier**: Executes 8 domain-specific consistency checks (model output, execution integrity, asset tag, NDT metrics, RAG citations, recommendations, output files, air-gap OS sockets).
5. **Finalizer**: Bundles output files, formatted citations, and execution telemetry into an `AgentResult`. (Note: Single-pass verification with detailed diagnostic reporting to finalizer; iterative correction loop is deferred to avoid memory thrashing on 16 GB non-CUDA hardware).

### 3.3 Multimodal Document & P&ID Pipeline
1. Documents (PDF/images) are inspected with PyMuPDF.
2. If digital text is present, extractable text and tables are structured per page.
3. Rendered high-resolution page bitmaps and diagrams are routed to the local vision model (`moondream`) for component, tag, measurement, and anomaly detection.
4. Extracted measurements (e.g. wall thickness, vibration, corrosion rate) are validated into structured JSON schemas.

### 3.4 Local RAG Architecture
- **Vector Database**: Embedded Qdrant storage (`path="./data/qdrant_storage"`), requiring zero external network calls or Docker daemon overhead.
- **Embeddings**: Deterministic 384-dimensional semantic term/n-gram hashing vectorizer (fast offline fallback embedding for air-gapped CPU inference, avoiding heavy PyTorch/CUDA runtime overhead on 16 GB non-CUDA machines; compatible with dense cosine distance retrieval in Qdrant).
- **Chunking**: Section-aware hierarchical chunking preserving metadata:
  `document`, `page`, `section`, `equipment_id`, `plant_area`, `revision`.
- **Retrieval**: Dense semantic search combined with exact keyword filtering, returning exact page and section provenance for grounding.
- **Data Provenance**: Demo corpus uses synthetic and public industrial engineering standards (API 570, ISO 10816-3). No proprietary MRPL information is included.

### 3.5 Deliverable Generation
- **DOCX**: Enterprise-grade MRPL Inspection Approval Note created via `python-docx` with formal header, metadata summary table, extracted findings, cited SOP standards, and official sign-off blocks.
- **XLSX**: Engineering calculation worksheets generated via `openpyxl`.

### 3.6 Sovereignty & Air-Gap Enforcement
- **Network Policy**: Server and models strictly bound to `127.0.0.1` (ENFORCED).
- **Outbound Telemetry**: Real socket-level telemetry monitoring active backend connections; verified zero external IP egress during test intervals (OBSERVED). Sandbox network socket creation is intercepted and denied (BLOCKED).
- **Audit Logging**: SQLite database recording every agent run, model routing decision, tool duration, and SHA-256 deliverable hashes.

---

## 4. AGENT + MODEL ORCHESTRATION

The Agent + Models subsystem provides local model orchestration, routing, execution, verification, and benchmarking for confidential industrial workloads without external network dependencies.

### 4.1 Planner
- **Decomposition**: Accepts task prompt and file metadata, producing a structured `Plan` containing typed `PlanStep` elements.
- **Validation**: Schema-validated via Pydantic; every step explicitly declares `step_id`, `name`, `description`, `required_capability`, `required_tools`, `required_files`, and `verification_requirements`. Malformed plans raise explicit `PlanValidationError` rather than silently fabricating missing fields.

### 4.2 Capability Router
- **Deterministic Routing**: Maps `Task` → `TaskProfile` → hard capability constraints → candidate scoring → `selected_model` and `fallback_chain`. Does NOT use LLMs, embeddings, or heuristic black-boxes for routing.
- **Explainability**: Every `RoutingDecision` exposes `task_type`, `required_capabilities`, `selected_model`, `reason`, `candidate_scores`, `fallback_chain`, and decision latency (sub-millisecond).

### 4.3 Local Model Registry
- **Centralized Single Source of Truth**: `ModelRegistry` maintains strongly typed `ModelSpec` records:
  - `llama3.1:8b` (Reasoning, planning, industrial synthesis)
  - `qwen2.5-coder:7b` (Coding, deterministic engineering calculations)
  - `moondream` (Multimodal vision inspection, scanned document analysis)
  - `mistral:latest` (General instruction following and fast text fallback)
- **Availability Caching**: Discovered models are cached with a 60-second TTL to avoid repeated expensive HTTP `/api/tags` queries during multi-step tasks.

### 4.4 LocalModelClient
- **Unified Local Interface**: Abstract `LocalModelClient` with concrete `OllamaProvider` targeting `http://127.0.0.1:11434`.
- **Strict Backward Compatibility**: Public methods `generate(...)`, `chat(...)`, and `vision(...)` return strings.
- **Additive Telemetry**: `generate_with_meta(...)`, `chat_with_meta(...)`, and `vision_with_meta(...)` return `(text, ModelInvocationMetadata)` capturing `requested_model`, `actual_model`, `request_id`, `step_id`, `attempt`, `retry_count`, `duration_ms`, `error_type`, and `local_endpoint`.
- **Bounded Retries**: Maximum 1 retry strictly limited to transient connection errors or socket timeouts; invalid models, unsupported capabilities, or malformed inputs fail immediately.

### 4.5 Executor
- **State Preservation**: Invokes routed models, parses tool outputs, and measures fine-grained latencies.
- **Error Classification**: Classifies failures (`TIMEOUT`, `CONNECTION_ERROR`, `MODEL_NOT_FOUND`, `INVALID_RESPONSE`, `EXECUTION_ERROR`) and propagates them cleanly into `AgentState` without swallowing exceptions.

### 4.6 Verifier (8-Point Quality Gate)
Enforces 8 domain-specific criteria before allowing finalization:
1. `model_output_valid`: Verifies non-empty output (>20 characters) and guards against error messages passing as content.
2. `zero_execution_errors`: Verifies `len(errors) == 0`.
3. `equipment_tag_identified`: Validates asset tag (e.g., `P-204`) in inspection synthesis.
4. `critical_findings_identified`: Validates quantitative NDT measurements (e.g. wall thickness, vibration).
5. `rag_evidence_cited`: Verifies grounded Qdrant SOP and API 570 citations.
6. `recommendation_formulated`: Validates actionable engineering maintenance disposition.
7. `deliverable_generated`: Verifies `.docx` deliverable exists on disk and exceeds minimum size (>1000 bytes).
8. `air_gap_integrity`: Verifies live OS telemetry loopback isolation via `NetworkTelemetry`.

### 4.7 Finalizer
- **Dynamic Compilation**: Compiles deliverable metadata, evidence citations, verification status, and model provenance strictly from upstream state (no hardcoded demo text).
- **Status Gating**: Sets `final_status` to `completed` or `completed_with_warnings` reflecting verifier gate outcomes.

### 4.8 Execution Trace & Observability
- **Trace Events**: Every LangGraph node emits structured trace records: `timestamp`, `step`, `duration_ms`, `status`, `model`, `capability`, `fallback`, and `details`.
- **Latency Breakdown**: End-to-end state tracks `planner_ms`, `router_ms`, `executor_ms`, `verifier_ms`, `finalizer_ms`, and `total_workflow_ms`.

### 4.9 Capability-Safe Fallback Policy
- **Modality Isolation**: Vision tasks are strictly prohibited from falling back to text-only models (`vision` → `moondream` only; no text fallback).
- **Structured Recording**: Every fallback event logs `primary_model`, `fallback_model`, `reason`, `attempt`, `duration`, and `result`.

### 4.10 Benchmark Methodology
- **Routing Benchmark (`routing_benchmark.py`)**: 60 representative industrial prompts across 5 categories (Reasoning: 20, Coding: 15, General: 10, Vision: 10, Ambiguous: 5). Evaluates routing logic in isolation without expensive model inference. Measured accuracy: **100.0%**, average latency: **<1 ms**.
- **Agent Reliability Benchmark (`agent_reliability_benchmark.py`)**: 20 end-to-end workflows executed with real local Ollama inference across reasoning, coding, industrial document, and failure/edge-case scenarios. Measures `workflow_success_rate`, `routing_accuracy`, `verifier_pass_rate`, `fallback_rate`, and latency percentiles (`min`, `median`, `average`, `p95`, `max`).

---

## 5. Operational Boundaries & Hardware Limitations

1. **Hardware Host Constraint**: Designed and validated on an edge hardware profile of 16 GB system RAM and shared Intel Arc graphics without dedicated NVIDIA CUDA VRAM.
2. **Sequential Inference Execution**: Models in Ollama are invoked sequentially rather than concurrently. Loading multiple 7B–8B parameter models simultaneously in 16 GB RAM risks operating system paging or out-of-memory crashes.
3. **Model Switching Latency**: When transitioning between models (e.g. `llama3.1:8b` and `qwen2.5-coder:7b`), Ollama reloads model weights from disk to RAM, introducing an observed 5–15 second transition latency.
4. **Lightweight Multimodal Vision**: `moondream` is a compact ~1.8B parameter multimodal model optimized for local CPU/edge execution. While effective for localized table/label inspection and P&ID component extraction, it operates as a proof-of-concept on-premise vision tool and does not possess the capacity of high-parameter cloud multimodal models.
5. **Deterministic Local Vectorization**: Local RAG utilizes an embedded 384-dimensional deterministic semantic hashing vectorizer paired with local disk Qdrant storage. This eliminates external embedding API dependencies and heavy PyTorch runtime overhead on CPU-only infrastructure.
6. **Synthetic Demo Corpus**: In strict compliance with MRPL confidentiality mandates, all demonstration documents (inspection reports, P&ID schematics, operating manuals) are synthetic industrial demonstration files. No confidential, classified, or proprietary MRPL refinery data is stored or fabricated.
7. **Air-Gap Compliance Boundary**: Software enforces loopback binding (`127.0.0.1`) and sandbox socket blocking. Physical air-gap compliance depends entirely on the deployment environment and network infrastructure.

