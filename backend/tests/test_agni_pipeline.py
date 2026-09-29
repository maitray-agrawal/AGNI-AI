"""
Comprehensive Unit Tests for AGNI Core Research Pipeline (Phases 2 - 8)
========================================================================
Validates all research intelligence subsystems:
- Event Ingestion & Manual Workflow
- Time Series Engine (Polars & DuckDB)
- Classical Baselines (Naive, ARIMA, GARCH)
- Markov Switching Regime Detection
- Dynamic Risk & Trade Graph Topology
- Event-Conditioned Probabilistic Forecaster
- Conformal Coverage Calibration
- Conditional Stress Testing (VaR / ES)
- Backtest Validation & Kupiec Testing
"""

import pytest
import numpy as np
from agni.data.ingestion.event_ingestion import event_ingestion_pipeline
from agni.markets.time_series import market_store
from agni.forecasting.baselines import NaiveForecastModel, ARIMAForecastModel, GARCHVolatilityModel
from agni.regimes.detector import regime_detector
from agni.graph.topology import risk_graph
from agni.forecasting.event_conditioned import event_conditioned_forecaster
from agni.calibration.conformal import conformal_calibrator
from agni.scenarios.stress_engine import stress_generator
from agni.backtesting.evaluator import backtest_evaluator
from backend.app.schemas.canonical import ScenarioShock
from backend.app.repositories.intel_store import intel_store


def test_event_ingestion_manual_workflow():
    event, signal = event_ingestion_pipeline.ingest_manual_event(
        title="Red Sea Bab el-Mandeb Interdiction Escalation",
        description="Naval escort telemetry confirms three missile launch detections.",
        country="Yemen",
        region="Middle East",
        latitude=12.6,
        longitude=43.3,
        severity="critical",
        confidence=0.94,
        affected_assets=["BRENT", "US10Y"],
        affected_commodities=["BRENT_CRUDE"],
        affected_routes=["Asia-Europe Lane"],
        transmission_channels=["Drone Probes", "Cape Diversions", "Bunker Fuel Surcharge"],
        analyst_notes_text="Force majeure declarations expected by major container lines.",
        evidence_text="UKMTO notice logged at 04:12 UTC.",
    )
    assert event.event_id.startswith("evt-analyst-")
    assert signal.signal_id == f"sig-{event.event_id}"
    assert signal.risk_score >= 70.0
    assert signal.risk_level == "critical"
    assert len(signal.transmission_path) == 2


def test_market_time_series_duckdb_polars():
    df = market_store.get_asset_series("BRENT", limit=50)
    assert len(df) == 50
    assert "price" in df.columns
    assert "realized_vol_30d" in df.columns
    # Verify values are positive floats
    assert float(df["price"][0]) > 0.0


def test_classical_forecasting_baselines():
    np.random.seed(42)
    sample_series = 80.0 + np.cumsum(np.random.normal(0, 1.2, 100))

    # 1. Naive
    naive = NaiveForecastModel().fit(sample_series)
    assert naive.predict(30) == sample_series[-1]
    dist_naive = naive.predict_distribution(30)
    assert len(dist_naive.quantiles) == 5

    # 2. ARIMA
    arima = ARIMAForecastModel().fit(sample_series)
    pred_arima = arima.predict(30)
    assert pred_arima > 0.0

    # 3. GARCH
    garch = GARCHVolatilityModel().fit(sample_series)
    dist_garch = garch.predict_distribution(30)
    assert dist_garch.standard_deviation > 0.0


def test_markov_regime_detection():
    np.random.seed(42)
    # Generate high volatility regime series
    vol_series = np.concatenate([
        np.random.normal(15.0, 1.5, 40),
        np.random.normal(38.0, 3.5, 40),
    ])
    state = regime_detector.fit_from_volatility(vol_series)
    assert state.current_regime in ["ELEVATED", "STRESSED", "CRISIS"]
    assert state.probability > 0.0
    assert "CALM" in state.regime_probabilities


def test_dynamic_risk_graph_topology():
    countries = intel_store.list_countries()
    chokepoints = intel_store.list_chokepoints()
    commodities = intel_store.list_commodities()
    assets = intel_store.list_assets()

    risk_graph.build_from_entities(countries, chokepoints, commodities, assets)

    # Trace shock path from Bab el-Mandeb to VIX
    path = risk_graph.trace_shock_path("bab-el-mandeb", "VIX")
    assert len(path) >= 2
    assert "Bab el-Mandeb" in path[0]

    # Centrality
    centrality = risk_graph.compute_chokepoint_centrality()
    assert len(centrality) > 0


def test_event_conditioned_probabilistic_forecaster():
    forecast = event_conditioned_forecaster.forecast_asset(
        target_asset="BRENT",
        horizon="30D",
        event_shock_magnitude=14.5,
        regime="STRESSED",
    )
    assert forecast.target_asset == "BRENT"
    assert forecast.horizon == "30D"
    assert forecast.distribution.mean > 80.0
    assert forecast.distribution.quantiles[0].quantile == 0.05
    assert forecast.distribution.quantiles[-1].quantile == 0.95
    assert forecast.distribution.quantiles[0].value < forecast.distribution.quantiles[-1].value


def test_conformal_calibrator():
    np.random.seed(42)
    actuals = np.array([80.0, 82.0, 85.0, 79.0, 83.0, 88.0, 84.0, 86.0])
    preds = np.array([81.0, 81.5, 84.0, 80.0, 82.0, 86.0, 83.5, 85.0])

    conformal_calibrator.calibrate(actuals, preds)
    assert conformal_calibrator.is_calibrated is True
    interval = conformal_calibrator.predict_interval(85.0)
    assert interval[0] < 85.0 < interval[1]

    cov_eval = conformal_calibrator.evaluate_coverage(actuals, preds)
    assert cov_eval["nominal_coverage"] == 0.90
    assert cov_eval["actual_coverage"] >= 0.75


def test_stress_scenario_engine():
    shocks = [
        ScenarioShock(target="BRENT", shock_pct=25.0, confidence_interval=(18.0, 32.0)),
        ScenarioShock(target="SPX", shock_pct=-8.0, confidence_interval=(-12.0, -5.0)),
        ScenarioShock(target="VIX", shock_pct=45.0, confidence_interval=(30.0, 60.0)),
    ]
    scen = stress_generator.create_custom_scenario(
        name="Gulf Strait Flare-up",
        description="Analyst custom stress test.",
        shocks=shocks,
        regime="STRESSED",
    )
    assert scen.var_95_portfolio_impact < 0.0
    assert scen.expected_shortfall_95 <= scen.var_95_portfolio_impact
    assert len(scen.shocks) == 3


def test_backtest_evaluator_and_kupiec():
    np.random.seed(42)
    n = 150
    actuals = np.random.normal(80.0, 3.0, n)
    preds = actuals + np.random.normal(0, 1.0, n)
    sigmas = np.full(n, 3.0)

    res = backtest_evaluator.run_rolling_origin_validation(
        model_name="Event-Conditioned Forecaster Test",
        actuals=actuals,
        predictions=preds,
        predicted_sigmas=sigmas,
    )
    assert res.sample_size_days == n
    assert res.crps > 0.0
    assert res.var_kupiec_p_value > 0.0


def test_mlops_training_pipeline(tmp_path):
    from agni.training.train_forecaster import train_event_conditioned_model
    res = train_event_conditioned_model(asset_id="BRENT", alpha=0.10, output_dir=str(tmp_path))
    assert res["model_name"] == "AGNI-EC-Forecaster-BRENT"
    assert res["target_coverage"] == 0.90
    assert res["empirical_coverage"] > 0.70
    assert res["status"] == "ready_for_inference"


def test_mlops_evaluation_pipeline(tmp_path):
    from agni.training.evaluate_forecaster import evaluate_model_performance
    res = evaluate_model_performance(asset_id="BRENT", output_dir=str(tmp_path))
    assert "point_metrics" in res
    assert "distribution_metrics" in res
    assert "kupiec_pof_test" in res
    assert res["point_metrics"]["MAE"] > 0.0
    assert res["distribution_metrics"]["CRPS"] > 0.0


def test_mlops_backtest_comparison(tmp_path):
    from agni.training.backtest import run_full_backtest_pipeline
    res = run_full_backtest_pipeline(horizons=[1, 7], output_dir=str(tmp_path))
    assert len(res["results"]) == 6
    models = {r["model"] for r in res["results"]}
    assert "AGNI Event-Conditioned" in models
    assert "ARIMA(1,1,0)" in models
    assert "Naive Drift" in models

