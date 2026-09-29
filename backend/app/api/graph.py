"""
AGNI Dynamic Risk & Trade Topology Graph API
============================================
Exposes interpretable NetworkX directed risk and trade transmission graph:
  Nodes: Country, Commodity, Financial Asset, Trade Route, Event
  Edges:
    country → commodity
    country → asset
    country → route
    commodity → asset
    route → commodity
    event → country

Edge attributes: exposure, correlation, importance, confidence, timestamp.
Connected directly to the Knowledge Graph interface.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional

from agni.graph.topology import dynamic_risk_graph

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get("")
async def get_dynamic_risk_graph() -> Dict[str, Any]:
    """
    Retrieve full dynamic knowledge and trade transmission graph.
    Returns nodes, directed causal edges with institutional attributes,
    and canonical cascades for interactive UI visualization.
    """
    return dynamic_risk_graph.to_dict()


@router.get("/nodes")
async def get_graph_nodes(
    node_type: Optional[str] = Query(None, description="country, commodity, financial_asset, trade_route, event")
) -> List[Dict[str, Any]]:
    """Retrieve graph nodes with optional type filtering."""
    graph_data = dynamic_risk_graph.to_dict()
    nodes = graph_data["nodes"]
    if node_type:
        nodes = [n for n in nodes if n.get("type") == node_type]
    return nodes


@router.get("/edges")
async def get_graph_edges(
    source_type: Optional[str] = None,
    target_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve edges with exposure, correlation, importance, confidence, and timestamp."""
    graph_data = dynamic_risk_graph.to_dict()
    edges = graph_data["edges"]
    if source_type:
        edges = [e for e in edges if e["source"].startswith(source_type)]
    if target_type:
        edges = [e for e in edges if e["target"].startswith(target_type)]
    return edges


@router.get("/path")
async def trace_causal_path(
    source: str = Query("event:strait-of-hormuz", description="Source node ID"),
    target: str = Query("asset:US10Y", description="Target node ID"),
) -> Dict[str, Any]:
    """Traces the shortest causal transmission chain between any two nodes in the graph."""
    path = dynamic_risk_graph.trace_transmission_path(source, target)
    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"No causal transmission path found from '{source}' to '{target}'",
        )

    # Extract edge steps along path
    steps = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge_data = dynamic_risk_graph.graph.get_edge_data(u, v)
        steps.append({
            "step": i + 1,
            "source": u,
            "target": v,
            "relationship": edge_data.get("relationship", "transmits_to"),
            "exposure": edge_data.get("exposure", 0.0),
            "correlation": edge_data.get("correlation", 0.0),
            "importance": edge_data.get("importance", 0.0),
            "confidence": edge_data.get("confidence", 0.0),
            "explanation": edge_data.get("explanation", ""),
        })

    return {
        "source": source,
        "target": target,
        "path_length": len(path) - 1,
        "nodes": path,
        "transmission_steps": steps,
    }


@router.get("/centrality")
async def get_node_centrality() -> Dict[str, Dict[str, float]]:
    """Computes PageRank and Betweenness Centrality for all nodes."""
    return dynamic_risk_graph.compute_centrality()
