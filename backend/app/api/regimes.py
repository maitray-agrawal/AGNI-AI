"""
AGNI Regime Detection API Router
================================
Provides current macro/volatility regime state and transition probability matrices.
"""

from fastapi import APIRouter
from backend.app.schemas.canonical import RegimeState
from backend.app.repositories.intel_store import intel_store

router = APIRouter(prefix="/regimes", tags=["Regimes"])


@router.get("", response_model=RegimeState)
async def get_current_regime():
    """Retrieve current fitted Markov Switching regime state and transition matrix."""
    return intel_store.get_regime_state()
