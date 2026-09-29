"""
AGNI Configuration System
=========================
Loads declarative YAML settings and environment overrides with strong typing.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    type: str = "duckdb_columnar"
    duckdb_memory_limit: str = "4GB"
    parquet_compression: str = "zstd"
    strict_point_in_time: bool = True


class RiskEngineConfig(BaseModel):
    severity_weights: Dict[str, float] = {
        "critical": 1.0,
        "high": 0.8,
        "elevated": 0.6,
        "moderate": 0.4,
        "low": 0.2,
        "info": 0.05,
    }
    chokepoint_amplification: float = 1.35
    max_transmission_hops: int = 5


class AgniResearchSettings(BaseModel):
    app_name: str = "AGNI Research Intelligence"
    app_version: str = "2.0.0"
    environment: str = "production_sovereign"
    air_gapped: bool = True
    seed: int = 42
    fixed_timestamp: str = "2026-09-29T12:00:00Z"
    epistemic_states: List[str] = ["OBSERVED", "DERIVED", "MODELLED", "SCENARIO"]
    storage: StorageConfig = Field(default_factory=StorageConfig)
    risk_engine: RiskEngineConfig = Field(default_factory=RiskEngineConfig)

    @classmethod
    def load_from_yaml(cls, path: str = None) -> "AgniResearchSettings":
        """Loads configuration from YAML file with fallback to defaults."""
        config_path = path or os.environ.get("AGNI_CONFIG_PATH")
        if not config_path:
            # Check default locations
            root_dir = Path(__file__).resolve().parent.parent
            default_yaml = root_dir / "configs" / "agni_config.yaml"
            if default_yaml.exists():
                config_path = str(default_yaml)

        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return cls(**data)
        return cls()


# Global singleton settings
research_settings = AgniResearchSettings.load_from_yaml()
