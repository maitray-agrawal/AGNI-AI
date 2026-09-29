"""
Unit & API Tests for AGNI Explainable Risk Engine & Research Endpoints
=====================================================================
Validates explainable risk calculations, manual event CRUD, scenario runs,
and FastAPI endpoint responses.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.schemas.canonical import Event
from backend.app.services.risk_engine import risk_signal_engine


def test_deterministic_risk_scoring():
    evt = Event(
        event_id="evt-eval-01",
        event_type="maritime_disruption",
        title="Taiwan Strait Naval Maneuver",
        description="Naval escorts deployed.",
        country="Taiwan / China",
        region="East Asia",
        latitude=24.0,
        longitude=119.5,
        severity="critical",
        confidence=0.92,
        affected_assets=["SPX", "VIX", "DXY"],
        affected_commodities=["CONTAINER_SCFI", "COPPER"],
        affected_routes=["Trans-Pacific Lane"],
        transmission_channels=["Naval Maneuvers", "Fab Logistics Delay", "Equity Multiple Repricing"],
    )

    sig = risk_signal_engine.evaluate_event(evt, current_regime="ELEVATED")

    assert sig.signal_id == "sig-evt-eval-01"
    assert sig.risk_score >= 80.0
    assert sig.risk_level == "critical"
    assert sig.components.regime_multiplier == 1.20
    assert sig.components.event_intensity == 92.0
    assert len(sig.drivers) > 0
    assert len(sig.transmission_path) == 2
    assert sig.transmission_path[0].from_node == "Naval Maneuvers"


@pytest.mark.asyncio
async def test_api_signals_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/signals")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 4
        # Verify first signal has components and drivers
        assert "risk_score" in data[0]
        assert "components" in data[0]
        assert "drivers" in data[0]


@pytest.mark.asyncio
async def test_api_manual_event_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create manual event
        new_event = {
            "event_id": "evt-manual-test-99",
            "event_type": "trade_restriction",
            "title": "Rare Earth Export Quota Reduction",
            "description": "Ministry announced tighter export licenses for heavy rare earths.",
            "country": "China",
            "region": "East Asia",
            "latitude": 39.9,
            "longitude": 116.4,
            "severity": "high",
            "confidence": 0.88,
            "source": "Ministry of Commerce Bulletin",
            "affected_assets": ["SPX"],
            "affected_commodities": ["COPPER"],
            "affected_routes": ["East Asia Freight"],
            "transmission_channels": ["Export Quota", "Refining Scarcity", "EV Battery Cost Shift"],
            "is_demo_data": False,
        }
        create_res = await ac.post("/api/events", json=new_event)
        assert create_res.status_code == 201
        created = create_res.json()
        assert created["event_id"] == "evt-manual-test-99"

        # 2. Check signal was generated automatically
        sig_res = await ac.get("/api/signals/sig-evt-manual-test-99")
        assert sig_res.status_code == 200
        sig_data = sig_res.json()
        assert sig_data["risk_level"] in ["high", "critical", "elevated"]

        # 3. Delete manual event
        del_res = await ac.delete("/api/events/evt-manual-test-99")
        assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_api_scenarios_and_run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/scenarios")
        assert res.status_code == 200
        scenarios = res.json()
        assert len(scenarios) >= 3

        # Run first scenario
        scen_id = scenarios[0]["scenario_id"]
        run_res = await ac.post(f"/api/scenarios/{scen_id}/run")
        assert run_res.status_code == 200
        run_data = run_res.json()
        assert run_data["status"] == "completed"
        assert "var_95_portfolio_impact" in run_data
        assert "asset_shock_distribution" in run_data


@pytest.mark.asyncio
async def test_api_graph_and_research_summary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Dynamic graph topology
        graph_res = await ac.get("/api/graph")
        assert graph_res.status_code == 200
        graph_data = graph_res.json()
        assert graph_data["node_count"] > 10
        assert graph_data["edge_count"] > 5

        # Research summary
        sum_res = await ac.get("/api/research/summary")
        assert sum_res.status_code == 200
        sum_data = sum_res.json()
        assert sum_data["air_gapped_sovereignty"] is True
        assert sum_data["total_active_signals"] >= 4
