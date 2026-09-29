"""
AGNI Earth Observation (EO) & Satellite Telemetry Schemas
=========================================================
Institutional canonical schemas for synthetic and observed satellite passes,
Synthetic Aperture Radar (SAR) vessel detection, and maritime chokepoint
congestion telemetry.
"""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


ConstellationType = Literal[
    "SENTINEL-1-SAR",
    "SENTINEL-2-MSI",
    "COSMO-SkyMed",
    "TERRASAR-X",
    "PLANET-SKYSAT",
    "RADARSAT-CONSTELLATION",
]

SensorModality = Literal[
    "SAR_C_BAND_VV_VH",
    "SAR_X_BAND_HH_HV",
    "OPTICAL_VNIR_SWIR",
    "THERMAL_INFRARED",
]

ChokepointCongestionState = Literal["NORMAL", "ELEVATED", "CONGESTED", "SEVERELY_BLOCKED"]


class VesselDetection(BaseModel):
    """Individual maritime vessel detected in satellite pass."""
    detection_id: str = Field(..., description="Unique SAR target detection ID")
    vessel_type: Literal["tanker", "container", "bulk_carrier", "naval", "cargo_general", "unknown"] = "tanker"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    estimated_length_m: float = Field(..., ge=10.0, le=500.0)
    estimated_speed_knots: float = Field(default=0.0, ge=0.0, le=40.0)
    heading_deg: Optional[float] = Field(default=None, ge=0.0, le=360.0)
    confidence: float = Field(default=0.92, ge=0.0, le=1.0)


class SatellitePass(BaseModel):
    """Metadata regarding a single satellite swath pass over an AOI."""
    pass_id: str = Field(..., description="Unique pass acquisition identifier")
    acquisition_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    constellation: ConstellationType = "SENTINEL-1-SAR"
    sensor_modality: SensorModality = "SAR_C_BAND_VV_VH"
    chokepoint_id: str = Field(..., description="Target chokepoint identifier (e.g. strait-of-hormuz)")
    resolution_meters: float = Field(default=10.0, description="Spatial resolution per pixel")
    swath_area_sq_km: float = Field(default=25000.0)
    cloud_cover_pct: float = Field(default=0.0, ge=0.0, le=100.0, description="Optical cloud interference (0 for SAR)")


class ChokepointSARAnalysis(BaseModel):
    """Calibrated SAR & optical congestion analysis for a strategic chokepoint."""
    analysis_id: str = Field(..., description="Unique report ID")
    pass_id: str
    chokepoint_id: str
    chokepoint_name: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    constellation: ConstellationType
    total_vessels_detected: int = Field(..., ge=0)
    anchored_vessels_count: int = Field(..., ge=0)
    transiting_vessels_count: int = Field(..., ge=0)
    anchorage_density_index: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Standardized anchorage saturation index (0.0=clear, 1.0=saturated)",
    )
    historical_baseline_vessels: float = Field(default=120.0, description="Historical 30-day moving average vessel count")
    congestion_anomaly_zscore: float = Field(
        ...,
        description="Statistical standard deviations relative to non-shock baseline",
    )
    congestion_state: ChokepointCongestionState
    estimated_cargo_delay_hours: float = Field(default=0.0, ge=0.0)
    detection_sample: List[VesselDetection] = Field(default_factory=list)
    confidence: float = Field(default=0.91, ge=0.0, le=1.0)
    provenance_hash: str = Field(default="", description="Cryptographic SHA-256 telemetry hash")


class SatelliteModuleStatus(BaseModel):
    """Institutional state of the gated Earth Observation module."""
    is_enabled: bool = False
    operational_mode: Literal["gated_synthetic_telemetry", "active_stream", "standby"] = "gated_synthetic_telemetry"
    monitored_chokepoints: List[str] = Field(
        default_factory=lambda: [
            "strait-of-hormuz",
            "bab-el-mandeb",
            "strait-of-malacca",
            "suez-canal",
            "panama-canal",
            "bosphorus-strait",
        ]
    )
    supported_constellations: List[str] = Field(
        default_factory=lambda: [
            "SENTINEL-1-SAR (Copernicus)",
            "SENTINEL-2-MSI (Copernicus)",
            "COSMO-SkyMed (ASI)",
            "PLANET-SKYSAT",
        ]
    )
    telemetry_latency_minutes: int = 45
    message: str = (
        "Earth Observation & SAR satellite telemetry is an advanced gated research module. "
        "High-fidelity synthetic SAR vessel and queue analysis is provided offline without external cloud dependencies."
    )
