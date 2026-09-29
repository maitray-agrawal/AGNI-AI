"""
AGNI Standardized Time Series Forecasting Baselines
===================================================
Rigorous classical statistical models adhering to `BaseForecastModel`:
- Naive Forecast (Random Walk baseline)
- Moving Average (SMA/Trailing Mean baseline)
- Autoregressive Integrated Moving Average (ARIMA) via statsmodels
- Vector Autoregression (VAR) via statsmodels
- Generalized Autoregressive Conditional Heteroskedasticity (GARCH) via arch
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, Union, List
import numpy as np
import polars as pl
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.api import VAR
from arch import arch_model

from backend.app.schemas.canonical import ForecastDistribution, QuantileForecast


class BaseForecastModel(ABC):
    """Standardized institutional forecasting interface."""

    def __init__(self, name: str):
        self.name = name
        self.is_fitted = False

    @abstractmethod
    def fit(self, series: Union[np.ndarray, pl.DataFrame], **kwargs) -> "BaseForecastModel":
        """Fits model parameters on historical values."""
        pass

    @abstractmethod
    def predict(self, horizon_steps: int = 30) -> float:
        """Returns point forecast at specified horizon."""
        pass

    @abstractmethod
    def predict_distribution(self, horizon_steps: int = 30) -> ForecastDistribution:
        """Returns parametric or empirical predictive distribution with quantiles."""
        pass

    def evaluate(self, actuals: np.ndarray, predictions: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculates standard regression loss metrics (MAE, RMSE, MASE). If predictions is None, generates predictions."""
        actuals = np.asarray(actuals, dtype=float)
        if predictions is None:
            preds = [self.predict(h) for h in range(1, len(actuals) + 1)]
            predictions = np.asarray(preds, dtype=float)
        else:
            predictions = np.asarray(predictions, dtype=float)

        errors = actuals - predictions
        mae = float(np.mean(np.abs(errors)))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        naive_mae = float(np.mean(np.abs(np.diff(actuals)))) if len(actuals) > 1 else 1.0
        mase = mae / (naive_mae + 1e-8)
        return {"mae": round(mae, 4), "rmse": round(rmse, 4), "mase": round(mase, 4)}


# ── 1. NAIVE PERSISTENCE MODEL ───────────────────────────────────────────────

class NaiveForecastModel(BaseForecastModel):
    """Last-observation persistence baseline."""

    def __init__(self):
        super().__init__("Naive")
        self.last_val = 0.0
        self.hist_std = 1.0

    def fit(self, series: Union[np.ndarray, pl.DataFrame], **kwargs) -> "NaiveForecastModel":
        arr = np.asarray(series, dtype=float).flatten()
        self.last_val = float(arr[-1])
        self.hist_std = float(np.std(np.diff(arr))) if len(arr) > 1 else 1.0
        self.is_fitted = True
        return self

    def predict(self, horizon_steps: int = 30) -> float:
        return self.last_val

    def predict_distribution(self, horizon_steps: int = 30) -> ForecastDistribution:
        sigma = max(0.01, self.hist_std * np.sqrt(horizon_steps))
        point = self.last_val
        quantiles = [
            QuantileForecast(quantile=0.05, value=round(point - 1.645 * sigma, 2)),
            QuantileForecast(quantile=0.25, value=round(point - 0.674 * sigma, 2)),
            QuantileForecast(quantile=0.50, value=round(point, 2)),
            QuantileForecast(quantile=0.75, value=round(point + 0.674 * sigma, 2)),
            QuantileForecast(quantile=0.95, value=round(point + 1.645 * sigma, 2)),
        ]
        return ForecastDistribution(
            mean=round(point, 2),
            standard_deviation=round(sigma, 2),
            quantiles=quantiles,
            prob_threshold_breach={"shock_up_10pct": 0.15, "shock_down_10pct": 0.15},
            conformal_interval_90=(round(point - 1.645 * sigma, 2), round(point + 1.645 * sigma, 2)),
        )


# ── 2. MOVING AVERAGE MODEL ──────────────────────────────────────────────────

class MovingAverageForecastModel(BaseForecastModel):
    """Trailing window simple moving average baseline."""

    def __init__(self, window: int = 20):
        super().__init__(f"Moving Average ({window}D)")
        self.window = window
        self.ma_val = 0.0
        self.std_val = 1.0

    def fit(self, series: Union[np.ndarray, pl.DataFrame], **kwargs) -> "MovingAverageForecastModel":
        arr = np.asarray(series, dtype=float).flatten()
        w = min(self.window, len(arr))
        tail = arr[-w:]
        self.ma_val = float(np.mean(tail))
        self.std_val = float(np.std(tail)) if len(tail) > 1 else 1.0
        self.is_fitted = True
        return self

    def predict(self, horizon_steps: int = 30) -> float:
        return self.ma_val

    def predict_distribution(self, horizon_steps: int = 30) -> ForecastDistribution:
        point = self.ma_val
        sigma = max(0.01, self.std_val * np.sqrt(1.0 + (horizon_steps / float(self.window))))
        quantiles = [
            QuantileForecast(quantile=0.05, value=round(point - 1.645 * sigma, 2)),
            QuantileForecast(quantile=0.25, value=round(point - 0.674 * sigma, 2)),
            QuantileForecast(quantile=0.50, value=round(point, 2)),
            QuantileForecast(quantile=0.75, value=round(point + 0.674 * sigma, 2)),
            QuantileForecast(quantile=0.95, value=round(point + 1.645 * sigma, 2)),
        ]
        return ForecastDistribution(
            mean=round(point, 2),
            standard_deviation=round(sigma, 2),
            quantiles=quantiles,
            prob_threshold_breach={"shock_up_10pct": 0.12, "shock_down_10pct": 0.12},
            conformal_interval_90=(round(point - 1.65 * sigma, 2), round(point + 1.65 * sigma, 2)),
        )


# ── 3. ARIMA MODEL (STATSMODELS) ─────────────────────────────────────────────

class ARIMAForecastModel(BaseForecastModel):
    """Autoregressive Integrated Moving Average via statsmodels."""

    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1)):
        super().__init__(f"ARIMA{order}")
        self.order = order
        self.fitted_res = None
        self.last_val = 0.0
        self.last_sigma = 1.0

    def fit(self, series: Union[np.ndarray, pl.DataFrame], **kwargs) -> "ARIMAForecastModel":
        arr = np.asarray(series, dtype=float).flatten()
        self.last_val = float(arr[-1])
        try:
            model = ARIMA(arr, order=self.order)
            self.fitted_res = model.fit()
            self.last_sigma = float(np.sqrt(self.fitted_res.params[-1])) if len(self.fitted_res.params) > 0 else 1.0
        except Exception:
            self.fitted_res = None
            self.last_sigma = float(np.std(np.diff(arr))) if len(arr) > 1 else 1.0
        self.is_fitted = True
        return self

    def predict(self, horizon_steps: int = 30) -> float:
        if self.fitted_res:
            try:
                forecast = self.fitted_res.forecast(steps=horizon_steps)
                return float(forecast[-1])
            except Exception:
                pass
        return self.last_val

    def predict_distribution(self, horizon_steps: int = 30) -> ForecastDistribution:
        point = self.predict(horizon_steps)
        sigma = max(0.01, self.last_sigma * np.sqrt(horizon_steps))
        return ForecastDistribution(
            mean=round(point, 2),
            standard_deviation=round(sigma, 2),
            quantiles=[
                QuantileForecast(quantile=0.05, value=round(point - 1.645 * sigma, 2)),
                QuantileForecast(quantile=0.25, value=round(point - 0.674 * sigma, 2)),
                QuantileForecast(quantile=0.50, value=round(point, 2)),
                QuantileForecast(quantile=0.75, value=round(point + 0.674 * sigma, 2)),
                QuantileForecast(quantile=0.95, value=round(point + 1.645 * sigma, 2)),
            ],
            prob_threshold_breach={"shock_up_10pct": 0.14, "shock_down_10pct": 0.14},
            conformal_interval_90=(round(point - 1.68 * sigma, 2), round(point + 1.68 * sigma, 2)),
        )


# ── 4. VECTOR AUTOREGRESSION MODEL (STATSMODELS) ─────────────────────────────

class VARForecastModel(BaseForecastModel):
    """
    Vector Autoregression (VAR) via statsmodels for cross-asset dynamic transmission.
    Fits simultaneous dynamic equations for multi-asset systems (e.g. Brent, SPX, VIX).
    """

    def __init__(self, max_lags: int = 2):
        super().__init__(f"VAR(lags={max_lags})")
        self.max_lags = max_lags
        self.fitted_res = None
        self.last_vals = np.zeros(1)
        self.k_vars = 1

    def fit(self, series: Union[np.ndarray, pl.DataFrame], **kwargs) -> "VARForecastModel":
        if isinstance(series, pl.DataFrame):
            # Select all numeric columns
            numeric_cols = [c for c in series.columns if series[c].dtype in [pl.Float64, pl.Float32]]
            arr = series[numeric_cols].to_numpy()
        else:
            arr = np.asarray(series, dtype=float)
            if arr.ndim == 1:
                # Univariate fallback: create 2-column lag system
                arr = np.column_stack([arr[1:], arr[:-1]])

        self.k_vars = arr.shape[1]
        self.last_vals = arr[-1, :]
        try:
            model = VAR(arr)
            self.fitted_res = model.fit(maxlags=self.max_lags, ic="aic")
        except Exception:
            self.fitted_res = None

        self.is_fitted = True
        return self

    def predict(self, horizon_steps: int = 30) -> float:
        """Returns forecast for the primary asset (first column)."""
        if self.fitted_res:
            try:
                lag_order = self.fitted_res.k_ar
                history = self.fitted_res.endog[-lag_order:]
                fc = self.fitted_res.forecast(y=history, steps=horizon_steps)
                return float(fc[-1, 0])
            except Exception:
                pass
        return float(self.last_vals[0])

    def predict_distribution(self, horizon_steps: int = 30) -> ForecastDistribution:
        point = self.predict(horizon_steps)
        sigma = 3.5 * np.sqrt(horizon_steps / 30.0)
        if self.fitted_res:
            try:
                cov = self.fitted_res.sigma_u
                sigma = float(np.sqrt(cov[0, 0])) * np.sqrt(horizon_steps)
            except Exception:
                pass

        sigma = max(0.01, sigma)
        return ForecastDistribution(
            mean=round(point, 2),
            standard_deviation=round(sigma, 2),
            quantiles=[
                QuantileForecast(quantile=0.05, value=round(point - 1.645 * sigma, 2)),
                QuantileForecast(quantile=0.25, value=round(point - 0.674 * sigma, 2)),
                QuantileForecast(quantile=0.50, value=round(point, 2)),
                QuantileForecast(quantile=0.75, value=round(point + 0.674 * sigma, 2)),
                QuantileForecast(quantile=0.95, value=round(point + 1.645 * sigma, 2)),
            ],
            prob_threshold_breach={"cross_asset_transmission_shock": 0.18},
            conformal_interval_90=(round(point - 1.65 * sigma, 2), round(point + 1.65 * sigma, 2)),
        )


# ── 5. GARCH VOLATILITY MODEL (ARCH) ─────────────────────────────────────────

class GARCHVolatilityModel(BaseForecastModel):
    """GARCH(1,1) conditional heteroskedasticity volatility model via arch."""

    def __init__(self, p: int = 1, q: int = 1):
        super().__init__(f"GARCH({p},{q})")
        self.p = p
        self.q = q
        self.res = None
        self.last_val = 0.0

    def fit(self, series: Union[np.ndarray, pl.DataFrame], **kwargs) -> "GARCHVolatilityModel":
        arr = np.asarray(series, dtype=float).flatten()
        self.last_val = float(arr[-1])
        returns = 100.0 * np.diff(np.log(arr + 1e-8))
        try:
            am = arch_model(returns, vol="Garch", p=self.p, q=self.q, rescale=False)
            self.res = am.fit(disp="off")
        except Exception:
            self.res = None
        self.is_fitted = True
        return self

    def predict(self, horizon_steps: int = 30) -> float:
        return self.last_val

    def predict_distribution(self, horizon_steps: int = 30) -> ForecastDistribution:
        point = self.last_val
        cond_vol = 2.5
        if self.res:
            try:
                forecasts = self.res.forecast(horizon=horizon_steps)
                cond_vol = float(np.sqrt(forecasts.variance.values[-1, -1]))
            except Exception:
                pass

        dollar_sigma = max(0.01, point * (cond_vol / 100.0))
        return ForecastDistribution(
            mean=round(point, 2),
            standard_deviation=round(dollar_sigma, 2),
            quantiles=[
                QuantileForecast(quantile=0.05, value=round(point - 1.645 * dollar_sigma, 2)),
                QuantileForecast(quantile=0.25, value=round(point - 0.674 * dollar_sigma, 2)),
                QuantileForecast(quantile=0.50, value=round(point, 2)),
                QuantileForecast(quantile=0.75, value=round(point + 0.674 * dollar_sigma, 2)),
                QuantileForecast(quantile=0.95, value=round(point + 1.645 * dollar_sigma, 2)),
            ],
            prob_threshold_breach={"tail_loss_exceedance": 0.05},
            conformal_interval_90=(round(point - 1.65 * dollar_sigma, 2), round(point + 1.65 * dollar_sigma, 2)),
        )
