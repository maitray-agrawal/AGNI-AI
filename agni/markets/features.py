"""
AGNI Market Feature Engineering Engine
======================================
Strictly causal, point-in-time feature transformation pipeline powered by Polars.
Guarantees zero forward-looking lookahead data leakage by strictly enforcing
trailing-only window functions and backward lags.

Features implemented:
1. Arithmetic returns & Log returns
2. Rolling annualized volatility & Realized volatility
3. Multi-horizon momentum (5D, 20D, 60D)
4. Peak-to-trough Drawdown
5. Pairwise rolling correlation & Multi-asset cross-correlation matrices
6. Pricing & Yield spreads
7. Rolling Z-scores (standardized deviations)
8. Volatility regime features (vol-of-vol, percentile ranking, regime classification)
9. Event-window features (days-to-event, window flags, cumulative abnormal returns)
"""

from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import numpy as np
import polars as pl


class MarketFeatureEngine:
    """Institutional feature engineering pipeline with zero future lookahead."""

    @staticmethod
    def compute_returns(df: pl.DataFrame, price_col: str = "price") -> pl.DataFrame:
        """
        Computes trailing arithmetic and continuous log returns:
          R_t = (P_t - P_{t-1}) / P_{t-1}
          r_t = ln(P_t / P_{t-1})
        """
        ret = ((pl.col(price_col) - pl.col(price_col).shift(1)) / pl.col(price_col).shift(1))
        log_ret = (pl.col(price_col) / pl.col(price_col).shift(1)).log()
        return df.with_columns([
            ret.alias("returns"),
            ret.alias("returns_1d"),
            log_ret.alias("log_returns"),
            log_ret.alias("log_returns_1d"),
        ])

    @staticmethod
    def compute_volatility(
        df: pl.DataFrame,
        return_col: str = "log_returns",
        windows: List[int] = [10, 20, 60],
        annualization_factor: float = 252.0,
    ) -> pl.DataFrame:
        """
        Computes rolling annualized volatility and realized volatility using strictly trailing windows:
          sigma_{t, k} = std(r_{t-k:t}) * sqrt(252)
          RV_{t, k} = sqrt( sum(r^2) * (252 / k) )
        """
        exprs = []
        for w in windows:
            roll = (pl.col(return_col).rolling_std(window_size=w) * np.sqrt(annualization_factor))
            real = (((pl.col(return_col) ** 2).rolling_sum(window_size=w) * (annualization_factor / w)).sqrt())
            exprs.append(roll.alias(f"rolling_vol_{w}"))
            exprs.append(roll.alias(f"volatility_rolling_{w}d"))
            exprs.append(real.alias(f"realized_vol_{w}"))
            exprs.append(real.alias(f"volatility_realized_{w}d"))
        return df.with_columns(exprs)

    @staticmethod
    def compute_momentum(
        df: pl.DataFrame,
        price_col: str = "price",
        windows: List[int] = [5, 20, 60],
    ) -> pl.DataFrame:
        """
        Trailing momentum / rate of change:
          M_{t, k} = (P_t - P_{t-k}) / P_{t-k}
        """
        exprs = []
        for w in windows:
            exprs.append(
                ((pl.col(price_col) - pl.col(price_col).shift(w)) / pl.col(price_col).shift(w))
                .alias(f"momentum_{w}d")
            )
        return df.with_columns(exprs)

    @staticmethod
    def compute_drawdown(df: pl.DataFrame, price_col: str = "price") -> pl.DataFrame:
        """
        Trailing cumulative peak and drawdown:
          Peak_t = max_{s <= t} P_s
          DD_t = (P_t - Peak_t) / Peak_t
        """
        dd = ((pl.col(price_col) - pl.col(price_col).cum_max()) / pl.col(price_col).cum_max())
        return df.with_columns([
            pl.col(price_col).cum_max().alias("cum_max_price"),
            dd.alias("drawdown"),
            dd.alias("drawdown_20d"),
        ])

    @staticmethod
    def compute_z_score(
        df: pl.DataFrame,
        col: str = "price",
        windows: List[int] = [20, 60],
    ) -> pl.DataFrame:
        """
        Rolling Z-score standardization using strictly trailing mean and standard deviation:
          Z_{t, k} = (x_t - mu_{t, k}) / sigma_{t, k}
        """
        exprs = []
        for w in windows:
            roll_mean = pl.col(col).rolling_mean(window_size=w)
            roll_std = pl.col(col).rolling_std(window_size=w)
            zs = ((pl.col(col) - roll_mean) / (roll_std + 1e-8))
            exprs.append(zs.alias(f"z_score_{w}"))
            exprs.append(zs.alias(f"z_score_{w}d"))
        return df.with_columns(exprs)

    @staticmethod
    def compute_volatility_regime_features(
        df: pl.DataFrame,
        vol_col: str = "rolling_vol_20",
        lookback: int = 100,
    ) -> pl.DataFrame:
        """
        Computes volatility regime features:
        - Volatility of volatility (std of rolling vol)
        - Rolling percentile ranking within trailing lookback window
        - Categorical regime state (LOW, NORMAL, HIGH, CRISIS)
        """
        if vol_col not in df.columns:
            # Fallback if not already calculated
            df = MarketFeatureEngine.compute_volatility(df, windows=[20])

        vol_min = pl.col(vol_col).rolling_min(window_size=lookback)
        vol_max = pl.col(vol_col).rolling_max(window_size=lookback)
        vol_range = (vol_max - vol_min) + 1e-8

        pct_expr = ((pl.col(vol_col) - vol_min) / vol_range).clip(0.0, 1.0).alias("vol_percentile_100")
        vol_of_vol = pl.col(vol_col).rolling_std(window_size=20).alias("vol_of_vol_20")

        res_df = df.with_columns([pct_expr, vol_of_vol])

        # Assign discrete regime label
        regime_expr = (
            pl.when(pl.col("vol_percentile_100") >= 0.90)
            .then(pl.lit("CRISIS"))
            .when(pl.col("vol_percentile_100") >= 0.70)
            .then(pl.lit("HIGH"))
            .when(pl.col("vol_percentile_100") >= 0.30)
            .then(pl.lit("NORMAL"))
            .otherwise(pl.lit("LOW"))
            .alias("volatility_regime")
        )
        res_df = res_df.with_columns(regime_expr)
        return res_df.with_columns(pl.col("volatility_regime").alias("vol_regime"))

    @staticmethod
    def compute_event_window_features(
        df: pl.DataFrame,
        event_timestamp: datetime,
        time_col: str = "timestamp",
        return_col: str = "returns",
        pre_window_days: int = 5,
        post_window_days: int = 10,
    ) -> pl.DataFrame:
        """
        Constructs event-window features for geopolitical shocks:
        - days_to_event: Signed integer days offset (t - t_event)
        - in_event_window: Boolean indicator for [-pre, +post] window
        - post_event_flag: Active during post-event propagation window [0, +post]
        - cumulative_abnormal_return: Cumulative return from t_event onwards
        """
        # Ensure returns exist
        if return_col not in df.columns:
            df = MarketFeatureEngine.compute_returns(df)

        # Convert timestamps to date differences
        event_dt = event_timestamp.replace(tzinfo=None) if hasattr(event_timestamp, "tzinfo") and event_timestamp.tzinfo else event_timestamp

        res = df.with_columns([
            ((pl.col(time_col).cast(pl.Date) - pl.lit(event_dt.date())).dt.total_days())
            .alias("days_to_event")
        ])

        in_win_expr = (
            (pl.col("days_to_event") >= -pre_window_days) &
            (pl.col("days_to_event") <= post_window_days)
        ).alias("in_event_window")

        post_flag_expr = (
            (pl.col("days_to_event") >= 0) &
            (pl.col("days_to_event") <= post_window_days)
        ).alias("post_event_flag")

        res = res.with_columns([in_win_expr, post_flag_expr])

        # Compute cumulative return across the window
        cum_ret_expr = (
            pl.when(pl.col("in_event_window"))
            .then((1.0 + pl.col(return_col).fill_null(0.0)).cum_prod() - 1.0)
            .otherwise(0.0)
            .alias("cumulative_event_return")
        )

        return res.with_columns(cum_ret_expr)

    @classmethod
    def compute_spread(
        cls,
        df_or_wide: pl.DataFrame,
        second_df_or_col_a: Any = "price",
        col_a: str = "price",
        col_b: str = "price",
        spread_name: Optional[str] = None,
        as_ratio: bool = False,
    ) -> pl.DataFrame:
        """
        Computes pricing or yield spread:
        Supports either:
          - single wide dataframe: compute_spread(wide_df, "BRENT", "WTI")
          - two dataframes: compute_spread(df_a, df_b, col_a="price", col_b="price")
        """
        if isinstance(second_df_or_col_a, pl.DataFrame):
            df_a = df_or_wide
            df_b = second_df_or_col_a
            # Align on timestamp
            joined = df_a.select(["timestamp", col_a]).join(
                df_b.select(["timestamp", col_b]),
                on="timestamp",
                how="inner",
                suffix="_b"
            )
            col_b_name = f"{col_b}_b" if f"{col_b}_b" in joined.columns else col_b
            s_name = spread_name or "spread"
            if as_ratio:
                expr = (pl.col(col_a) / (pl.col(col_b_name) + 1e-8)).alias(s_name)
            else:
                expr = (pl.col(col_a) - pl.col(col_b_name)).alias(s_name)
            res = joined.with_columns(expr)
            s_mean = pl.col(s_name).rolling_mean(window_size=20)
            s_std = pl.col(s_name).rolling_std(window_size=20)
            return res.with_columns(((pl.col(s_name) - s_mean) / (s_std + 1e-8)).alias("spread_zscore"))
        else:
            wide_df = df_or_wide
            ca = str(second_df_or_col_a) if isinstance(second_df_or_col_a, str) else col_a
            cb = col_b
            s_name = spread_name or f"{ca}_{cb}_spread"
            if as_ratio:
                expr = (pl.col(ca) / (pl.col(cb) + 1e-8)).alias(s_name)
            else:
                expr = (pl.col(ca) - pl.col(cb)).alias(s_name)
            res = wide_df.with_columns(expr)
            s_mean = pl.col(s_name).rolling_mean(window_size=20)
            s_std = pl.col(s_name).rolling_std(window_size=20)
            return res.with_columns(((pl.col(s_name) - s_mean) / (s_std + 1e-8)).alias("spread_zscore"))

    @staticmethod
    def compute_cross_asset_correlations(
        wide_df: pl.DataFrame,
        asset_cols: List[str],
        window: int = 30,
    ) -> Dict[str, float]:
        """
        Computes rolling pairwise correlation across multiple assets.
        Returns a dictionary of pairs: {"BRENT_SPX": 0.42, "BRENT_VIX": -0.31, ...}
        """
        corr_dict = {}
        for i in range(len(asset_cols)):
            for j in range(i + 1, len(asset_cols)):
                a, b = asset_cols[i], asset_cols[j]
                if a in wide_df.columns and b in wide_df.columns:
                    s_a = wide_df[a].tail(window).to_numpy()
                    s_b = wide_df[b].tail(window).to_numpy()
                    # Filter nans
                    mask = ~np.isnan(s_a) & ~np.isnan(s_b)
                    if np.sum(mask) > 5:
                        c = float(np.corrcoef(s_a[mask], s_b[mask])[0, 1])
                        corr_dict[f"{a}_{b}"] = round(c, 4)
                    else:
                        corr_dict[f"{a}_{b}"] = 0.0
        return corr_dict

    @classmethod
    def compute_cross_asset_correlation(
        cls,
        assets: Optional[List[str]] = None,
        wide_df: Optional[pl.DataFrame] = None,
        window: int = 30,
    ) -> Dict[str, Dict[str, float]]:
        """
        Computes full square cross-asset correlation matrix.
        Returns nested dictionary: corr[asset_a][asset_b] = 0.42
        """
        if wide_df is None:
            from agni.markets.store import market_data_store
            assets = assets or ["BRENT_CRUDE", "SPX", "DXY", "VIX"]
            wide_df = market_data_store.get_cross_asset_series(assets, limit=window * 2)

        asset_cols = [c for c in wide_df.columns if c != "timestamp" and (assets is None or c in assets)]
        matrix: Dict[str, Dict[str, float]] = {a: {} for a in asset_cols}

        for i, a in enumerate(asset_cols):
            matrix[a][a] = 1.0
            for j in range(i + 1, len(asset_cols)):
                b = asset_cols[j]
                s_a = wide_df[a].tail(window).to_numpy()
                s_b = wide_df[b].tail(window).to_numpy()
                mask = ~np.isnan(s_a) & ~np.isnan(s_b)
                if np.sum(mask) > 5:
                    c = round(float(np.corrcoef(s_a[mask], s_b[mask])[0, 1]), 4)
                else:
                    c = 0.0
                matrix[a][b] = c
                matrix[b][a] = c

        return matrix

    @classmethod
    def compute_full_feature_matrix(
        cls,
        df: pl.DataFrame,
        price_col: str = "price",
        event_timestamp: Optional[datetime] = None,
    ) -> pl.DataFrame:
        """
        Runs the full end-to-end feature pipeline for a single asset time series:
        Returns -> Volatility -> Momentum -> Drawdown -> Z-scores -> Regime -> Event Window.
        """
        res = cls.compute_returns(df, price_col=price_col)
        res = cls.compute_volatility(res, return_col="log_returns")
        res = cls.compute_momentum(res, price_col=price_col)
        res = cls.compute_drawdown(res, price_col=price_col)
        res = cls.compute_z_score(res, col=price_col)
        res = cls.compute_volatility_regime_features(res, vol_col="rolling_vol_20")

        # Always compute event window features (anchored causally to series start if not specified)
        evt_time = event_timestamp if event_timestamp is not None else (df["timestamp"].min() + timedelta(days=15))
        res = cls.compute_event_window_features(res, event_timestamp=evt_time)

        return res
