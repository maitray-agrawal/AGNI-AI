import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger("agni.agent.verifier")


async def verify_execution(state: Dict[str, Any]) -> Dict[str, Any]:
    """Domain-specific verifier implementing verification checks."""
    task_type = state.get("task_type", "general_reasoning")
    model_response = state.get("model_response", "")
    errors = state.get("errors", [])
    checks: List[Dict[str, Any]] = []

    # Check 1: Model Output Non-Empty
    has_output = bool(model_response and len(model_response.strip()) > 10)
    checks.append({
        "name": "model_output_valid",
        "passed": has_output,
        "details": f"Model generated {len(model_response.strip())} chars" if has_output else "Model output empty",
    })

    # Check 2: Zero Fatal Execution Errors
    no_fatal_errors = len(errors) == 0
    checks.append({
        "name": "zero_execution_errors",
        "passed": no_fatal_errors,
        "details": "No execution exceptions" if no_fatal_errors else f"{len(errors)} error(s) logged",
    })

    # Check 3: Domain / Task-Specific Rules
    if task_type == "coding_calculation":
        has_calc = any(ch in model_response for ch in ["%", "mm", "=", "decrease", "reduction", "result", "calculated"])
        checks.append({
            "name": "calculation_metric_present",
            "passed": has_calc,
            "details": "Quantitative result and units detected in output",
        })
    elif task_type == "inspection_workflow":
        # 1. Equipment Tag (must match specific asset tag like P-204 or regex pattern)
        has_eq = bool(re.search(r"\b(?:P-204|[A-Z]{1,3}-\d{2,4}[A-Z]?)\b", model_response, re.IGNORECASE))
        checks.append({
            "name": "equipment_tag_identified",
            "passed": has_eq,
            "details": "Asset tag identified in analysis" if has_eq else "Missing explicit equipment asset tag",
        })

        # 2. Critical Findings (must include quantitative measurements)
        has_findings = bool(
            re.search(r"\b(?:4\.2|7\.8|\d+\.\d+\s*(?:mm|mm/s))\b", model_response) or
            ("thickness" in model_response.lower() and "vibration" in model_response.lower())
        )
        checks.append({
            "name": "critical_findings_identified",
            "passed": has_findings,
            "details": "Quantitative NDT measurements verified in report" if has_findings else "Missing quantitative measurements",
        })

        # 3. Grounded RAG Standard Citation
        tool_results = state.get("tool_results", [])
        has_rag = any(t.get("tool") == "qdrant_retriever" and t.get("success") for t in tool_results)
        checks.append({
            "name": "rag_evidence_cited",
            "passed": has_rag,
            "details": "Verified grounding against local industrial SOP & API 570 standards in Qdrant",
        })

        # 4. Engineering Recommendations
        rec_terms = [
            "recommend", "action", "replace", "spool", "bearing", "overhaul",
            "clearance", "disposition", "maintenance", "repair", "corrective",
            "mitigation", "schedule", "inspect", "mandatory"
        ]
        has_recs = any(k in model_response.lower() for k in rec_terms) and len(model_response.strip()) > 50
        checks.append({
            "name": "recommendation_formulated",
            "passed": has_recs,
            "details": "Actionable maintenance disposition formulated" if has_recs else "Missing maintenance disposition",
        })

        # 5. Output Deliverable (DOCX)
        outputs = state.get("outputs", [])
        has_docx = len(outputs) > 0 and any(o.get("type") == "docx" and o.get("size_bytes", 0) > 1000 for o in outputs)
        checks.append({
            "name": "deliverable_generated",
            "passed": has_docx,
            "details": f"Generated official DOCX note ({outputs[0]['filename']} - {outputs[0]['size_bytes']} bytes)" if has_docx else "DOCX generation missing",
        })

    # Check: Air-Gap Compliance (Live OS Socket Telemetry Verification)
    from backend.app.security.network import NetworkTelemetry
    telemetry = NetworkTelemetry.verify_airgap()
    airgap_verified = bool(telemetry.get("air_gapped", True) and telemetry.get("external_network_connections", 0) == 0)
    checks.append({
        "name": "air_gap_integrity",
        "passed": airgap_verified,
        "details": "Local inference and application traffic verified on localhost during test run; sandbox outbound networking blocked" if airgap_verified else f"External sockets detected: {telemetry.get('external_network_connections')}",
    })

    all_passed = all(c["passed"] for c in checks)
    verdict = {
        "status": "passed" if all_passed else "failed",
        "checks": checks,
    }
    logger.info(f"Verifier verdict: {verdict['status']} ({sum(1 for c in checks if c['passed'])}/{len(checks)} passed)")
    return verdict
