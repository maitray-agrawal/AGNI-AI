"""
AGNI Statistical Regime Detection Engine (Markov Switching & Gaussian HMM)
==========================================================================
Implements statistically grounded macro-volatility regime estimation across:
  - CALM
  - ELEVATED
  - STRESSED
  - CRISIS

Estimates:
1. Filtered and smoothed regime posterior probabilities (zero manual assignment)
2. 4x4 Markov transition probability matrix (P_ij = P(S_t = j | S_{t-1} = i))
3. Expected regime durations (E[D_i] = 1 / (1 - P_ii))
4. Feature contributions (standardized attribution of observable stress drivers)
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timezone
import numpy as np
from scipy import stats
import polars as pl

from backend.app.schemas.canonical import RegimeState, RegimeType


class StatisticalRegimeEngine:
    """
    4-State Gaussian Hidden Markov / Markov Switching Engine.
    Estimates state posterior distributions, transition persistence, and driver attributions.
    """

    REGIMES: List[RegimeType] = ["CALM", "ELEVATED", "STRESSED", "CRISIS"]

    def __init__(self, k_regimes: int = 4, max_iter: int = 40, tol: float = 1e-4):
        self.k_regimes = k_regimes
        self.max_iter = max_iter
        self.tol = tol

        # Fitted parameters
        self.means: Optional[np.ndarray] = None          # (K, D)
        self.variances: Optional[np.ndarray] = None      # (K, D)
        self.transition_matrix: Optional[np.ndarray] = None  # (K, K)
        self.initial_probs: Optional[np.ndarray] = None  # (K,)
        self.is_fitted: bool = False
        self.feature_names: List[str] = [
            "realized_volatility",
            "vix_implied_volatility",
            "cross_asset_correlation",
            "drawdown_stress",
        ]

    def _init_parameters(self, X: np.ndarray):
        """Initializes emission means strictly sorted by volatility stress intensity."""
        N, D = X.shape
        K = self.k_regimes

        # Order samples by primary stress feature (feature 0: realized vol)
        primary_feature = X[:, 0]
        percentiles = np.linspace(15, 85, K)
        sorted_indices = np.argsort(primary_feature)

        split_indices = np.array_split(sorted_indices, K)
        self.means = np.zeros((K, D))
        self.variances = np.zeros((K, D))

        for k in range(K):
            cluster = X[split_indices[k]]
            self.means[k] = np.mean(cluster, axis=0)
            self.variances[k] = np.var(cluster, axis=0) + 1e-4

        # Transition matrix with high diagonal persistence typical of financial regimes
        # CALM is most persistent (0.92), CRISIS is least persistent (0.65)
        P = np.array([
            [0.92, 0.06, 0.019, 0.001],
            [0.10, 0.80, 0.080, 0.020],
            [0.02, 0.14, 0.740, 0.100],
            [0.01, 0.09, 0.300, 0.600],
        ])
        # Ensure row-stochastic
        self.transition_matrix = P / P.sum(axis=1, keepdims=True)
        self.initial_probs = np.array([0.70, 0.20, 0.08, 0.02])

    def _emission_log_prob(self, x: np.ndarray, k: int) -> float:
        """Log-likelihood of observation vector under state k Gaussian emission."""
        mu = self.means[k]
        var = np.maximum(self.variances[k], 1e-5)
        d = len(x)
        log_norm = -0.5 * (d * np.log(2.0 * np.pi) + np.sum(np.log(var)))
        sq_dist = -0.5 * np.sum(((x - mu) ** 2) / var)
        return float(log_norm + sq_dist)

    def fit(self, X: np.ndarray, feature_names: Optional[List[str]] = None) -> "StatisticalRegimeEngine":
        """
        Fits 4-state Gaussian HMM via Expectation-Maximization (Baum-Welch algorithm).
        Guarantees that state indices monotonically correspond to CALM < ELEVATED < STRESSED < CRISIS.
        """
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        N, D = X.shape
        K = self.k_regimes
        if feature_names:
            self.feature_names = feature_names

        self._init_parameters(X)

        for iteration in range(self.max_iter):
            # 1. Compute Emission Log-Probabilities: shape (N, K)
            log_B = np.zeros((N, K))
            for t in range(N):
                for k in range(K):
                    log_B[t, k] = self._emission_log_prob(X[t], k)

            # 2. Forward Pass with scaling (Alpha)
            alpha = np.zeros((N, K))
            c = np.zeros(N)

            alpha[0] = self.initial_probs * np.exp(log_B[0] - np.max(log_B[0]))
            c[0] = np.sum(alpha[0]) + 1e-12
            alpha[0] /= c[0]

            for t in range(1, N):
                alpha[t] = (alpha[t - 1] @ self.transition_matrix) * np.exp(log_B[t] - np.max(log_B[t]))
                c[t] = np.sum(alpha[t]) + 1e-12
                alpha[t] /= c[t]

            # 3. Backward Pass (Beta)
            beta = np.zeros((N, K))
            beta[-1] = 1.0

            for t in range(N - 2, -1, -1):
                beta[t] = (self.transition_matrix @ (beta[t + 1] * np.exp(log_B[t + 1] - np.max(log_B[t + 1]))))
                beta[t] /= c[t + 1]

            # 4. Posterior State Probabilities: gamma_t(i)
            gamma = alpha * beta
            gamma_sum = np.sum(gamma, axis=1, keepdims=True) + 1e-12
            gamma /= gamma_sum

            # 5. Transition Posteriors: xi_t(i, j)
            xi = np.zeros((N - 1, K, K))
            for t in range(N - 1):
                b_next = np.exp(log_B[t + 1] - np.max(log_B[t + 1]))
                numer = alpha[t, :, None] * self.transition_matrix * (b_next * beta[t + 1])[None, :]
                denom = np.sum(numer) + 1e-12
                xi[t] = numer / denom

            # 6. M-Step Parameter Updates
            new_init = gamma[0]
            new_trans = np.sum(xi, axis=0) / (np.sum(gamma[:-1], axis=0)[:, None] + 1e-12)
            # Row-stochastic normalization
            new_trans = new_trans / (new_trans.sum(axis=1, keepdims=True) + 1e-12)

            new_means = np.zeros((K, D))
            new_variances = np.zeros((K, D))
            for k in range(K):
                gamma_k = gamma[:, k][:, None]
                sum_gamma_k = np.sum(gamma[:, k]) + 1e-12
                new_means[k] = np.sum(gamma_k * X, axis=0) / sum_gamma_k
                diff = X - new_means[k]
                new_variances[k] = np.sum(gamma_k * (diff ** 2), axis=0) / sum_gamma_k + 1e-4

            # Enforce monotonic stress ordering on means by primary feature
            order = np.argsort(new_means[:, 0])
            self.means = new_means[order]
            self.variances = new_variances[order]
            self.transition_matrix = new_trans[order][:, order]
            self.initial_probs = new_init[order]

        self.is_fitted = True
        return self

    def infer_regime(self, X: np.ndarray) -> RegimeState:
        """
        Runs inference on the observation series to estimate:
        - Current regime state and posterior probabilities
        - Expected regime durations
        - Feature contribution scores
        """
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        N, D = X.shape
        K = self.k_regimes

        if not self.is_fitted:
            self.fit(X)

        # Compute log-emissions
        log_B = np.zeros((N, K))
        for t in range(N):
            for k in range(K):
                log_B[t, k] = self._emission_log_prob(X[t], k)

        # Forward filter to get latest filtered state distribution
        alpha = np.zeros((N, K))
        c = np.zeros(N)

        alpha[0] = self.initial_probs * np.exp(log_B[0] - np.max(log_B[0]))
        c[0] = np.sum(alpha[0]) + 1e-12
        alpha[0] /= c[0]

        for t in range(1, N):
            alpha[t] = (alpha[t - 1] @ self.transition_matrix) * np.exp(log_B[t] - np.max(log_B[t]))
            c[t] = np.sum(alpha[t]) + 1e-12
            alpha[t] /= c[t]

        # Latest posterior probabilities
        latest_probs = alpha[-1]
        active_idx = int(np.argmax(latest_probs))
        current_regime = self.REGIMES[active_idx]
        current_prob = float(latest_probs[active_idx])

        # Regime probabilities dict
        regime_probs_dict = {
            self.REGIMES[k]: round(float(latest_probs[k]), 4)
            for k in range(K)
        }

        # Transition probabilities dictionary (4x4)
        trans_dict: Dict[str, Dict[str, float]] = {}
        for i, from_r in enumerate(self.REGIMES):
            trans_dict[from_r] = {}
            for j, to_r in enumerate(self.REGIMES):
                trans_dict[from_r][to_r] = round(float(self.transition_matrix[i, j]), 4)

        # Expected Regime Durations: E[D_i] = 1 / (1 - P_ii)
        expected_durations = {}
        for i, r in enumerate(self.REGIMES):
            p_stay = float(self.transition_matrix[i, i])
            # Clip between 1.0 and 250 days to prevent numerical divergence
            denom = max(1e-4, 1.0 - p_stay)
            expected_durations[r] = round(float(min(250.0, 1.0 / denom)), 1)

        # Feature Contributions:
        # Standardized deviation of latest vector x_T from the CALM baseline mean
        latest_x = X[-1]
        calm_mu = self.means[0]
        calm_std = np.sqrt(np.maximum(self.variances[0], 1e-4))
        deviations = np.abs((latest_x - calm_mu) / calm_std)

        total_dev = np.sum(deviations) + 1e-8
        contributions = {}
        for d, f_name in enumerate(self.feature_names[:D]):
            contributions[f_name] = round(float(deviations[d] / total_dev), 4)

        return RegimeState(
            regime_id=f"regime-hmm-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            current_regime=current_regime,
            probability=round(current_prob, 4),
            regime_probabilities=regime_probs_dict,
            features_used=self.feature_names[:D],
            transition_probabilities=trans_dict,
            expected_durations=expected_durations,
            feature_contributions=contributions,
            model_type="hidden_markov_model",
        )

    def fit_from_market_store(self, store: Any = None) -> RegimeState:
        """
        Builds feature matrix from canonical market observations:
        1. Realized volatility of Brent crude
        2. Implied volatility (VIX)
        3. Cross-asset correlation (Brent vs SPX)
        4. SPX peak-to-trough drawdown
        """
        if store is None:
            from agni.markets.store import market_data_store
            store = market_data_store

        brent_df = store.get_asset_series("BRENT_CRUDE", limit=120)
        vix_df = store.get_asset_series("VIX", limit=120)
        spx_df = store.get_asset_series("SPX", limit=120)

        # Extract features
        brent_vol = brent_df["realized_vol_30d"].to_numpy()
        vix_price = vix_df["price"].to_numpy()

        # Returns for correlation
        n = min(len(brent_vol), len(vix_price), len(spx_df))
        brent_vol = brent_vol[-n:]
        vix_price = vix_price[-n:]
        spx_prices = spx_df["price"].to_numpy()[-n:]

        # Simple trailing drawdown
        cum_max = np.maximum.accumulate(spx_prices)
        drawdown = np.abs((spx_prices - cum_max) / (cum_max + 1e-8)) * 100.0

        # Trailing correlation proxy
        b_ret = np.diff(spx_prices, prepend=spx_prices[0])
        corr_feature = np.zeros(n)
        for i in range(15, n):
            corr_feature[i] = float(np.corrcoef(b_ret[i-15:i], vix_price[i-15:i])[0, 1])

        X = np.column_stack([brent_vol, vix_price, corr_feature, drawdown])
        self.feature_names = [
            "realized_volatility",
            "vix_implied_volatility",
            "cross_asset_correlation",
            "spx_drawdown",
        ]

        self.fit(X)
        return self.infer_regime(X)


# Global singleton instance
statistical_regime_engine = StatisticalRegimeEngine()
