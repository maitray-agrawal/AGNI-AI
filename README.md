# AGNI-AI (Agentic Government Neural Intelligence)

> **A sovereign, air-gapped, on-premise multimodal agentic AI workbench for confidential industrial knowledge work at Mangalore Refinery and Petrochemicals Limited (MRPL).**

**SIH 2026 — Problem Statement 26117**  
**Category:** Software | **Theme:** Smart Automation | **Target Entity:** MRPL

---

## 1. What AGNI-AI Is & Why It Exists

Critical refining infrastructure handles highly confidential industrial assets:
- Scanned Non-Destructive Testing (NDT) inspection reports
- Piping & Instrumentation Diagrams (P&IDs)
- Operating manuals and maintenance SOPs
- Equipment vibration and wall-thickness telemetry

These assets cannot be transmitted to commercial public cloud LLM APIs due to commercial confidentiality and national critical infrastructure cybersecurity mandates.

**AGNI-AI** is a sovereign workbench engineered to run 100% on local enterprise infrastructure. It combines open-weight multimodal models (`llama3.1:8b`, `qwen2.5-coder:7b`, `moondream`), LangGraph autonomous multi-step orchestration, embedded local vector RAG (Qdrant), a hardened code sandbox, and an automated 7-point domain verification engine that produces real engineering deliverables (`.docx` Approval Notes).

---

## 2. Core System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        AGNI-AI REACT WORKBENCH                         │
│                  React 18 + TypeScript + Tailwind CSS                  │
│                                                                        │
│   Inspection Hub  │  Coding Sandbox  │  Execution Trace  │ Sovereignty │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ REST / JSON (127.0.0.1:8000)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND                             │
│                                                                        │
│  /api/tasks   /api/files   /api/knowledge   /api/outputs   /api/security│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH AGENT ENGINE                          │
│                                                                        │
│  START ──► Planner ──► Router ──► Executor ──► Verifier ──► Finalize   │
└───────────────────────┬──────────────────────────────┬─────────────────┘
                        │                              │
                        ▼                              ▼
       ┌────────────────────────────────┐    ┌───────────────────────────┐
       │      MODEL RUNTIME LAYER       │    │      KNOWLEDGE LAYER      │
       │                                │    │                           │
       │  LocalModelClient (Interface)  │    │  Local Document Parser    │
       │  └── OllamaProvider (Active)   │    │  384-dim Dense Embeddings │
       │                                │    │  Embedded Qdrant Storage  │
       │  • llama3.1:8b (Reasoning)     │    │  Exact Citation Provenance│
       │  • qwen2.5-coder:7b (Coding)   │    └───────────────────────────┘
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
       │  • qdrant_retriever (RAG)      │
       │  • code_sandbox (Isolated)     │
       │  • docx_generator (python-docx)│
       └────────────────┬───────────────┘
                        │
                        ▼
       ┌────────────────────────────────┐
       │     SECURITY & SOVEREIGNTY     │
       │                                │
       │  • Loopback 127.0.0.1 Binding  │
       │  • Sandbox Zero-Socket Guard   │
       │  • Live OS Telemetry Scanning  │
       │  • SQLite Audit Ledger         │
       └────────────────────────────────┘
```

---

## 3. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **Backend**: Python 3.11, FastAPI, Pydantic v2, Uvicorn
- **Agent Orchestrator**: LangGraph (StateGraph DAG state machine)
- **Local Model Runtime**: Ollama (bound strictly to `127.0.0.1:11434`)
- **Open-Weight Models**:
  - `llama3.1:8b` (Planning, Reasoning, Approval Synthesis)
  - `qwen2.5-coder:7b` (Deterministic Calculations, Technical Python Scripts)
  - `moondream` (Multimodal Vision, Scanned Inspection extraction, P&ID visual analysis)
  - `mistral:latest` (Fast General Instruction fallback)
- **Vector Database**: Embedded Qdrant (`qdrant-client` local disk storage at `./data/qdrant_storage`)
- **Document Processing**: PyMuPDF (`fitz`), `python-docx`, `openpyxl`
- **Security & Telemetry**: `psutil` OS socket inspection, Python socket monkey-patch isolation, SQLite audit trail

---

## 4. Quick Start & Installation

### Prerequisites
- Windows 11 / Linux (x86_64)
- Python 3.11+
- Node.js 18+ and npm
- Ollama installed (`https://ollama.com`)

### 1. Setup Virtual Environment
```bash
# Clone or navigate to workspace
cd d:/AGNI-AI

# Create Python 3.11 virtual environment
py -3.11 -m venv .venv

# Activate environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Prepare Local Models via Ollama
Ensure the Ollama daemon is running locally:
```bash
ollama serve
```
Verify the model suite is present (or pull if running for the first time):
```bash
ollama list
# Required models:
# llama3.1:8b
# qwen2.5-coder:7b
# moondream
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 5. Running AGNI-AI

### Start Backend API Server
```bash
# From workspace root with .venv active:
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation is available at: `http://127.0.0.1:8000/docs`

### Start Frontend Workbench
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 6. Flagship Demonstration Workflows

### Flagship 1: Scanned Inspection Report → DOCX Approval Note
1. In the workbench UI, select the preset **"Flagship: Inspection Approval Note"**.
2. Document: `data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf`
3. Click **Execute Autonomous Workflow**.
4. The agent executes:
   - **Planner**: 6-stage milestone decomposition
   - **Router**: Assigns `llama3.1:8b` (reasoning) & `moondream` (vision)
   - **Document Parser**: Extracts pages & renders high-res bitmaps
   - **Vision Analyzer**: Detects wall thickness (4.2 mm) & vibration (7.8 mm/s)
   - **Local RAG**: Retrieves MRPL CDU Piping Manual (Page 14) & ISO 10816 SOP (Page 8)
   - **Reasoning**: Formulates repair disposition & mandatory 72-hr spool replacement
   - **DOCX Generator**: Writes `outputs/MRPL_Inspection_Approval_Note_P204.docx`
   - **7-Point Verifier**: Validates tag, dates, measurements, and air-gap integrity
5. Click **Download Deliverable** to review the official Word document.

### Flagship 2: Technical Engineering Calculation & Code Sandbox
1. Select preset **"Calculation: Wall Thickness Reduction"**.
2. Query: `"Calculate the percentage reduction from 8.2 mm to 4.2 mm wall thickness and compare against 4.0 mm API 570 retirement limit."`
3. Router assigns `qwen2.5-coder:7b`.
4. Executes deterministic calculation in the isolated sandbox.

### Flagship 3: Offline Demonstration Script (Zero Internet)
Run the fully automated CLI test suite completely disconnected from the network:
```bash
python scripts/demo_run.py
```

---

## 7. Security & Air-Gap Compliance

AGNI-AI guarantees sovereignty through two distinct layers:

### A. Enforcement Mechanisms
1. **Strict Loopback Binding**: All inference requests and database queries are bound to `127.0.0.1`.
2. **Zero Cloud API Keys**: Codebase contains zero commercial cloud SDKs (`openai`, `anthropic`).
3. **Hardened Sandbox**: Python sandbox executes code with environment stripping and a monkey-patched `socket.socket` that blocks all outbound socket creation.
4. **Air-Gapped Vector DB**: Qdrant runs as an embedded local disk engine (`./data/qdrant_storage`), eliminating open container ports.

### B. Observability & Telemetry
- `GET /api/security/status`: Inspects active OS network sockets via `psutil`.
- Displays real-time counts of:
  - External AI API calls: **0**
  - External network connections: **0**
  - Active localhost sockets: Verified
- Every run is logged to an immutable local SQLite audit database (`outputs/audit.db`).

---

## 8. Automated Test Suite

Run the full verification test suite:
```bash
# Run all automated tests
pytest backend/tests/ -v

# Run individual test modules
pytest backend/tests/test_vertical_poc.py -v       # Model routing & execution POC
pytest backend/tests/test_flagship_workflow.py -v   # Full Flagship NDT pipeline
pytest backend/tests/test_sandbox.py -v             # Sandbox & network blocking
pytest backend/tests/test_api.py -v                 # REST API endpoints
```

---

## 9. Three-Developer Modular Ownership

- **Developer 1 (Agent & Models)**: `backend/app/agent/`, `backend/app/models/`
- **Developer 2 (RAG & Multimodal)**: `backend/app/rag/`, `backend/app/tools/document.py`, `backend/app/tools/vision.py`, `data/`
- **Developer 3 (Platform, UI, Security)**: `frontend/`, `backend/app/api/`, `backend/app/security/`, `backend/app/tools/docx.py`

---

## 10. Demonstration Artifacts

- **Inspection Report PDF**: `data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf`
- **P&ID Schematic**: `data/raw/pidqa/pid_cdu_pump_p204.png`
- **Generated DOCX**: `outputs/MRPL_Inspection_Approval_Note_P204.docx`
- **System Architecture**: `docs/ARCHITECTURE.md`
- **API Reference**: `docs/API.md`
- **Security Guide**: `docs/SECURITY.md`
- **Team Plan**: `docs/TEAM_PLAN.md`
