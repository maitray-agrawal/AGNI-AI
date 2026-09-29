"""
AGNI Dynamic Risk & Trade Topology Graph API
============================================
Exposes relational node-edge topology mapping:
Country → Chokepoint → Commodity → Financial Asset → Macro Shocks
"""

from fastapi import APIRouter
from typing import List, Dict, Any
from backend.app.repositories.intel_store import intel_store

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get("")
async def get_intelligence_graph() -> Dict[str, Any]:
    """Retrieve full dynamic knowledge and trade transmission graph nodes and edges."""
    countries = intel_store.list_countries()
    chokepoints = intel_store.list_chokepoints()
    commodities = intel_store.list_commodities()
    assets = intel_store.list_assets()
    events = intel_store.list_events()

    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Country Nodes
    for c in countries:
        nodes.append({
            "id": f"country-{c.country_code.lower()}",
            "label": c.name,
            "type": "country",
            "region": c.region,
            "risk_index": c.geopolitical_risk_index,
            "coordinates": [c.longitude, c.latitude],
        })

    # Chokepoint Nodes
    for cp in chokepoints:
        nodes.append({
            "id": f"cp-{cp.chokepoint_id}",
            "label": cp.name,
            "type": "chokepoint",
            "trade_share_pct": cp.global_trade_share_pct,
            "status": cp.current_status,
            "coordinates": [cp.longitude, cp.latitude],
        })

    # Commodity Nodes
    for comm in commodities:
        nodes.append({
            "id": f"comm-{comm.commodity_id.lower()}",
            "label": comm.name,
            "type": "commodity",
            "category": comm.category,
        })
        # Link Chokepoints to Commodity
        for cp_id in comm.primary_chokepoint_dependencies:
            edges.append({
                "source": f"cp-{cp_id}",
                "target": f"comm-{comm.commodity_id.lower()}",
                "relationship": "traverses",
                "weight": 0.85,
                "confidence": 0.95,
            })

    # Financial Asset Nodes
    for a in assets:
        nodes.append({
            "id": f"asset-{a.asset_id.lower()}",
            "label": a.name,
            "type": "financial_asset",
            "asset_class": a.asset_class,
            "value": a.current_value,
            "change_pct": a.daily_change_pct,
        })

    # Macro Economic Nodes
    macro_nodes = [
        {"id": "macro-inflation", "label": "Headline Inflation (CPI)", "type": "macro_indicator", "epistemic_state": "DERIVED"},
        {"id": "macro-bond_yields", "label": "US 10Y Sovereign Yields", "type": "sovereign_rate", "epistemic_state": "OBSERVED"},
        {"id": "macro-equity_volatility", "label": "Equity Volatility (VIX)", "type": "volatility_index", "epistemic_state": "MODELLED"},
    ]
    nodes.extend(macro_nodes)

    # Country -> Chokepoint Edges
    edges.append({
        "source": "country-irn",
        "target": "cp-strait-of-hormuz",
        "relationship": "sovereign_projection",
        "weight": 0.95,
        "confidence": 0.98,
        "explanation": "Naval and missile projection directly flanking the 21-nautical-mile navigable maritime corridor.",
        "epistemic_state": "OBSERVED",
    })
    edges.append({
        "source": "country-twn",
        "target": "cp-taiwan-strait",
        "relationship": "territorial_chokepoint",
        "weight": 0.92,
        "confidence": 0.97,
        "explanation": "Critical maritime chokepoint transited by 48% of global container vessel tonnage.",
        "epistemic_state": "OBSERVED",
    })

    # Chokepoint -> Commodity Edges (with explanation)
    edges.append({
        "source": "cp-strait-of-hormuz",
        "target": "comm-brent_crude",
        "relationship": "oil_supply_artery",
        "weight": 0.90,
        "confidence": 0.96,
        "explanation": "Transits 21 million barrels/day of petroleum liquids; disruption immediately constrains physical prompt crude.",
        "epistemic_state": "DERIVED",
    })
    edges.append({
        "source": "cp-bab-el-mandeb",
        "target": "comm-container_scfi",
        "relationship": "freight_bottleneck",
        "weight": 0.88,
        "confidence": 0.94,
        "explanation": "Corridor disruption forces Cape of Good Hope rerouting, adding 10-14 transit days and spiking bunker fuel costs.",
        "epistemic_state": "DERIVED",
    })

    # Commodity -> Financial Asset Edges
    edges.append({
        "source": "comm-brent_crude",
        "target": "asset-brent",
        "relationship": "benchmarks",
        "weight": 1.0,
        "confidence": 0.99,
        "explanation": "Direct settlement benchmark for two-thirds of the world's physical seaborne crude contracts.",
        "epistemic_state": "OBSERVED",
    })

    # Asset -> Macro Inflation
    edges.append({
        "source": "asset-brent",
        "target": "macro-inflation",
        "relationship": "cost_push_inflation",
        "weight": 0.72,
        "confidence": 0.91,
        "explanation": "Crude price escalation feeds directly into refinery crack spreads, headline CPI, and transport logistics expenses.",
        "epistemic_state": "MODELLED",
    })

    # Inflation -> Bond Yields
    edges.append({
        "source": "macro-inflation",
        "target": "macro-bond_yields",
        "relationship": "hawkish_monetary_reaction",
        "weight": 0.68,
        "confidence": 0.89,
        "explanation": "Elevated inflation expectations trigger higher policy terminal rates, driving up 10-year sovereign yields.",
        "epistemic_state": "MODELLED",
    })

    # Bond Yields -> Equity Volatility
    edges.append({
        "source": "macro-bond_yields",
        "target": "macro-equity_volatility",
        "relationship": "discount_rate_shock",
        "weight": 0.64,
        "confidence": 0.87,
        "explanation": "Rising discount rates compress equity valuation multiples, triggering cross-asset hedging and VIX volatility surges.",
        "epistemic_state": "SCENARIO",
    })

    # Container Freights -> Equity Margins
    edges.append({
        "source": "comm-container_scfi",
        "target": "asset-spx",
        "relationship": "margin_compression",
        "weight": -0.45,
        "confidence": 0.82,
        "explanation": "Surging spot freight rates compress operating margins for multinational retail and industrial manufacturing firms.",
        "epistemic_state": "MODELLED",
    })

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "canonical_cascades": [
            {
                "cascade_id": "hormuz_energy_shock",
                "name": "Persian Gulf Oil Shock Transmission",
                "sequence": [
                    "country-irn",
                    "cp-strait-of-hormuz",
                    "comm-brent_crude",
                    "asset-brent",
                    "macro-inflation",
                    "macro-bond_yields",
                    "macro-equity_volatility",
                ],
                "description": "Iran → Strait of Hormuz → Oil supply → Brent → Inflation → Bond yields → Equity volatility",
            },
            {
                "cascade_id": "red_sea_container_shock",
                "name": "Red Sea Shipping Disruption Cascade",
                "sequence": [
                    "cp-bab-el-mandeb",
                    "comm-container_scfi",
                    "macro-inflation",
                    "asset-spx",
                ],
                "description": "Bab el-Mandeb → Container Freight (SCFI) → Inflation → S&P 500 Margins",
            }
        ],
    }
