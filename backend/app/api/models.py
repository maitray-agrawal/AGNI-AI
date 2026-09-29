"""
AGNI Forecasting Models & Statistical Baseline Comparison Router
================================================================
Provides model comparison and evaluation across:
- Naive
- Moving Average
- ARIMA (statsmodels)
- VAR (statsmodels)
- GARCH (arch)

Metrics evaluated:
MAE, RMSE, CRPS, Pinball Loss, Empirical Coverage.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

from backend.app.config import settings
from backend.app.models.registry import model_registry
from agni.markets.store import market_data_store
from agni.forecasting.baselines import (
    NaiveForecastModel,
    MovingAverageForecastModel,
    ARIMAForecastModel,
    VARForecastModel,
    GARCHVolatilityModel,
    BaseForecastModel,
)
from agni.backtesting.rolling_origin import RollingOriginBacktester

router = APIRouter(tags=["Models"])


@router.get("/models")
async def get_models():
    """Retrieve available local neural/language models."""
    reg_info = await model_registry.get_registry_info()
    return {
        "provider": settings.MODEL_PROVIDER,
        "endpoint": settings.OLLAMA_BASE_URL,
        "models": reg_info,
        "statistical_baselines": ["Naive", "Moving Average", "ARIMA", "VAR", "GARCH"],
    }


@router.get("/models/comparison")
async def compare_baseline_models(
    asset_id: str = Query("BRENT_CRUDE", description="Target asset ticker"),
    horizon: int = Query(7, ge=1, le=60, description="Forecast horizon in steps (days)"),
    history_limit: int = Query(120, ge=60, le=400, description="Historical sample size"),
):
    """
    Model Comparison Endpoint:
    Compares baseline models (Naive, Moving Average, ARIMA, VAR, GARCH) using
    strict rolling-origin walk-forward validation with zero lookahead leakage.

    Metrics returned for each model:
    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Squared Error)
    - CRPS (Continuous Ranked Probability Score)
    - Pinball Loss (tau=0.90, tau=0.50)
    - Empirical Coverage (at nominal 90% confidence)
    """
    df = market_data_store.get_asset_series(asset_id, limit=history_limit)
    if df.is_empty():
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found in store")

    series = df["price"].to_numpy()

    # Instantiate baseline models
    models: List[BaseForecastModel] = [
        NaiveForecastModel(),
        MovingAverageForecastModel(window=20),
        ARIMAForecastModel(order=(1, 1, 0)),
        VARForecastModel(max_lags=1),
        GARCHVolatilityModel(p=1, q=1),
    ]

    try:
        comparison_results = RollingOriginBacktester.compare_models(
            models=models,
            series=series,
            horizon=horizon,
            initial_train_window=min(50, len(series) // 2),
            step_size=3,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtesting error: {str(e)}")

    best_model = comparison_results[0]["model_name"] if comparison_results else "None"

    return {
        "asset_id": asset_id.upper(),
        "horizon_steps": horizon,
        "sample_size_days": len(series),
        "evaluation_protocol": "rolling_origin_walk_forward",
        "best_model_by_mae": best_model,
        "evaluated_at": datetime.utcnow().isoformat(),
        "models": comparison_results,
    }


@router.post("/models/forecast")
async def run_single_forecast(
    asset_id: str = Query("BRENT_CRUDE"),
    model_name: str = Query("ARIMA", description="Naive, Moving Average, ARIMA, VAR, or GARCH"),
    horizon: int = Query(7, ge=1, le=60),
):
    """Generates on-demand point forecast and predictive distribution for an asset."""
    df = market_data_store.get_asset_series(asset_id, limit=120)
    if df.is_empty():
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")

    series = df["price"].to_numpy()

    m_lower = model_name.lower()
    if "naive" in m_lower:
        model: BaseForecastModel = NaiveForecastModel()
    elif "moving" in m_lower or "ma" in m_lower:
        model = MovingAverageForecastModel(window=20)
    elif "var" in m_lower:
        model = VARForecastModel(max_lags=1)
    elif "garch" in m_lower:
        model = GARCHVolatilityModel(p=1, q=1)
    else:
        model = ARIMAForecastModel(order=(1, 1, 0))

    model.fit(series)
    point_forecast = model.predict(horizon_steps=horizon)
    dist = model.predict_distribution(horizon_steps=horizon)

    return {
        "asset_id": asset_id.upper(),
        "model": model.name,
        "horizon_steps": horizon,
        "current_price": float(series[-1]),
        "point_forecast": round(float(point_forecast), 2),
        "distribution": dist.model_dump(),
        "generated_at": datetime.utcnow().isoformat(),
    }
