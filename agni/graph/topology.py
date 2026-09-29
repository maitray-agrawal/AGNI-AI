"""
AGNI Dynamic Risk & Trade Topology Graph Engine (NetworkX)
==========================================================
Interpretable multi-layer directed knowledge graph modeling geopolitical
and macroeconomic transmission:
  - Nodes: Country, Commodity, Financial Asset, Trade Route, Event
  - Edges:
      country → commodity
      country → asset
      country → route
      commodity → asset
      route → commodity
      event → country

Edge attributes:
  - exposure: float (direct trade dependency, sovereign beta, or throughput share)
  - correlation: float (empirical market/economic co-movement [-1.0, 1.0])
  - importance: float (topological centrality / systemic criticality [0.0, 1.0])
  - confidence: float (epistemic certainty [0.0, 1.0])
  - timestamp: ISO-8601 observation/calculation timestamp
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timezone
import networkx as nx

from backend.app.schemas.canonical import Country, Commodity, FinancialAsset, TradeRoute, Event


class DynamicRiskGraph:
    """NetworkX-based dynamic risk graph modeling geopolitical transmission paths."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.created_at = datetime.now(timezone.utc).isoformat()
        self._build_canonical_topology()

    def _build_canonical_topology(self):
        """Constructs canonical multi-layer directed risk graph with explicit causal edges."""
        self.graph.clear()
        now = datetime.now(timezone.utc).isoformat()

        # ── 1. NODES ──────────────────────────────────────────────────────────

        # Countries
        COUNTRIES = [
            {"id": "country:IRN", "label": "Islamic Republic of Iran", "code": "IRN", "region": "Middle East", "risk_index": 165.0, "coords": [53.6880, 32.4279]},
            {"id": "country:TWN", "label": "Taiwan (ROC)", "code": "TWN", "region": "East Asia", "risk_index": 155.0, "coords": [120.9605, 23.6978]},
            {"id": "country:EGY", "label": "Arab Republic of Egypt", "code": "EGY", "region": "North Africa / MENA", "risk_index": 138.0, "coords": [30.8025, 26.8206]},
            {"id": "country:CHN", "label": "People's Republic of China", "code": "CHN", "region": "East Asia", "risk_index": 128.0, "coords": [104.1954, 35.8617]},
            {"id": "country:USA", "label": "United States of America", "code": "USA", "region": "North America", "risk_index": 95.0, "coords": [-95.7129, 37.0902]},
            {"id": "country:PAN", "label": "Republic of Panama", "code": "PAN", "region": "Central America", "risk_index": 110.0, "coords": [-80.7821, 8.5380]},
            {"id": "country:SGP", "label": "Republic of Singapore", "code": "SGP", "region": "Southeast Asia", "risk_index": 82.0, "coords": [103.8198, 1.3521]},
            {"id": "country:UKR", "label": "Ukraine", "code": "UKR", "region": "Eastern Europe", "risk_index": 180.0, "coords": [31.1656, 48.3794]},
        ]
        for c in COUNTRIES:
            self.graph.add_node(
                c["id"],
                node_type="country",
                label=c["label"],
                country_code=c["code"],
                region=c["region"],
                risk_index=c["risk_index"],
                coordinates=c["coords"],
                epistemic_state="OBSERVED",
            )

        # Commodities
        COMMODITIES = [
            {"id": "commodity:BRENT_CRUDE", "label": "Brent Crude Oil", "category": "Energy", "unit": "USD/bbl"},
            {"id": "commodity:NATURAL_GAS_TTF", "label": "Dutch TTF Natural Gas", "category": "Energy", "unit": "EUR/MWh"},
            {"id": "commodity:CONTAINER_SCFI", "label": "Container Freight (SCFI)", "category": "Logistics", "unit": "USD/TEU"},
            {"id": "commodity:COPPER", "label": "LME Grade A Copper", "category": "Industrial Metals", "unit": "USD/tonne"},
            {"id": "commodity:WHEAT", "label": "CBOT Milling Wheat", "category": "Agriculture", "unit": "USD/bu"},
        ]
        for comm in COMMODITIES:
            self.graph.add_node(
                comm["id"],
                node_type="commodity",
                label=comm["label"],
                category=comm["category"],
                benchmark_unit=comm["unit"],
                epistemic_state="OBSERVED",
            )

        # Financial Assets
        ASSETS = [
            {"id": "asset:SPX", "label": "S&P 500 Equity Index", "asset_class": "equity_index", "value": 5050.0},
            {"id": "asset:US10Y", "label": "US 10-Year Treasury Yield", "asset_class": "sovereign_bond", "value": 4.25},
            {"id": "asset:DXY", "label": "US Dollar Index", "asset_class": "fx_rate", "value": 103.4},
            {"id": "asset:VIX", "label": "CBOE Volatility Index", "asset_class": "volatility", "value": 16.8},
        ]
        for a in ASSETS:
            self.graph.add_node(
                a["id"],
                node_type="financial_asset",
                label=a["label"],
                asset_class=a["asset_class"],
                current_value=a["value"],
                epistemic_state="OBSERVED",
            )

        # Trade Routes
        TRADE_ROUTES = [
            {"id": "route:asia-europe-suez", "label": "Asia-Europe Container Route via Suez", "origin": "East Asia", "dest": "North Europe", "delay_days": 10.5},
            {"id": "route:gulf-asia-tanker", "label": "Persian Gulf to East Asia Tanker Route", "origin": "Middle East", "dest": "East Asia", "delay_days": 2.0},
            {"id": "route:transpacific-us-east", "label": "Transpacific to US East Coast via Panama", "origin": "East Asia", "dest": "US East Coast", "delay_days": 6.0},
            {"id": "route:black-sea-grain", "label": "Black Sea Agricultural Maritime Corridor", "origin": "Black Sea", "dest": "MENA / Global", "delay_days": 14.0},
        ]
        for r in TRADE_ROUTES:
            self.graph.add_node(
                r["id"],
                node_type="trade_route",
                label=r["label"],
                origin_region=r["origin"],
                destination_region=r["dest"],
                current_delay_days=r["delay_days"],
                epistemic_state="OBSERVED",
            )

        # Events
        EVENTS = [
            {"id": "event:strait-of-hormuz", "label": "Hormuz Tanker Seizure & Mine Hazard", "severity": "critical", "country": "IRN"},
            {"id": "event:taiwan-strait", "label": "Taiwan Strait Joint Air-Maritime Patrol Blockade", "severity": "high", "country": "TWN"},
            {"id": "event:red-sea-bab-el-mandeb", "label": "Southern Red Sea ASBM Anti-Ship Salvoes", "severity": "critical", "country": "EGY"},
            {"id": "event:black-sea-danube-strike", "label": "Danube Delta Grain Silo Missile Strikes", "severity": "high", "country": "UKR"},
        ]
        for e in EVENTS:
            self.graph.add_node(
                e["id"],
                node_type="event",
                label=e["label"],
                severity=e["severity"],
                primary_country=e["country"],
                epistemic_state="OBSERVED",
            )

        # ── 2. EDGES (STRICTLY REQUIRED TAXONOMY) ─────────────────────────────

        # A. country → commodity
        self.add_edge_with_attrs(
            source="country:IRN",
            target="commodity:BRENT_CRUDE",
            relationship="sovereign_producer",
            exposure=0.78,
            correlation=0.64,
            importance=0.88,
            confidence=0.96,
            explanation="Iran produces ~3.2M bpd of crude and controls coastal batteries overlooking physical export channels.",
        )
        self.add_edge_with_attrs(
            source="country:USA",
            target="commodity:NATURAL_GAS_TTF",
            relationship="lng_swing_supplier",
            exposure=0.62,
            correlation=0.55,
            importance=0.75,
            confidence=0.92,
            explanation="US Gulf LNG export terminals represent Europe's critical marginal gas supply replacement.",
        )
        self.add_edge_with_attrs(
            source="country:TWN",
            target="commodity:COPPER",
            relationship="semiconductor_demand_sink",
            exposure=0.58,
            correlation=0.48,
            importance=0.72,
            confidence=0.90,
            explanation="Taiwan consumes high-purity refined copper cathodes for advanced IC packaging and fab manufacturing.",
        )
        self.add_edge_with_attrs(
            source="country:UKR",
            target="commodity:WHEAT",
            relationship="agricultural_breadbasket",
            exposure=0.84,
            correlation=0.72,
            importance=0.85,
            confidence=0.95,
            explanation="Ukraine supplies 10% of global seaborne wheat, predominantly feeding MENA import tenders.",
        )
        self.add_edge_with_attrs(
            source="country:CHN",
            target="commodity:CONTAINER_SCFI",
            relationship="manufacturing_export_origin",
            exposure=0.92,
            correlation=0.81,
            importance=0.94,
            confidence=0.98,
            explanation="China generates over 45% of global containerized outbound TEU departures.",
        )

        # B. country → asset
        self.add_edge_with_attrs(
            source="country:USA",
            target="asset:SPX",
            relationship="sovereign_equity_jurisdiction",
            exposure=0.95,
            correlation=0.88,
            importance=0.96,
            confidence=0.99,
            explanation="US fiscal and macroeconomic policies directly anchor domestic equity valuations.",
        )
        self.add_edge_with_attrs(
            source="country:USA",
            target="asset:US10Y",
            relationship="sovereign_debt_benchmark",
            exposure=0.98,
            correlation=0.91,
            importance=0.99,
            confidence=0.99,
            explanation="Federal borrowing and inflation terminal rate expectations determine the 10-year Treasury yield.",
        )
        self.add_edge_with_attrs(
            source="country:TWN",
            target="asset:SPX",
            relationship="tech_supply_chain_contagion",
            exposure=0.76,
            correlation=-0.62,
            importance=0.89,
            confidence=0.93,
            explanation="Disruption to Taiwan's semiconductor foundries halts 60% of US mega-cap tech hardware manufacturing.",
        )
        self.add_edge_with_attrs(
            source="country:IRN",
            target="asset:VIX",
            relationship="geopolitical_volatility_spark",
            exposure=0.82,
            correlation=0.68,
            importance=0.84,
            confidence=0.94,
            explanation="Escalation in the Persian Gulf triggers immediate options hedging and volatility index spikes.",
        )

        # C. country → route
        self.add_edge_with_attrs(
            source="country:IRN",
            target="route:gulf-asia-tanker",
            relationship="territorial_flanking",
            exposure=0.94,
            correlation=0.78,
            importance=0.96,
            confidence=0.98,
            explanation="Iranian naval and IRGC fast boats directly overlook the 21-nautical-mile navigable Hormuz corridor.",
        )
        self.add_edge_with_attrs(
            source="country:EGY",
            target="route:asia-europe-suez",
            relationship="sovereign_transit_corridor",
            exposure=0.90,
            correlation=0.74,
            importance=0.92,
            confidence=0.97,
            explanation="Egypt exercises sovereign control and collects transit tolls over the Suez Canal artery.",
        )
        self.add_edge_with_attrs(
            source="country:PAN",
            target="route:transpacific-us-east",
            relationship="canal_lock_administrator",
            exposure=0.88,
            correlation=0.70,
            importance=0.89,
            confidence=0.96,
            explanation="Panama Canal Authority draft restrictions and booking slot auctions dictate vessel transit queues.",
        )
        self.add_edge_with_attrs(
            source="country:UKR",
            target="route:black-sea-grain",
            relationship="coastal_grain_terminal",
            exposure=0.86,
            correlation=0.75,
            importance=0.88,
            confidence=0.95,
            explanation="Ukrainian maritime ports (Odesa, Chornomorsk, Yuzhny) originate Black Sea grain voyages.",
        )

        # D. commodity → asset
        self.add_edge_with_attrs(
            source="commodity:BRENT_CRUDE",
            target="asset:US10Y",
            relationship="inflation_expectation_transmission",
            exposure=0.74,
            correlation=0.57,
            importance=0.85,
            confidence=0.92,
            explanation="Energy price shocks elevate short-term break-evens and force central banks to sustain restrictive policy rates.",
        )
        self.add_edge_with_attrs(
            source="commodity:BRENT_CRUDE",
            target="asset:VIX",
            relationship="tail_risk_volatility_spillover",
            exposure=0.68,
            correlation=0.42,
            importance=0.80,
            confidence=0.91,
            explanation="Crude oil price spikes over $100 trigger asymmetric market crash hedges and volatility spikes.",
        )
        self.add_edge_with_attrs(
            source="commodity:CONTAINER_SCFI",
            target="asset:SPX",
            relationship="margin_compression_transmission",
            exposure=0.65,
            correlation=-0.79,
            importance=0.83,
            confidence=0.93,
            explanation="Multiplying container freight rates compresses gross retail margins and postpones holiday replenishment.",
        )
        self.add_edge_with_attrs(
            source="commodity:NATURAL_GAS_TTF",
            target="asset:DXY",
            relationship="terms_of_trade_shock",
            exposure=0.58,
            correlation=0.45,
            importance=0.74,
            confidence=0.89,
            explanation="European natural gas spikes deteriorate EU trade balance, driving capital flows into the US Dollar.",
        )

        # E. route → commodity
        self.add_edge_with_attrs(
            source="route:gulf-asia-tanker",
            target="commodity:BRENT_CRUDE",
            relationship="physical_energy_chokepoint",
            exposure=0.89,
            correlation=0.76,
            importance=0.95,
            confidence=0.97,
            explanation="Carries 21 million barrels/day of petroleum liquids; closure creates instantaneous physical crude shortages.",
        )
        self.add_edge_with_attrs(
            source="route:asia-europe-suez",
            target="commodity:CONTAINER_SCFI",
            relationship="rerouting_freight_spike",
            exposure=0.86,
            correlation=0.83,
            importance=0.93,
            confidence=0.98,
            explanation="Diversion around Cape of Good Hope adds 3,500 nautical miles, consuming vessel capacity and inflating freight rates.",
        )
        self.add_edge_with_attrs(
            source="route:asia-europe-suez",
            target="commodity:NATURAL_GAS_TTF",
            relationship="lng_carrier_diversion",
            exposure=0.72,
            correlation=0.61,
            importance=0.82,
            confidence=0.92,
            explanation="Qatari LNG carriers rerouting away from Suez prolong voyage times to European regasification terminals.",
        )
        self.add_edge_with_attrs(
            source="route:black-sea-grain",
            target="commodity:WHEAT",
            relationship="agricultural_logistics_severance",
            exposure=0.81,
            correlation=0.75,
            importance=0.87,
            confidence=0.95,
            explanation="Blockade or drone interdiction of Black Sea cargo vessels paralyzes Ukrainian wheat exports.",
        )

        # F. event → country
        self.add_edge_with_attrs(
            source="event:strait-of-hormuz",
            target="country:IRN",
            relationship="geopolitical_theater_origin",
            exposure=0.92,
            correlation=0.85,
            importance=0.94,
            confidence=0.98,
            explanation="Naval encounters and boarding actions centered along Iran's southern maritime perimeter.",
        )
        self.add_edge_with_attrs(
            source="event:taiwan-strait",
            target="country:TWN",
            relationship="sovereign_coercion_target",
            exposure=0.96,
            correlation=0.89,
            importance=0.97,
            confidence=0.99,
            explanation="Encirclement drills and maritime quarantine zones targeting Taiwanese sovereign airspace and sea lanes.",
        )
        self.add_edge_with_attrs(
            source="event:red-sea-bab-el-mandeb",
            target="country:EGY",
            relationship="downstream_canal_revenue_choke",
            exposure=0.88,
            correlation=0.79,
            importance=0.91,
            confidence=0.96,
            explanation="Houthi missile attacks off Bab-el-Mandeb cut Suez Canal vessel transits by over 50%, impacting Egypt.",
        )
        self.add_edge_with_attrs(
            source="event:black-sea-danube-strike",
            target="country:UKR",
            relationship="critical_infrastructure_strike",
            exposure=0.90,
            correlation=0.82,
            importance=0.92,
            confidence=0.97,
            explanation="Precision munition strikes against Reni and Izmail river grain elevators on Ukrainian territory.",
        )

    def add_edge_with_attrs(
        self,
        source: str,
        target: str,
        relationship: str,
        exposure: float,
        correlation: float,
        importance: float,
        confidence: float,
        explanation: str = "",
        timestamp: Optional[str] = None,
    ):
        """Adds a directed edge with all mandatory attributes."""
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        # Ensure nodes exist
        if not self.graph.has_node(source):
            self.graph.add_node(source, label=source, node_type=source.split(":")[0])
        if not self.graph.has_node(target):
            self.graph.add_node(target, label=target, node_type=target.split(":")[0])

        self.graph.add_edge(
            source,
            target,
            relationship=relationship,
            exposure=round(float(exposure), 3),
            correlation=round(float(correlation), 3),
            importance=round(float(importance), 3),
            confidence=round(float(confidence), 3),
            weight=round(float(exposure * importance), 3),
            timestamp=ts,
            explanation=explanation,
            epistemic_state="DERIVED" if confidence < 0.95 else "OBSERVED",
        )

    # ── Interpretability & Topological Algorithms ────────────────────────────

    def compute_centrality(self) -> Dict[str, Dict[str, float]]:
        """Computes PageRank and Betweenness Centrality for all nodes."""
        pagerank = nx.pagerank(self.graph, weight="weight")
        betweenness = nx.betweenness_centrality(self.graph, weight="weight")

        res: Dict[str, Dict[str, float]] = {}
        for node in self.graph.nodes:
            res[node] = {
                "pagerank": round(float(pagerank.get(node, 0.0)), 4),
                "betweenness": round(float(betweenness.get(node, 0.0)), 4),
            }
        return res

    def trace_transmission_path(self, source: str, target: str) -> List[str]:
        """Calculates shortest causal transmission chain through the topology."""
        if not (self.graph.has_node(source) and self.graph.has_node(target)):
            return []
        try:
            path = nx.shortest_path(self.graph, source=source, target=target)
            return path
        except nx.NetworkXNoPath:
            return []

    def get_canonical_cascades(self) -> List[Dict[str, Any]]:
        """Generates standard end-to-end multi-step cascades for UI display."""
        return [
            {
                "cascade_id": "hormuz_energy_shock",
                "name": "Hormuz Naval Interdiction → Brent Crude → US Yields",
                "sequence": [
                    "event:strait-of-hormuz",
                    "country:IRN",
                    "route:gulf-asia-tanker",
                    "commodity:BRENT_CRUDE",
                    "asset:US10Y",
                ],
                "description": "Naval interdiction in the Persian Gulf disrupts seaborne crude, spiking oil prices and driving 10-year Treasury yields upward via inflation expectations.",
            },
            {
                "cascade_id": "red_sea_container_shock",
                "name": "Red Sea ASBM Strike → Suez Diversion → SCFI Freight → S&P 500",
                "sequence": [
                    "event:red-sea-bab-el-mandeb",
                    "country:EGY",
                    "route:asia-europe-suez",
                    "commodity:CONTAINER_SCFI",
                    "asset:SPX",
                ],
                "description": "Southern Red Sea missile strikes throttle Suez transits, forcing Cape of Good Hope rerouting, spiking container rates, and compressing equity profit margins.",
            },
            {
                "cascade_id": "taiwan_semiconductor_shock",
                "name": "Taiwan Strait Blockade → Tech Supply Chain → S&P 500",
                "sequence": [
                    "event:taiwan-strait",
                    "country:TWN",
                    "commodity:COPPER",
                    "asset:SPX",
                ],
                "description": "Maritime blockade around Taiwan disrupts semiconductor logistics, choking electronic manufacturing and causing broad equity market drawdown.",
            },
            {
                "cascade_id": "black_sea_grain_shock",
                "name": "Danube Silo Strike → Black Sea Route → Wheat Surge",
                "sequence": [
                    "event:black-sea-danube-strike",
                    "country:UKR",
                    "route:black-sea-grain",
                    "commodity:WHEAT",
                ],
                "description": "Missile attacks on Ukrainian grain export elevators paralyze Black Sea bulk shipping, driving CBOT wheat futures into backwardation.",
            },
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the complete graph into frontend-compatible format with full edge attributes."""
        centrality = self.compute_centrality()

        nodes_list = []
        for n, attrs in self.graph.nodes(data=True):
            node_data = {
                "id": n,
                "label": attrs.get("label", n),
                "type": attrs.get("node_type", "entity"),
                "region": attrs.get("region"),
                "risk_index": attrs.get("risk_index"),
                "epistemic_state": attrs.get("epistemic_state", "OBSERVED"),
                "coordinates": attrs.get("coordinates"),
                "pagerank": centrality.get(n, {}).get("pagerank", 0.0),
                "betweenness": centrality.get(n, {}).get("betweenness", 0.0),
            }
            # Append optional entity details
            for k in ["category", "benchmark_unit", "asset_class", "current_value", "severity"]:
                if k in attrs:
                    node_data[k] = attrs[k]
            nodes_list.append(node_data)

        edges_list = []
        for u, v, attrs in self.graph.edges(data=True):
            edges_list.append({
                "source": u,
                "target": v,
                "relationship": attrs.get("relationship", "transmits_to"),
                "exposure": attrs.get("exposure", 0.75),
                "correlation": attrs.get("correlation", 0.50),
                "importance": attrs.get("importance", 0.75),
                "confidence": attrs.get("confidence", 0.90),
                "weight": attrs.get("weight", 0.75),
                "timestamp": attrs.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "explanation": attrs.get("explanation", ""),
                "epistemic_state": attrs.get("epistemic_state", "OBSERVED"),
            })

        return {
            "graph_id": "dynamic-risk-trade-topology",
            "nodes_count": len(nodes_list),
            "edges_count": len(edges_list),
            "created_at": self.created_at,
            "nodes": nodes_list,
            "edges": edges_list,
            "canonical_cascades": self.get_canonical_cascades(),
        }


# Global singleton instance
dynamic_risk_graph = DynamicRiskGraph()
