"""
AGNI Deterministic Demo Data Engine
===================================
Generates mathematically reproducible, fixed-seed geopolitical and financial
intelligence entities so AGNI runs fully offline with high analytical fidelity.
Every record has `is_demo_data = True` so production feeds are never confused.
"""

from typing import List, Dict
from backend.app.schemas.canonical import (
    Event,
    Chokepoint,
    Country,
    Commodity,
    FinancialAsset,
    RiskSignal,
    RiskSignalComponent,
    TransmissionLink,
    RegimeState,
    Scenario,
    ScenarioShock,
    Forecast,
    ForecastDistribution,
    QuantileForecast,
    BacktestResult,
    Evidence,
    AnalystNote,
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. SOVEREIGN ENTITIES & CHOKEPOINTS
# ─────────────────────────────────────────────────────────────────────────────

DEMO_COUNTRIES: List[Country] = [
    Country(country_code="TWN", name="Taiwan", region="East Asia", latitude=24.0, longitude=119.5, gdp_usd_billions=790.0, geopolitical_risk_index=142.5),
    Country(country_code="YEM", name="Yemen", region="Middle East & Horn of Africa", latitude=15.3, longitude=44.2, gdp_usd_billions=21.0, geopolitical_risk_index=185.0),
    Country(country_code="IRN", name="Iran", region="Middle East", latitude=32.4, longitude=53.7, gdp_usd_billions=388.0, geopolitical_risk_index=172.0),
    Country(country_code="UKR", name="Ukraine", region="Eastern Europe", latitude=48.3, longitude=31.1, gdp_usd_billions=160.0, geopolitical_risk_index=190.0),
    Country(country_code="PAN", name="Panama", region="Central America", latitude=8.5, longitude=-80.1, gdp_usd_billions=76.0, geopolitical_risk_index=72.0),
    Country(country_code="EGY", name="Egypt", region="North Africa / Middle East", latitude=26.8, longitude=30.8, gdp_usd_billions=476.0, geopolitical_risk_index=115.0),
    Country(country_code="SGP", name="Singapore", region="Southeast Asia", latitude=1.35, longitude=103.8, gdp_usd_billions=501.0, geopolitical_risk_index=65.0),
    Country(country_code="USA", name="United States", region="North America", latitude=37.1, longitude=-95.7, gdp_usd_billions=26950.0, geopolitical_risk_index=78.0),
]

DEMO_CHOKEPOINTS: List[Chokepoint] = [
    Chokepoint(
        chokepoint_id="taiwan-strait",
        name="Taiwan Strait",
        latitude=24.0,
        longitude=119.5,
        global_trade_share_pct=48.0,
        critical_commodities=["Advanced Semiconductors", "Containerized Freight", "LNG"],
        current_status="critical",
    ),
    Chokepoint(
        chokepoint_id="bab-el-mandeb",
        name="Bab el-Mandeb / Southern Red Sea",
        latitude=12.6,
        longitude=43.3,
        global_trade_share_pct=12.0,
        critical_commodities=["Brent Crude", "European Refined Products", "Grain"],
        current_status="critical",
    ),
    Chokepoint(
        chokepoint_id="strait-of-hormuz",
        name="Strait of Hormuz",
        latitude=26.6,
        longitude=56.3,
        global_trade_share_pct=21.0,
        critical_commodities=["Crude Oil", "Liquefied Natural Gas (LNG)", "Petrochemicals"],
        current_status="critical",
    ),
    Chokepoint(
        chokepoint_id="panama-canal",
        name="Panama Canal",
        latitude=9.1,
        longitude=-79.7,
        global_trade_share_pct=5.0,
        critical_commodities=["US Gulf Grain", "LNG", "Chemicals"],
        current_status="elevated",
    ),
    Chokepoint(
        chokepoint_id="suez-canal",
        name="Suez Canal",
        latitude=30.5,
        longitude=32.3,
        global_trade_share_pct=15.0,
        critical_commodities=["Manufactured Goods", "Oil", "Fertilizer"],
        current_status="critical",
    ),
    Chokepoint(
        chokepoint_id="malacca-strait",
        name="Malacca Strait",
        latitude=2.5,
        longitude=101.5,
        global_trade_share_pct=25.0,
        critical_commodities=["Crude Oil", "Iron Ore", "Manufactured Electronics"],
        current_status="elevated",
    ),
]

DEMO_COMMODITIES: List[Commodity] = [
    Commodity(commodity_id="BRENT_CRUDE", name="Brent Crude Oil", category="Energy", benchmark_unit="USD/bbl", primary_chokepoint_dependencies=["strait-of-hormuz", "bab-el-mandeb"]),
    Commodity(commodity_id="TTF_GAS", name="European Natural Gas (TTF)", category="Energy", benchmark_unit="EUR/MWh", primary_chokepoint_dependencies=["bab-el-mandeb", "suez-canal"]),
    Commodity(commodity_id="WHEAT", name="CBOT Milling Wheat", category="Agricultural", benchmark_unit="USD/bu", primary_chokepoint_dependencies=["danube-black-sea", "suez-canal"]),
    Commodity(commodity_id="CONTAINER_SCFI", name="Shanghai Containerized Freight Index", category="Logistics", benchmark_unit="Points", primary_chokepoint_dependencies=["bab-el-mandeb", "taiwan-strait"]),
    Commodity(commodity_id="COPPER", name="LME Grade A Copper", category="Industrial Metals", benchmark_unit="USD/mt", primary_chokepoint_dependencies=["panama-canal", "malacca-strait"]),
]

DEMO_ASSETS: List[FinancialAsset] = [
    FinancialAsset(asset_id="SPX", name="S&P 500 Index", asset_class="equity_index", current_value=5720.0, daily_change_pct=-0.42),
    FinancialAsset(asset_id="US10Y", name="US 10-Year Treasury Yield", asset_class="sovereign_bond", current_value=4.12, daily_change_pct=1.8),
    FinancialAsset(asset_id="DXY", name="US Dollar Index", asset_class="fx_rate", current_value=103.8, daily_change_pct=0.35),
    FinancialAsset(asset_id="VIX", name="CBOE Volatility Index", asset_class="volatility", current_value=18.4, daily_change_pct=6.5),
    FinancialAsset(asset_id="BRENT", name="Brent Crude Futures", asset_class="commodity", current_value=78.4, daily_change_pct=2.1),
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. CANONICAL GEOPOLITICAL EVENTS
# ─────────────────────────────────────────────────────────────────────────────

DEMO_EVENTS: List[Event] = [
    Event(
        event_id="evt-taiwan-01",
        event_type="maritime_disruption",
        title="Taiwan Strait High-Density Naval Patrols & Semiconductor Scrutiny",
        description="Naval escorts and air patrols intensified along southwest maritime corridors. 48% of global container transit and high-grade silicon foundry supply traverse this maritime avenue.",
        country="Taiwan / China",
        region="East Asia",
        latitude=24.0,
        longitude=119.5,
        severity="critical",
        confidence=0.92,
        source="AstraX Sovereign Satellite & AIS Monitor",
        affected_assets=["SPX", "VIX", "DXY"],
        affected_commodities=["CONTAINER_SCFI", "COPPER"],
        affected_routes=["Trans-Pacific High-Tech Lane", "Intra-Asia Feeder Network"],
        transmission_channels=[
            "Naval Corridor Maneuvers",
            "Advanced Wafer Foundry Logistics Delays",
            "Tech Hardware Gross Margin Compression",
            "Equity Volatility Index Spike",
        ],
        evidence=[
            Evidence(
                evidence_id="evi-twn-101",
                evidence_state="OBSERVED",
                source_name="AIS Maritime Telemetry Registry",
                headline="Commercial vessel routing deviations observed in southern Taiwan approach lanes.",
                confidence=0.95,
            )
        ],
        analyst_notes=[
            AnalystNote(
                note_id="note-twn-01",
                content="Supply elasticity for 3nm logic wafers is near-zero over 6-month horizons. Any physical corridor interdiction causes immediate tail risk.",
            )
        ],
        is_demo_data=True,
    ),
    Event(
        event_id="evt-redsea-02",
        event_type="maritime_disruption",
        title="Bab el-Mandeb Commercial Fleet Cape of Good Hope Diversions",
        description="Persistent anti-ship missile probes and uncrewed surface vessel telemetry forcing container liners to reroute around South Africa, adding 12-14 transit days and +110% spot freight premiums.",
        country="Yemen / Djibouti",
        region="Middle East & Horn of Africa",
        latitude=12.6,
        longitude=43.3,
        severity="critical",
        confidence=0.96,
        source="Lloyd's Intelligence & Regional Maritime Security Center",
        affected_assets=["VIX", "US10Y"],
        affected_commodities=["BRENT_CRUDE", "TTF_GAS", "CONTAINER_SCFI"],
        affected_routes=["Asia-Europe Far East Lane", "Mediterranean Feeder"],
        transmission_channels=[
            "Asymmetric Drone & Missile Threat",
            "Cape of Good Hope Diversions (+14 Days)",
            "Bunker Fuel Demand Escalation",
            "European Import Price Inflation",
            "Central Bank Rate Cut Delay",
        ],
        evidence=[
            Evidence(
                evidence_id="evi-red-201",
                evidence_state="OBSERVED",
                source_name="UKMTO Incident Watch",
                headline="Multiple anti-ship ballistic missile telemetry traces logged over Bab el-Mandeb transit sector.",
                confidence=0.98,
            )
        ],
        analyst_notes=[
            AnalystNote(
                note_id="note-red-01",
                content="Net Suez transits remain depressed at -64% year-over-year. Structural persistence confirmed through Q4.",
            )
        ],
        is_demo_data=True,
    ),
    Event(
        event_id="evt-hormuz-03",
        event_type="energy_disruption",
        title="Strait of Hormuz Hydrocarbon Transit & Electronic Telemetry Spoofing",
        description="Widespread GNSS spoofing and asymmetric naval fast-boat shadowing reported near UAE and Oman coastal approaches. 21 million barrels/day crude throughput placed under elevated readiness.",
        country="Iran / Oman",
        region="Persian Gulf",
        latitude=26.6,
        longitude=56.3,
        severity="critical",
        confidence=0.89,
        source="IMB Piracy & Armed Robbery Center / AIS Feeds",
        affected_assets=["BRENT", "SPX", "US10Y"],
        affected_commodities=["BRENT_CRUDE", "TTF_GAS"],
        affected_routes=["Middle East Crude to East Asia", "VLCC Gulf to Western Europe"],
        transmission_channels=[
            "Electronic Warfare GNSS Spoofing",
            "Crude Tanker War-Risk Premium Repricing",
            "Immediate Upward Drift in Brent Front-Month Futures",
            "Global Headline Inflation Re-acceleration",
        ],
        evidence=[
            Evidence(
                evidence_id="evi-hor-301",
                evidence_state="OBSERVED",
                source_name="Regional P&I Maritime Clubs",
                headline="War risk hull insurance premiums elevated by +35 bps for northern Gulf transit corridors.",
                confidence=0.91,
            )
        ],
        analyst_notes=[
            AnalystNote(
                note_id="note-hor-01",
                content="Historical elasticity: Each 1 mbpd sustained flow impairment generates approximately +$8.50/bbl price impulse on Brent.",
            )
        ],
        is_demo_data=True,
    ),
    Event(
        event_id="evt-panama-04",
        event_type="infrastructure_disruption",
        title="Panama Canal Transit Slot Normalization & Lake Gatun Recovery",
        description="Freshwater reservoir replenishment following rainfall recovery allows daily transits to expand to 36 vessels, easing US Gulf grain and LNG export bottlenecks.",
        country="Panama",
        region="Central America",
        latitude=9.1,
        longitude=-79.7,
        severity="elevated",
        confidence=0.94,
        source="Panama Canal Authority (ACP) Operations Bulletin",
        affected_assets=["SPX"],
        affected_commodities=["WHEAT", "COPPER"],
        affected_routes=["US Gulf to Northeast Asia", "West Coast South America to US East Coast"],
        transmission_channels=[
            "Lake Gatun Water Level Recovery",
            "Daily Auction Slot Normalization",
            "Trans-Isthmus LNG Freight Rate Moderation",
        ],
        evidence=[
            Evidence(
                evidence_id="evi-pan-401",
                evidence_state="OBSERVED",
                source_name="ACP Hydrographic Service",
                headline="Maximum draft authorized at 48.0 feet in Neopanamax locks.",
                confidence=0.97,
            )
        ],
        analyst_notes=[
            AnalystNote(
                note_id="note-pan-01",
                content="Backlog normalized from 160 ships to under 45 vessels. Downside tail risk to agricultural trade flows substantially mitigated.",
            )
        ],
        is_demo_data=True,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. EXPLAINABLE RISK SIGNALS
# ─────────────────────────────────────────────────────────────────────────────

DEMO_RISK_SIGNALS: List[RiskSignal] = [
    RiskSignal(
        signal_id="sig-taiwan-01",
        event_id="evt-taiwan-01",
        risk_score=91.4,
        risk_level="critical",
        confidence=0.92,
        components=RiskSignalComponent(
            event_intensity=92.0,
            market_sensitivity=88.5,
            country_exposure=95.0,
            commodity_exposure=86.0,
            route_exposure=94.0,
            historical_response=85.0,
            regime_multiplier=1.25,
            confidence=0.92,
        ),
        drivers=[
            "Global reliance on high-end foundry fabrication (> 60%)",
            "Maritime container volume density in Taiwan Strait (48% global share)",
            "Elevated sensitivity in semiconductor equity multiples",
        ],
        affected_regions=["East Asia", "North America", "European Union"],
        affected_assets=["SPX", "VIX", "DXY"],
        affected_commodities=["CONTAINER_SCFI", "COPPER"],
        transmission_path=[
            TransmissionLink(
                from_node="Taiwan Strait Transit Alert",
                to_node="Semiconductor Lead Times",
                link_type="supply_disruption",
                elasticity_or_beta=1.85,
                explanation="Foundry material replenishment cycles delay downstream packaging.",
            ),
            TransmissionLink(
                from_node="Semiconductor Lead Times",
                to_node="Technology Sector Earnings (SPX)",
                link_type="price_transmission",
                elasticity_or_beta=-0.65,
                explanation="Gross margin compression from air freight substitution and inventory buffer depletion.",
            ),
        ],
        is_demo_data=True,
    ),
    RiskSignal(
        signal_id="sig-redsea-02",
        event_id="evt-redsea-02",
        risk_score=87.2,
        risk_level="critical",
        confidence=0.96,
        components=RiskSignalComponent(
            event_intensity=89.0,
            market_sensitivity=82.0,
            country_exposure=80.0,
            commodity_exposure=91.0,
            route_exposure=96.0,
            historical_response=88.0,
            regime_multiplier=1.20,
            confidence=0.96,
        ),
        drivers=[
            "Cape of Good Hope rerouting adding 12-14 transit days",
            "Bunker fuel demand shock and freight spot rate surge (+110%)",
            "European energy import schedule delays",
        ],
        affected_regions=["Middle East", "Horn of Africa", "Western Europe"],
        affected_assets=["US10Y", "VIX"],
        affected_commodities=["BRENT_CRUDE", "TTF_GAS", "CONTAINER_SCFI"],
        transmission_path=[
            TransmissionLink(
                from_node="Bab el-Mandeb Interdiction",
                to_node="Cape of Good Hope Routing",
                link_type="geopolitical_shock",
                elasticity_or_beta=1.0,
                explanation="Carriers declare force majeure and re-route around southern Africa.",
            ),
            TransmissionLink(
                from_node="Cape of Good Hope Routing",
                to_node="Container Spot Rates (SCFI)",
                link_type="price_transmission",
                elasticity_or_beta=2.1,
                explanation="Vessel capacity absorption drives immediate freight index repricing.",
            ),
        ],
        is_demo_data=True,
    ),
    RiskSignal(
        signal_id="sig-hormuz-03",
        event_id="evt-hormuz-03",
        risk_score=84.8,
        risk_level="critical",
        confidence=0.89,
        components=RiskSignalComponent(
            event_intensity=86.0,
            market_sensitivity=90.0,
            country_exposure=88.0,
            commodity_exposure=94.0,
            route_exposure=92.0,
            historical_response=82.0,
            regime_multiplier=1.20,
            confidence=0.89,
        ),
        drivers=[
            "21 million barrels/day crude flow exposure",
            "GPS spoofing affecting navigation certainty",
            "Spillover into international war risk insurance rates",
        ],
        affected_regions=["Persian Gulf", "OECD Importers", "East Asia"],
        affected_assets=["BRENT", "SPX"],
        affected_commodities=["BRENT_CRUDE", "TTF_GAS"],
        transmission_path=[
            TransmissionLink(
                from_node="Strait of Hormuz Navigational Stress",
                to_node="Brent Crude Futures",
                link_type="price_transmission",
                elasticity_or_beta=1.45,
                explanation="Precautionary inventory build by East Asian refiners widens front-month spread.",
            )
        ],
        is_demo_data=True,
    ),
    RiskSignal(
        signal_id="sig-panama-04",
        event_id="evt-panama-04",
        risk_score=46.5,
        risk_level="elevated",
        confidence=0.94,
        components=RiskSignalComponent(
            event_intensity=42.0,
            market_sensitivity=48.0,
            country_exposure=55.0,
            commodity_exposure=52.0,
            route_exposure=60.0,
            historical_response=50.0,
            regime_multiplier=0.95,
            confidence=0.94,
        ),
        drivers=[
            "Transit slot expansion to 36 vessels/day",
            "Reservoir recovery easing trade friction",
        ],
        affected_regions=["Central America", "North America", "East Asia"],
        affected_assets=["SPX"],
        affected_commodities=["WHEAT", "COPPER"],
        transmission_path=[],
        is_demo_data=True,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. REGIME STATE (MARKOV SWITCHING MODEL)
# ─────────────────────────────────────────────────────────────────────────────

DEMO_REGIME_STATE: RegimeState = RegimeState(
    regime_id="regime-current-2026",
    current_regime="ELEVATED",
    probability=0.68,
    regime_probabilities={
        "CALM": 0.12,
        "ELEVATED": 0.68,
        "STRESSED": 0.16,
        "CRISIS": 0.04,
    },
    features_used=[
        "realized_volatility_brent_30d (28.4%)",
        "cross_asset_correlation_spread (0.54)",
        "geopolitical_risk_index (148.2)",
        "shipping_chokepoint_delay_ratio (1.38)",
    ],
    transition_probabilities={
        "CALM": {"CALM": 0.88, "ELEVATED": 0.10, "STRESSED": 0.02, "CRISIS": 0.00},
        "ELEVATED": {"CALM": 0.14, "ELEVATED": 0.72, "STRESSED": 0.12, "CRISIS": 0.02},
        "STRESSED": {"CALM": 0.04, "ELEVATED": 0.22, "STRESSED": 0.64, "CRISIS": 0.10},
        "CRISIS": {"CALM": 0.01, "ELEVATED": 0.08, "STRESSED": 0.35, "CRISIS": 0.56},
    },
    model_type="markov_switching",
)

# ─────────────────────────────────────────────────────────────────────────────
# 5. CONDITIONAL STRESS SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

DEMO_SCENARIOS: List[Scenario] = [
    Scenario(
        scenario_id="scen-base-01",
        name="Baseline: Protracted Red Sea Deviation with Stable Hormuz Transit",
        scenario_type="BASE",
        description="Commercial carriers maintain Cape routing; Bab el-Mandeb remains restricted while Strait of Hormuz maintains full crude throughput.",
        trigger_event_id="evt-redsea-02",
        shocks=[
            ScenarioShock(target="BRENT", shock_pct=3.5, confidence_interval=(1.2, 5.8)),
            ScenarioShock(target="CONTAINER_SCFI", shock_pct=15.0, confidence_interval=(10.0, 22.0)),
            ScenarioShock(target="US10Y", shock_pct=0.15, confidence_interval=(0.05, 0.28)),
            ScenarioShock(target="SPX", shock_pct=-1.2, confidence_interval=(-2.5, 0.4)),
        ],
        macro_transmission_summary="Modest headline CPI pressure (+0.18% annual rate). Fed and ECB keep rate cycle calibrated without emergency policy shifts.",
        var_95_portfolio_impact=-1.85,
        expected_shortfall_95=-2.64,
        affected_regions=["Western Europe", "Middle East"],
        affected_assets=["BRENT", "US10Y", "SPX"],
        is_demo_data=True,
    ),
    Scenario(
        scenario_id="scen-adverse-02",
        name="Adverse: Multi-Chokepoint Friction (Hormuz Escort Scrutiny + Red Sea Impasse)",
        scenario_type="ADVERSE",
        description="Naval fast-boat boardings in Strait of Hormuz trigger precautionary crude tanker holding patterns alongside active Bab el-Mandeb diversions.",
        trigger_event_id="evt-hormuz-03",
        shocks=[
            ScenarioShock(target="BRENT", shock_pct=18.5, confidence_interval=(14.0, 24.5)),
            ScenarioShock(target="TTF_GAS", shock_pct=26.0, confidence_interval=(18.0, 36.0)),
            ScenarioShock(target="VIX", shock_pct=42.0, confidence_interval=(30.0, 58.0)),
            ScenarioShock(target="SPX", shock_pct=-6.4, confidence_interval=(-8.8, -4.1)),
        ],
        macro_transmission_summary="Energy price shock transmits into global manufacturing margins. 10Y yields invert on stagflationary re-pricing.",
        var_95_portfolio_impact=-5.40,
        expected_shortfall_95=-7.82,
        affected_regions=["Persian Gulf", "Europe", "Asia-Pacific"],
        affected_assets=["BRENT", "SPX", "VIX", "US10Y"],
        is_demo_data=True,
    ),
    Scenario(
        scenario_id="scen-severe-03",
        name="Severe: Dual Maritime Interdiction (Hormuz Closure + Taiwan Strait Air Exclusion)",
        scenario_type="SEVERE",
        description="Physical denial of commercial navigation through Hormuz coupled with declaration of a maritime exclusion zone across Taiwan Strait.",
        trigger_event_id="evt-taiwan-01",
        shocks=[
            ScenarioShock(target="BRENT", shock_pct=48.0, confidence_interval=(38.0, 62.0)),
            ScenarioShock(target="CONTAINER_SCFI", shock_pct=140.0, confidence_interval=(105.0, 185.0)),
            ScenarioShock(target="SPX", shock_pct=-18.5, confidence_interval=(-24.0, -13.0)),
            ScenarioShock(target="VIX", shock_pct=125.0, confidence_interval=(90.0, 175.0)),
        ],
        macro_transmission_summary="Global systemic liquidity stress. Simultaneous physical silicon shortages and energy supply contraction induce worldwide recessionary tail event.",
        var_95_portfolio_impact=-14.80,
        expected_shortfall_95=-21.50,
        affected_regions=["Global Systemic"],
        affected_assets=["SPX", "BRENT", "VIX", "DXY", "US10Y"],
        is_demo_data=True,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# 6. PROBABILISTIC FORECASTS (BRENT CRUDE, CONTAINER SCFI, SPX)
# ─────────────────────────────────────────────────────────────────────────────

DEMO_FORECASTS: List[Forecast] = [
    Forecast(
        forecast_id="fc-brent-30d",
        target_asset="BRENT",
        horizon="30D",
        model_name="Event-Conditioned GARCH-VAR Engine",
        conditioning_events=["evt-redsea-02", "evt-hormuz-03"],
        conditioning_regime="ELEVATED",
        point_forecast=82.60,
        distribution=ForecastDistribution(
            mean=82.60,
            standard_deviation=6.15,
            quantiles=[
                QuantileForecast(quantile=0.05, value=73.20),
                QuantileForecast(quantile=0.25, value=78.10),
                QuantileForecast(quantile=0.50, value=82.60),
                QuantileForecast(quantile=0.75, value=86.80),
                QuantileForecast(quantile=0.95, value=93.40),
            ],
            prob_threshold_breach={
                "brent_above_90": 0.28,
                "brent_above_100": 0.11,
                "brent_below_75": 0.14,
            },
            conformal_interval_90=(72.80, 93.90),
        ),
        empirical_coverage_90=0.912,
        is_demo_data=True,
    ),
    Forecast(
        forecast_id="fc-scfi-30d",
        target_asset="CONTAINER_SCFI",
        horizon="30D",
        model_name="Chokepoint Transmission VAR",
        conditioning_events=["evt-redsea-02"],
        conditioning_regime="ELEVATED",
        point_forecast=3420.0,
        distribution=ForecastDistribution(
            mean=3420.0,
            standard_deviation=290.0,
            quantiles=[
                QuantileForecast(quantile=0.05, value=2980.0),
                QuantileForecast(quantile=0.25, value=3210.0),
                QuantileForecast(quantile=0.50, value=3420.0),
                QuantileForecast(quantile=0.75, value=3640.0),
                QuantileForecast(quantile=0.95, value=3910.0),
            ],
            prob_threshold_breach={
                "freight_above_3800": 0.19,
                "freight_above_4200": 0.06,
            },
            conformal_interval_90=(2950.0, 3940.0),
        ),
        empirical_coverage_90=0.895,
        is_demo_data=True,
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# 7. BACKTESTING BENCHMARKS & VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

DEMO_BACKTESTS: List[BacktestResult] = [
    BacktestResult(
        backtest_id="bt-garch-brent-01",
        model_name="Event-Conditioned GARCH-VAR",
        evaluation_window="2023-01-01 to 2026-09-01",
        validation_protocol="rolling_origin",
        sample_size_days=915,
        mae=2.45,
        rmse=3.62,
        mase=0.84,
        crps=1.78,
        pinball_loss_90=0.48,
        nominal_coverage_90=0.90,
        actual_coverage_90=0.912,
        var_kupiec_p_value=0.42,
        var_christoffersen_p_value=0.38,
    ),
    BacktestResult(
        backtest_id="bt-arima-baseline-02",
        model_name="ARIMA(2,1,2) Baseline",
        evaluation_window="2023-01-01 to 2026-09-01",
        validation_protocol="rolling_origin",
        sample_size_days=915,
        mae=3.82,
        rmse=5.14,
        mase=1.12,
        crps=2.85,
        pinball_loss_90=0.76,
        nominal_coverage_90=0.90,
        actual_coverage_90=0.841,
        var_kupiec_p_value=0.03,  # Fails at 5% nominal
        var_christoffersen_p_value=0.04,
    ),
]
