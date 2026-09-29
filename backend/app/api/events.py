"""
AGNI Canonical Event API Router
===============================
Supports automated event ingestion and manual analyst workflows:
Create, read, update, and delete events with automatic risk engine evaluation.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import datetime
from backend.app.schemas.canonical import Event
from backend.app.repositories.intel_store import intel_store

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=List[Event])
async def list_events():
    """Retrieve all ingested and analyst-created geopolitical events."""
    return intel_store.list_events()


@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Retrieve a specific geopolitical event by ID."""
    evt = intel_store.get_event(event_id)
    if not evt:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    return evt


@router.post("", response_model=Event, status_code=201)
async def create_event(event: Event):
    """Create a new geopolitical event (manual analyst workbench or automated feed)."""
    if not event.event_id:
        event.event_id = f"evt-{uuid.uuid4().hex[:8]}"
    if not event.timestamp:
        event.timestamp = datetime.utcnow().isoformat()
    return intel_store.create_event(event)


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
