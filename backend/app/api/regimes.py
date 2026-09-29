"""
AGNI Statistical Regime Detection API Router
============================================
Exposes 4-state Markov Switching / Gaussian HMM regime detection:
- Regimes: CALM, ELEVATED, STRESSED, CRISIS
- Estimates:
    * Filtered & smoothed regime probabilities (zero manual assignment)
    * 4x4 Markov transition probability matrix
    * Expected regime persistence duration (1 / (1 - P_ii))
    * Standardized feature contribution scores
"""

from fastapi import APIRouter, Query
from typing import Optional, Dict, Any

from backend.app.schemas.canonical import RegimeState
from agni.regimes.detector import statistical_regime_engine
from backend.app.repositories.intel_store import intel_store

router = APIRouter(prefix="/regimes", tags=["Regimes"])


@router.get("", response_model=RegimeState)
async def get_current_regime():
    """
    Retrieve current statistically fitted Markov Switching / Gaussian HMM regime state.
    Includes posterior probabilities, 4x4 transition matrix, expected durations,
    and feature driver contributions.
    """
    state = statistical_regime_engine.fit_from_market_store()
    intel_store.set_regime_state(state)
    return state


@router.get("/probabilities")
async def get_regime_probabilities() -> Dict[str, Any]:
    """Retrieve discrete regime probabilities and dominant state."""
    state = statistical_regime_engine.fit_from_market_store()
    return {
        "current_regime": state.current_regime,
        "probability": state.probability,
        "regime_probabilities": state.regime_probabilities,
        "model_type": state.model_type,
        "timestamp": state.timestamp,
    }


@router.get("/transition-matrix")
async def get_transition_matrix() -> Dict[str, Any]:
    """Retrieve 4x4 Markov transition probability matrix and expected regime durations."""
    state = statistical_regime_engine.fit_from_market_store()
    return {
        "transition_probabilities": state.transition_probabilities,
        "expected_durations_days": state.expected_durations,
        "formula": "E[D_i] = 1 / (1 - P_ii)",
    }


@router.get("/drivers")
async def get_regime_drivers() -> Dict[str, Any]:
    """Retrieve feature attribution scores contributing to the active regime."""
    state = statistical_regime_engine.fit_from_market_store()
    return {
        "current_regime": state.current_regime,
        "feature_contributions": state.feature_contributions,
        "features_used": state.features_used,
    }
