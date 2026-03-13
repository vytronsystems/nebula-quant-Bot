"""Tests for cross-venue services."""
from __future__ import annotations

import unittest

from nq_cross_venue import VenueAbstractionService
from nq_cross_venue.models import VenueSummary
from nq_cross_venue.risk_movement import RiskMovementRequest, risk_movement_hook


class TestVenueAbstractionService(unittest.TestCase):
    def test_list_venues(self) -> None:
        svc = VenueAbstractionService()
        venues = svc.list_venues()
        self.assertIsInstance(venues, list)
        self.assertGreaterEqual(len(venues), 1)
        self.assertTrue(any(v.venue_id == "binance" for v in venues))


class TestRiskMovementHook(unittest.TestCase):
    def test_default_rejects(self) -> None:
        req = RiskMovementRequest(from_venue="binance", to_venue="tradestation", amount=1000.0, reason="test")
        result = risk_movement_hook(req)
        self.assertFalse(result.approved)
