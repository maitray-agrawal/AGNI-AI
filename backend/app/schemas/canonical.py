"""
AGNI Canonical Data Schemas
===========================
Institutional-grade, event-conditioned probabilistic intelligence data models.
Covers all core entities: Events, Market Observations, Macro Observations,
Sovereign Entities, Commodities, Financial Assets, Trade Routes, Maritime
Chokepoints, Risk Signals, Transmission Links, Scenarios, Forecasts,
Regime States, Backtest Results, and Evidence Provenance.

Every entity features:
- Stable unique ID
- RFC-3339 / ISO-8601 Timestamp
- Verified Source & Provenance
- Confidence Calibration Metrics
"""

from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# 1. CORE ENUMS & LITERALS
# ─────────────────────────────────────────────────────────────────────────────

EventType = Literal[
    "armed_conflict",
    "sanctions",
    "political_instability",
    "trade_restriction",
    "election_shock",
    "diplomatic_escalation",
    "maritime_disruption",
    "energy_disruption",
    "commodity_supply_shock",
    "financial_stress",
    "natural_hazard",
    "infrastructure_disruption",
    "geopolitical_escalation",
    "other",
]

SeverityLevel = Literal["critical", "high", "elevated", "moderate", "low", "info"]

EvidenceState = Literal["OBSERVED", "DERIVED", "MODELLED", "SCENARIO"]
EpistemicState = EvidenceState

RegimeType = Literal["CALM", "ELEVATED", "STRESSED", "CRISIS"]

AssetClass = Literal["equity_index", "sovereign_bond", "commodity", "fx_rate", "credit_spread", "volatility"]

ScenarioType = Literal["BASE", "ADVERSE", "SEVERE", "CUSTOM"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. EVIDENCE & PROVENANCE
# ─────────────────────────────────────────────────────────────────────────────

class Evidence(BaseModel):
    evidence_id: str = Field(..., description="Unique immutable evidence identifier")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    evidence_state: EvidenceState = Field(
        ..., description="Epistemic status: OBSERVED, DERIVED, MODELLED, or SCENARIO"
    )
    source_name: str = Field(..., description="Reporting agency, satellite feed, or institutional registry")
    source_uri: Optional[str] = Field(None, description="Direct URL, DOI, or internal document path")
    headline: str = Field(..., description="Concise statement of verifiable evidence")
    extracted_text: Optional[str] = Field(None, description="Verbatim raw excerpt")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence rating between 0 and 1")
    is_air_gapped: bool = Field(True, description="Whether processed on-premise without external data egress")


class AnalystNote(BaseModel):
    note_id: str = Field(..., description="Unique note identifier")
    analyst_id: str = Field("analyst-sovereign-01", description="Author identifier")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    content: str = Field(..., description="Analytical commentary or institutional assessment")
    tags: List[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# 3. GEOSPATIAL & SOVEREIGN GRAPH ENTITIES
# ─────────────────────────────────────────────────────────────────────────────

class Country(BaseModel):
    country_code: str = Field(..., description="ISO 3166-1 alpha-3 code (e.g. TWN, PAN, IRN)")
    name: str = Field(..., description="Full sovereign name")
    region: str = Field(..., description="Geopolitical theater (e.g. East Asia, Middle East)")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    gdp_usd_billions: Optional[float] = None
    geopolitical_risk_index: float = Field(100.0, description="Calibrated country risk index")


class Chokepoint(BaseModel):
    chokepoint_id: str = Field(..., description="Unique slug (e.g. bab-el-mandeb, strait-of-hormuz)")
    name: str = Field(..., description="Official maritime/logistics chokepoint name")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    global_trade_share_pct: float = Field(..., description="Percentage of global commercial trade traversing")
    critical_commodities: List[str] = Field(default_factory=list, description="Primary dependent commodities")
    current_status: SeverityLevel = Field("moderate")


class TradeRoute(BaseModel):
    route_id: str = Field(..., description="Unique route identifier")
    name: str = Field(..., description="Trade route descriptor (e.g. Asia-Europe via Suez)")
    origin_region: str
    destination_region: str
    traversed_chokepoints: List[str] = Field(default_factory=list)
    average_transit_days: float
    current_delay_days: float = 0.0


class Commodity(BaseModel):
    commodity_id: str = Field(..., description="Ticker or slug (e.g. BRENT_CRUDE, LNG, COPPER, WHEAT)")
    name: str
    category: str = Field(..., description="Energy, Agricultural, Industrial Metals, or Precious")
    benchmark_unit: str = Field("USD/bbl", description="Quotation unit")
    primary_chokepoint_dependencies: List[str] = Field(default_factory=list)


class FinancialAsset(BaseModel):
    asset_id: str = Field(..., description="Ticker or identifier (e.g. SPX, US10Y, DXY, VIX)")
    name: str
    asset_class: AssetClass
    currency: str = Field("USD")
    current_value: float
    daily_change_pct: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 4. CANONICAL EVENT SCHEMA
# ─────────────────────────────────────────────────────────────────────────────

class Event(BaseModel):
    event_id: str = Field(..., description="Stable unique UUID or identifier")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: EventType = Field("geopolitical_escalation", description="Taxonomic classification")
    title: str = Field(..., min_length=3, description="Crisp descriptive headline")
    description: str = Field("", description="Detailed factual intelligence briefing")
    country: str = Field(..., description="Primary affected country or sovereign actor")
    region: str = Field(..., description="Geopolitical theater")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    severity: SeverityLevel = Field("moderate")
    confidence: float = Field(0.85, ge=0.0, le=1.0)
    source: str = Field("AstraX Sovereign Signal Feed")
    affected_assets: List[str] = Field(default_factory=list)
    affected_commodities: List[str] = Field(default_factory=list)
    affected_routes: List[str] = Field(default_factory=list)
    transmission_channels: List[str] = Field(
        default_factory=list,
        description="Sequential transmission chain (e.g. Missile Strike -> Cape Diversion -> Bunker Fuel Spike)",
    )
    evidence: List[Evidence] = Field(default_factory=list)
    analyst_notes: List[AnalystNote] = Field(default_factory=list)
    is_demo_data: bool = Field(False, description="Flag explicitly distinguishing demo records from live feeds")


# ─────────────────────────────────────────────────────────────────────────────
# 5. MARKET & MACRO OBSERVATIONS
# ─────────────────────────────────────────────────────────────────────────────

class MarketObservation(BaseModel):
    observation_id: str
    asset_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    available_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Point-in-time timestamp preventing lookahead data leakage",
    )
    price: float
    volume: Optional[float] = None
    implied_volatility: Optional[float] = None
    realized_volatility_30d: Optional[float] = None
    source: str = "Market Feeds / Parquet Store"
    is_demo_data: bool = False


class MacroObservation(BaseModel):
    observation_id: str
    country_code: str
    indicator_code: str = Field(..., description="e.g. CPI_YOY, POLICY_RATE, DEBT_GDP, TRADE_BALANCE")
    timestamp: str
    available_at: str
    value: float
    source: str = "FRED / IMF / World Bank"
    is_demo_data: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# 6. EXPLAINABLE RISK SIGNAL & TRANSMISSION GRAPH
# ─────────────────────────────────────────────────────────────────────────────

class RiskSignalComponent(BaseModel):
    """Component-level explainable decomposition of a risk signal."""
    event_intensity: float = Field(..., ge=0.0, le=100.0, description="Direct severity magnitude (0-100)")
    country_exposure: float = Field(..., ge=0.0, le=100.0, description="Sovereign criticality and systemic weight (0-100)")
    commodity_exposure: float = Field(..., ge=0.0, le=100.0, description="Concentration of critical commodity flows (0-100)")
    asset_exposure: float = Field(50.0, ge=0.0, le=100.0, description="Financial asset exposure and cross-market sensitivity (0-100)")
    market_sensitivity: float = Field(50.0, ge=0.0, le=100.0, description="Beta/volatility responsiveness (0-100)")
    route_exposure: float = Field(..., ge=0.0, le=100.0, description="Global trade percentage traversing affected routes (0-100)")
    historical_response: float = Field(..., ge=0.0, le=100.0, description="Shock persistence from historical analogues (0-100)")
    regime_multiplier: float = Field(1.0, ge=0.5, le=3.0, description="Macro volatility regime multiplier")
    confidence: float = Field(0.85, ge=0.0, le=1.0, description="Epistemic confidence score (0-1)")

    @model_validator(mode="before")
    @classmethod
    def sync_asset_and_market(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "asset_exposure" in data and "market_sensitivity" not in data:
                data["market_sensitivity"] = data["asset_exposure"]
            elif "market_sensitivity" in data and "asset_exposure" not in data:
                data["asset_exposure"] = data["market_sensitivity"]
        return data


class TransmissionLink(BaseModel):
    from_node: str = Field(..., description="Upstream entity (e.g. Houthi Drone Probes)")
    to_node: str = Field(..., description="Downstream entity (e.g. Bab el-Mandeb Rerouting)")
    link_type: Literal["geopolitical_shock", "supply_disruption", "price_transmission", "volatility_contagion"]
    elasticity_or_beta: float = Field(1.0, description="Estimated sensitivity parameter")
    explanation: str = Field(..., description="Verifiable causal justification")


class RiskSignal(BaseModel):
    signal_id: str
    event_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Deterministic synthesized risk score 0-100")
    risk_level: SeverityLevel
    confidence: float = Field(0.85, ge=0.0, le=1.0)
    components: RiskSignalComponent
    drivers: List[str] = Field(default_factory=list, description="Top explanatory driver factors")
    affected_regions: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)
    affected_commodities: List[str] = Field(default_factory=list)
    transmission_path: List[TransmissionLink] = Field(default_factory=list)
    is_demo_data: bool = False


class EventIntelligenceResult(BaseModel):
    """Synthesized intelligence output for an event evaluated by the risk engine."""
    event_id: str
    title: str = ""
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: SeverityLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    components: RiskSignalComponent
    drivers: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)
    affected_commodities: List[str] = Field(default_factory=list)
    affected_routes: List[str] = Field(default_factory=list)
    transmission_path: List[TransmissionLink] = Field(default_factory=list)
    epistemic_state: EpistemicState = "DERIVED"
    calculated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ─────────────────────────────────────────────────────────────────────────────
# 7. REGIME DETECTION
# ─────────────────────────────────────────────────────────────────────────────

class RegimeState(BaseModel):
    regime_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    current_regime: RegimeType
    probability: float = Field(..., ge=0.0, le=1.0)
    regime_probabilities: Dict[RegimeType, float]
    features_used: List[str] = Field(
        default_factory=lambda: [
            "realized_volatility_brent",
            "cross_asset_correlation",
            "geopolitical_risk_spread",
            "sovereign_cds_spread",
        ]
    )
    transition_probabilities: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    model_type: Literal["markov_switching", "hidden_markov_model", "deterministic_baseline"] = "markov_switching"


# ─────────────────────────────────────────────────────────────────────────────
# 8. PROBABILISTIC FORECASTING & CALIBRATION
# ─────────────────────────────────────────────────────────────────────────────

class QuantileForecast(BaseModel):
    quantile: float = Field(..., ge=0.0, le=1.0, description="e.g. 0.05, 0.25, 0.50, 0.75, 0.95")
    value: float


class ForecastDistribution(BaseModel):
    mean: float
    standard_deviation: float
    quantiles: List[QuantileForecast]
    prob_threshold_breach: Dict[str, float] = Field(
        default_factory=dict,
        description="e.g. {'oil_above_100': 0.38, 'oil_above_120': 0.12}",
    )
    conformal_interval_90: tuple[float, float] = Field(
        default=(0.0, 0.0),
        description="Calibrated lower and upper bounds at 90% nominal coverage",
    )


class Forecast(BaseModel):
    forecast_id: str
    target_asset: str
    horizon: Literal["1D", "7D", "30D", "90D"]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    available_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    model_name: str
    conditioning_events: List[str] = Field(default_factory=list)
    conditioning_regime: RegimeType = "CALM"
    point_forecast: float
    distribution: ForecastDistribution
    empirical_coverage_90: float = Field(0.89, description="Observed historical test coverage")
    is_demo_data: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# 9. CONDITIONAL SCENARIO ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class ScenarioShock(BaseModel):
    target: str = Field(..., description="Asset or commodity ticker")
    shock_pct: float = Field(..., description="Percentage shift (e.g. +18.5%)")
    confidence_interval: tuple[float, float] = (0.0, 0.0)


class Scenario(BaseModel):
    scenario_id: str
    name: str = Field(..., description="e.g. Hormuz Closure Escalation")
    scenario_type: ScenarioType
    description: str
    trigger_event_id: Optional[str] = None
    shocks: List[ScenarioShock]
    macro_transmission_summary: str
    var_95_portfolio_impact: float = Field(..., description="Value at Risk (95% confidence)")
    expected_shortfall_95: float = Field(..., description="Conditional VaR / Expected Shortfall")
    affected_regions: List[str]
    affected_assets: List[str]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    is_demo_data: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# 10. BACKTESTING & MODEL VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

class BacktestResult(BaseModel):
    backtest_id: str
    model_name: str
    evaluation_window: str = "2023-01-01 to 2026-09-01"
    validation_protocol: Literal["rolling_origin", "purged_walk_forward", "k_fold_cross_validation"] = "rolling_origin"
    sample_size_days: int
    mae: float
    rmse: float
    mase: float
    crps: float = Field(..., description="Continuous Ranked Probability Score for distribution accuracy")
    pinball_loss_90: float
    nominal_coverage_90: float = 0.90
    actual_coverage_90: float
    var_kupiec_p_value: float = Field(..., description="Kupiec unconditional coverage test p-value (> 0.05 passes)")
    var_christoffersen_p_value: float = Field(..., description="Christoffersen independence test p-value")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
