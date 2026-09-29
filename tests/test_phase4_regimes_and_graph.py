"""
AGNI Phase 4 Test Suite: Statistical Regime Detection Engine & Dynamic Risk Graph
==================================================================================
Validates:
1. Statistically grounded 4-state Markov Switching / Gaussian HMM regime engine:
   - CALM, ELEVATED, STRESSED, CRISIS (zero manual assignment)
   - Filtered/smoothed posterior regime probabilities
   - 4x4 Markov transition probability matrix
   - Expected regime durations: E[D_i] = 1 / (1 - P_ii)
   - Normalized feature contribution scores
2. Dynamic directed Risk Graph using NetworkX:
   - Nodes: Country, Commodity, Financial Asset, Trade Route, Event
   - Edges:
       country → commodity
       country → asset
       country → route
       commodity → asset
       route → commodity
       event → country
   - Edge attributes: exposure, correlation, importance, confidence, timestamp
   - NetworkX graph analytics: PageRank, betweenness centrality, shortest path tracing
3. FastAPI Endpoints:
   - GET /graph & GET /api/graph
   - GET /graph/nodes, GET /graph/edges, GET /graph/path, GET /graph/centrality
   - GET /regimes & GET /api/regimes
   - GET /regimes/probabilities, GET /regimes/transition-matrix, GET /regimes/drivers
"""

import pytest
import numpy as np
from datetime import datetime
from fastapi.testclient import TestClient

from agni.regimes.detector import StatisticalRegimeEngine, statistical_regime_engine
from agni.graph.topology import DynamicRiskGraph, dynamic_risk_graph
from backend.app.schemas.canonical import RegimeState
from backend.app.main import app

client = TestClient(app)


# =====================================================================
# 1. REGIME DETECTION ENGINE TESTS
# =====================================================================

def test_regime_engine_fit_and_states():
    """Verify statistical regime model fits 4 states strictly sorted by volatility stress."""
    np.random.seed(42)
    # Generate multi-regime synthetic data: Calm -> Elevated -> Stressed -> Crisis
    calm = np.random.normal(12.0, 2.0, (40, 2))
    elevated = np.random.normal(24.0, 3.5, (40, 2))
    stressed = np.random.normal(42.0, 5.0, (30, 2))
    crisis = np.random.normal(68.0, 8.0, (20, 2))
    X = np.vstack([calm, elevated, stressed, crisis])

    engine = StatisticalRegimeEngine(k_regimes=4, max_iter=25)
    engine.fit(X, feature_names=["realized_volatility", "vix_index"])

    assert engine.is_fitted is True
    assert engine.means.shape == (4, 2)
    assert engine.variances.shape == (4, 2)

    # Monotonic stress ordering: CALM < ELEVATED < STRESSED < CRISIS
    primary_means = engine.means[:, 0]
    assert primary_means[0] < primary_means[1] < primary_means[2] < primary_means[3]


def test_regime_inference_probabilities_and_durations():
    """Verify inference yields posterior probabilities, 4x4 transition matrix, and durations."""
    np.random.seed(101)
    X = np.random.exponential(scale=20.0, size=(100, 3)) + 10.0

    engine = StatisticalRegimeEngine(k_regimes=4, max_iter=20)
    engine.fit(X, feature_names=["realized_vol", "vix", "correlation"])
    state = engine.infer_regime(X)

    assert isinstance(state, RegimeState)
    assert state.current_regime in ["CALM", "ELEVATED", "STRESSED", "CRISIS"]
    assert 0.0 <= state.probability <= 1.0

    # Probabilities sum to 1.0
    prob_sum = sum(state.regime_probabilities.values())
    assert pytest.approx(prob_sum, abs=1e-3) == 1.0
    for r in ["CALM", "ELEVATED", "STRESSED", "CRISIS"]:
        assert r in state.regime_probabilities
        assert 0.0 <= state.regime_probabilities[r] <= 1.0

    # 4x4 Transition Probability Matrix: each row must sum to 1.0
    trans = state.transition_probabilities
    assert len(trans) == 4
    for from_r in ["CALM", "ELEVATED", "STRESSED", "CRISIS"]:
        row_sum = sum(trans[from_r].values())
        assert pytest.approx(row_sum, abs=1e-3) == 1.0
        for to_r in ["CALM", "ELEVATED", "STRESSED", "CRISIS"]:
            assert 0.0 <= trans[from_r][to_r] <= 1.0

    # Expected Durations: E[D_i] = 1 / (1 - P_ii)
    durations = state.expected_durations
    assert len(durations) == 4
    for r in ["CALM", "ELEVATED", "STRESSED", "CRISIS"]:
        p_stay = trans[r][r]
        expected_calc = min(250.0, 1.0 / max(1e-4, (1.0 - p_stay)))
        assert pytest.approx(durations[r], abs=0.2) == expected_calc
        assert durations[r] >= 1.0

    # Feature Contributions sum to 1.0
    contributions = state.feature_contributions
    assert len(contributions) == 3
    contrib_sum = sum(contributions.values())
    assert pytest.approx(contrib_sum, abs=1e-3) == 1.0
    for f in contributions.values():
        assert 0.0 <= f <= 1.0


def test_regime_fit_from_market_store():
    """Verify live market store regime estimation."""
    state = statistical_regime_engine.fit_from_market_store()
    assert isinstance(state, RegimeState)
    assert state.model_type == "hidden_markov_model"
    assert len(state.features_used) == 4
    assert state.current_regime in ["CALM", "ELEVATED", "STRESSED", "CRISIS"]


# =====================================================================
# 2. DYNAMIC RISK GRAPH ENGINE TESTS
# =====================================================================

def test_graph_node_types_present():
    """Verify nodes exist for Country, Commodity, Financial Asset, Trade Route, Event."""
    g = dynamic_risk_graph.graph
    node_types = {attrs.get("node_type") for _, attrs in g.nodes(data=True)}

    assert "country" in node_types
    assert "commodity" in node_types
    assert "financial_asset" in node_types
    assert "trade_route" in node_types
    assert "event" in node_types


def test_graph_edge_taxonomy_coverage():
    """
    Verify all 6 required edge types exist:
    - country → commodity
    - country → asset
    - country → route
    - commodity → asset
    - route → commodity
    - event → country
    """
    g = dynamic_risk_graph.graph
    edge_types_found = set()

    for u, v, _ in g.edges(data=True):
        u_type = g.nodes[u].get("node_type")
        v_type = g.nodes[v].get("node_type")
        edge_types_found.add(f"{u_type}->{v_type}")

    assert "country->commodity" in edge_types_found
    assert "country->financial_asset" in edge_types_found
    assert "country->trade_route" in edge_types_found
    assert "commodity->financial_asset" in edge_types_found
    assert "trade_route->commodity" in edge_types_found
    assert "event->country" in edge_types_found


def test_graph_edge_attributes_completeness():
    """Verify every edge contains exposure, correlation, importance, confidence, and timestamp."""
    g = dynamic_risk_graph.graph
    required_attrs = {"exposure", "correlation", "importance", "confidence", "timestamp"}

    assert g.number_of_edges() >= 15

    for u, v, attrs in g.edges(data=True):
        for attr in required_attrs:
            assert attr in attrs, f"Edge {u} -> {v} missing mandatory attribute '{attr}'"

        assert 0.0 <= attrs["exposure"] <= 1.0
        assert -1.0 <= attrs["correlation"] <= 1.0
        assert 0.0 <= attrs["importance"] <= 1.0
        assert 0.0 <= attrs["confidence"] <= 1.0

        # Check ISO timestamp format
        datetime.fromisoformat(attrs["timestamp"].replace("Z", "+00:00"))


def test_graph_analytics_and_path_tracing():
    """Verify NetworkX PageRank centrality and shortest path transmission chain."""
    centrality = dynamic_risk_graph.compute_centrality()
    assert len(centrality) == dynamic_risk_graph.graph.number_of_nodes()

    # Trace transmission: event -> country -> route -> commodity -> asset
    path = dynamic_risk_graph.trace_transmission_path("event:strait-of-hormuz", "asset:US10Y")
    assert len(path) >= 4
    assert path[0] == "event:strait-of-hormuz"
    assert path[-1] == "asset:US10Y"
    assert "commodity:BRENT_CRUDE" in path


def test_graph_canonical_cascades():
    """Verify canonical cascades for interactive UI visualization."""
    cascades = dynamic_risk_graph.get_canonical_cascades()
    assert len(cascades) >= 4
    for c in cascades:
        assert "cascade_id" in c
        assert "sequence" in c
        assert len(c["sequence"]) >= 3


# =====================================================================
# 3. FASTAPI API ENDPOINTS TESTS
# =====================================================================

def test_api_get_graph_root_and_prefix():
    """Verify GET /graph and GET /api/graph return identical full graph schema."""
    res_api = client.get("/api/graph")
    assert res_api.status_code == 200
    data_api = res_api.json()
    assert "nodes" in data_api
    assert "edges" in data_api
    assert "canonical_cascades" in data_api

    res_root = client.get("/graph")
    assert res_root.status_code == 200
    data_root = res_root.json()
    assert len(data_root["nodes"]) == len(data_api["nodes"])
    assert len(data_root["edges"]) == len(data_api["edges"])


def test_api_get_graph_nodes_and_edges():
    """Verify GET /api/graph/nodes and GET /api/graph/edges with filters."""
    res_nodes = client.get("/api/graph/nodes?node_type=commodity")
    assert res_nodes.status_code == 200
    commodities = res_nodes.json()
    assert len(commodities) >= 5
    for c in commodities:
        assert c["type"] == "commodity"

    res_edges = client.get("/api/graph/edges?source_type=country")
    assert res_edges.status_code == 200
    country_edges = res_edges.json()
    assert len(country_edges) >= 5
    for e in country_edges:
        assert e["source"].startswith("country:")
        assert "exposure" in e
        assert "correlation" in e
        assert "importance" in e
        assert "confidence" in e


def test_api_get_graph_path_and_centrality():
    """Verify GET /api/graph/path and GET /api/graph/centrality."""
    res_path = client.get("/api/graph/path?source=event:strait-of-hormuz&target=asset:US10Y")
    assert res_path.status_code == 200
    data = res_path.json()
    assert data["path_length"] >= 3
    assert len(data["transmission_steps"]) == data["path_length"]

    res_cent = client.get("/api/graph/centrality")
    assert res_cent.status_code == 200
    scores = res_cent.json()
    assert "country:USA" in scores
    assert "pagerank" in scores["country:USA"]


def test_api_get_regimes_root_and_prefix():
    """Verify GET /regimes and GET /api/regimes return fitted RegimeState."""
    res_api = client.get("/api/regimes")
    assert res_api.status_code == 200
    state = res_api.json()
    assert state["current_regime"] in ["CALM", "ELEVATED", "STRESSED", "CRISIS"]
    assert "regime_probabilities" in state
    assert "transition_probabilities" in state
    assert "expected_durations" in state
    assert "feature_contributions" in state

    res_root = client.get("/regimes")
    assert res_root.status_code == 200


def test_api_get_regimes_sub_endpoints():
    """Verify /regimes/probabilities, /regimes/transition-matrix, /regimes/drivers."""
    p_res = client.get("/api/regimes/probabilities")
    assert p_res.status_code == 200
    assert "regime_probabilities" in p_res.json()

    tm_res = client.get("/api/regimes/transition-matrix")
    assert tm_res.status_code == 200
    tm_data = tm_res.json()
    assert "transition_probabilities" in tm_data
    assert "expected_durations_days" in tm_data

    drv_res = client.get("/api/regimes/drivers")
    assert drv_res.status_code == 200
    drv_data = drv_res.json()
    assert "feature_contributions" in drv_data
