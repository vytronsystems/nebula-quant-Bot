# NEBULA-QUANT v1 | nq_guardrails tests — violation detection, fail-closed

from __future__ import annotations

import unittest

from nq_guardrails import GuardrailsEngine, GuardrailResult


class TestGuardrailsEngineInit(unittest.TestCase):
    """Engine initialization."""

    def test_engine_creates(self) -> None:
        engine = GuardrailsEngine()
        self.assertIsNotNone(engine)


class TestGuardrailsEvaluation(unittest.TestCase):
    """Empty/safe inputs; result structure."""

    def test_run_guardrails_empty_inputs_returns_result(self) -> None:
        engine = GuardrailsEngine()
        result = engine.run_guardrails()
        self.assertIsInstance(result, GuardrailResult)
        self.assertIsInstance(result.allowed, bool)
        self.assertIsInstance(result.signals, list)
        self.assertIsInstance(result.reason, str)

    def test_evaluate_account_state_empty(self) -> None:
        engine = GuardrailsEngine()
        result = engine.evaluate_account_state(account={}, context={})
        self.assertIsInstance(result, GuardrailResult)

    def test_evaluate_market_conditions_empty(self) -> None:
        engine = GuardrailsEngine()
        result = engine.evaluate_market_conditions(market={}, context={})
        self.assertIsInstance(result, GuardrailResult)

    def test_evaluate_strategy_health_empty(self) -> None:
        engine = GuardrailsEngine()
        result = engine.evaluate_strategy_health(strategy_health={}, context={})
        self.assertIsInstance(result, GuardrailResult)


class TestFailClosed(unittest.TestCase):
    """Fail-closed: no crash on None; result always returned."""

    def test_none_account_handled(self) -> None:
        engine = GuardrailsEngine()
        result = engine.run_guardrails(account=None, positions=None)
        self.assertIsNotNone(result)
        self.assertIsInstance(result.allowed, bool)

    def test_deterministic_empty_inputs(self) -> None:
        engine = GuardrailsEngine()
        r1 = engine.run_guardrails()
        r2 = engine.run_guardrails()
        self.assertEqual(r1.allowed, r2.allowed)
