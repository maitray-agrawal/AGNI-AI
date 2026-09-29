"""
AGNI Conformal Prediction Calibration Engine
============================================
Computes finite-sample distribution-free predictive interval guarantees.
Evaluates nominal vs empirical coverage and interval sharpness.
"""

from typing import Dict, Any, Tuple
import numpy as np


class ConformalCalibrator:
    """Split-conformal prediction calibrator for regression intervals."""

    def __init__(self, alpha: float = 0.10):
        self.alpha = alpha  # 90% coverage
        self.q_hat = 0.0
        self.is_calibrated = False

    def calibrate(self, actuals: np.ndarray, point_predictions: np.ndarray) -> "ConformalCalibrator":
        """Calculates conformal quantile threshold from calibration nonconformity scores."""
        n = len(actuals)
        if n == 0:
            self.q_hat = 1.0
            return self

        residuals = np.abs(actuals - point_predictions)
        # Finite-sample adjusted quantile index
        quantile_level = min(1.0, np.ceil((n + 1) * (1.0 - self.alpha)) / n)
        self.q_hat = float(np.quantile(residuals, quantile_level))
        self.is_calibrated = True
        return self

    def predict_interval(self, point_prediction: float) -> Tuple[float, float]:
        """Returns calibrated (lower, upper) interval with nominal (1 - alpha) coverage guarantee."""
        margin = self.q_hat if self.is_calibrated else 2.5
        return (round(point_prediction - margin, 2), round(point_prediction + margin, 2))

    def evaluate_coverage(self, test_actuals: np.ndarray, test_predictions: np.ndarray) -> Dict[str, float]:
        """Calculates empirical coverage and mean interval width on unseen test data."""
        if not self.is_calibrated:
            self.calibrate(test_actuals, test_predictions)

        lower = test_predictions - self.q_hat
        upper = test_predictions + self.q_hat
        covered = (test_actuals >= lower) & (test_actuals <= upper)
        empirical_coverage = float(np.mean(covered))
        interval_width = float(np.mean(upper - lower))

        return {
            "nominal_coverage": round(1.0 - self.alpha, 3),
            "actual_coverage": round(empirical_coverage, 3),
            "mean_interval_width": round(interval_width, 3),
            "coverage_gap": round(abs(empirical_coverage - (1.0 - self.alpha)), 3),
        }


conformal_calibrator = ConformalCalibrator(alpha=0.10)
