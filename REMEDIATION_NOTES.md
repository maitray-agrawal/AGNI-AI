# AGNI-AI — Remediation & Engineering Roadmap Notes

**Project:** AGNI-AI (AstraX Project Family)
**Document Version:** 1.0.0
**Updated:** September 2026

---

## 1. Completed in Final Hardening Pass

### Fix-1: Retry Correction Injection into Real Model Prompt
- **Root Cause Addressed:** Previously, verifier failure checks were appended only to the general task string in `graph.py` without being consumed deterministically by the `inspection_workflow` prompt builder in `executor.py`.
- **Implementation:**
  - `graph.py` now explicitly sets `exec_state["retry_correction"] = failed_str`.
  - `executor.py` explicitly reads `state.get("retry_correction")` and conditionally inserts a dedicated `[CORRECTION REQUIRED FROM PRIOR ATTEMPT]` block immediately preceding the final engineering recommendation instruction.
  - Added code audit comments in `coding_calculation` and `general_reasoning` paths documenting that task string propagation already routes retry context to those workflows.
- **Verification:** Unit test spying on `client.generate_with_meta` asserting prompt argument ordering, plus live end-to-end multi-step LangGraph retry test capturing the literal retry prompt.

### Fix-2: Degraded Mode Observability & Finalizer Surfacing
- **Root Cause Addressed:** When live extraction failed in `document_parser` or `vision_analyzer`, fallback reference values were substituted silently, making cached/reference values indistinguishable from live document extraction.
- **Implementation:**
  - `executor.py` extends failure tool result entries with `"degraded_mode": True` and `"degraded_reason": str(e)` while preserving `"success": False`.
  - `finalizer.py` scans `tool_results` for `degraded_mode == True` and prepends a visible warning banner (`⚠ DEGRADED MODE: Live extraction failed for {tool} — reference values were used. Reason: {reason}`) to the final returned summary.
  - Frontend `InspectionWorkbench.tsx` renders a prominent `DEGRADED MODE (REFERENCE FALLBACK)` badge when degraded mode is active, or `LIVE EXTRACTION` when live extraction succeeds.
- **Verification:** Real integration test forcing `document_parser.parse_pdf` failure and asserting summary warning banner and tool result metadata.

### Fix-3: Resolution of Port Conflict & `{"detail":"Not Found"}`
- **Root Cause Addressed:** Port 8000 and 5173 were bound by an unrelated background project server (`CrisisOps`/`VAJRA`) running on Python 3.14. Incoming browser requests to `/api/tasks/run` were proxied to the wrong backend, which returned FastAPI's default 404 response: `{"detail":"Not Found"}`.
- **Resolution:** Terminated conflicting processes, bound AGNI-AI FastAPI backend cleanly to `127.0.0.1:8000`, launched Vite frontend on `127.0.0.1:5173`, and validated full browser end-to-end task execution.

### Fix-4: Product Identity & AstraX Realignment
- Removed all hackathon/SIH (Smart India Hackathon, SIH 2025/2026, Problem Statement 26117) terminology from all user-facing documentation, frontend UI headers, footers, backend metadata, and demo scripts.
- Positioned AGNI-AI as an independent product within the **AstraX** project family.

---

## 2. Deferred Items

### P1-1 — Advanced Document Ingestion Pipeline
- **Status:** Deferred
- **Reason:** The current local document extraction path (PyMuPDF with structured page-text and image extraction) is sufficient for the current product milestone and flagship demo path. A broader ingestion pipeline can be integrated subsequently without modifying the core agent, LangGraph state machine, or vector retrieval architecture.
- **Potential Future Scope:**
  - Multi-format ingestion (DOCX, scanned TIFF, complex multi-page PDF schematics)
  - Dedicated local OCR engine fallback (e.g., Tesseract / Surya OCR) for degraded scans
  - Specialized table extraction and tabular parsing (Camelot / pdfplumber table bounding)
  - Fine-grained chunk provenance with bounding-box coordinates
  - Structured metadata schema extraction at ingest time
  - Ingestion integrity validation and checksum deduplication
  - Incremental corpus indexing and background change-detection

---

## 3. Known Limitations

1. **Embedded Qdrant Process Exclusivity:**
   - The current embedded local Qdrant engine stores vector data in `./data/qdrant_storage` using file-based locking (`portalocker`). Only one process (either the backend server or a pytest process) may access the on-disk storage directory concurrently. For multi-process horizontal scaling, an isolated local Qdrant server container or background daemon process can be employed.
2. **CPU Inference Latency:**
   - In environments without dedicated NVIDIA GPU acceleration (e.g., Intel Arc / CPU-only inference), 8B parameter models (`llama3.1:8b`) take between 20 to 60 seconds per synthesis step. The model registry provides lightweight fallbacks (`mistral:latest`, `qwen2.5-coder:7b`) to mitigate latency when needed.
3. **Single Active Retry Cap:**
   - The LangGraph verifier retry loop is strictly capped at `max_retry = 1` to prevent unbounded execution loops and resource exhaustion in air-gapped environments. If verification fails on attempt 2, the task finalizes with `completed_with_warnings` status rather than retrying indefinitely.

---

## 4. Future Improvements

- **Hybrid Dense + Sparse Retrieval:** Combine dense embeddings (`all-MiniLM-L6-v2`) with sparse BM25 lexical search to enhance retrieval for precise engineering alphanumeric codes (e.g., specific valve tags like `FCV-204` or flange ratings).
- **Cross-Encoder Reranking:** Integrate a lightweight local cross-encoder model (e.g., `ms-marco-MiniLM-L-6-v2`) to rerank top-k candidates prior to LLM reasoning context injection.
- **Hardware Acceleration Profiles:** Add automatic hardware detection for Intel oneAPI / OpenVINO / Apple Metal / CUDA to optimize tensor execution on local workstations.
- **Local Quantitative Evaluation Benchmark:** Establish an offline evaluation dataset of engineering inspection reports with ground-truth citations to systematically benchmark precision, recall, and verifier sensitivity across quantized model variants (Q4_K_M vs Q8_0).
- **Multi-Document Knowledge Base Partitioning:** Partition Qdrant collections into isolated tenant/unit spaces (e.g., CDU, VDU, FCCU) with role-based access tokens for multi-unit facilities.
