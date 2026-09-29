"""
AGNI Global Signal Field API Router
===================================
Provides real-time explainable risk signals for the global map and intelligence panels.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from backend.app.schemas.canonical import RiskSignal
from backend.app.repositories.intel_store import intel_store

router = APIRouter(prefix="/signals", tags=["Signals"])


@router.get("", response_model=List[RiskSignal])
async def list_signals():
    """Retrieve all active geopolitical risk signals."""
    return intel_store.list_signals()


@router.get("/{signal_id}", response_model=RiskSignal)
async def get_signal(signal_id: str):
    """Retrieve an individual risk signal with full component explainability and transmission path."""
    sig = intel_store.get_signal(signal_id)
    if not sig:
        raise HTTPException(status_code=404, detail=f"Signal '{signal_id}' not found")
    return sig
