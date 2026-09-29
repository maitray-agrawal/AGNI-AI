"""
AGNI Market & Macroeconomic Intelligence API Router
===================================================
Provides high-performance point-in-time asset time series, causal feature engineering,
cross-asset correlations, and macroeconomic indicators.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from agni.markets.store import market_data_store
from agni.markets.features import MarketFeatureEngine

router = APIRouter(prefix="/markets", tags=["Markets"])


@router.get("/assets")
async def list_assets():
    """List all supported assets across FX, Commodities, Equities, Yields, and Volatility."""
    assets = market_data_store.list_available_assets()
    return {
        "count": len(assets),
        "assets": assets,
        "supported_classes": ["fx_rate", "commodity", "equity_index", "sovereign_bond", "volatility"],
    }


@router.get("/series/{asset_id}")
async def get_asset_series(
    asset_id: str,
    limit: int = Query(250, ge=10, le=1000),
    as_of: Optional[str] = None,
):
    """
    Retrieve point-in-time historical prices and volumes for an asset.
    Strictly filters out observations where available_at > as_of to prevent leakage.
    """
    cutoff = None
    if as_of:
        try:
            cutoff = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid ISO timestamp '{as_of}'")

    df = market_data_store.get_asset_series(asset_id, as_of=cutoff, limit=limit)
    if df.is_empty():
        raise HTTPException(status_code=404, detail=f"No observations found for asset '{asset_id}'")

    return {
        "asset_id": asset_id.upper(),
        "count": len(df),
        "data": df.to_dicts(),
    }


@router.get("/features/{asset_id}")
async def get_engineered_features(
    asset_id: str,
    limit: int = Query(150, ge=30, le=500),
    as_of: Optional[str] = None,
):
    """
    Returns time series enriched with strictly causal, trailing feature engineering:
    Returns, Log returns, Rolling/Realized volatility, Momentum, Drawdown, Z-scores, and Volatility Regime.
    """
    cutoff = None
    if as_of:
        try:
            cutoff = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid ISO timestamp '{as_of}'")

    # Fetch extra buffer for lookbacks
    df = market_data_store.get_asset_series(asset_id, as_of=cutoff, limit=limit + 60)
    if df.is_empty():
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")

    feat_df = MarketFeatureEngine.compute_full_feature_matrix(df).tail(limit)

    return {
        "asset_id": asset_id.upper(),
        "rows": len(feat_df),
        "features": feat_df.columns,
        "data": feat_df.to_dicts(),
    }


@router.get("/correlations")
async def get_cross_asset_correlations(
    assets: Optional[str] = Query(None, description="Comma-separated list of assets"),
    window: int = Query(30, ge=10, le=120),
):
    """
    Computes rolling cross-asset correlation matrix for multi-asset transmission analysis.
    """
    if assets:
        asset_list = [a.strip().upper() for a in assets.split(",") if a.strip()]
    else:
        asset_list = ["BRENT_CRUDE", "SPX", "VIX", "US10Y", "DXY"]

    wide_df = market_data_store.get_cross_asset_series(asset_list, limit=window * 2)
    if wide_df.is_empty():
        raise HTTPException(status_code=404, detail="No time series found for selected assets")

    corrs = MarketFeatureEngine.compute_cross_asset_correlations(wide_df, asset_list, window=window)
    matrix = MarketFeatureEngine.compute_cross_asset_correlation(assets=asset_list, wide_df=wide_df, window=window)

    return {
        "window_days": window,
        "assets": asset_list,
        "pairwise_correlations": corrs,
        "correlation_matrix": matrix,
    }


@router.get("/macro")
async def get_macro_indicators(indicator: Optional[str] = None):
    """Retrieve point-in-time macroeconomic indicator series."""
    indicators = [indicator] if indicator else market_data_store.list_macro_indicators()
    out = {}
    for ind in indicators:
        df = market_data_store.get_macro_series(ind)
        if not df.is_empty():
            out[ind] = df.to_dicts()

    return {
        "indicators": list(out.keys()),
        "data": out,
    }
