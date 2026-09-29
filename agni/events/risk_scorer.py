"""
AGNI Explainable Risk Scoring Engine
====================================
Computes transparent, auditable sovereign and supply chain risk scores.
No black-box or arbitrary random components. Every driver is directly traced to its factor.
"""

from typing import List, Tuple
from agni.data.schemas import (
    RiskSignalComponent,
    SeverityLevel,
)

# Standard component weights summing to 1.00
FACTOR_WEIGHTS = {
    "event_intensity": 0.25,
    "country_exposure": 0.15,
    "commodity_exposure": 0.20,
    "asset_exposure": 0.15,
    "route_exposure": 0.15,
    "historical_response": 0.10,
}


class ExplainableRiskScorer:
    """Calculates composite risk score and explanatory drivers from explicit factors."""

    @classmethod
    def classify_severity(cls, score: float) -> SeverityLevel:
        """Standard institutional risk rating thresholds."""
        if score >= 80.0:
            return "critical"
        elif score >= 65.0:
            return "high"
        elif score >= 45.0:
            return "elevated"
        elif score >= 25.0:
            return "moderate"
        elif score >= 10.0:
            return "low"
        return "info"

    @classmethod
    def compute_score(
        cls,
        components: RiskSignalComponent,
        custom_weights: dict = None,
    ) -> Tuple[float, SeverityLevel, List[str]]:
        """
        Executes explicit linear factor combination:
          raw_score = sum(factor_i * weight_i)
          calibrated_score = min(100.0, raw_score * regime_multiplier)
        Returns (risk_score, risk_level, drivers).
        """
        w = custom_weights or FACTOR_WEIGHTS

        raw_score = (
            (w["event_intensity"] * components.event_intensity)
            + (w["country_exposure"] * components.country_exposure)
            + (w["commodity_exposure"] * components.commodity_exposure)
            + (w["asset_exposure"] * components.asset_exposure)
            + (w["route_exposure"] * components.route_exposure)
            + (w["historical_response"] * components.historical_response)
        )

        calibrated_score = round(
            min(100.0, max(0.0, raw_score * components.regime_multiplier)),
            1,
        )
        risk_level = cls.classify_severity(calibrated_score)

        # Generate auditable explanatory drivers from explicit factors
        drivers: List[str] = []
        if components.event_intensity >= 75.0:
            drivers.append(f"High verified event intensity ({components.event_intensity:.1f}/100) from ground telemetry")
        if components.country_exposure >= 80.0:
            drivers.append(f"Elevated sovereign systemic exposure ({components.country_exposure:.1f}/100) in strategic theater")
        if components.commodity_exposure >= 65.0:
            drivers.append(f"Critical commodity transit dependency ({components.commodity_exposure:.1f}/100)")
        if components.asset_exposure >= 60.0:
            drivers.append(f"Broad capital market transmission sensitivity ({components.asset_exposure:.1f}/100)")
        if components.route_exposure >= 75.0:
            drivers.append(f"Direct operational shock to global maritime transit arteries ({components.route_exposure:.1f}/100)")
        if components.historical_response >= 70.0:
            drivers.append(f"Historical analogue persistence confirms multi-week shock half-life ({components.historical_response:.1f}/100)")
        if components.regime_multiplier > 1.0:
            drivers.append(f"Regime amplifier active (multiplier ×{components.regime_multiplier:.2f})")

        if not drivers:
            drivers.append(f"Baseline risk index computed from {risk_level.upper()} severity factors")

        return (calibrated_score, risk_level, drivers)
