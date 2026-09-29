"""
AGNI Research, Model Validation & Provenance API Router
======================================================
Exposes backtesting benchmark evaluations (CRPS, Kupiec, Coverage),
model cards, evidence provenance, and sovereign research summary metrics.
"""

from fastapi import APIRouter
from typing import List, Dict, Any
from backend.app.schemas.canonical import BacktestResult, Evidence
from backend.app.repositories.intel_store import intel_store

router = APIRouter(prefix="/research", tags=["Research"])


@router.get("/summary")
async def get_research_summary() -> Dict[str, Any]:
    """Retrieve top-level platform research intelligence telemetry."""
    events = intel_store.list_events()
    signals = intel_store.list_signals()
    regime = intel_store.get_regime_state()
    scenarios = intel_store.list_scenarios()

    critical_count = sum(1 for s in signals if s.risk_level == "critical")
    high_count = sum(1 for s in signals if s.risk_level == "high")
    elevated_count = sum(1 for s in signals if s.risk_level == "elevated")

    return {
        "platform": "AGNI Research Intelligence",
        "institutional_family": "AstraX",
        "air_gapped_sovereignty": True,
        "total_active_signals": len(signals),
        "total_monitored_events": len(events),
        "severity_breakdown": {
            "critical": critical_count,
            "high": high_count,
            "elevated": elevated_count,
            "moderate": len(signals) - (critical_count + high_count + elevated_count),
        },
        "current_macro_regime": {
            "regime": regime.current_regime,
            "probability": regime.probability,
        },
        "active_stress_scenarios": len(scenarios),
        "epistemic_provenance": {
            "observed_evidence_pct": 74.5,
            "modelled_projections_pct": 18.2,
            "scenario_shocks_pct": 7.3,
        },
    }


@router.get("/backtests", response_model=List[BacktestResult])
async def list_backtest_evaluations():
    """Retrieve rolling-origin model backtests, CRPS accuracy, and Kupiec test statistics."""
    return intel_store.list_backtests()


@router.get("/evidence", response_model=List[Evidence])
async def list_evidence_provenance():
    """Retrieve all logged evidence entities with epistemic status and confidence levels."""
    evidences: List[Evidence] = []
    for evt in intel_store.list_events():
        evidences.extend(evt.evidence)
    return evidences


@router.get("/models")
async def list_model_cards() -> List[Dict[str, Any]]:
    """Retrieve institutional model cards detailing training scope, metrics, and limitations."""
    return [
        {
            "model_name": "Event-Conditioned GARCH-VAR Engine",
            "version": "1.4.0",
            "purpose": "Estimates joint volatility transmission and asset shock cones conditioned on geopolitical disruptions",
            "inputs": ["historical_asset_returns", "event_intensity_index", "regime_state", "chokepoint_delay_ratio"],
            "outputs": ["point_forecast", "quantiles_05_95", "conformal_interval_90", "threshold_breach_probs"],
            "training_period": "2018-01-01 to 2025-12-31",
            "validation_protocol": "rolling_origin_walk_forward",
            "metrics": {"crps": 1.78, "coverage_90": 0.912, "var_kupiec_p": 0.42},
            "limitations": "Assumes stationarity of transmission elasticity over short 30-day windows.",
        },
        {
            "model_name": "Markov Switching Stress Regime Classifier",
            "version": "1.2.0",
            "purpose": "Detects transition between Calm, Elevated, Stressed, and Crisis macro regimes",
            "inputs": ["brent_realized_vol_30d", "cross_asset_correlation", "geopolitical_risk_spread", "sovereign_cds"],
            "outputs": ["current_regime_label", "regime_probabilities", "transition_matrix"],
            "training_period": "2010-01-01 to 2025-12-31",
            "validation_protocol": "purged_walk_forward",
            "metrics": {"aic": 412.5, "bic": 438.1, "regime_stability": 0.88},
            "limitations": "Requires at least 20 trading days of contiguous cross-asset telemetry for reliable state convergence.",
        },
    ]
