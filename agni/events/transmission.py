"""
AGNI Transmission-Path Generator
================================
Constructs causal multi-hop transmission chains detailing shock propagation
from geopolitical root events across maritime routes, physical commodities,
and capital market instruments.
"""

from typing import List
from agni.data.schemas import Event, TransmissionLink


class TransmissionGenerator:
    """Generates structured, verifiable transmission links for an event."""

    @classmethod
    def generate_path(cls, event: Event) -> List[TransmissionLink]:
        links: List[TransmissionLink] = []

        # Case A: Analyst provided explicit sequential transmission channels
        if event.transmission_channels and len(event.transmission_channels) >= 2:
            channels = event.transmission_channels
            for i in range(len(channels) - 1):
                from_n = channels[i]
                to_n = channels[i + 1]

                if i == 0:
                    l_type = "geopolitical_shock"
                    beta = 1.00
                    exp = f"Tactical shock at {from_n} impairs local operational capacity and activates {to_n}"
                elif i == 1:
                    l_type = "supply_disruption"
                    beta = round(1.15 + (i * 0.1), 2)
                    exp = f"Physical throughput impairment at {from_n} forces logistical rerouting and cascades into {to_n}"
                elif i == 2:
                    l_type = "price_transmission"
                    beta = round(1.30 + (i * 0.1), 2)
                    exp = f"Supply deficit at {from_n} reprices prompt benchmark futures into {to_n}"
                else:
                    l_type = "volatility_contagion"
                    beta = round(1.50 + (i * 0.15), 2)
                    exp = f"Price volatility at {from_n} spills into broader capital asset risk premiums at {to_n}"

                links.append(
                    TransmissionLink(
                        from_node=from_n,
                        to_node=to_n,
                        link_type=l_type,
                        elasticity_or_beta=beta,
                        explanation=exp,
                    )
                )
            return links

        # Case B: Synthesize from event entities (Country -> Route -> Commodity -> Asset)
        origin = event.country or event.region or "Sovereign Epicenter"

        # Hop 1: Origin to Route / Chokepoint
        route_target = event.affected_routes[0] if event.affected_routes else f"{event.region} Maritime Corridors"
        links.append(
            TransmissionLink(
                from_node=f"Tactical Incident ({origin})",
                to_node=route_target,
                link_type="geopolitical_shock",
                elasticity_or_beta=1.05,
                explanation=f"Sovereign incident in {origin} elevates war-risk hull insurance and restricts transit along {route_target}",
            )
        )

        # Hop 2: Route to Primary Commodity
        comm_target = event.affected_commodities[0] if event.affected_commodities else "BRENT_CRUDE"
        links.append(
            TransmissionLink(
                from_node=route_target,
                to_node=f"{comm_target} Spot & Futures",
                link_type="supply_disruption",
                elasticity_or_beta=1.25,
                explanation=f"Corridor congestion and rerouting delays compress prompt deliveries of {comm_target}",
            )
        )

        # Hop 3: Commodity to Financial Asset / Volatility
        asset_target = event.affected_assets[0] if event.affected_assets else "VIX"
        links.append(
            TransmissionLink(
                from_node=f"{comm_target} Spot & Futures",
                to_node=f"{asset_target} Index",
                link_type="price_transmission" if asset_target != "VIX" else "volatility_contagion",
                elasticity_or_beta=1.40,
                explanation=f"Input cost inflation from {comm_target} shifts terminal cashflow expectations and drives {asset_target} volatility",
            )
        )

        # Hop 4: Macro Volatility Contagion (if multiple assets)
        if len(event.affected_assets) > 1:
            second_asset = event.affected_assets[1]
            links.append(
                TransmissionLink(
                    from_node=f"{asset_target} Index",
                    to_node=f"{second_asset} Benchmark",
                    link_type="volatility_contagion",
                    elasticity_or_beta=1.65,
                    explanation=f"Systemic portfolio rebalancing transmits cross-market volatility into {second_asset}",
                )
            )

        return links
