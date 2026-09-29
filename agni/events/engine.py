"""
AGNI Event Processing Engine
============================
Orchestrates the complete event-to-risk intelligence pipeline:
validate → normalize → persist → calculate features → calculate risk → construct transmission links → generate intelligence result.
"""

from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime, timezone

from agni.data.schemas import (
    Event,
    RiskSignal,
    RiskSignalComponent,
    TransmissionLink,
    EventIntelligenceResult,
    RegimeType,
)
from agni.events.ingestion import EventIngestionService
from agni.events.features import FeatureCalculator
from agni.events.risk_scorer import ExplainableRiskScorer
from agni.events.transmission import TransmissionGenerator


class EventProcessingEngine:
    """Core intelligence engine executing the full event evaluation workflow."""

    @classmethod
    def evaluate_and_generate_intelligence(
        cls,
        event: Event,
        current_regime: RegimeType = "ELEVATED",
    ) -> Tuple[RiskSignal, EventIntelligenceResult]:
        """
        Executes analytical steps:
        1. Calculate features (8 explicit factors)
        2. Calculate risk (explainable linear scoring + regime adjustment)
        3. Construct transmission links (causal multi-hop path)
        4. Assemble canonical RiskSignal and EventIntelligenceResult
        """
        # 1. Calculate features
        components: RiskSignalComponent = FeatureCalculator.calculate_components(
            event=event,
            current_regime=current_regime,
        )

        # 2. Calculate risk score & explanatory drivers
        risk_score, risk_level, drivers = ExplainableRiskScorer.compute_score(components)

        # 3. Construct transmission links
        transmission_path: list[TransmissionLink] = TransmissionGenerator.generate_path(event)

        # 4. Canonical RiskSignal model
        signal = RiskSignal(
            signal_id=f"sig-{event.event_id}",
            event_id=event.event_id,
            timestamp=event.timestamp or datetime.now(timezone.utc).isoformat(),
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=components.confidence,
            components=components,
            drivers=drivers,
            affected_regions=[event.region],
            affected_assets=event.affected_assets,
            affected_commodities=event.affected_commodities,
            transmission_path=transmission_path,
            is_demo_data=event.is_demo_data,
        )

        # 5. Synthesized EventIntelligenceResult model
        intel_result = EventIntelligenceResult(
            event_id=event.event_id,
            title=event.title,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=components.confidence,
            components=components,
            drivers=drivers,
            affected_assets=event.affected_assets,
            affected_commodities=event.affected_commodities,
            affected_routes=event.affected_routes,
            transmission_path=transmission_path,
            epistemic_state="DERIVED",
            calculated_at=datetime.now(timezone.utc).isoformat(),
        )

        return (signal, intel_result)

    @classmethod
    def process_event(
        cls,
        payload: Union[Dict[str, Any], Event],
        persist: bool = True,
        current_regime: Optional[RegimeType] = None,
    ) -> Dict[str, Any]:
        """
        Full AGNI manual and automated workflow:
        CREATE EVENT → validate → normalize → persist → calculate features → calculate risk → construct transmission links → generate intelligence result.
        """
        # Step 1 & 2: Ingest, Validate, and Normalize
        normalized_event: Event = EventIngestionService.ingest(payload)

        # Retrieve prevailing regime
        from backend.app.repositories.intel_store import intel_store
        regime = current_regime or intel_store.get_regime_state().current_regime

        # Step 4, 5, 6: Calculate features, risk score, and transmission path
        signal, intel_result = cls.evaluate_and_generate_intelligence(
            event=normalized_event,
            current_regime=regime,
        )

        # Step 3: Persist into analytical store
        if persist:
            intel_store.create_event(normalized_event)
            # Store signal into store index
            intel_store._signals[signal.signal_id] = signal

        return {
            "event": normalized_event,
            "signal": signal,
            "intelligence": intel_result,
            # Direct mapping matching the example output requested:
            "risk_score": intel_result.risk_score,
            "risk_level": intel_result.risk_level,
            "confidence": intel_result.confidence,
            "drivers": intel_result.drivers,
            "affected_assets": intel_result.affected_assets,
            "affected_commodities": intel_result.affected_commodities,
            "transmission_path": [link.model_dump() for link in intel_result.transmission_path],
        }
