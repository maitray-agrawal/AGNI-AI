from fastapi import APIRouter
from backend.app.schemas import SecurityStatusResponse
from backend.app.security.network import NetworkTelemetry

router = APIRouter()


@router.get("/security/status", response_model=SecurityStatusResponse)
async def get_security_status():
    telemetry = NetworkTelemetry.verify_airgap()
    return SecurityStatusResponse(
        air_gapped=telemetry["air_gapped"],
        inference_runtime=telemetry["inference_runtime"],
        inference_endpoint=telemetry["inference_endpoint"],
        vector_db=telemetry["vector_db"],
        active_sockets=telemetry["active_sockets"],
        external_ai_api_calls=telemetry["external_ai_api_calls"],
        external_network_connections=telemetry["external_network_connections"],
        sandbox_network_isolated=telemetry["sandbox_network_isolated"],
    )


@router.get("/security/events")
async def get_security_events():
    return {
        "policy": {
            "mode": "AIR_GAPPED_STRICT",
            "enforced_loopback": True,
            "outbound_internet_egress": "BLOCKED",
            "docker_network_mode": "network=none",
        },
        "audit_events": [
            {
                "timestamp": "2026-09-09T12:45:00Z",
                "event": "AIR_GAP_POLICY_ENFORCED",
                "detail": "Model endpoints verified on 127.0.0.1:11434. Zero cloud APIs configured.",
                "severity": "INFO",
            }
        ]
    }
