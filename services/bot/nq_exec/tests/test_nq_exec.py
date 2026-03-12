# NEBULA-QUANT v1 | nq_exec tests — order validation, fail-closed

from __future__ import annotations

import unittest

from nq_exec import ExecutionEngine, ExecutionOrder, ExecutionResult


def valid_order() -> ExecutionOrder:
    return ExecutionOrder(
        order_id="ord_1",
        symbol="QQQ",
        side="buy",
        qty=10.0,
        order_type="market",
        limit_price=0.0,
        status="pending",
        created_ts=1000.0,
        metadata={},
    )


class TestExecutionEngineInit(unittest.TestCase):
    """Engine initialization."""

    def test_engine_creates(self) -> None:
        engine = ExecutionEngine()
        self.assertIsNotNone(engine)

    def test_engine_with_execution_disabled(self) -> None:
        engine = ExecutionEngine(execution_enabled=False)
        result = engine.submit_order(order=valid_order())
        self.assertEqual(result.status, "rejected")
        self.assertIn("disabled", result.message.lower())


class TestSubmitOrderFailClosed(unittest.TestCase):
    """Invalid order or no adapter returns rejected; no exception."""

    def test_none_order_returns_rejected(self) -> None:
        engine = ExecutionEngine()
        result = engine.submit_order(order=None)
        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.status, "rejected")
        self.assertIsInstance(result.fills, list)
        self.assertEqual(len(result.fills), 0)

    def test_missing_order_id_returns_rejected(self) -> None:
        engine = ExecutionEngine()
        order = ExecutionOrder(
            order_id="",
            symbol="QQQ",
            side="buy",
            qty=10.0,
            order_type="market",
            limit_price=0.0,
            status="pending",
            created_ts=0.0,
            metadata={},
        )
        result = engine.submit_order(order=order)
        self.assertEqual(result.status, "rejected")
        self.assertIn("order_id", result.message.lower() or "")

    def test_zero_qty_returns_rejected(self) -> None:
        engine = ExecutionEngine()
        order = ExecutionOrder(
            order_id="o1",
            symbol="QQQ",
            side="buy",
            qty=0.0,
            order_type="market",
            limit_price=0.0,
            status="pending",
            created_ts=0.0,
            metadata={},
        )
        result = engine.submit_order(order=order)
        self.assertEqual(result.status, "rejected")
        self.assertIn("qty", result.message.lower() or "")

    def test_no_adapter_returns_rejected(self) -> None:
        engine = ExecutionEngine(adapter=None, execution_enabled=True)
        result = engine.submit_order(order=valid_order())
        self.assertEqual(result.status, "rejected")
        self.assertIn("adapter", result.message.lower())


class TestDeterminism(unittest.TestCase):
    """Same invalid input produces same rejected result."""

    def test_same_invalid_order_same_message(self) -> None:
        engine = ExecutionEngine()
        r1 = engine.submit_order(order=None)
        r2 = engine.submit_order(order=None)
        self.assertEqual(r1.status, r2.status)
        self.assertEqual(r1.message, r2.message)
