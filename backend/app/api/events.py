"""
AGNI Canonical Event API Router
===============================
Supports automated event ingestion and manual analyst workflows:
CREATE EVENT → validate → normalize → persist → calculate features → calculate risk → construct transmission links → generate intelligence result.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

from backend.app.schemas.canonical import Event, EventIntelligenceResult
from backend.app.repositories.intel_store import intel_store
from agni.events.workflow import EventWorkflow
from agni.events.validation import ValidationError

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=List[Event])
async def list_events(region: Optional[str] = None):
    """Retrieve all ingested and analyst-created geopolitical events."""
    events = intel_store.list_events()
    if region:
        events = [e for e in events if region.lower() in e.region.lower()]
    return events


@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Retrieve a specific geopolitical event by ID."""
    evt = intel_store.get_event(event_id)
    if not evt:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    return evt


@router.get("/{event_id}/intelligence", response_model=EventIntelligenceResult)
async def get_event_intelligence(event_id: str):
    """
    Retrieve explainable intelligence results for an event:
    Explicit factors (event_intensity, country_exposure, commodity_exposure,
    asset_exposure, route_exposure, historical_response, regime_multiplier, confidence),
    synthesized risk score, explanatory drivers, and multi-hop transmission path.
    """
    intel = intel_store.get_event_intelligence(event_id)
    if not intel:
        # Fallback to EventWorkflow on-demand evaluation
        intel = EventWorkflow.get_event_intelligence(event_id)
    if not intel:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    return intel


@router.post("", response_model=Event, status_code=201)
async def create_event(payload: Dict[str, Any]):
    """
    Manual Analyst Event Creation & Ingestion Workflow:
    CREATE EVENT
    → validate
    → normalize
    → persist
    → calculate features (8 explicit factors)
    → calculate risk
    → construct transmission links
    → generate intelligence result
    """
    try:
        result = EventWorkflow.execute_manual_workflow(payload)
        return result["event"]
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Event ingestion error: {str(ex)}")


@router.put("/{event_id}", response_model=Event)
async def update_event(event_id: str, updated_event: Event):
    """Update an existing geopolitical event and re-evaluate risk scores."""
    updated = intel_store.update_event(event_id, updated_event)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    return updated


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: str):
    """Delete a geopolitical event and associated risk signals."""
    deleted = intel_store.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    return None
