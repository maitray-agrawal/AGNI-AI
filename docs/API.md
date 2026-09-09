# AGNI-AI REST API Specification

Base URL: `http://127.0.0.1:8000`

All endpoints return and accept JSON. All requests and responses are strictly local.

---

## 1. System & Health

### `GET /api/health`
Checks server health, local model runtime connectivity, and vector store readiness.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "sovereign_local",
  "ollama_connected": true,
  "qdrant_ready": true,
  "timestamp": "2026-09-09T12:45:00Z"
}
```

---

## 2. Models & Capability Registry

### `GET /api/models`
Returns list of registered local models, their providers, and supported capabilities.

**Response `200 OK`**:
```json
{
  "provider": "ollama",
  "endpoint": "http://127.0.0.1:11434",
  "models": [
    {
      "id": "llama3.1:8b",
      "name": "Llama 3.1 8B",
      "capabilities": ["reasoning", "planning", "summarization"],
      "status": "available"
    },
    {
      "id": "qwen2.5-coder:7b",
      "name": "Qwen 2.5 Coder 7B",
      "capabilities": ["coding", "mathematics", "python"],
      "status": "available"
    },
    {
      "id": "moondream",
      "name": "Moondream Multimodal",
      "capabilities": ["vision", "scanned_document", "visual_analysis"],
      "status": "available"
    },
    {
      "id": "mistral:latest",
      "name": "Mistral 7B",
      "capabilities": ["reasoning", "instruction"],
      "status": "available"
    }
  ]
}
```

---

## 3. Tasks & Agent Execution

### `POST /api/tasks/run`
Submits a task to the LangGraph autonomous agent.

**Request**:
```json
{
  "task": "Analyze this inspection report, identify critical findings, consult relevant local procedures, determine the recommended action, verify the result and generate an approval note.",
  "files": ["data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf"],
  "stream": false
}
```

**Response `200 OK`**:
```json
{
  "task_id": "task_20260909_001",
  "status": "completed",
  "selected_model": "llama3.1:8b",
  "summary": "Completed inspection analysis for Equipment P-204 with 7-point verification passed.",
  "verification": {
    "status": "passed",
    "checks": [
      {"name": "equipment_id_extracted", "passed": true},
      {"name": "inspection_date_extracted", "passed": true},
      {"name": "critical_findings_identified", "passed": true},
      {"name": "rag_evidence_cited", "passed": true},
      {"name": "recommendation_formulated", "passed": true},
      {"name": "deliverable_generated", "passed": true},
      {"name": "air_gap_compliance", "passed": true}
    ]
  },
  "outputs": [
    {
      "type": "docx",
      "filename": "MRPL_Inspection_Approval_Note_P204.docx",
      "path": "outputs/MRPL_Inspection_Approval_Note_P204.docx",
      "size_bytes": 38450
    }
  ],
  "trace_summary": [
    {"step": "planner", "duration_ms": 320, "status": "completed"},
    {"step": "router", "duration_ms": 110, "status": "completed"},
    {"step": "vision_analyzer", "duration_ms": 1450, "status": "completed"},
    {"step": "rag_retriever", "duration_ms": 280, "status": "completed"},
    {"step": "reasoning", "duration_ms": 2100, "status": "completed"},
    {"step": "verifier", "duration_ms": 90, "status": "completed"},
    {"step": "docx_generator", "duration_ms": 180, "status": "completed"}
  ]
}
```

### `GET /api/tasks/{task_id}`
Retrieves task status and metadata.

### `GET /api/tasks/{task_id}/trace`
Retrieves detailed, node-by-node execution trace for visual inspection in the UI.

---

## 4. File Management

### `POST /api/files/upload`
Uploads a local inspection report, engineering drawing, or CSV dataset into `data/raw/`.

**Response `200 OK`**:
```json
{
  "filename": "MRPL_Inspection_Report_P204.pdf",
  "saved_path": "data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf",
  "size_bytes": 104520,
  "content_type": "application/pdf"
}
```

---

## 5. Knowledge Base & RAG

### `POST /api/knowledge/ingest`
Ingests a directory or single PDF/TXT document into the local Qdrant collection.

### `POST /api/knowledge/search`
Queries the local knowledge base directly with metadata filtering.

**Request**:
```json
{
  "query": "Minimum allowable wall thickness and retirement limits for Heavy Gas Oil piping API 570",
  "top_k": 3
}
```

**Response `200 OK`**:
```json
{
  "results": [
    {
      "document": "MRPL_CDU_Piping_Inspection_Manual.pdf",
      "page": 14,
      "section": "Section 4.2 - Minimum Wall Thickness Criteria",
      "text": "For Carbon Steel Schedule 80 piping operating above 350 deg C, minimum retirement thickness t_min is 4.0 mm. Immediate repair or replacement required if t_actual <= 4.5 mm.",
      "score": 0.892
    }
  ]
}
```

---

## 6. Deliverables & Outputs

### `GET /api/outputs/{filename}`
Streams generated deliverable (`.docx`, `.xlsx`, `.pptx`) to client for immediate download.

---

## 7. Security & Sovereignty

### `GET /api/security/status`
Returns real-time hardware, network socket telemetry, and air-gap verification stats.

**Response `200 OK`**:
```json
{
  "air_gapped": true,
  "inference_runtime": "local_ollama",
  "inference_endpoint": "http://127.0.0.1:11434",
  "vector_db": "embedded_qdrant_disk",
  "active_sockets": [
    {"process": "uvicorn", "local_addr": "127.0.0.1:8000", "state": "LISTEN"},
    {"process": "ollama", "local_addr": "127.0.0.1:11434", "state": "LISTEN"}
  ],
  "external_ai_api_calls": 0,
  "external_network_connections": 0,
  "sandbox_network_isolated": true
}
```

### `GET /api/security/events`
Returns structured audit trail from SQLite ledger.
