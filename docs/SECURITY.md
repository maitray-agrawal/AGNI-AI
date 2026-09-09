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

### 2.3 Grounded Verification (8-Point Guardrail)
Before any approval note or deliverable is finalized:
1. **Model Output Validity**: Validates non-empty model generation (>10 characters).
2. **Execution Integrity**: Confirms zero unhandled runtime or tool exceptions.
3. **Equipment Tag Check**: Validates that target asset tag matches engineering conventions (e.g. `P-204`).
4. **Quantitative Findings Check**: Verifies quantitative NDT measurements (e.g. wall thickness in mm, vibration in mm/s).
5. **Standard Citation Check**: Verifies that recommendations cite indexed industrial standards (API 570, ISO 10816-3).
6. **Recommendation Formulation**: Confirms actionable engineering maintenance disposition.
7. **Deliverable Check**: Validates that the generated `.docx` file was written, is non-zero (>1,000 bytes), and is structurally valid XML.
8. **Air-Gap Telemetry Check**: Validates via real OS socket inspection (`psutil`) that all active application sockets remain on localhost loopback with zero external connections during task execution.

---

## 3. Observability & Telemetry (No Faked Status)

AGNI-AI distinguishes strictly between:
- **Network Policy (Enforced)**: Enforced loopback binding (`127.0.0.1`) and sandbox `network=none` container mode.
- **Sandbox Defense (Blocked)**: Outbound socket creation in sandbox processes is intercepted by a runtime monkey-patch raising `PermissionError`.
- **Network Observation (Observed)**: Live socket scanning using OS-level inspection (`psutil.net_connections()`), identifying PID, protocol, local IP, and remote IP. Any remote IP outside `127.0.0.1`, `::1`, or `0.0.0.0` triggers an immediate security alert.
- **Inferred Scope (Inferred)**: Socket observation confirms that no outbound network connections were open at scan time; this empirical observation is combined with enforced localhost binding for multi-layered defense.
- **Application Audit Ledger**: SQLite database (`outputs/audit.db`) storing an immutable record of every run:
  - `task_id` (UUID)
  - `timestamp_utc`
  - `prompt_summary`
  - `models_invoked`
  - `tools_executed`
  - `retrieved_chunks` (with exact document and page references)
  - `deliverable_hashes` (SHA-256 digest of generated DOCX/XLSX)
  - `security_verdict` (Localhost Verified / Flagged)
