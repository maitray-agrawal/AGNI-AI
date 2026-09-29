"""
Phase 1 Tests: Canonical AGNI Data Schemas
==========================================
Validates that all 15 canonical research models instantiate correctly
with strict Pydantic v2 type safety and coordinate boundaries.
"""

import pytest
from datetime import datetime, timezone

from agni.data.schemas import (
    Event,
    MarketObservation,
    MacroObservation,
    Country,
    Commodity,
    FinancialAsset,
    TradeRoute,
    Chokepoint,
    RiskSignal,
    TransmissionLink,
    Scenario,
    Forecast,
    RegimeState,
    BacktestResult,
    Evidence,
    RiskSignalComponent,
    ScenarioShock,
    ForecastDistribution,
    QuantileForecast,
)


def test_canonical_event_model():
    evt = Event(
        event_id="evt-unit-001",
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type="maritime_disruption",
        title="Strait of Malacca AIS Signal Anomaly",
        description="Multiple commercial vessels reporting GPS spoofing and AIS transponder degradation.",
        country="Singapore",
        region="Southeast Asia",
        latitude=1.3521,
        longitude=103.8198,
        severity="elevated",
        confidence=0.92,
        affected_assets=["BRENT", "SPX"],
        affected_commodities=["CONTAINER_SCFI"],
        affected_routes=["asia-europe-suez"],
        transmission_channels=["AIS Jamming", "Convoy Delays", "Freight Spot Escalation"],
        is_demo_data=True,
    )
    assert evt.event_id == "evt-unit-001"
    assert evt.severity == "elevated"
    assert -90.0 <= evt.latitude <= 90.0
    assert -180.0 <= evt.longitude <= 180.0


def test_canonical_geospatial_models():
    country = Country(
        country_code="IRN",
        name="Iran",
        region="Middle East",
        latitude=32.4279,
        longitude=53.6880,
        gdp_usd_billions=388.8,
        geopolitical_risk_index=148.5,
    )
    assert country.country_code == "IRN"

    cp = Chokepoint(
        chokepoint_id="strait-of-hormuz",
        name="Strait of Hormuz",
        latitude=26.5667,
        longitude=56.2500,
        global_trade_share_pct=21.0,
        critical_commodities=["BRENT_CRUDE"],
        current_status="high",
    )
    assert cp.global_trade_share_pct == 21.0

    route = TradeRoute(
        route_id="asia-europe",
        name="Asia to Europe",
        origin_region="East Asia",
        destination_region="Europe",
        traversed_chokepoints=["strait-of-malacca", "bab-el-mandeb"],
        average_transit_days=26.0,
        current_delay_days=4.5,
    )
    assert route.current_delay_days == 4.5


def test_canonical_economic_and_market_models():
    comm = Commodity(
        commodity_id="BRENT_CRUDE",
        name="Brent Crude Oil",
        category="Energy",
        benchmark_unit="USD/bbl",
        primary_chokepoint_dependencies=["strait-of-hormuz"],
    )
    assert comm.commodity_id == "BRENT_CRUDE"

    asset = FinancialAsset(
        asset_id="BRENT",
        name="Brent Crude",
        asset_class="commodity",
        currency="USD",
        current_value=82.50,
        daily_change_pct=1.8,
    )
    assert asset.current_value == 82.50

    mkt_obs = MarketObservation(
        observation_id="obs-001",
        asset_id="BRENT",
        timestamp="2026-09-29T12:00:00Z",
        available_at="2026-09-29T12:05:00Z",
        price=82.50,
        volume=250000.0,
    )
    assert mkt_obs.price == 82.50

    macro_obs = MacroObservation(
        observation_id="macro-001",
        country_code="GLOBAL",
        indicator_code="GPR_INDEX",
        timestamp="2026-09-01T00:00:00Z",
        available_at="2026-09-02T12:00:00Z",
        value=142.8,
        unit="points",
        frequency="monthly",
        source="Federal Reserve Board Research",
    )
    assert macro_obs.value == 142.8


def test_canonical_risk_and_transmission_models():
    comp = RiskSignalComponent(
        event_intensity=85.0,
        market_sensitivity=70.0,
        country_exposure=60.0,
        commodity_exposure=75.0,
        route_exposure=65.0,
        historical_response=75.0,
        regime_multiplier=1.2,
        confidence=0.90,
    )
    link = TransmissionLink(
        from_node="Chokepoint Disruption",
        to_node="Bunker Surcharge",
        link_type="supply_disruption",
        elasticity_or_beta=0.85,
        explanation="Direct rerouting freight escalation",
    )
    sig = RiskSignal(
        signal_id="sig-001",
        event_id="evt-001",
        timestamp="2026-09-29T12:00:00Z",
        risk_score=78.5,
        risk_level="high",
        confidence=0.85,
        components=comp,
        drivers=["Drone strike", "Tanker diversion"],
        transmission_path=[link],
    )
    assert sig.risk_score == 78.5
    assert sig.components.event_intensity == 85.0
    assert len(sig.transmission_path) == 1


def test_canonical_scenario_forecast_and_regime_models():
    shock = ScenarioShock(
        target="BRENT",
        shock_pct=15.0,
        confidence_interval=(10.0, 20.0),
    )
    scenario = Scenario(
        scenario_id="scen-001",
        name="Hormuz Closure Escalation",
        scenario_type="SEVERE",
        description="Simulated total maritime blockade of Hormuz.",
        shocks=[shock],
        macro_transmission_summary="Immediate physical crude deficit transmitting to energy inflation.",
        var_95_portfolio_impact=-18.5,
        expected_shortfall_95=-26.8,
        affected_regions=["Middle East", "Europe"],
        affected_assets=["BRENT", "SPX"],
    )
    assert scenario.var_95_portfolio_impact == -18.5

    dist = ForecastDistribution(
        mean=85.0,
        standard_deviation=3.5,
        quantiles=[
            QuantileForecast(quantile=0.05, value=79.5),
            QuantileForecast(quantile=0.50, value=85.0),
            QuantileForecast(quantile=0.95, value=91.2),
        ],
        conformal_interval_90=(78.2, 92.5),
    )
    fc = Forecast(
        forecast_id="fc-001",
        target_asset="BRENT",
        horizon="7D",
        point_forecast=85.0,
        distribution=dist,
        model_name="Event-Conditioned Forecaster",
        conformal_calibrated=True,
    )
    assert fc.distribution.conformal_interval_90 == (78.2, 92.5)

    regime = RegimeState(
        regime_id="reg-001",
        current_regime="ELEVATED",
        probability=0.74,
        regime_probabilities={"CALM": 0.12, "ELEVATED": 0.74, "STRESSED": 0.11, "CRISIS": 0.03},
    )
    assert regime.current_regime == "ELEVATED"

    bt = BacktestResult(
        backtest_id="bt-001",
        model_name="Event-Conditioned Forecaster",
        sample_size_days=180,
        mae=1.24,
        rmse=1.65,
        mase=0.88,
        crps=0.92,
        pinball_loss_90=0.22,
        actual_coverage_90=0.912,
        var_kupiec_p_value=0.54,
        var_christoffersen_p_value=0.48,
    )
    assert bt.mae == 1.24

    ev = Evidence(
        evidence_id="ev-001",
        evidence_state="OBSERVED",
        source_name="UKMTO",
        headline="Direct kinetic coordinate confirmation",
        confidence=0.95,
    )
    assert ev.evidence_state == "OBSERVED"
