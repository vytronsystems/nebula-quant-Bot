# NEBULA-QUANT v1 | Binance paper/shadow tests (deterministic, no network)

from __future__ import annotations

import unittest
from typing import Any

from adapters.binance.paper import BinancePaperTradingEngine
from adapters.binance.models import BinanceValidationError


def _fixed_clock() -> float:
    return 1000000.0


class TestBinancePaper(unittest.TestCase):
    def test_paper_session_starts_correctly(self) -> None:
        engine = BinancePaperTradingEngine(mode="paper", initial_cash_usdt=50_000.0, clock=_fixed_clock)
        engine.start_session("s1")
        state = engine.get_session_state()
        self.assertEqual(state.cash_usdt, 50_000.0)
        self.assertEqual(len(state.orders), 0)
        self.assertEqual(len(state.fills), 0)

    def test_paper_order_submission_updates_state_deterministically(self) -> None:
        engine = BinancePaperTradingEngine(mode="paper", initial_cash_usdt=100_000.0, clock=_fixed_clock)
        engine.start_session("s2")
        order = engine.submit_paper_order("BTCUSDT", "BUY", "MARKET", 0.01, client_order_id="c1")
        self.assertEqual(order.status, "FILLED")
        state = engine.get_session_state()
        self.assertEqual(len(state.orders), 1)
        self.assertEqual(len(state.fills), 1)
        self.assertEqual(len(state.positions), 1)
        self.assertEqual(state.positions[0].symbol, "BTCUSDT")

    def test_paper_fill_and_position_tracking_deterministic(self) -> None:
        engine = BinancePaperTradingEngine(mode="paper", initial_cash_usdt=100_000.0, clock=_fixed_clock)
        engine.start_session("s3")
        engine.submit_paper_order("BTCUSDT", "BUY", "MARKET", 0.01)
        engine.submit_paper_order("BTCUSDT", "BUY", "MARKET", 0.01)
        state = engine.get_session_state()
        self.assertEqual(len(state.fills), 2)
        self.assertEqual(len(state.positions), 1)
        self.assertAlmostEqual(state.positions[0].position_amt, 0.02)

    def test_shadow_mode_records_intended_orders_without_fills(self) -> None:
        engine = BinancePaperTradingEngine(mode="shadow", initial_cash_usdt=100_000.0, clock=_fixed_clock)
        engine.start_session("s4")
        engine.submit_paper_order("BTCUSDT", "BUY", "MARKET", 0.01)
        state = engine.get_session_state()
        self.assertEqual(len(state.orders), 1)
        self.assertEqual(state.orders[0].status, "PENDING")
        self.assertEqual(len(state.fills), 0)
        report = engine.build_session_report()
        self.assertEqual(report.mode, "shadow")
        self.assertEqual(len(report.intended_orders_shadow), 1)

    def test_same_input_same_paper_results(self) -> None:
        def run() -> tuple[float, int]:
            e = BinancePaperTradingEngine(mode="paper", initial_cash_usdt=100_000.0, clock=_fixed_clock)
            e.start_session("same")
            e.submit_paper_order("BTCUSDT", "SELL", "MARKET", 0.005)
            r = e.build_session_report()
            return r.final_cash, r.fills_count
        a, b = run(), run()
        self.assertEqual(a, b)

    def test_unsupported_symbol_fails_closed(self) -> None:
        engine = BinancePaperTradingEngine(mode="paper", clock=_fixed_clock)
        engine.start_session("s5")
        with self.assertRaises(BinanceValidationError):
            engine.submit_paper_order("ETHUSDT", "BUY", "MARKET", 0.01)

    def test_process_bar_returns_hold_without_strategy(self) -> None:
        engine = BinancePaperTradingEngine(mode="paper", clock=_fixed_clock)
        engine.start_session("s6")
        bar = {"ts": 1000.0, "close": 50000.0}
        self.assertEqual(engine.process_bar(bar, strategy=None), "hold")

    def test_process_bar_invokes_strategy(self) -> None:
        engine = BinancePaperTradingEngine(mode="paper", clock=_fixed_clock)
        engine.start_session("s7")

        def strat(bar: Any) -> str:
            return "long"

        bar = {"ts": 1000.0, "close": 50000.0}
        self.assertEqual(engine.process_bar(bar, strategy=strat), "long")


if __name__ == "__main__":
    unittest.main()
