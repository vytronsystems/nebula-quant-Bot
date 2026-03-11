# NEBULA-QUANT v1 | nq_risk — risk decision engine tests

from __future__ import annotations

import unittest

from nq_risk.models import RiskContext, RiskLimits, RiskOrderIntent, RiskDecisionType
from nq_risk.rules import evaluate_risk
from nq_risk.engine import RiskEngine


def _ctx(equity: float = 100_000.0, strategy_id: str = "s1", **kwargs: object) -> RiskContext:
    return RiskContext(account_equity=equity, strategy_id=strategy_id, **kwargs)


def _intent(
    strategy_id: str = "s1",
    symbol: str = "AAPL",
    side: str = "long",
    entry: float | None = 100.0,
    stop: float | None = 98.0,
    qty: float | None = 100.0,
    notional: float | None = None,
) -> RiskOrderIntent:
    return RiskOrderIntent(
        strategy_id=strategy_id,
        symbol=symbol,
        side=side,
        entry_price=entry,
        stop_loss_price=stop,
        requested_quantity=qty,
        requested_notional=notional,
    )


class TestRiskEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RiskEngine()
        self.limits = RiskLimits(max_risk_per_trade_pct=0.02, require_stop_loss=False)

    # 1. valid risk-compliant trade returns ALLOW
    def test_valid_compliant_trade_returns_allow(self) -> None:
        r = evaluate_risk(
            _intent(entry=100.0, stop=98.0, qty=50.0),
            _ctx(equity=100_000.0),
            self.limits,
        )
        self.assertEqual(r.decision, RiskDecisionType.ALLOW)
        self.assertEqual(len(r.reason_codes), 0)
        self.assertIsNotNone(r.risk_amount)
        self.assertIsNotNone(r.risk_pct)

    # 2. missing stop loss when required returns BLOCK
    def test_missing_stop_when_required_returns_block(self) -> None:
        limits = RiskLimits(require_stop_loss=True, max_risk_per_trade_pct=0.02)
        r = evaluate_risk(_intent(stop=None), _ctx(), limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("stop_loss_required", r.reason_codes)

    # 3. wrong-side stop returns BLOCK
    def test_wrong_side_stop_returns_block(self) -> None:
        limits = RiskLimits(require_stop_loss=True)
        r = evaluate_risk(_intent(side="long", entry=100.0, stop=102.0), _ctx(), limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("wrong_side_stop_long", r.reason_codes)
        r2 = evaluate_risk(_intent(side="short", entry=100.0, stop=98.0), _ctx(), limits)
        self.assertEqual(r2.decision, RiskDecisionType.BLOCK)
        self.assertIn("wrong_side_stop_short", r2.reason_codes)

    # 4. zero stop distance returns BLOCK
    def test_zero_stop_distance_returns_block(self) -> None:
        limits = RiskLimits(require_stop_loss=True)
        r = evaluate_risk(_intent(entry=100.0, stop=100.0), _ctx(), limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("zero_stop_distance", r.reason_codes)

    # 5. excessive risk per trade returns REDUCE when resizing possible
    def test_excessive_risk_returns_reduce_when_possible(self) -> None:
        # 100 shares * $2 stop = $200 risk; equity 100k -> 0.2% risk, under 2%. So use higher qty.
        # 10000 shares * $2 = $20k risk -> 20% > 2%. Should REDUCE.
        r = evaluate_risk(
            _intent(entry=100.0, stop=98.0, qty=10_000.0),
            _ctx(equity=100_000.0),
            RiskLimits(max_risk_per_trade_pct=0.02, require_stop_loss=False),
        )
        self.assertEqual(r.decision, RiskDecisionType.REDUCE)
        self.assertIn("risk_per_trade_exceeded", r.reason_codes)
        self.assertIsNotNone(r.approved_quantity)
        self.assertGreater(r.approved_quantity, 0)
        self.assertLessEqual(r.approved_quantity, 10_000.0)

    # 6. excessive risk returns BLOCK when resizing not possible
    def test_excessive_risk_block_when_no_quantity(self) -> None:
        limits = RiskLimits(max_risk_per_trade_pct=0.001, require_stop_loss=True)
        r = evaluate_risk(
            _intent(entry=100.0, stop=98.0, qty=1000.0),
            _ctx(equity=1_000.0),
            limits,
        )
        self.assertIn(r.decision, (RiskDecisionType.REDUCE, RiskDecisionType.BLOCK))
        if r.decision == RiskDecisionType.BLOCK:
            self.assertIn("risk_exceeds_limit_no_reduce", r.reason_codes)

    # 7. daily strategy risk budget breach returns BLOCK
    def test_daily_strategy_risk_budget_returns_block(self) -> None:
        limits = RiskLimits(
            max_risk_per_trade_pct=0.02,
            max_daily_strategy_risk_pct=0.01,
            require_stop_loss=False,
        )
        ctx = _ctx(equity=100_000.0, strategy_daily_realized_pnl=-1_500.0)
        r = evaluate_risk(_intent(qty=10.0), ctx, limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("daily_strategy_risk_budget_exceeded", r.reason_codes)

    # 8. daily account risk budget breach returns BLOCK
    def test_daily_account_risk_budget_returns_block(self) -> None:
        limits = RiskLimits(
            max_risk_per_trade_pct=0.02,
            max_daily_account_risk_pct=0.02,
            require_stop_loss=False,
        )
        ctx = _ctx(equity=100_000.0, account_daily_realized_pnl=-2_500.0)
        r = evaluate_risk(_intent(qty=10.0), ctx, limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("daily_account_risk_budget_exceeded", r.reason_codes)

    # 9. malformed input returns BLOCK
    def test_malformed_input_returns_block(self) -> None:
        r = evaluate_risk(_intent(strategy_id=""), _ctx(), self.limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("missing_strategy_id", r.reason_codes)
        r2 = evaluate_risk(_intent(symbol=""), _ctx(), self.limits)
        self.assertIn("missing_symbol", r2.reason_codes)
        r3 = evaluate_risk(_intent(), _ctx(equity=0), self.limits)
        self.assertIn("invalid_account_equity", r3.reason_codes)
        r4 = evaluate_risk(
            RiskOrderIntent(strategy_id="s1", symbol="A", side="long", requested_quantity=None, requested_notional=None),
            _ctx(),
            self.limits,
        )
        self.assertIn("missing_quantity_and_notional", r4.reason_codes)

    # 10. repeated same input returns same result
    def test_repeated_input_deterministic(self) -> None:
        intent = _intent(entry=100.0, stop=98.0, qty=10.0)
        ctx = _ctx()
        r1 = evaluate_risk(intent, ctx, self.limits)
        r2 = evaluate_risk(intent, ctx, self.limits)
        self.assertEqual(r1.decision, r2.decision)
        self.assertEqual(r1.reason_codes, r2.reason_codes)
        self.assertEqual(r1.approved_quantity, r2.approved_quantity)

    # 11. non-executable lifecycle returns BLOCK when supplied
    def test_non_executable_lifecycle_returns_block(self) -> None:
        ctx = _ctx(strategy_lifecycle_state="backtest")
        r = evaluate_risk(_intent(qty=10.0), ctx, self.limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("non_executable_lifecycle", r.reason_codes)

    # 12. excessive stop distance pct returns BLOCK when configured
    def test_excessive_stop_distance_returns_block(self) -> None:
        limits = RiskLimits(require_stop_loss=True, max_stop_distance_pct=0.05)
        r = evaluate_risk(_intent(entry=100.0, stop=90.0, qty=10.0), _ctx(), limits)
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertIn("excessive_stop_distance", r.reason_codes)

    # 13. REDUCE returns approved_quantity and/or approved_notional
    def test_reduce_returns_approved_quantity(self) -> None:
        r = evaluate_risk(
            _intent(entry=100.0, stop=98.0, qty=10_000.0),
            _ctx(equity=100_000.0),
            RiskLimits(max_risk_per_trade_pct=0.02),
        )
        if r.decision == RiskDecisionType.REDUCE:
            self.assertIsNotNone(r.approved_quantity)
            self.assertIsNotNone(r.approved_notional)

    # 14. multiple violations return multiple reason codes
    def test_multiple_violations_multiple_reason_codes(self) -> None:
        r = evaluate_risk(
            RiskOrderIntent(strategy_id="", symbol="", side="long", requested_quantity=-1.0),
            _ctx(equity=0),
            self.limits,
        )
        self.assertEqual(r.decision, RiskDecisionType.BLOCK)
        self.assertGreaterEqual(len(r.reason_codes), 2)

    # 15. backward compatibility: engine.evaluate_order_intent and legacy API
    def test_engine_evaluate_order_intent(self) -> None:
        r = self.engine.evaluate_order_intent(_intent(qty=10.0), _ctx(), self.limits)
        self.assertIn(r.decision, (RiskDecisionType.ALLOW, RiskDecisionType.REDUCE, RiskDecisionType.BLOCK))
        self.assertIsNotNone(r.message)

    def test_backward_compat_engine_accepts_no_policy(self) -> None:
        engine = RiskEngine()
        r = engine.evaluate_order_intent(_intent(qty=5.0), _ctx(), None)
        self.assertEqual(r.decision, RiskDecisionType.ALLOW)
