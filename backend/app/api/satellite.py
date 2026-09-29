"""
AGNI Earth Observation (EO) & Satellite Intelligence API
========================================================
REST endpoints for inspecting the gated satellite module status,
retrieving multi-constellation SAR chokepoint vessel analyses,
and simulating maritime corridor queue saturation.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agni.satellite.schemas import (
    SatelliteModuleStatus,
    ChokepointSARAnalysis,
    ConstellationType,
)
from agni.satellite.observer import satellite_observer, CHOKEPOINT_REGISTRY

router = APIRouter(prefix="/satellite", tags=["Earth Observation (Satellite)"])


class ScanRequest(BaseModel):
    chokepoint_id: str = Field(..., description="Chokepoint ID (e.g. 'strait-of-hormuz')")
    constellation: ConstellationType = Field(default="SENTINEL-1-SAR")
    shock_multiplier: float = Field(default=1.0, ge=0.5, le=5.0)


@router.get("/status", response_model=SatelliteModuleStatus)
async def get_satellite_status():
    """Returns the operational status, gate state, and active constellations of the EO module."""
    return satellite_observer.get_status()


@router.get("/chokepoints")
async def list_monitored_chokepoints():
    """Lists all monitored maritime chokepoints with baseline vessel traffic metrics."""
    return [
        {
            "chokepoint_id": cp_id,
            "name": data["name"],
            "latitude": data["lat"],
            "longitude": data["lon"],
            "baseline_vessels": data["baseline_vessels"],
            "baseline_std": data["baseline_std"],
            "normal_transit_vessels": data["normal_transit_vessels"],
            "normal_anchored": data["normal_anchored"],
        }
        for cp_id, data in CHOKEPOINT_REGISTRY.items()
    ]


@router.get("/analyses", response_model=List[ChokepointSARAnalysis])
async def list_all_analyses(
    constellation: ConstellationType = Query(default="SENTINEL-1-SAR"),
):
    """Retrieves high-resolution SAR and optical vessel density analyses for all chokepoints."""
    return satellite_observer.scan_all_chokepoints(constellation=constellation)


@router.get("/analyses/{chokepoint_id}", response_model=ChokepointSARAnalysis)
async def get_chokepoint_analysis(
    chokepoint_id: str,
    constellation: ConstellationType = Query(default="SENTINEL-1-SAR"),
    shock_multiplier: float = Query(default=1.0, ge=0.5, le=5.0),
):
    """Retrieves or simulates a SAR observation pass for a specific maritime chokepoint."""
    if chokepoint_id not in CHOKEPOINT_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Chokepoint '{chokepoint_id}' not found. Available: {list(CHOKEPOINT_REGISTRY.keys())}",
        )
    return satellite_observer.analyze_chokepoint(
        chokepoint_id=chokepoint_id,
        constellation=constellation,
        shock_multiplier=shock_multiplier,
    )


@router.post("/scan", response_model=ChokepointSARAnalysis)
async def trigger_satellite_scan(request: ScanRequest):
    """Dispatches a satellite synthetic aperture radar acquisition pass over the targeted chokepoint."""
    return satellite_observer.analyze_chokepoint(
        chokepoint_id=request.chokepoint_id,
        constellation=request.constellation,
        shock_multiplier=request.shock_multiplier,
    )
