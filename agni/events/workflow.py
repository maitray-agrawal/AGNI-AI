"""
AGNI Event Workflow
===================
Manual analyst workbench and automated ingestion workflow for canonical events.
Provides high-level entry points for:
CREATE EVENT → validate → normalize → persist → calculate features → calculate risk → construct transmission links → generate intelligence result.
"""

from typing import List, Optional, Dict, Any, Union
from agni.data.schemas import Event, RiskSignal, EventIntelligenceResult
from agni.events.engine import EventProcessingEngine


class EventWorkflow:
    """Orchestrates creation, validation, storage, and signal generation for events."""

    @classmethod
    def execute_manual_workflow(
        cls,
        payload: Union[Dict[str, Any], Event],
    ) -> Dict[str, Any]:
        """
        Executes the mandatory AGNI Phase 2 workflow:
        1. Validate
        2. Normalize
        3. Persist
        4. Calculate features (8 explicit factors)
        5. Calculate risk
        6. Construct transmission links
        7. Generate intelligence result
        """
        return EventProcessingEngine.process_event(payload, persist=True)

    @classmethod
    def ingest_event(cls, event: Event) -> RiskSignal:
        """Stores event in the analytical intel store and generates risk signal."""
        res = cls.execute_manual_workflow(event)
        return res["signal"]

    @classmethod
    def get_event_intelligence(cls, event_id: str) -> Optional[EventIntelligenceResult]:
        """Retrieves or calculates the real intelligence result for an event."""
        from backend.app.repositories.intel_store import intel_store
        # Check if event exists
        event = intel_store.get_event(event_id)
        if not event:
            return None

        # Check existing signal in store
        sig = intel_store.get_signal(f"sig-{event_id}") or intel_store.get_signal(event_id)
        if sig:
            return EventIntelligenceResult(
                event_id=event.event_id,
                title=event.title,
                risk_score=sig.risk_score,
                risk_level=sig.risk_level,
                confidence=sig.confidence,
                components=sig.components,
                drivers=sig.drivers,
                affected_assets=sig.affected_assets,
                affected_commodities=sig.affected_commodities,
                affected_routes=event.affected_routes,
                transmission_path=sig.transmission_path,
                epistemic_state="DERIVED",
                calculated_at=sig.timestamp,
            )

        # Otherwise evaluate on-demand
        _, intel_result = EventProcessingEngine.evaluate_and_generate_intelligence(
            event=event,
            current_regime=intel_store.get_regime_state().current_regime,
        )
        return intel_result

    @classmethod
    def list_all_events(cls) -> List[Event]:
        from backend.app.repositories.intel_store import intel_store
        return intel_store.list_events()

    @classmethod
    def list_all_signals(cls) -> List[RiskSignal]:
        from backend.app.repositories.intel_store import intel_store
        return intel_store.list_signals()
