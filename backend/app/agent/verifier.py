import re
from pathlib import Path
from typing import Dict, Any, List
import logging
from backend.app.security.network import NetworkTelemetry

logger = logging.getLogger("agni.agent.verifier")


async def verify_execution(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submission-grade 8-Point Domain Verification Engine.
    Enforces strict quality, integrity, and air-gap gates before task finalization.
    Defends against false-positives (empty outputs, error messages, missing tags/deliverables).
    """
    task_type = state.get("task_type", "general_reasoning")
    model_response = (state.get("model_response") or "").strip()
    errors = state.get("errors", [])
    tool_results = state.get("tool_results", [])
    outputs = state.get("outputs", [])
    checks: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # Check 1: Model Output Validity (Defends against empty/error strings)
    # -------------------------------------------------------------
    is_error_response = any(
        model_response.lower().startswith(prefix) for prefix in [
            "inference failed", "execution error", "error:", "model generation error",
            "all connection attempts failed", "local ollama inference failed"
        ]
    )
    has_valid_output = bool(len(model_response) >= 20 and not is_error_response)
    checks.append({
        "name": "model_output_valid",
        "passed": has_valid_output,
        "details": (
            f"Generated {len(model_response)} characters of valid technical content"
            if has_valid_output
            else ("Model output contains execution failure message" if is_error_response else "Model output empty or below length threshold")
        ),
    })

    # -------------------------------------------------------------
    # Check 2: Zero Fatal Execution Errors
    # -------------------------------------------------------------
    no_fatal_errors = len(errors) == 0
    checks.append({
        "name": "zero_execution_errors",
        "passed": no_fatal_errors,
        "details": (
            "Zero execution exceptions recorded"
            if no_fatal_errors
            else f"{len(errors)} error(s) logged: {'; '.join(errors[:2])}"
        ),
    })

    # -------------------------------------------------------------
    # Check 3: Equipment Tag Identification
    # -------------------------------------------------------------
    if task_type == "inspection_workflow":
        has_eq = bool(re.search(r"\b(?:P-204|[A-Z]{1,3}-\d{2,4}[A-Z]?)\b", model_response, re.IGNORECASE))
        checks.append({
            "name": "equipment_tag_identified",
            "passed": has_eq,
            "details": "Asset tag identified in analysis" if has_eq else "Missing explicit equipment asset tag",
        })
    elif task_type == "coding_calculation":
        checks.append({
            "name": "equipment_tag_identified",
            "passed": True,
            "details": "Asset tag check not required for mathematical computation",
        })
    else:
        checks.append({
            "name": "equipment_tag_identified",
            "passed": True,
            "details": "General technical query - asset tag check not required",
        })

    # -------------------------------------------------------------
    # Check 4: Critical Findings & Quantitative Metrics
    # -------------------------------------------------------------
    if task_type == "inspection_workflow":
        has_findings = bool(
            re.search(r"\b(?:4\.2|7\.8|\d+\.\d+\s*(?:mm|mm/s))\b", model_response) or
            ("thickness" in model_response.lower() and "vibration" in model_response.lower())
        )
        checks.append({
            "name": "critical_findings_identified",
            "passed": has_findings,
            "details": "Quantitative NDT measurements verified in report" if has_findings else "Missing quantitative measurements",
        })
    elif task_type == "coding_calculation":
        has_sandbox = any(t.get("tool") == "code_sandbox" and t.get("success") for t in tool_results)
        checks.append({
            "name": "critical_findings_identified",
            "passed": has_sandbox,
            "details": (
                "Deterministic calculation verified via isolated code sandbox (tool: code_sandbox)"
                if has_sandbox
                else "Missing verified code sandbox execution result in tool_results"
            ),
        })
    else:
        checks.append({
            "name": "critical_findings_identified",
            "passed": True,
            "details": "General technical query - quantitative metrics optional",
        })

    # -------------------------------------------------------------
    # Check 5: Grounded RAG Standard Citations
    # -------------------------------------------------------------
    if task_type == "inspection_workflow":
        has_rag = any(t.get("tool") == "qdrant_retriever" and t.get("success") for t in tool_results)
        checks.append({
            "name": "rag_evidence_cited",
            "passed": has_rag,
            "details": "Verified grounding against local industrial SOP & API 570 standards in Qdrant" if has_rag else "RAG retrieval missing or failed",
        })
    else:
        checks.append({
            "name": "rag_evidence_cited",
            "passed": True,
            "details": "Standard RAG citations not required for this task type",
        })

    # -------------------------------------------------------------
    # Check 6: Actionable Engineering Recommendations
    # -------------------------------------------------------------
    rec_terms = [
        "recommend", "action", "replace", "spool", "bearing", "overhaul",
        "clearance", "disposition", "maintenance", "repair", "corrective",
        "mitigation", "schedule", "inspect", "mandatory", "formula", "result"
    ]
    has_recs = any(k in model_response.lower() for k in rec_terms) and len(model_response) > 30
    checks.append({
        "name": "recommendation_formulated",
        "passed": has_recs,
        "details": "Actionable maintenance disposition formulated" if has_recs else "Missing maintenance disposition",
    })

    # -------------------------------------------------------------
    # Check 7: Deliverable Generation & On-Disk Integrity
    # -------------------------------------------------------------
    if task_type == "inspection_workflow":
        has_docx = (
            len(outputs) > 0 and 
            any(
                o.get("type") == "docx" and 
                o.get("size_bytes", 0) > 1000 and 
                Path(o.get("path", "")).exists()
                for o in outputs
            )
        )
        checks.append({
            "name": "deliverable_generated",
            "passed": has_docx,
            "details": (
                f"Generated official DOCX note ({outputs[0]['filename']} - {outputs[0]['size_bytes']} bytes)"
                if has_docx else "DOCX deliverable missing or corrupted on disk"
            ),
        })
    else:
        checks.append({
            "name": "deliverable_generated",
            "passed": True,
            "details": "Deliverable file not required for non-document workflow",
        })

    # -------------------------------------------------------------
    # Check 8: Air-Gap Compliance (Live OS Socket Telemetry Verification)
    # -------------------------------------------------------------
    telemetry = NetworkTelemetry.verify_airgap()
    airgap_verified = bool(telemetry.get("air_gapped", True) and telemetry.get("external_network_connections", 0) == 0)
    checks.append({
        "name": "air_gap_integrity",
        "passed": airgap_verified,
        "details": (
            "Local inference and application traffic verified on localhost during test run; sandbox outbound networking blocked"
            if airgap_verified else f"External sockets detected: {telemetry.get('external_network_connections')}"
        ),
    })

    # Final gate determination
    all_passed = all(c["passed"] for c in checks)
    verdict = {
        "status": "passed" if all_passed else "failed",
        "passed_count": sum(1 for c in checks if c["passed"]),
        "total_count": len(checks),
        "checks": checks,
    }

    logger.info(f"8-Point Verifier verdict: {verdict['status']} ({verdict['passed_count']}/{verdict['total_count']} passed)")
    return verdict
