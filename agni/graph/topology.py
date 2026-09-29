"""
AGNI Dynamic Risk & Trade Topology Graph (NetworkX)
===================================================
Constructs dynamic directed graphs modeling geopolitical transmission:
Country → Chokepoint → Commodity → Financial Asset → Macro Vulnerability
"""

import networkx as nx
from typing import Dict, List, Any, Optional
from backend.app.schemas.canonical import Country, Chokepoint, Commodity, FinancialAsset


class GeopoliticalRiskGraph:
    """Network topology modeling systemic trade dependencies and shock propagation."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_entities(
        self,
        countries: List[Country],
        chokepoints: List[Chokepoint],
        commodities: List[Commodity],
        assets: List[FinancialAsset],
    ):
        """Constructs canonical multi-layer directed risk graph."""
        self.graph.clear()

        for c in countries:
            self.graph.add_node(
                f"country:{c.country_code}",
                node_type="country",
                label=c.name,
                region=c.region,
                risk_index=c.geopolitical_risk_index,
            )

        for cp in chokepoints:
            self.graph.add_node(
                f"chokepoint:{cp.chokepoint_id}",
                node_type="chokepoint",
                label=cp.name,
                trade_share=cp.global_trade_share_pct,
                status=cp.current_status,
            )

        for comm in commodities:
            self.graph.add_node(
                f"commodity:{comm.commodity_id}",
                node_type="commodity",
                label=comm.name,
                category=comm.category,
            )
            for cp_id in comm.primary_chokepoint_dependencies:
                cp_node = f"chokepoint:{cp_id}"
                if self.graph.has_node(cp_node):
                    self.graph.add_edge(
                        cp_node,
                        f"commodity:{comm.commodity_id}",
                        relationship="traverses",
                        weight=0.85,
                        elasticity=1.45,
                    )

        for a in assets:
            self.graph.add_node(
                f"asset:{a.asset_id}",
                node_type="financial_asset",
                label=a.name,
                asset_class=a.asset_class,
                value=a.current_value,
            )

        # Transmission edges: Commodities to Assets
        self.graph.add_edge("commodity:BRENT_CRUDE", "asset:BRENT", relationship="benchmarks", weight=1.0, elasticity=1.0)
        self.graph.add_edge("commodity:BRENT_CRUDE", "asset:VIX", relationship="volatility_contagion", weight=0.65, elasticity=0.85)
        self.graph.add_edge("commodity:CONTAINER_SCFI", "asset:SPX", relationship="margin_compression", weight=-0.45, elasticity=-0.35)
        self.graph.add_edge("commodity:BRENT_CRUDE", "asset:US10Y", relationship="inflation_expectation", weight=0.55, elasticity=0.25)

    def trace_shock_path(self, source_chokepoint_id: str, target_asset_id: str) -> List[str]:
        """Calculates shortest causal transmission chain through the topology."""
        src = f"chokepoint:{source_chokepoint_id}"
        dst = f"asset:{target_asset_id}"

        if not (self.graph.has_node(src) and self.graph.has_node(dst)):
            return []

        try:
            path = nx.shortest_path(self.graph, source=src, target=dst)
            return [self.graph.nodes[node].get("label", node) for node in path]
        except nx.NetworkXNoPath:
            return []

    def compute_chokepoint_centrality(self) -> Dict[str, float]:
        """Calculates PageRank / Betweenness Centrality for all maritime chokepoints."""
        betweenness = nx.betweenness_centrality(self.graph)
        result = {}
        for node, score in betweenness.items():
            if self.graph.nodes[node].get("node_type") == "chokepoint":
                label = self.graph.nodes[node].get("label", node)
                result[label] = round(float(score), 4)
        return result


risk_graph = GeopoliticalRiskGraph()
