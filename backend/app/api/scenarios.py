"""
AGNI Conditional Scenario Engine API Router
===========================================
Supports conditional stress testing, scenario execution, and portfolio VaR / ES simulation.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid
from datetime import datetime
from backend.app.schemas.canonical import Scenario, ScenarioShock
from backend.app.repositories.intel_store import intel_store

from agni.scenarios.stress_engine import StressScenarioGenerator

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.get("", response_model=List[Scenario])
async def list_scenarios():
    """Retrieve all defined stress scenarios (Base, Adverse, Severe, Custom)."""
    return intel_store.list_scenarios()


@router.get("/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    """Retrieve an individual stress scenario definition and historical shock parameters."""
    scen = intel_store.get_scenario(scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return scen


@router.post("", response_model=Scenario, status_code=201)
async def create_scenario(scenario: Scenario):
    """Define a custom user-parameterized stress scenario."""
    if not scenario.scenario_id:
        scenario.scenario_id = f"scen-custom-{uuid.uuid4().hex[:6]}"
    if not scenario.created_at:
        scenario.created_at = datetime.utcnow().isoformat()
    return intel_store.create_scenario(scenario)


@router.post("/{scenario_id}/run")
async def run_scenario(scenario_id: str) -> Dict[str, Any]:
    """Execute conditional shock propagation on a scenario and compute VaR / Expected Shortfall."""
    scen = intel_store.get_scenario(scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")

    regime = intel_store.get_regime_state()

    var_95, es_95, detailed_shocks = StressScenarioGenerator.simulate_joint_shocks(
        scenario_type=scen.scenario_type,
        shocks=scen.shocks,
        regime=regime.current_regime,
    )

    return {
        "scenario_id": scen.scenario_id,
        "name": scen.name,
        "status": "completed",
        "current_regime": regime.current_regime,
        "var_95_portfolio_impact": var_95,
        "expected_shortfall_95": es_95,
        "asset_shock_distribution": detailed_shocks,
        "affected_regions": scen.affected_regions,
        "affected_assets": scen.affected_assets,
        "computed_at": datetime.utcnow().isoformat(),
    }
