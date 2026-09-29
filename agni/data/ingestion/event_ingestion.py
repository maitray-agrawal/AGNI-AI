"""
AGNI Event Ingestion Pipeline & Manual Workflow Service
======================================================
Processes automated incoming feeds and manual analyst submissions through
a unified pipeline:
1. Validation against Canonical Event Schema
2. Geocoding & Regional Harmonization
3. Feature Engineering & Exposure Mapping
4. Deterministic Risk Scoring & Shock Transmission Extraction
"""

import uuid
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from backend.app.schemas.canonical import (
    Event,
    RiskSignal,
    Evidence,
    AnalystNote,
    EventType,
    SeverityLevel,
)
from backend.app.services.risk_engine import risk_signal_engine
from backend.app.repositories.intel_store import intel_store


class EventIngestionPipeline:
    """Unified ingestion pipeline for automated telemetry and manual analyst creation."""

    @classmethod
    def ingest_manual_event(
        cls,
        title: str,
        description: str,
        country: str,
        region: str,
        latitude: float,
        longitude: float,
        event_type: EventType = "other",
        severity: SeverityLevel = "moderate",
        confidence: float = 0.85,
        source: str = "Analyst Manual Entry",
        affected_assets: list[str] = None,
        affected_commodities: list[str] = None,
        affected_routes: list[str] = None,
        transmission_channels: list[str] = None,
        analyst_notes_text: Optional[str] = None,
        evidence_text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Tuple[Event, RiskSignal]:
        """Ingests a manual event, validates it, and generates its risk signal."""
        eid = event_id or f"evt-analyst-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        # Build evidence list if provided
        evidence_list = []
        if evidence_text:
            evidence_list.append(
                Evidence(
                    evidence_id=f"evi-{uuid.uuid4().hex[:6]}",
                    timestamp=now,
                    evidence_state="OBSERVED",
                    source_name=source,
                    headline=evidence_text,
                    confidence=confidence,
                )
            )

        # Build analyst notes
        notes_list = []
        if analyst_notes_text:
            notes_list.append(
                AnalystNote(
                    note_id=f"note-{uuid.uuid4().hex[:6]}",
                    timestamp=now,
                    content=analyst_notes_text,
                    tags=["manual_analysis", country.lower()],
                )
            )

        # Construct canonical Event
        event = Event(
            event_id=eid,
            timestamp=now,
            event_type=event_type,
            title=title,
            description=description,
            country=country,
            region=region,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            confidence=confidence,
            source=source,
            affected_assets=affected_assets or [],
            affected_commodities=affected_commodities or [],
            affected_routes=affected_routes or [],
            transmission_channels=transmission_channels or [title, "Asset Repricing"],
            evidence=evidence_list,
            analyst_notes=notes_list,
            is_demo_data=False,
        )

        # Store event and generate explainable risk signal
        stored_event = intel_store.create_event(event)
        risk_signal = intel_store.get_signal(f"sig-{stored_event.event_id}")

        return stored_event, risk_signal


event_ingestion_pipeline = EventIngestionPipeline()
