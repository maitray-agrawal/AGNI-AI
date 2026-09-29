"""
AGNI Quantitative Risk Research Engine
======================================
Deterministic risk scoring calculation based on severity, confidence,
cross-asset/commodity exposures, and multi-hop transmission chains.
"""

from typing import List, Dict, Any
from backend.app.schemas.canonical import (
    Event,
    RiskSignal,
    RiskSignalComponent,
    TransmissionLink,
)


class RiskResearchEngine:
    """Core deterministic risk scoring and transmission path tracing."""

    @staticmethod
    def calculate_event_risk(event: Event) -> Dict[str, Any]:
        """Calculates multi-dimensional risk scores from a canonical Event."""
        severity_multipliers = {
            "critical": 1.0,
            "high": 0.80,
            "elevated": 0.60,
            "moderate": 0.40,
            "low": 0.20,
            "info": 0.05,
        }

        mult = severity_multipliers.get(event.severity, 0.40)
        base_score = 100.0 * mult
        calibrated_score = round(base_score * event.confidence, 1)

        exposure_count = len(event.affected_assets) + len(event.affected_commodities) + len(event.affected_routes)
        exposure_multiplier = min(1.5, 1.0 + (exposure_count * 0.08))

        systemic_risk_index = round(min(100.0, calibrated_score * exposure_multiplier), 1)

        return {
            "event_id": event.event_id,
            "severity": event.severity,
            "confidence": event.confidence,
            "base_score": base_score,
            "calibrated_score": calibrated_score,
            "systemic_risk_index": systemic_risk_index,
            "exposure_count": exposure_count,
            "epistemic_state": "DERIVED",
        }
