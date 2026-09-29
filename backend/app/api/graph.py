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

    # Explicit Geo-Transmission Links
    edges.append({
        "source": "comm-brent_crude",
        "target": "asset-brent",
        "relationship": "benchmarks",
        "weight": 1.0,
        "confidence": 0.99,
    })
    edges.append({
        "source": "comm-brent_crude",
        "target": "asset-vix",
        "relationship": "transmits_volatility",
        "weight": 0.65,
        "confidence": 0.88,
    })
    edges.append({
        "source": "comm-container_scfi",
        "target": "asset-spx",
        "relationship": "margin_compression",
        "weight": -0.45,
        "confidence": 0.82,
    })

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }
