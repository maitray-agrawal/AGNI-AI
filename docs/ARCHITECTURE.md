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
       │  ├── OllamaProvider (Active)   │     │  384-dim Dense Embeddings │
       │  ├── LMStudioProvider (Ext)    │     │  Embedded Qdrant Storage  │
       │  └── VLLMProvider (Ext)        │     │  Exact Citation Provenance│
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
- **Network Policy**: Server and models strictly bound to `127.0.0.1`.
- **Outbound Telemetry**: Real socket-level inspection monitoring all active backend connections to verify zero external IP egress.
- **Audit Logging**: SQLite database recording every agent run, model routing decision, tool duration, and SHA-256 deliverable hashes.
