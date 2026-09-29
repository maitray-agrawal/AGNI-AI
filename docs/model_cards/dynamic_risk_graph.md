# Model Card: AGNI Dynamic Risk Graph Topology

## Model Details
- **Model Name:** `AGNI-DRG-Topology-v1`
- **Model Version:** `1.0.0`
- **Model Family:** Directed Multi-Hop Relational Knowledge Graph
- **Implementation:** `networkx.DiGraph` & PyTorch Geometric baseline
- **Developer:** AstraX Sovereign Intelligence Research Group
- **Release Date:** September 2026
- **License:** Apache-2.0

## Intended Use
- **Primary Purpose:** Model the multi-hop transmission mechanics of geopolitical shocks through physical supply corridors and commodity bottlenecks into financial and macroeconomic volatility.
- **Node Entities:**
  - Sovereign Countries / States ($N_{\text{country}}$)
  - Strategic Maritime Chokepoints ($N_{\text{chokepoint}}$)
  - Physical & Benchmark Commodities ($N_{\text{commodity}}$)
  - Financial & Capital Assets ($N_{\text{asset}}$)
  - Macroeconomic Volatility Indicators ($N_{\text{macro}}$)
- **Edge Semantics:**
  - `geopolitical_shock`: Country military exercise or drone strike directly threatening transit safety.
  - `supply_disruption`: Maritime closure forcing rerouting and reducing effective cargo throughput.
  - `price_transmission`: Shipping deviation adding bunker fuel cost and transit delays, raising physical delivery prices.
  - `volatility_contagion`: Elevated commodity inflation increasing rate hike expectations and equity market volatility.

## Topological Metrics Computed
- **Betweenness Centrality:** Identifies systemic chokepoints whose interdiction fractures international trade lanes.
- **Degree Centrality:** Measures direct asset and commodity dependencies.
- **Shortest Transmission Path:** Traces the verifiable causal chain from event origin to affected portfolio assets.
- **Reachability Subgraph:** Extracts all downstream nodes impacted within $k$ transmission hops.

## Limitations & Known Failure Modes
1. **Static Elasticity Approximations:** Elasticity coefficients ($\beta$) between nodes are estimated on historical normal-flow windows; non-linear physical exhaustion thresholds during total blockades may deviate from historical betas.
2. **Alternative Route Dynamic Capacity:** If alternative ports or bypass pipelines operate at 100% capacity, excess volume cannot be absorbed linearly.
