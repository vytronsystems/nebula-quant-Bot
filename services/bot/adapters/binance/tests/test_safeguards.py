# NEBULA-QUANT v1 | Binance safeguards tests (deterministic, no network)

from __future__ import annotations

import unittest
from typing import Any

from adapters.binance.safeguards import (
    BinanceLiveSafeguards,
    BinanceSafeguardError,
)
from adapters.binance.execution import BinanceExecutionAdapter
from adapters.binance.enums import BinanceOrderSide, BinanceOrderType
from adapters.binance.models import NormalizedOrderRequest


def _fixed_clock() -> float:
    return 2000000.0


class _MockConfig:
    binance_live_enabled = True
    binance_reset_hour_utc = 0
    binance_max_daily_loss = 5000.0
    binance_max_order_rate_per_minute = 10
    binance_max_position_size = 1.0
    binance_max_notional_per_order = 100_000.0
    binance_max_open_positions = 5
    binance_heartbeat_timeout_seconds = 60.0
    binance_rolling_window_minutes = 5


class TestBinanceSafeguards(unittest.TestCase):
    def test_venue_disabled_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=False, clock=_fixed_clock)
        d = sg.check_venue_enabled()
        self.assertFalse(d.allowed)
        self.assertIn("disabled", d.reason.lower())

    def test_binance_live_disabled_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=False, clock=_fixed_clock)
        with self.assertRaises(BinanceSafeguardError):
            sg.assert_can_send_live()

    def test_kill_switch_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, kill_switch_active=True, clock=_fixed_clock)
        sg.set_heartbeat(_fixed_clock())
        d = sg.check_kill_switch()
        self.assertFalse(d.allowed)
        with self.assertRaises(BinanceSafeguardError):
            sg.assert_can_send_live()

    def test_leverage_above_2_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, clock=_fixed_clock)
        sg.set_heartbeat(_fixed_clock())
        d = sg.check_leverage(3)
        self.assertFalse(d.allowed)

    def test_max_daily_loss_breach_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, clock=_fixed_clock)
        sg.set_heartbeat(_fixed_clock())
        sg.record_daily_loss_delta(-6000.0)
        d = sg.check_max_daily_loss()
        self.assertFalse(d.allowed)

    def test_max_position_size_breach_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(config=_MockConfig(), venue_enabled=True, clock=_fixed_clock)
        d = sg.check_max_position_size(2.0)
        self.assertFalse(d.allowed)

    def test_max_notional_per_order_breach_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, clock=_fixed_clock)
        d = sg.check_max_notional_per_order(200_000.0)
        self.assertFalse(d.allowed)

    def test_order_rate_limit_breach_fails_closed(self) -> None:
        cfg = _MockConfig()
        cfg.binance_max_order_rate_per_minute = 2
        sg = BinanceLiveSafeguards(config=cfg, venue_enabled=True, clock=_fixed_clock)
        sg.set_heartbeat(_fixed_clock())
        sg.record_order()
        sg.record_order()
        d = sg.check_order_rate_limit()
        self.assertFalse(d.allowed)

    def test_stale_heartbeat_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, clock=_fixed_clock)
        self.assertFalse(sg.check_heartbeat().allowed)
        with self.assertRaises(BinanceSafeguardError):
            sg.assert_can_send_live()

    def test_rolling_window_checks_deterministic(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, clock=_fixed_clock)
        sg.set_heartbeat(_fixed_clock())
        sg.record_order()
        s1 = sg.get_state()
        s2 = sg.get_state()
        self.assertEqual(s1.orders_in_window, s2.orders_in_window)

    def test_utc_reset_window_deterministic(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, clock=_fixed_clock)
        sg.set_heartbeat(_fixed_clock())
        sg.record_daily_loss_delta(-100.0)
        s = sg.get_state()
        self.assertIsInstance(s.utc_day_key, str)
        self.assertEqual(len(s.utc_day_key), 10)

    def test_execution_adapter_with_safeguards_kill_switch_fails_closed(self) -> None:
        sg = BinanceLiveSafeguards(venue_enabled=True, kill_switch_active=True, clock=_fixed_clock)
        sg.set_heartbeat(_fixed_clock())
        adapter = BinanceExecutionAdapter(safeguards=sg)
        order = NormalizedOrderRequest(
            symbol="BTCUSDT",
            side=BinanceOrderSide.BUY,
            order_type=BinanceOrderType.MARKET,
            quantity=0.01,
        )
        with self.assertRaises(BinanceSafeguardError):
            adapter.submit_order(order)

    def test_execution_adapter_without_safeguards_still_works(self) -> None:
        adapter = BinanceExecutionAdapter(safeguards=None)
        order = NormalizedOrderRequest(
            symbol="BTCUSDT",
            side=BinanceOrderSide.BUY,
            order_type=BinanceOrderType.MARKET,
            quantity=0.01,
        )
        result = adapter.submit_order(order)
        self.assertEqual(result.response.status, "NEW")


if __name__ == "__main__":
    unittest.main()
