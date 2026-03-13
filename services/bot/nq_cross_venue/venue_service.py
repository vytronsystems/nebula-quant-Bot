"""Venue abstraction service: list venues, config (no live routing)."""
from __future__ import annotations

from nq_cross_venue.models import VenueSummary


class VenueAbstractionService:
    """Provide venue list and config; capital/risk movement via approved limits only."""

    def list_venues(self) -> list[VenueSummary]:
        """Return known venues (binance, tradestation). Config can be extended from DB/env."""
        return [
            VenueSummary(venue_id="binance", name="Binance", enabled=True, meta={}),
            VenueSummary(venue_id="tradestation", name="TradeStation", enabled=False, meta={}),
        ]
