# NEBULA-QUANT v1 | Phase 58 — Binance live activation tests (deterministic, no network)

from __future__ import annotations

import unittest
from typing import Any

from adapters.binance.activation import (
    BINANCE_LIVE_ACTIVATION_CONFIG,
    BinanceActivationEngine,
    BinanceActivationError,
    BinanceLiveActivationConfig,
    StrategyPerformanceMetrics,
)
from adapters.binance.execution import BinanceExecutionAdapter
from adapters.binance.models import NormalizedOrderRequest
from adapters.binance.enums import BinanceOrderSide, BinanceOrderType


# Governance enum value matching nq_strategy_governance
GOVERNANCE_APPROVED = "approved_for_live"


def _strong_metrics(strategy_id: str = "s1") -> StrategyPerformanceMetrics:
    return StrategyPerformanceMetrics(
        strategy_id=strategy_id,
        win_rate=0.62,
        rr=2.0,
        profit_factor=1.5,
        expectancy=0.5,
        max_drawdown_pct=0.10,
        shadow_trade_count=50,
        paper_trade_count=50,
    )


class TestActivationConfig(unittest.TestCase):
    def test_default_config_shadow_paper_enabled_live_disabled(self) -> None:
        cfg = BINANCE_LIVE_ACTIVATION_CONFIG
        self.assertTrue(cfg.shadow_enabled)
        self.assertTrue(cfg.paper_enabled)
        self.assertFalse(cfg.live_enabled)
        self.assertEqual(cfg.allowed_live_strategies, [])


class TestStrategyEligibility(unittest.TestCase):
    def test_strong_metrics_becomes_eligible(self) -> None:
        engine = BinanceActivationEngine()
        m = _strong_metrics("s1")
        rec = engine.evaluate_strategy_eligibility("s1", m, GOVERNANCE_APPROVED, "paper")
        self.assertTrue(rec.eligible_for_live)
        self.assertFalse(rec.not_eligible)
        self.assertEqual(rec.reasons, [])

    def test_insufficient_win_rate_not_eligible(self) -> None:
        engine = BinanceActivationEngine()
        m = StrategyPerformanceMetrics(
            strategy_id="s2",
            win_rate=0.50,
            rr=2.0,
            profit_factor=1.5,
            expectancy=0.5,
            max_drawdown_pct=0.10,
            shadow_trade_count=50,
            paper_trade_count=50,
        )
        rec = engine.evaluate_strategy_eligibility("s2", m, GOVERNANCE_APPROVED, "paper")
        self.assertFalse(rec.eligible_for_live)
        self.assertTrue(rec.not_eligible)
        self.assertIn("win_rate", rec.failed_metrics)

    def test_insufficient_rr_not_eligible(self) -> None:
        engine = BinanceActivationEngine()
        m = StrategyPerformanceMetrics(
            strategy_id="s3",
            win_rate=0.62,
            rr=1.0,
            profit_factor=1.5,
            expectancy=0.5,
            max_drawdown_pct=0.10,
            shadow_trade_count=50,
            paper_trade_count=50,
        )
        rec = engine.evaluate_strategy_eligibility("s3", m, GOVERNANCE_APPROVED, "paper")
        self.assertFalse(rec.eligible_for_live)
        self.assertIn("rr", rec.failed_metrics)

    def test_insufficient_trade_count_not_eligible(self) -> None:
        engine = BinanceActivationEngine()
        m = StrategyPerformanceMetrics(
            strategy_id="s4",
            win_rate=0.62,
            rr=2.0,
            profit_factor=1.5,
            expectancy=0.5,
            max_drawdown_pct=0.10,
            shadow_trade_count=10,
            paper_trade_count=50,
        )
        rec = engine.evaluate_strategy_eligibility("s4", m, GOVERNANCE_APPROVED, "paper")
        self.assertFalse(rec.eligible_for_live)
        self.assertIn("shadow_trade_count", rec.failed_metrics)

    def test_excessive_drawdown_not_eligible(self) -> None:
        engine = BinanceActivationEngine()
        m = StrategyPerformanceMetrics(
            strategy_id="s5",
            win_rate=0.62,
            rr=2.0,
            profit_factor=1.5,
            expectancy=0.5,
            max_drawdown_pct=0.30,
            shadow_trade_count=50,
            paper_trade_count=50,
        )
        rec = engine.evaluate_strategy_eligibility("s5", m, GOVERNANCE_APPROVED, "paper")
        self.assertFalse(rec.eligible_for_live)
        self.assertIn("max_drawdown_pct", rec.failed_metrics)

    def test_governance_required_without_approval_not_eligible(self) -> None:
        engine = BinanceActivationEngine()
        m = _strong_metrics("s6")
        rec = engine.evaluate_strategy_eligibility("s6", m, "remain_in_paper", "paper")
        self.assertFalse(rec.eligible_for_live)
        self.assertIn("governance", rec.failed_metrics)

    def test_allowed_live_strategies_updates_deterministically(self) -> None:
        cfg = BinanceLiveActivationConfig(live_enabled=False, require_governance_approval=False)
        engine = BinanceActivationEngine(config=cfg)
        candidates = [
            ("a", _strong_metrics("a"), GOVERNANCE_APPROVED, "paper"),
            ("b", _strong_metrics("b"), GOVERNANCE_APPROVED, "paper"),
        ]
        report = engine.update_allowed_live_strategies(candidates)
        self.assertEqual(set(report.eligible_strategies), {"a", "b"})
        self.assertEqual(set(cfg.allowed_live_strategies), {"a", "b"})
        # Same input again
        report2 = engine.update_allowed_live_strategies(candidates)
        self.assertEqual(report2.eligible_strategies, report.eligible_strategies)

    def test_same_input_same_eligibility_result(self) -> None:
        engine = BinanceActivationEngine()
        m = _strong_metrics("s7")
        r1 = engine.evaluate_strategy_eligibility("s7", m, GOVERNANCE_APPROVED, "paper")
        r2 = engine.evaluate_strategy_eligibility("s7", m, GOVERNANCE_APPROVED, "paper")
        self.assertEqual(r1.eligible_for_live, r2.eligible_for_live)
        self.assertEqual(r1.reasons, r2.reasons)
        self.assertEqual(r1.failed_metrics, r2.failed_metrics)

    def test_insufficient_profit_factor_not_eligible(self) -> None:
        engine = BinanceActivationEngine()
        m = StrategyPerformanceMetrics(
            strategy_id="pf",
            win_rate=0.62,
            rr=2.0,
            profit_factor=1.0,
            expectancy=0.5,
            max_drawdown_pct=0.10,
            shadow_trade_count=50,
            paper_trade_count=50,
        )
        rec = engine.evaluate_strategy_eligibility("pf", m, GOVERNANCE_APPROVED, "paper")
        self.assertFalse(rec.eligible_for_live)
        self.assertIn("profit_factor", rec.failed_metrics)


class TestActivationGating(unittest.TestCase):
    def test_live_disabled_fails_closed(self) -> None:
        cfg = BinanceLiveActivationConfig(live_enabled=False, allowed_live_strategies=["s1"])
        engine = BinanceActivationEngine(config=cfg)
        with self.assertRaises(BinanceActivationError) as ctx:
            engine.assert_live_activation_allowed("s1", venue="binance")
        self.assertIn("disabled", str(ctx.exception).lower())

    def test_non_eligible_strategy_fails_closed(self) -> None:
        cfg = BinanceLiveActivationConfig(live_enabled=True, allowed_live_strategies=[])
        engine = BinanceActivationEngine(config=cfg)
        with self.assertRaises(BinanceActivationError):
            engine.assert_live_activation_allowed("unknown", venue="binance")

    def test_binance_venue_disabled_fails_closed(self) -> None:
        cfg = BinanceLiveActivationConfig(live_enabled=True, allowed_live_strategies=["s1"])
        engine = BinanceActivationEngine(config=cfg, binance_venue_enabled=False)
        with self.assertRaises(BinanceActivationError):
            engine.assert_live_activation_allowed("s1", venue="binance")

    def test_tradestation_remains_disabled_by_default(self) -> None:
        cfg = BinanceLiveActivationConfig(live_enabled=True, allowed_live_strategies=["s1"])
        engine = BinanceActivationEngine(config=cfg, tradestation_venue_enabled=False)
        with self.assertRaises(BinanceActivationError):
            engine.assert_live_activation_allowed("s1", venue="tradestation")


class TestPaperShadowUnaffected(unittest.TestCase):
    def test_paper_shadow_flows_unaffected_by_live_gating(self) -> None:
        # Execution adapter without activation_engine: submit_order without strategy_id works (paper/shadow path)
        adapter = BinanceExecutionAdapter(safeguards=None, activation_engine=None)
        order = NormalizedOrderRequest(
            symbol="BTCUSDT",
            side=BinanceOrderSide.BUY,
            order_type=BinanceOrderType.MARKET,
            quantity=0.01,
        )
        result = adapter.submit_order(order, strategy_id=None)
        self.assertEqual(result.response.status, "NEW")
        # With strategy_id but no activation_engine: no activation check, so still works when no safeguards
        result2 = adapter.submit_order(order, strategy_id="some_id")
        self.assertEqual(result2.response.status, "NEW")

    def test_execution_adapter_with_activation_rejects_non_eligible_strategy(self) -> None:
        cfg = BinanceLiveActivationConfig(live_enabled=True, allowed_live_strategies=["allowed_only"])
        engine = BinanceActivationEngine(config=cfg)
        adapter = BinanceExecutionAdapter(safeguards=None, activation_engine=engine)
        order = NormalizedOrderRequest(
            symbol="BTCUSDT",
            side=BinanceOrderSide.BUY,
            order_type=BinanceOrderType.MARKET,
            quantity=0.01,
        )
        with self.assertRaises(BinanceActivationError):
            adapter.submit_order(order, strategy_id="not_allowed")
        # Eligible strategy passes activation gate (safeguards not set so submit continues)
        result = adapter.submit_order(order, strategy_id="allowed_only")
        self.assertEqual(result.response.status, "NEW")


if __name__ == "__main__":
    unittest.main()
