"""
AGNI Phase 3 Test Suite: Market & Macroeconomic Intelligence Pipeline
=====================================================================
Validates:
1. Canonical market datasets (FX, commodities, equities, yields, volatility, macro)
2. Polars, DuckDB, and Parquet data store with point-in-time filtering
3. Causal feature engineering (returns, log returns, rolling & realized vol, momentum,
   drawdown, z-scores, regime classification, event-window features, correlations)
4. Strict temporal ordering & zero lookahead leakage proofs (TemporalLeakageAuditor)
5. Baseline models (Naive, Moving Average, ARIMA, VAR, GARCH) with common interface
6. Rolling-origin walk-forward backtesting (MAE, RMSE, CRPS, Pinball Loss, Coverage)
7. FastAPI endpoints for market series, features, correlations, macro, and model comparison
"""

import pytest
import numpy as np
import polars as pl
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from agni.markets.store import MarketDataStore, market_data_store
from agni.markets.features import MarketFeatureEngine
from agni.markets.leakage import TemporalLeakageAuditor
from agni.forecasting.baselines import (
    BaseForecastModel,
    NaiveForecastModel,
    MovingAverageForecastModel,
    ARIMAForecastModel,
    VARForecastModel,
    GARCHVolatilityModel,
)
from agni.backtesting.rolling_origin import RollingOriginBacktester
from backend.app.main import app

client = TestClient(app)


# =====================================================================
# 1. CANONICAL MARKET DATASETS & STORE TESTS
# =====================================================================

def test_market_store_dataset_coverage():
    """Verify that market store covers all required asset classes."""
    assets = market_data_store.list_available_assets()
    assert len(assets) >= 9

    # Verify coverage across FX, Commodities, Equities, Yields, Volatility
    asset_ids = {a["asset_id"] for a in assets}
    expected = {
        "DXY", "EURUSD",  # FX
        "BRENT_CRUDE", "NATURAL_GAS_TTF", "CONTAINER_SCFI", "COPPER", "WHEAT",  # Commodities
        "SPX",  # Equities
        "US10Y",  # Yields
        "VIX",  # Volatility
    }
    for item in expected:
        assert item in asset_ids, f"Expected canonical asset '{item}' missing from store"


def test_market_store_retrieval_and_schema():
    """Verify market series queries return valid Polars DataFrames with required columns."""
    df = market_data_store.get_asset_series("BRENT_CRUDE", limit=100)
    assert isinstance(df, pl.DataFrame)
    assert not df.is_empty()
    assert len(df) == 100

    required_cols = {"timestamp", "asset_id", "price", "volume", "realized_vol_30d", "available_at"}
    assert required_cols.issubset(set(df.columns))

    # Verify temporal ordering (chronological ascending)
    timestamps = df["timestamp"].to_list()
    assert timestamps == sorted(timestamps)


def test_macro_indicators_store():
    """Verify retrieval of macroeconomic indicators."""
    macro_df = market_data_store.get_macro_indicators(limit=100)
    assert isinstance(macro_df, pl.DataFrame)
    assert not macro_df.is_empty()

    macro_indicators = set(macro_df["indicator_code"].unique().to_list())
    assert "CPI_YOY" in macro_indicators
    assert "FED_FUNDS_RATE" in macro_indicators
    assert "GPR_INDEX" in macro_indicators
    assert "SOVEREIGN_CDS" in macro_indicators


def test_point_in_time_filtering():
    """Verify that as_of parameter strictly filters out any observations after the cutoff."""
    cutoff = datetime(2024, 6, 1)
    df = market_data_store.get_asset_series("BRENT_CRUDE", as_of=cutoff, limit=500)
    assert not df.is_empty()

    # All available_at timestamps must be <= cutoff
    avail_times = df["available_at"].to_list()
    for t in avail_times:
        if isinstance(t, str):
            t_dt = datetime.fromisoformat(t.replace("Z", "+00:00")).replace(tzinfo=None)
        else:
            t_dt = t.replace(tzinfo=None) if hasattr(t, "tzinfo") and t.tzinfo else t
        assert t_dt <= cutoff, f"Data leakage detected: {t_dt} > {cutoff}"


# =====================================================================
# 2. FEATURE ENGINEERING TESTS
# =====================================================================

def test_feature_engineering_pipeline():
    """Verify feature calculation generates all 12 required feature groups."""
    df = market_data_store.get_asset_series("BRENT_CRUDE", limit=200)
    features_df = MarketFeatureEngine.compute_full_feature_matrix(df)

    assert isinstance(features_df, pl.DataFrame)
    assert len(features_df) == len(df)

    cols = set(features_df.columns)

    # 1. Returns & Log returns
    assert "returns_1d" in cols
    assert "log_returns_1d" in cols

    # 2. Rolling & Realized Volatility
    assert "volatility_rolling_20d" in cols
    assert "volatility_realized_20d" in cols

    # 3. Momentum
    assert "momentum_5d" in cols
    assert "momentum_20d" in cols
    assert "momentum_60d" in cols

    # 4. Drawdown
    assert "drawdown_20d" in cols

    # 5. Z-Score
    assert "z_score_20d" in cols

    # 6. Volatility Regime
    assert "vol_regime" in cols

    # 7. Event-window features
    assert "days_to_event" in cols
    assert "in_event_window" in cols
    assert "post_event_flag" in cols
    assert "cumulative_event_return" in cols


def test_cross_asset_correlations():
    """Verify cross-asset correlation matrix computation across multiple asset classes."""
    corr_matrix = MarketFeatureEngine.compute_cross_asset_correlation(
        assets=["BRENT_CRUDE", "SPX", "DXY", "VIX"],
        window=60,
    )
    assert isinstance(corr_matrix, dict)
    assert "BRENT_CRUDE" in corr_matrix
    assert "SPX" in corr_matrix

    # Diagonal must be 1.0
    for a in ["BRENT_CRUDE", "SPX", "DXY", "VIX"]:
        assert pytest.approx(corr_matrix[a][a], abs=1e-3) == 1.0


def test_spread_calculation():
    """Verify price and yield spread computations."""
    df_brent = market_data_store.get_asset_series("BRENT_CRUDE", limit=100)
    df_gas = market_data_store.get_asset_series("NATURAL_GAS_TTF", limit=100)

    spread_df = MarketFeatureEngine.compute_spread(df_brent, df_gas, col_a="price", col_b="price")
    assert "spread" in spread_df.columns
    assert "spread_zscore" in spread_df.columns
    assert len(spread_df) > 0


# =====================================================================
# 3. TEMPORAL LEAKAGE AUDIT TESTS
# =====================================================================

def test_temporal_leakage_audit_truncation():
    """
    Mathematical leakage audit:
    Features at time t must be identical whether calculated on series [0:t] or full series [0:N].
    """
    df = market_data_store.get_asset_series("BRENT_CRUDE", limit=150)
    audit_result = TemporalLeakageAuditor.audit_features_against_truncation(df, eval_index=80)

    assert audit_result["is_clean"] is True, f"Leakage detected: {audit_result.get('leaked_columns')}"
    assert audit_result["status"] == "PASSED_ZERO_LEAKAGE"
    assert audit_result["max_delta"] < 1e-5


def test_temporal_leakage_point_in_time():
    """Audit point-in-time filtering guarantees zero future lookahead."""
    audit_result = TemporalLeakageAuditor.audit_point_in_time_filtering(
        market_data_store,
        asset_id="BRENT_CRUDE",
        cutoff_date=datetime(2024, 5, 1),
    )
    assert audit_result["is_clean"] is True
    assert audit_result["status"] == "PASSED_POINT_IN_TIME"


# =====================================================================
# 4. BASELINE FORECAST MODELS TESTS
# =====================================================================

@pytest.fixture
def sample_price_series():
    """Generates a realistic synthetic asset price series for model testing."""
    np.random.seed(42)
    steps = 150
    returns = np.random.normal(0.0005, 0.015, steps)
    prices = 100.0 * np.exp(np.cumsum(returns))
    return prices


def test_naive_model_interface(sample_price_series):
    """Test Naive persistence model satisfies BaseForecastModel interface."""
    model = NaiveForecastModel()
    assert isinstance(model, BaseForecastModel)

    # Fit & Predict
    model.fit(sample_price_series)
    pred = model.predict(horizon_steps=7)
    assert isinstance(pred, float)
    assert pytest.approx(pred, abs=1e-4) == float(sample_price_series[-1])

    # Predict distribution
    dist = model.predict_distribution(horizon_steps=7)
    assert pytest.approx(dist.mean, abs=0.05) == pred
    assert dist.standard_deviation > 0.0
    assert len(dist.quantiles) >= 3
    assert len(dist.conformal_interval_90) == 2

    # In-sample evaluation
    metrics = model.evaluate(sample_price_series[-20:])
    assert "mae" in metrics and "rmse" in metrics


def test_moving_average_model_interface(sample_price_series):
    """Test Moving Average model."""
    model = MovingAverageForecastModel(window=15)
    model.fit(sample_price_series)
    pred = model.predict(horizon_steps=5)
    assert isinstance(pred, float)

    expected_ma = float(np.mean(sample_price_series[-15:]))
    assert pytest.approx(pred, abs=1e-4) == expected_ma

    dist = model.predict_distribution(horizon_steps=5)
    assert pytest.approx(dist.mean, abs=0.05) == pred
    assert dist.standard_deviation > 0.0


def test_arima_model_interface(sample_price_series):
    """Test ARIMA model via statsmodels."""
    model = ARIMAForecastModel(order=(1, 1, 0))
    model.fit(sample_price_series)
    pred = model.predict(horizon_steps=7)
    assert isinstance(pred, float)
    assert not np.isnan(pred)

    dist = model.predict_distribution(horizon_steps=7)
    assert pytest.approx(dist.mean, abs=0.05) == pred
    assert dist.standard_deviation > 0.0
    assert dist.conformal_interval_90[0] < dist.mean < dist.conformal_interval_90[1]


def test_var_model_interface(sample_price_series):
    """Test VAR model via statsmodels."""
    model = VARForecastModel(max_lags=1)
    model.fit(sample_price_series)
    pred = model.predict(horizon_steps=5)
    assert isinstance(pred, float)
    assert not np.isnan(pred)

    dist = model.predict_distribution(horizon_steps=5)
    assert pytest.approx(dist.mean, abs=0.05) == pred


def test_garch_model_interface(sample_price_series):
    """Test GARCH volatility model via arch package."""
    model = GARCHVolatilityModel(p=1, q=1)
    model.fit(sample_price_series)
    pred = model.predict(horizon_steps=7)
    assert isinstance(pred, float)

    dist = model.predict_distribution(horizon_steps=7)
    assert dist.standard_deviation > 0.0


# =====================================================================
# 5. ROLLING-ORIGIN BACKTESTING TESTS
# =====================================================================

def test_rolling_origin_backtester_metrics(sample_price_series):
    """Verify rolling-origin walk-forward backtest produces all required institutional metrics."""
    model = NaiveForecastModel()
    result = RollingOriginBacktester.run_backtest(
        model=model,
        series=sample_price_series,
        horizon=5,
        initial_train_window=60,
        step_size=5,
    )

    # Check metrics
    assert "mae" in result
    assert "rmse" in result
    assert "crps" in result
    assert "pinball_loss_90" in result
    assert "pinball_loss_50" in result
    assert "nominal_coverage_90" in result
    assert "empirical_coverage_90" in result

    assert result["mae"] > 0.0
    assert result["rmse"] >= result["mae"]
    assert result["crps"] >= 0.0
    assert 0.0 <= result["empirical_coverage_90"] <= 1.0


def test_model_comparison_engine(sample_price_series):
    """Verify multi-model comparison across baselines."""
    models = [
        NaiveForecastModel(),
        MovingAverageForecastModel(window=10),
        ARIMAForecastModel(order=(1, 1, 0)),
    ]

    comparison = RollingOriginBacktester.compare_models(
        models=models,
        series=sample_price_series,
        horizon=5,
        initial_train_window=60,
        step_size=10,
    )

    assert len(comparison) == 3
    # Sorted by MAE ascending
    assert comparison[0]["mae"] <= comparison[1]["mae"] <= comparison[2]["mae"]


# =====================================================================
# 6. FASTAPI API ENDPOINTS TESTS
# =====================================================================

def test_api_markets_assets():
    """Verify GET /api/markets/assets."""
    res = client.get("/api/markets/assets")
    assert res.status_code == 200
    data = res.json()
    assert "assets" in data
    assert data["count"] >= 9


def test_api_markets_series():
    """Verify GET /api/markets/series/{asset_id}."""
    res = client.get("/api/markets/series/BRENT_CRUDE?limit=50")
    assert res.status_code == 200
    data = res.json()
    assert data["asset_id"] == "BRENT_CRUDE"
    assert len(data["data"]) == 50


def test_api_markets_features():
    """Verify GET /api/markets/features/{asset_id}."""
    res = client.get("/api/markets/features/BRENT_CRUDE?limit=50")
    assert res.status_code == 200
    data = res.json()
    assert "features" in data
    assert "volatility_rolling_20d" in data["features"]


def test_api_markets_correlations():
    """Verify GET /api/markets/correlations."""
    res = client.get("/api/markets/correlations?window=30")
    assert res.status_code == 200
    data = res.json()
    assert "correlation_matrix" in data


def test_api_markets_macro():
    """Verify GET /api/markets/macro."""
    res = client.get("/api/markets/macro?limit=30")
    assert res.status_code == 200
    data = res.json()
    assert "indicators" in data


def test_api_models_comparison():
    """Verify GET /api/models/comparison."""
    res = client.get("/api/models/comparison?asset_id=BRENT_CRUDE&horizon=5&history_limit=80")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) >= 5
    assert "evaluation_protocol" in data
    assert data["evaluation_protocol"] == "rolling_origin_walk_forward"


def test_api_models_forecast():
    """Verify POST /api/models/forecast."""
    res = client.post("/api/models/forecast?asset_id=BRENT_CRUDE&model_name=ARIMA&horizon=7")
    assert res.status_code == 200
    data = res.json()
    assert data["asset_id"] == "BRENT_CRUDE"
    assert "point_forecast" in data
    assert "distribution" in data
    assert "conformal_interval_90" in data["distribution"]
