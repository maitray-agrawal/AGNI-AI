# AGNI-AI Security & Sovereignty Architecture

## 1. Threat Model for Confidential Industrial Environments

In critical infrastructure and refining facilities such as **MRPL**, leakage of engineering drawings, non-destructive testing (NDT) reports, operational logs, and maintenance procedures presents grave operational, commercial, and national security risks:
- **Risk 1: Data Exfiltration via Cloud AI APIs**: Transmitting plant schematics or equipment vulnerabilities to external commercial LLM APIs exposes confidential assets.
- **Risk 2: Remote Code Execution via LLM Code Generation**: Agents generating unchecked Python scripts could execute arbitrary commands or establish reverse shells.
- **Risk 3: Model Hallucination in Life-Critical Operations**: Generating invalid equipment clearance approvals without source grounding could lead to catastrophic industrial failure.

---

## 2. Enforcement Architecture (Air-Gap & Isolation)

AGNI-AI enforces multi-layered local boundaries:

### 2.1 Loopback Model & Database Binding
- FastAPI backend binds exclusively to `127.0.0.1:8000`.
- Ollama inference runtime binds exclusively to `127.0.0.1:11434`.
- Embedded Qdrant vector database operates in-process with local disk storage (`./data/qdrant_storage`), eliminating open network ports.
- No cloud API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.) are configured, permitted, or imported anywhere in the codebase.

### 2.2 Sandboxed Code Execution
- Generated Python code is executed in an isolated environment with:
  - `network=none` (Docker container network disabled completely).
  - Strict wall-clock execution timeout (default 10 seconds).
  - Memory limit (maximum 512 MB).
  - Read-only root filesystem where applicable, with temporary scratch directory discarded on exit.
  - Zero access to host environment variables, secrets, or parent directories.
- In process-fallback mode (when Docker daemon is absent), the system invokes subprocesses with restricted environment (`env={}`), explicit socket-creation monkey-patch blocking, and execution timeouts.

### 2.3 Grounded Verification (7-Point Guardrail)
Before any approval note or deliverable is finalized:
1. **Equipment ID Check**: Validates that target asset tag matches engineering conventions (e.g. `P-204`).
2. **Date Extraction Check**: Validates valid inspection timestamp.
3. **Findings Extraction Check**: Verifies non-empty quantitative measurements (e.g. wall thickness, vibration).
4. **Citation Check**: Verifies that recommendation directly references an indexed local standard or SOP page.
5. **Recommendation Formulation**: Confirms engineering disposition (Acceptable / Monitor / Repair / Replace).
6. **Deliverable Check**: Validates that the generated `.docx` file was written, is non-zero, and is structurally valid XML.
7. **Air-Gap Verification**: Validates that zero external network egress occurred during task execution.

---

## 3. Observability & Telemetry (No Faked Status)

AGNI-AI distinguishes strictly between:
- **Network Policy**: Enforced loopback binding and disabled outbound routes.
- **Network Observation**: Live socket scanning using OS-level inspection (`psutil.net_connections()`), identifying PID, protocol, local IP, and remote IP. Any remote IP outside `127.0.0.1`, `::1`, or `0.0.0.0` triggers an immediate security alert.
- **Application Audit Ledger**: SQLite database (`outputs/audit.db`) storing an immutable record of every run:
  - `task_id` (UUID)
  - `timestamp_utc`
  - `prompt_summary`
  - `models_invoked`
  - `tools_executed`
  - `retrieved_chunks` (with exact document and page references)
  - `deliverable_hashes` (SHA-256 digest of generated DOCX/XLSX)
  - `security_verdict` (100% Local / Flagged)
