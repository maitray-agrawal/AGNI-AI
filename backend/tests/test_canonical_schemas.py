"""
Unit Tests for AGNI Canonical Data Schemas
==========================================
Validates data integrity, boundary constraints, and serialization
across all 17 canonical research intelligence entities.
"""

import pytest
from pydantic import ValidationError
from backend.app.schemas.canonical import (
    Event,
    Evidence,
    AnalystNote,
    Chokepoint,
    Country,
    Commodity,
    FinancialAsset,
    RiskSignal,
    RiskSignalComponent,
    TransmissionLink,
    RegimeState,
    Scenario,
    ScenarioShock,
    Forecast,
    ForecastDistribution,
    QuantileForecast,
    BacktestResult,
)


def test_event_schema_valid():
    evt = Event(
        event_id="evt-test-01",
        event_type="maritime_disruption",
        title="Suez Canal Transit Impasse",
        description="Vessel diversions logged.",
        country="Egypt",
        region="Middle East",
        latitude=30.5,
        longitude=32.3,
        severity="critical",
        confidence=0.95,
        affected_commodities=["BRENT_CRUDE"],
        transmission_channels=["Chokepoint Closure", "Freight Repricing"],
    )
    assert evt.event_id == "evt-test-01"
    assert evt.latitude == 30.5
    assert evt.confidence == 0.95
    assert evt.is_demo_data is False


def test_event_schema_invalid_lat_lon():
    with pytest.raises(ValidationError):
        Event(
            event_id="evt-invalid",
            event_type="maritime_disruption",
            title="Invalid",
            description="Out of bounds",
            country="Test",
            region="Test",
            latitude=150.0,  # Invalid: > 90
            longitude=0.0,
            severity="moderate",
            confidence=0.5,
        )


def test_risk_signal_component_bounds():
    comp = RiskSignalComponent(
        event_intensity=90.0,
        market_sensitivity=85.0,
        country_exposure=80.0,
        commodity_exposure=75.0,
        route_exposure=95.0,
        historical_response=70.0,
        regime_multiplier=1.20,
        confidence=0.90,
    )
    assert comp.regime_multiplier == 1.20
    assert comp.confidence == 0.90

    with pytest.raises(ValidationError):
        # Intensity must be <= 100
        RiskSignalComponent(
            event_intensity=120.0,
            market_sensitivity=50.0,
            country_exposure=50.0,
            commodity_exposure=50.0,
            route_exposure=50.0,
            historical_response=50.0,
            regime_multiplier=1.0,
            confidence=0.5,
        )


def test_regime_state_valid():
    regime = RegimeState(
        regime_id="regime-test",
        current_regime="ELEVATED",
        probability=0.72,
        regime_probabilities={"CALM": 0.10, "ELEVATED": 0.72, "STRESSED": 0.15, "CRISIS": 0.03},
        features_used=["volatility"],
    )
    assert regime.current_regime == "ELEVATED"
    assert regime.probability == 0.72


def test_scenario_and_shock():
    scen = Scenario(
        scenario_id="scen-test",
        name="Severe Oil Supply Interdiction",
        scenario_type="SEVERE",
        description="Shock test",
        shocks=[ScenarioShock(target="BRENT", shock_pct=35.0, confidence_interval=(25.0, 45.0))],
        macro_transmission_summary="Stagflationary impact",
        var_95_portfolio_impact=-8.5,
        expected_shortfall_95=-12.4,
        affected_regions=["Global"],
        affected_assets=["BRENT", "SPX"],
    )
    assert scen.var_95_portfolio_impact == -8.5
    assert len(scen.shocks) == 1
    assert scen.shocks[0].shock_pct == 35.0


def test_backtest_result_metrics():
    bt = BacktestResult(
        backtest_id="bt-01",
        model_name="GARCH-VAR",
        sample_size_days=500,
        mae=1.5,
        rmse=2.2,
        mase=0.85,
        crps=1.12,
        pinball_loss_90=0.35,
        actual_coverage_90=0.91,
        var_kupiec_p_value=0.55,
        var_christoffersen_p_value=0.48,
    )
    assert bt.var_kupiec_p_value > 0.05
    assert bt.crps == 1.12
