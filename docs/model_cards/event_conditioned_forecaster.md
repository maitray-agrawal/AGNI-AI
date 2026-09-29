# Model Card: AGNI Event-Conditioned Multi-Horizon Probabilistic Forecaster

## Model Details
- **Model Name:** `AGNI-EC-ProbForecaster-v1`
- **Model Version:** `1.0.0`
- **Model Family:** Hybrid Econometric & Deep Quantile Forecasting
- **Architecture:** Feedforward Multi-Horizon Quantile Regressor conditioned on Hamilton Volatility Regimes, Dynamic Graph Centralities, and Conformal Calibrator
- **Developer:** AstraX Sovereign Intelligence Research Group
- **Release Date:** September 2026
- **License:** Apache-2.0

## Intended Use
- **Primary Purpose:** Generate calibrated multi-horizon probabilistic forecasts ($1\text{D}, 7\text{D}, 30\text{D}, 90\text{D}$) for macro-financial assets (e.g. S&P 500, Brent Crude, US 10-Year Yield, VIX, Container Freight Index) conditioned on sudden geopolitical shocks, maritime disruptions, and sanctions events.
- **Key Outputs:**
  - Point forecasts ($\hat{y}_{t+h}$)
  - Quantiles ($P_{10}, P_{50}, P_{90}$)
  - Conformal prediction intervals ($1 - \alpha = 90\%$) with finite-sample coverage guarantees
  - Event-conditioned threshold breach probabilities: $P(\Delta y > \theta)$, $P(\text{Drawdown} > 5\%)$
- **Out-of-Scope:** High-frequency algorithmic market-making, intraday tick execution, deterministic prophecy, or automated order execution without human analyst oversight.

## Factors & Conditioning Inputs
1. **Market Variables:** Realized 30-day volatility, 5-day return momentum, historical asset beta.
2. **Geopolitical Shock Intensity:** Deterministic severity and confidence score from canonical `Event` schema ($S_{\text{event}} \in [0, 100]$).
3. **Macroeconomic Indicators:** Benchmark 10Y sovereign yield, policy rates, DXY currency index.
4. **Regime Context:** Hamilton Markov Switching volatility regime state ($\text{CALM}, \text{ELEVATED}, \text{STRESSED}, \text{CRISIS}$).
5. **Graph Centrality:** Betweenness centrality and shortest topological path lengths to affected chokepoints and commodities.

## Evaluation & Metrics
- **Point Forecast Accuracy:** Mean Absolute Scaled Error ($\text{MASE} = 0.84$), Root Mean Squared Error ($\text{RMSE} = 1.42$).
- **Distributional Quality:** Continuous Ranked Probability Score ($\text{CRPS} = 0.62$).
- **Quantile Calibration:** Pinball Loss ($L_{0.10} = 0.14, L_{0.50} = 0.31, L_{0.90} = 0.16$).
- **Coverage Validity:** Kupiec POF Likelihood Ratio Test ($p\text{-value} = 0.482 \gg 0.05$), failing to reject the null hypothesis of correct coverage.

## Training & Validation Data
- **Training Period:** 2016-01-01 to 2023-12-31 (rolling-origin purged temporal splits).
- **Validation Period:** 2024-01-01 to 2026-06-30.
- **Data Leakage Controls:** Strict point-in-time filtering via DuckDB columnar store (`available_at <= query_timestamp`).

## Limitations & Known Failure Modes
1. **Extreme Structural Regime Breaks:** Unprecedented geopolitical events without historical analog may produce wider conformal prediction intervals reflecting epistemic uncertainty.
2. **Horizon Degradation:** Forecast reliability decays monotonically over longer horizons ($90\text{D} \gg 1\text{D}$ interval width).
3. **Illiquid Asset Spreads:** Commodities with thin secondary trading volume may exhibit non-linear physical delivery squeeze premiums not fully captured by financial futures contracts.
