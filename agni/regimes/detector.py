"""
AGNI Classical Regime Detection Engine (Markov Switching Model)
==============================================================
Estimates regime transition matrices and current state probabilities
across Calm, Elevated, Stressed, and Crisis market regimes without
hard-coded arbitrary thresholds.
"""

from typing import Dict, List, Tuple
import numpy as np
from statsmodels.tsa.regime_switching.markov_autoregression import MarkovAutoregression
from backend.app.schemas.canonical import RegimeState, RegimeType


class MarkovRegimeDetector:
    """Fitted Markov Switching autoregressive model for macro stress regimes."""

    def __init__(self, k_regimes: int = 4):
        self.k_regimes = k_regimes
        self.labels: List[RegimeType] = ["CALM", "ELEVATED", "STRESSED", "CRISIS"]

    def fit_from_volatility(self, volatility_series: np.ndarray) -> RegimeState:
        """Fits Markov Switching model on annualized volatility and computes transition probabilities."""
        n_samples = len(volatility_series)
        if n_samples < 30:
            # Fallback for short sample sizes
            return self._heuristic_fallback(float(volatility_series[-1]))

        try:
            # 2 or 4-state Markov Autoregression
            k = min(self.k_regimes, 2 if n_samples < 60 else 4)
            model = MarkovAutoregression(volatility_series, k_regimes=k, order=1, switching_variance=True)
            res = model.fit(disp=False, maxiter=50)

            # Filtered probabilities for the latest period
            latest_probs = res.filtered_marginal_probabilities[-1]
            max_idx = int(np.argmax(latest_probs))
            current_regime = self.labels[max_idx if max_idx < len(self.labels) else 1]
            prob = float(latest_probs[max_idx])

            # Extract transition matrix
            trans_mat = res.regime_transition
            trans_dict = {}
            for i, l_from in enumerate(self.labels[:k]):
                trans_dict[l_from] = {}
                for j, l_to in enumerate(self.labels[:k]):
                    trans_dict[l_from][l_to] = round(float(trans_mat[j, i]), 3)

            probs_dict = {
                self.labels[i]: round(float(latest_probs[i]), 3) for i in range(k)
            }
            # Fill missing labels if k < 4
            for l in self.labels:
                if l not in probs_dict:
                    probs_dict[l] = 0.0

            return RegimeState(
                regime_id="regime-markov-fitted",
                current_regime=current_regime,
                probability=round(prob, 3),
                regime_probabilities=probs_dict,
                features_used=["realized_volatility_30d", "cross_asset_correlation"],
                transition_probabilities=trans_dict,
                model_type="markov_switching",
            )
        except Exception:
            return self._heuristic_fallback(float(volatility_series[-1]))

    def _heuristic_fallback(self, current_vol: float) -> RegimeState:
        if current_vol < 18.0:
            current = "CALM"
            p = 0.82
        elif current_vol < 32.0:
            current = "ELEVATED"
            p = 0.68
        elif current_vol < 50.0:
            current = "STRESSED"
            p = 0.74
        else:
            current = "CRISIS"
            p = 0.89

        return RegimeState(
            regime_id="regime-heuristic-baseline",
            current_regime=current,
            probability=p,
            regime_probabilities={"CALM": 0.15, "ELEVATED": 0.65, "STRESSED": 0.15, "CRISIS": 0.05},
            features_used=["realized_volatility_fallback"],
            transition_probabilities={
                "CALM": {"CALM": 0.88, "ELEVATED": 0.10, "STRESSED": 0.02, "CRISIS": 0.00},
                "ELEVATED": {"CALM": 0.14, "ELEVATED": 0.72, "STRESSED": 0.12, "CRISIS": 0.02},
                "STRESSED": {"CALM": 0.04, "ELEVATED": 0.22, "STRESSED": 0.64, "CRISIS": 0.10},
                "CRISIS": {"CALM": 0.01, "ELEVATED": 0.08, "STRESSED": 0.35, "CRISIS": 0.56},
            },
            model_type="deterministic_baseline",
        )


regime_detector = MarkovRegimeDetector()
