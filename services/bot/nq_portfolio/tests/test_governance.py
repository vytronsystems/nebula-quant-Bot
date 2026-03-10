# NEBULA-QUANT v1 | nq_portfolio — governance (portfolio risk engine) tests

from __future__ import annotations

import unittest

from nq_portfolio.models import (
    OrderIntent,
    PortfolioDecisionType,
    PortfolioLimits,
    PortfolioState,
    PositionSnapshot,
    StrategyAllocation,
)
from nq_portfolio.governance import evaluate_order_intent, PortfolioRiskEngine


def _base_state() -> PortfolioState:
    return PortfolioState(
        portfolio_equity=1_000_000.0,
        cash_available=500_000.0,
        open_positions=[],
        strategy_allocations=[
            StrategyAllocation(
                strategy_id="s1",
                allocated_capital=200_000.0,
                used_capital=0.0,
                max_positions=10,
                strategy_enabled=True,
                strategy_lifecycle_state="paper",
            ),
        ],
        daily_pnl=0.0,
        strategy_daily_pnl={"s1": 0.0},
    )


def _base_limits() -> PortfolioLimits:
    return PortfolioLimits(
        max_portfolio_capital_usage_pct=0.95,
        max_strategy_capital_usage_pct=0.25,
        max_open_positions_total=50,
        max_open_positions_per_strategy=10,
        max_daily_drawdown_pct=0.05,
        max_strategy_drawdown_pct=0.10,
        warning_capital_usage_pct=0.80,
        warning_open_positions_pct=0.85,
        warning_drawdown_pct=0.03,
    )


def _intent(strategy_id: str = "s1", notional: float = 10_000.0, quantity: float = 100.0) -> OrderIntent:
    return OrderIntent(
        strategy_id=strategy_id,
        symbol="AAPL",
        requested_notional=notional,
        requested_quantity=quantity,
        side="long",
        timestamp=0.0,
    )


# --- 1. valid order returns ALLOW ---
class TestGovernance(unittest.TestCase):
    # --- 1. valid order returns ALLOW ---
    def test_valid_order_returns_allow(self) -> None:
        d = evaluate_order_intent(_intent(), _base_state(), _base_limits())
        self.assertEqual(d.decision, PortfolioDecisionType.ALLOW)
        self.assertEqual(d.reason_codes, [])
        self.assertIsNone(d.throttle_ratio)

    # --- 2. strategy disabled returns BLOCK ---
    def test_strategy_disabled_returns_block(self) -> None:
        state = _base_state()
        state.strategy_allocations[0].strategy_enabled = False
        d = evaluate_order_intent(_intent(), state, _base_limits())
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("strategy_disabled", d.reason_codes)

    # --- 3. missing allocation returns BLOCK ---
    def test_missing_allocation_returns_block(self) -> None:
        state = _base_state()
        state.strategy_allocations = []
        d = evaluate_order_intent(_intent(), state, _base_limits())
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("missing_allocation", d.reason_codes)

    # --- 4. strategy capital overflow returns BLOCK ---
    def test_strategy_capital_overflow_returns_block(self) -> None:
        limits = _base_limits()
        limits.max_strategy_capital_usage_pct = 0.25
        state = _base_state()
        state.strategy_allocations[0].allocated_capital = 100_000.0
        state.open_positions = [
            PositionSnapshot("p1", "s1", "AAPL", notional_value=26_000.0),
        ]
        d = evaluate_order_intent(_intent(notional=5_000.0), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("strategy_capital_overflow", d.reason_codes)

    # --- 5. portfolio capital overflow returns BLOCK ---
    def test_portfolio_capital_overflow_returns_block(self) -> None:
        limits = _base_limits()
        limits.max_portfolio_capital_usage_pct = 0.50
        state = _base_state()
        state.open_positions = [
            PositionSnapshot("p1", "s1", "AAPL", notional_value=400_000.0),
        ]
        d = evaluate_order_intent(_intent(notional=150_000.0), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("portfolio_capital_overflow", d.reason_codes)

    # --- 6. open positions overflow returns BLOCK ---
    def test_open_positions_overflow_returns_block(self) -> None:
        limits = _base_limits()
        limits.max_open_positions_total = 3
        state = _base_state()
        state.open_positions = [
            PositionSnapshot("p1", "s1", "A", notional_value=1.0),
            PositionSnapshot("p2", "s1", "B", notional_value=1.0),
            PositionSnapshot("p3", "s1", "C", notional_value=1.0),
        ]
        d = evaluate_order_intent(_intent(), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("open_positions_overflow", d.reason_codes)

    # --- 7. near limits returns THROTTLE ---
    def test_near_limits_returns_throttle(self) -> None:
        limits = _base_limits()
        limits.warning_drawdown_pct = 0.02
        limits.max_daily_drawdown_pct = 0.05
        state = _base_state()
        state.daily_pnl = -20_000.0  # 2% of 1M -> at warning
        d = evaluate_order_intent(_intent(), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.THROTTLE)
        self.assertTrue("near_limit" in d.reason_codes[0] or "drawdown" in str(d.reason_codes))

    # --- 8. daily drawdown breach returns BLOCK ---
    def test_daily_drawdown_breach_returns_block(self) -> None:
        limits = _base_limits()
        limits.max_daily_drawdown_pct = 0.05
        state = _base_state()
        state.daily_pnl = -60_000.0  # 6% of 1M
        d = evaluate_order_intent(_intent(), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("daily_drawdown_breach", d.reason_codes)

    # --- 9. malformed input returns BLOCK ---
    def test_malformed_intent_returns_block(self) -> None:
        d = evaluate_order_intent(
            OrderIntent(strategy_id="", symbol="AAPL"),
            _base_state(),
            _base_limits(),
        )
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("malformed_intent", d.reason_codes)

    def test_missing_input_returns_block(self) -> None:
        d = evaluate_order_intent(None, _base_state(), _base_limits())
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("missing_input", d.reason_codes)

    # --- 10. repeated input returns deterministic decision ---
    def test_repeated_input_deterministic(self) -> None:
        intent = _intent()
        state = _base_state()
        limits = _base_limits()
        d1 = evaluate_order_intent(intent, state, limits)
        d2 = evaluate_order_intent(intent, state, limits)
        self.assertEqual(d1.decision, d2.decision)
        self.assertEqual(d1.reason_codes, d2.reason_codes)
        self.assertEqual(d1.message, d2.message)

    # --- 11. THROTTLE populates throttle_ratio ---
    def test_throttle_populates_throttle_ratio(self) -> None:
        limits = _base_limits()
        limits.warning_capital_usage_pct = 0.50
        limits.max_portfolio_capital_usage_pct = 0.95
        state = _base_state()
        state.strategy_allocations[0].allocated_capital = 3_000_000.0
        state.open_positions = [
            PositionSnapshot("p1", "s1", "X", notional_value=450_000.0),
        ]
        d = evaluate_order_intent(_intent(notional=100_000.0), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.THROTTLE)
        self.assertIsNotNone(d.throttle_ratio)
        self.assertGreaterEqual(d.throttle_ratio, 0.0)
        self.assertLessEqual(d.throttle_ratio, 1.0)

    # --- 12. THROTTLE includes recommended reduction metadata ---
    def test_throttle_includes_recommended_metadata(self) -> None:
        limits = _base_limits()
        limits.warning_capital_usage_pct = 0.50
        limits.max_portfolio_capital_usage_pct = 0.95
        state = _base_state()
        state.strategy_allocations[0].allocated_capital = 3_000_000.0
        state.open_positions = [
            PositionSnapshot("p1", "s1", "X", notional_value=450_000.0),
        ]
        d = evaluate_order_intent(_intent(notional=100_000.0), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.THROTTLE)
        self.assertIsNotNone(d.metadata)
        self.assertIn("applied_warning_domains", d.metadata)
        self.assertTrue("recommended_notional" in d.metadata or "recommended_quantity" in d.metadata)

    # --- 13. multiple violations return multiple reason codes ---
    def test_multiple_violations_multiple_reason_codes(self) -> None:
        limits = _base_limits()
        limits.max_open_positions_total = 2
        limits.max_daily_drawdown_pct = 0.05
        state = _base_state()
        state.open_positions = [
            PositionSnapshot("p1", "s1", "A", notional_value=1.0),
            PositionSnapshot("p2", "s1", "B", notional_value=1.0),
        ]
        state.daily_pnl = -60_000.0
        d = evaluate_order_intent(_intent(), state, limits)
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("open_positions_overflow", d.reason_codes)
        self.assertIn("daily_drawdown_breach", d.reason_codes)
        self.assertGreaterEqual(len(d.reason_codes), 2)

    # --- Lifecycle: non-executable states BLOCK ---
    def test_lifecycle_backtest_returns_block(self) -> None:
        state = _base_state()
        state.strategy_allocations[0].strategy_lifecycle_state = "backtest"
        d = evaluate_order_intent(_intent(), state, _base_limits())
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("lifecycle_not_executable", d.reason_codes)

    def test_lifecycle_live_returns_allow(self) -> None:
        state = _base_state()
        state.strategy_allocations[0].strategy_lifecycle_state = "live"
        d = evaluate_order_intent(_intent(), state, _base_limits())
        self.assertEqual(d.decision, PortfolioDecisionType.ALLOW)

    # --- Drawdown formula ---
    def test_drawdown_formula_zero_equity_guarded(self) -> None:
        state = _base_state()
        state.portfolio_equity = 0.0
        d = evaluate_order_intent(_intent(), state, _base_limits())
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("invalid_equity", d.reason_codes)

    # --- PortfolioRiskEngine class ---
    def test_risk_engine_evaluate(self) -> None:
        engine = PortfolioRiskEngine()
        d = engine.evaluate(_intent(), _base_state())
        self.assertEqual(d.decision, PortfolioDecisionType.ALLOW)

    def test_risk_engine_uses_provided_limits(self) -> None:
        strict = PortfolioLimits(max_open_positions_total=0)
        engine = PortfolioRiskEngine(limits=strict)
        d = engine.evaluate(_intent(), _base_state())
        self.assertEqual(d.decision, PortfolioDecisionType.BLOCK)
        self.assertIn("open_positions_overflow", d.reason_codes)
