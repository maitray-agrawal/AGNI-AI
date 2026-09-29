"""
AGNI Event Processing Engine
============================
Deterministic ingestion, validation, and risk score calculation for canonical events.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from backend.app.schemas.canonical import (
    Event,
    RiskSignal,
    RiskSignalComponent,
    TransmissionLink,
    SeverityLevel,
)
from configs.settings import research_settings


SEVERITY_SCORES: Dict[SeverityLevel, float] = {
    "critical": 92.0,
    "high": 78.0,
    "elevated": 62.0,
    "moderate": 44.0,
    "low": 25.0,
    "info": 10.0,
}


class EventProcessingEngine:
    """Processes canonical geopolitical events into deterministic risk signals."""

    @staticmethod
    def process_event(event: Event) -> RiskSignal:
        """Calculates deterministic composite risk score and transmission links."""
        base_score = SEVERITY_SCORES.get(event.severity, 50.0)
        calibrated_score = round(base_score * event.confidence, 1)

        # Build components
        components: List[RiskSignalComponent] = [
            RiskSignalComponent(
                component_name="Severity Weight",
                weight=0.45,
                raw_score=base_score,
                weighted_contribution=round(base_score * 0.45, 1),
                description=f"Direct severity ranking: {event.severity.upper()}",
            ),
            RiskSignalComponent(
                component_name="Epistemic Confidence",
                weight=0.30,
                raw_score=event.confidence * 100,
                weighted_contribution=round(event.confidence * 30.0, 1),
                description=f"Source reliability and verification confidence ({event.confidence:.0%})",
            ),
            RiskSignalComponent(
                component_name="Exposure Breadth",
                weight=0.25,
                raw_score=min(100.0, float(len(event.affected_assets) + len(event.affected_commodities)) * 25.0),
                weighted_contribution=round(min(25.0, float(len(event.affected_assets) + len(event.affected_commodities)) * 6.25), 1),
                description="Cross-asset & commodity exposure breadth",
            ),
        ]

        # Build sequential transmission links
        transmission_links: List[TransmissionLink] = []
        channels = event.transmission_channels or ["Sovereign Disruption", "Market Volatility"]
        for i in range(len(channels) - 1):
            transmission_links.append(
                TransmissionLink(
                    source=channels[i],
                    target=channels[i + 1],
                    weight=round(0.95 - (i * 0.08), 2),
                    confidence=event.confidence,
                    evidence_state="DERIVED",
                )
            )

        return RiskSignal(
            signal_id=f"sig-{event.event_id}",
            event_id=event.event_id,
            timestamp=event.timestamp or datetime.now(timezone.utc).isoformat(),
            title=f"Risk Signal: {event.title}",
            composite_score=min(100.0, max(0.0, calibrated_score)),
            risk_level=event.severity,
            primary_region=event.region,
            latitude=event.latitude,
            longitude=event.longitude,
            components=components,
            transmission_path=transmission_links,
            is_demo_data=event.is_demo_data,
        )
