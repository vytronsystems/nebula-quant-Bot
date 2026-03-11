# NEBULA-QUANT v1 | nq_strategy_registry — get_registration_record fail-closed and resolution

from __future__ import annotations

import unittest
import time

from nq_strategy_registry.engine import StrategyRegistryEngine
from nq_strategy_registry.models import StrategyDefinition
from nq_strategy_registry.storage import add_strategy


class TestRegistryLookup(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = StrategyRegistryEngine()

    def test_registered_strategy_resolves_correctly(self) -> None:
        self.engine.register_strategy("s1", "Strategy One", version="1.0.0", status="paper")
        result = self.engine.get_registration_record("s1")
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.record)
        self.assertEqual(result.record.strategy_id, "s1")
        self.assertEqual(result.record.lifecycle_state, "paper")
        self.assertTrue(result.record.enabled)
        self.assertEqual(result.reason_codes, [])

    def test_missing_strategy_fails_closed(self) -> None:
        result = self.engine.get_registration_record("nonexistent")
        self.assertFalse(result.ok)
        self.assertIsNone(result.record)
        self.assertIn("strategy_not_found", result.reason_codes)

    def test_missing_strategy_id_fails_closed(self) -> None:
        result = self.engine.get_registration_record("")
        self.assertFalse(result.ok)
        self.assertIn("missing_strategy_id", result.reason_codes)

    def test_malformed_record_missing_lifecycle_fails_closed(self) -> None:
        definition = StrategyDefinition(
            strategy_id="malformed_s",
            name="x",
            version="1",
            status="",
            market="US",
            instrument_type="equity",
            timeframe="1h",
            regime_target="",
            risk_profile="",
            hypothesis="",
            activation_rules={},
            deactivation_rules={},
            owner="system",
            created_at=time.time(),
            updated_at=time.time(),
        )
        add_strategy(definition)
        result = self.engine.get_registration_record("malformed_s")
        self.assertFalse(result.ok)
        self.assertIn("missing_lifecycle_state", result.reason_codes)

    def test_deterministic_same_input_same_result(self) -> None:
        self.engine.register_strategy("det_s", "Det", status="live")
        r1 = self.engine.get_registration_record("det_s")
        r2 = self.engine.get_registration_record("det_s")
        self.assertEqual(r1.ok, r2.ok)
        self.assertEqual(r1.reason_codes, r2.reason_codes)
        if r1.record and r2.record:
            self.assertEqual(r1.record.lifecycle_state, r2.record.lifecycle_state)
