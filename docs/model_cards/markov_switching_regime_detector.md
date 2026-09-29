# Model Card: AGNI Markov Switching Volatility Regime Detector

## Model Details
- **Model Name:** `AGNI-MS-RegimeDetector-v1`
- **Model Version:** `1.0.0`
- **Model Family:** Hamilton Markov Switching Autoregressive Model
- **Implementation:** `statsmodels.tsa.regime_switching.markov_autoregression`
- **Developer:** AstraX Sovereign Intelligence Research Group
- **Release Date:** September 2026
- **License:** Apache-2.0

## Intended Use
- **Primary Purpose:** Categorize prevailing financial and geopolitical environments into distinct macro volatility regimes (`CALM`, `ELEVATED`, `STRESSED`, `CRISIS`) using measurable volatility and market returns rather than arbitrary hard-coded thresholds.
- **Key Outputs:**
  - Active regime state classification
  - Smoothed regime state probabilities: $P(S_t = j \mid \mathcal{F}_T)$
  - Transition probability matrix: $P_{i,j} = P(S_{t+1} = j \mid S_t = i)$
  - Regime multiplier for portfolio stress testing ($M_{\text{CALM}} = 1.0, M_{\text{ELEVATED}} = 1.25, M_{\text{STRESSED}} = 1.5, M_{\text{CRISIS}} = 1.8$).

## Input Features
- 30-day realized volatility of benchmark equities (S&P 500, MSCI World)
- CBOE Volatility Index (VIX)
- Crude Oil implied volatility (OVX)
- High-yield credit default swap spreads (CDX HY)
- Caldara-Iacoviello Geopolitical Risk Index (GPR)

## Transition Matrix Characteristics
| From / To | CALM | ELEVATED | STRESSED | CRISIS |
| :--- | :--- | :--- | :--- | :--- |
| **CALM** | 0.94 | 0.05 | 0.01 | 0.00 |
| **ELEVATED** | 0.08 | 0.85 | 0.06 | 0.01 |
| **STRESSED** | 0.02 | 0.12 | 0.80 | 0.06 |
| **CRISIS** | 0.00 | 0.04 | 0.18 | 0.78 |

## Limitations & Known Failure Modes
1. **Convergence on Flat Volatility Regimes:** When realized volatility remains uncharacteristically constant over prolonged holiday periods, expectation-maximization (EM) iterations may produce degenerate corner solutions.
2. **Lagged Detection of Flash Shocks:** Being a statistical filter on trailing windowed observations, sudden black-swan intraday moves may show a 1-day detection latency before regime shift is fully confirmed.
