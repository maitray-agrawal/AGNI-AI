"""
AGNI Rolling-Origin Walk-Forward Backtester
==========================================
Implements rigorous rolling-origin evaluation without lookahead data leakage.
Computes comprehensive institutional metrics:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- CRPS (Continuous Ranked Probability Score for distribution accuracy)
- Pinball Loss (Quantile verification across tau=0.10, 0.50, 0.90)
- Empirical Coverage (Conformal / Quantile interval hit rate vs nominal 90%)
"""

from typing import Dict, Any, List, Optional, Type
import numpy as np
from scipy import stats
import polars as pl

from agni.forecasting.baselines import BaseForecastModel


class RollingOriginBacktester:
    """Walk-forward rolling-origin evaluation framework."""

    @staticmethod
    def calculate_crps_gaussian(actual: float, mu: float, sigma: float) -> float:
        """Closed-form Gaussian Continuous Ranked Probability Score."""
        if sigma <= 1e-6:
            return float(abs(actual - mu))
        z = (actual - mu) / sigma
        norm_pdf = float(stats.norm.pdf(z))
        norm_cdf = float(stats.norm.cdf(z))
        crps = sigma * (z * (2.0 * norm_cdf - 1.0) + 2.0 * norm_pdf - (1.0 / np.sqrt(np.pi)))
        return float(max(0.0, crps))

    @staticmethod
    def calculate_pinball_loss(actual: float, q_pred: float, tau: float = 0.90) -> float:
        """Asymmetric piecewise quantile loss."""
        diff = actual - q_pred
        return float(max(tau * diff, (tau - 1.0) * diff))

    @classmethod
    def run_backtest(
        cls,
        model: BaseForecastModel,
        series: np.ndarray,
        horizon: int = 7,
        initial_train_window: int = 60,
        step_size: int = 3,
    ) -> Dict[str, Any]:
        """
        Executes rolling-origin walk-forward backtest:
        At each origin t:
          train on series[0:t]
          forecast step h
          evaluate actual series[t + h - 1]
        """
        series = np.asarray(series, dtype=float).flatten()
        n = len(series)

        if n < initial_train_window + horizon + 5:
            raise ValueError(f"Series length {n} is too short for train_window={initial_train_window} and horizon={horizon}")

        abs_errors = []
        sq_errors = []
        crps_scores = []
        pinball_90_scores = []
        pinball_50_scores = []
        pinball_10_scores = []
        coverage_90_hits = []

        # Iterate origins
        for t in range(initial_train_window, n - horizon + 1, step_size):
            train_slice = series[:t]
            actual = float(series[t + horizon - 1])

            # Fit model strictly on trailing history
            model.fit(train_slice)

            # Point forecast & predictive distribution
            pred = float(model.predict(horizon_steps=horizon))
            dist = model.predict_distribution(horizon_steps=horizon)

            # Error metrics
            err = actual - pred
            abs_errors.append(abs(err))
            sq_errors.append(err ** 2)

            # Probabilistic metrics
            mu = dist.mean
            sig = max(0.01, dist.standard_deviation)
            crps_scores.append(cls.calculate_crps_gaussian(actual, mu, sig))

            # Quantiles & Coverage
            q10 = mu - 1.282 * sig
            q50 = mu
            q90 = mu + 1.282 * sig

            if dist.quantiles:
                for q in dist.quantiles:
                    if abs(q.quantile - 0.10) < 0.06:
                        q10 = q.value
                    elif abs(q.quantile - 0.50) < 0.06:
                        q50 = q.value
                    elif abs(q.quantile - 0.90) < 0.06:
                        q90 = q.value

            pinball_10_scores.append(cls.calculate_pinball_loss(actual, q10, tau=0.10))
            pinball_50_scores.append(cls.calculate_pinball_loss(actual, q50, tau=0.50))
            pinball_90_scores.append(cls.calculate_pinball_loss(actual, q90, tau=0.90))

            # Conformal / empirical coverage test: actual in [q10, q90] or conformal interval
            c_low, c_high = dist.conformal_interval_90
            hit = 1.0 if (c_low <= actual <= c_high) else 0.0
            coverage_90_hits.append(hit)

        k = len(abs_errors)
        mae = float(np.mean(abs_errors)) if k else 0.0
        rmse = float(np.sqrt(np.mean(sq_errors))) if k else 0.0
        crps = float(np.mean(crps_scores)) if k else 0.0
        pinball_90 = float(np.mean(pinball_90_scores)) if k else 0.0
        pinball_50 = float(np.mean(pinball_50_scores)) if k else 0.0
        coverage = float(np.mean(coverage_90_hits)) if k else 0.0

        return {
            "model_name": model.name,
            "horizon_steps": horizon,
            "rolling_origins_evaluated": k,
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "crps": round(crps, 4),
            "pinball_loss_90": round(pinball_90, 4),
            "pinball_loss_50": round(pinball_50, 4),
            "nominal_coverage_90": 0.90,
            "empirical_coverage_90": round(coverage, 4),
            "coverage_gap": round(abs(coverage - 0.90), 4),
        }

    @classmethod
    def compare_models(
        cls,
        models: List[BaseForecastModel],
        series: np.ndarray,
        horizon: int = 7,
        initial_train_window: int = 60,
        step_size: int = 3,
    ) -> List[Dict[str, Any]]:
        """Compares multiple forecasting models across the identical rolling-origin walk-forward protocol."""
        results = []
        for m in models:
            res = cls.run_backtest(
                model=m,
                series=series,
                horizon=horizon,
                initial_train_window=initial_train_window,
                step_size=step_size,
            )
            results.append(res)

        # Sort by MAE ascending
        results.sort(key=lambda x: x["mae"])
        return results
