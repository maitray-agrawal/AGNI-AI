# Model Card: AGNI Conditional Stress Scenario Generator

## Model Details
- **Model Name:** `AGNI-CSS-Engine-v1`
- **Model Version:** `1.0.0`
- **Model Family:** Conditional Multi-Asset Joint Shock Stress Engine
- **Implementation:** Covariance Decomposition & Non-Parametric Loss Aggregation
- **Developer:** AstraX Sovereign Intelligence Research Group
- **Release Date:** September 2026
- **License:** Apache-2.0

## Intended Use
- **Primary Purpose:** Evaluate the vulnerability of multi-asset sovereign and institutional portfolios under severe hypothetical or historical geopolitical crises (e.g. Strait of Hormuz full closure, Taiwan Strait naval interdiction, protracted Red Sea diversion).
- **Core Metrics:**
  - **Portfolio Value at Risk ($\text{VaR}_{95}$):**
    $$\text{VaR}_{95} = \min\left(-0.85, \sum_{i=1}^N w_i \cdot s_i \cdot M_{\text{regime}}\right)$$
  - **Expected Shortfall ($\text{CVaR}_{95}$ / $\text{ES}_{95}$):**
    $$\text{ES}_{95} = 1.45 \cdot \text{VaR}_{95}$$
  - **Joint Asset Shock Vectors:** Projected percentage changes with 90% confidence intervals for equities (SPX), commodities (Brent Crude, TTF Gas), logistics (SCFI Container Index), interest rates (US10Y), and volatility (VIX).

## Scenario Typology
1. **BASE:** Baseline de-escalation; multilateral naval escorts and diplomatic stabilization.
2. **ADVERSE:** Regional crisis escalation with persistent rerouting around Cape of Good Hope (+12 to 14 days delay).
3. **SEVERE:** Physical chokepoint interdiction, tanker boarding probes, and mining of critical narrows.
4. **CUSTOM:** Parameterized shocks defined manually by analysts via the Analyst Studio UI or `/api/scenarios` API.

## Assumptions & Risk Modeling
- Equity market drawdowns and commodity/volatility spikes jointly contribute to portfolio downside risk.
- Regime multipliers reflect the empirical observation that market drawdowns are amplified during `STRESSED` and `CRISIS` regimes due to reduced market liquidity and forced margin liquidation.

## Limitations & Known Failure Modes
1. **Correlation Breakdown:** Under unprecedented systemic collapse, historical correlations may break down (e.g., commodities and equities crashing simultaneously in liquidity crunches).
2. **Horizon Sensitivity:** Calculations assume a 30-day horizon; longer-term macroeconomic substitution effects are not modeled in initial stress vectors.
