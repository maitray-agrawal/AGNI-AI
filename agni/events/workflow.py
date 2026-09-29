"""
AGNI Event Workflow
===================
Manual analyst workbench and automated ingestion workflow for canonical events.
"""

from typing import List, Optional
from datetime import datetime, timezone
import uuid

from backend.app.schemas.canonical import Event, RiskSignal
from agni.events.engine import EventProcessingEngine
from backend.app.repositories.intel_store import intel_store


class EventWorkflow:
    """Orchestrates creation, validation, storage, and signal generation for events."""

    @staticmethod
    def ingest_event(event: Event) -> RiskSignal:
        """Stores event in the analytical intel store and generates risk signal."""
        if not event.event_id:
            event.event_id = f"evt-{uuid.uuid4().hex[:8]}"
        if not event.timestamp:
            event.timestamp = datetime.now(timezone.utc).isoformat()

        # Save to store
        stored_event = intel_store.create_event(event)

        # Generate deterministic risk signal
        signal = EventProcessingEngine.process_event(stored_event)
        return signal

    @staticmethod
    def list_all_events() -> List[Event]:
        return intel_store.list_events()

    @staticmethod
    def list_all_signals() -> List[RiskSignal]:
        return intel_store.list_signals()
