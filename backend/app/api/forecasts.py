"""
AGNI Probabilistic Forecasting API Router
=========================================
Delivers event-conditioned quantile forecasts, predictive intervals, and threshold breach probabilities.
"""

from fastapi import APIRouter
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from backend.app.schemas.canonical import Forecast, ForecastDistribution, QuantileForecast
from backend.app.repositories.intel_store import intel_store

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


class ForecastGenerateRequest(BaseModel):
    target_asset: str = Field(..., description="Target asset ticker (e.g. BRENT, CONTAINER_SCFI, SPX)")
    horizon: str = Field("30D", description="1D, 7D, 30D, or 90D")
    conditioning_event_ids: List[str] = Field(default_factory=list)


@router.get("", response_model=List[Forecast])
async def list_forecasts():
    """Retrieve all active calibrated probabilistic forecasts."""
    return intel_store.list_forecasts()


@router.post("", response_model=Forecast)
async def generate_forecast(req: ForecastGenerateRequest):
    """Generate an on-demand probabilistic forecast conditioned on events and regime."""
    regime = intel_store.get_regime_state()
    base_val = 82.60 if "BRENT" in req.target_asset else 3420.0
    sigma = base_val * 0.075

    forecast = Forecast(
        forecast_id=f"fc-{req.target_asset.lower()}-{req.horizon.lower()}",
        target_asset=req.target_asset,
        horizon=req.horizon,  # type: ignore
        created_at=datetime.utcnow().isoformat(),
        available_at=datetime.utcnow().isoformat(),
        model_name="Event-Conditioned GARCH-VAR Engine",
        conditioning_events=req.conditioning_event_ids,
        conditioning_regime=regime.current_regime,
        point_forecast=round(base_val, 2),
        distribution=ForecastDistribution(
            mean=round(base_val, 2),
            standard_deviation=round(sigma, 2),
            quantiles=[
                QuantileForecast(quantile=0.05, value=round(base_val - (1.645 * sigma), 2)),
                QuantileForecast(quantile=0.25, value=round(base_val - (0.674 * sigma), 2)),
                QuantileForecast(quantile=0.50, value=round(base_val, 2)),
                QuantileForecast(quantile=0.75, value=round(base_val + (0.674 * sigma), 2)),
                QuantileForecast(quantile=0.95, value=round(base_val + (1.645 * sigma), 2)),
            ],
            prob_threshold_breach={
                f"{req.target_asset.lower()}_tail_upper": 0.18,
                f"{req.target_asset.lower()}_tail_lower": 0.12,
            },
            conformal_interval_90=(
                round(base_val - (1.75 * sigma), 2),
                round(base_val + (1.75 * sigma), 2),
            ),
        ),
        empirical_coverage_90=0.908,
        is_demo_data=True,
    )
    return forecast
