# NEBULA-QUANT v1 | nq_promotion — registry integration tests

from __future__ import annotations

import unittest

from nq_strategy_registry.engine import StrategyRegistryEngine
from nq_promotion.engine import PromotionEngine
from nq_promotion.integration import (
    check_execution_eligibility,
    resolve_lifecycle_from_registry,
    validate_transition_with_registry,
)
from nq_promotion.models import ExecutionEligibilityResult, PromotionTransitionDecision


class TestPromotionRegistryIntegration(unittest.TestCase):
    """Integration: lifecycle from registry, transition validation, execution eligibility."""

    def setUp(self) -> None:
        self.registry = StrategyRegistryEngine()
        self.promotion = PromotionEngine()

    # --- 1. registered strategy with valid lifecycle resolves correctly ---
    def test_registered_strategy_valid_lifecycle_resolves(self) -> None:
        self.registry.register_strategy("r1", "R1", status="paper")
        state, codes, msg = resolve_lifecycle_from_registry(self.registry, "r1")
        self.assertEqual(state, "paper")
        self.assertEqual(codes, [])
        self.assertEqual(msg, "ok")

    # --- 2. missing strategy registration fails closed ---
    def test_missing_strategy_fails_closed(self) -> None:
        d = validate_transition_with_registry(self.registry, "nonexistent", "live")
        self.assertFalse(d.allowed)
        self.assertIn("strategy_not_found", d.reason_codes)
        e = check_execution_eligibility(self.registry, "nonexistent")
        self.assertFalse(e.executable)
        self.assertIn("strategy_not_found", e.reason_codes)

    # --- 3. missing lifecycle state fails closed ---
    def test_missing_lifecycle_state_fails_closed(self) -> None:
        from nq_strategy_registry.models import StrategyDefinition
        from nq_strategy_registry.storage import add_strategy
        import time
        add_strategy(StrategyDefinition(
            strategy_id="no_state",
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
        ))
        d = validate_transition_with_registry(self.registry, "no_state", "paper")
        self.assertFalse(d.allowed)
        self.assertIn("missing_lifecycle_state", d.reason_codes)

    # --- 4. malformed registry record fails closed (covered by empty status above) ---
    # --- 5. allowed transition succeeds ---
    def test_allowed_transition_succeeds(self) -> None:
        self.registry.register_strategy("t1", "T1", status="backtest")
        d = validate_transition_with_registry(self.registry, "t1", "walkforward")
        self.assertTrue(d.allowed)
        self.assertEqual(d.reason_codes, [])
        self.assertEqual(d.message, "ok")

    # --- 6. invalid transition is rejected ---
    def test_invalid_transition_rejected(self) -> None:
        self.registry.register_strategy("t2", "T2", status="idea")
        d = validate_transition_with_registry(self.registry, "t2", "live")
        self.assertFalse(d.allowed)
        self.assertIn("transition_not_allowed", d.reason_codes)

    # --- 7. retired -> active transition is rejected ---
    def test_retired_to_active_rejected(self) -> None:
        self.registry.register_strategy("t3", "T3", status="retired")
        d = validate_transition_with_registry(self.registry, "t3", "paper")
        self.assertFalse(d.allowed)
        self.assertIn("retired_not_reactivatable", d.reason_codes)

    # --- 8. unknown target state is rejected ---
    def test_unknown_target_state_rejected(self) -> None:
        self.registry.register_strategy("t4", "T4", status="paper")
        d = validate_transition_with_registry(self.registry, "t4", "invalid_state")
        self.assertFalse(d.allowed)
        self.assertIn("unknown_target_state", d.reason_codes)

    # --- 9. execution eligibility true only for paper/live ---
    def test_execution_eligibility_true_for_paper_and_live(self) -> None:
        self.registry.register_strategy("e1", "E1", status="paper")
        e = check_execution_eligibility(self.registry, "e1")
        self.assertTrue(e.executable)
        self.assertEqual(e.lifecycle_state, "paper")
        self.registry.register_strategy("e2", "E2", status="live")
        e2 = check_execution_eligibility(self.registry, "e2")
        self.assertTrue(e2.executable)
        self.assertEqual(e2.lifecycle_state, "live")

    # --- 10. execution eligibility false for idea/research/backtest/walkforward/retired ---
    def test_execution_eligibility_false_for_non_executable_states(self) -> None:
        for state in ("idea", "research", "backtest", "walkforward", "retired"):
            sid = f"ex_{state}"
            self.registry.register_strategy(sid, sid, status=state)
            r = check_execution_eligibility(self.registry, sid)
            self.assertFalse(r.executable, f"state {state} should not be executable")
            self.assertIn("lifecycle_not_executable", r.reason_codes)

    # --- 11. repeated same input returns same deterministic result ---
    def test_repeated_input_deterministic(self) -> None:
        self.registry.register_strategy("rep", "Rep", status="paper")
        d1 = validate_transition_with_registry(self.registry, "rep", "live")
        d2 = validate_transition_with_registry(self.registry, "rep", "live")
        self.assertEqual(d1.allowed, d2.allowed)
        self.assertEqual(d1.reason_codes, d2.reason_codes)
        e1 = check_execution_eligibility(self.registry, "rep")
        e2 = check_execution_eligibility(self.registry, "rep")
        self.assertEqual(e1.executable, e2.executable)
        self.assertEqual(e1.reason_codes, e2.reason_codes)

    # --- 12. duplicate or ambiguous registry state: current storage has one per id, so no duplicate ---
    # If multiple records for same id existed we would fail closed; storage guarantees one per id.
    def test_single_record_per_id_no_ambiguity(self) -> None:
        self.registry.register_strategy("single", "Single", status="live")
        result = self.registry.get_registration_record("single")
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.record)
        self.assertEqual(result.record.strategy_id, "single")

    # --- 13. backward compatibility: evaluate_promotion still works with caller-provided current_status ---
    def test_backward_compat_evaluate_promotion(self) -> None:
        from nq_promotion.models import PromotionInput
        inp = PromotionInput(strategy_id="bc", current_status="backtest")
        res = self.promotion.evaluate_promotion(promotion_input=inp, target_status="walkforward")
        self.assertIsNotNone(res.decision)
        self.assertEqual(res.decision.from_status, "backtest")
        self.assertEqual(res.decision.to_status, "walkforward")

    # --- Engine API: evaluate_transition_with_registry and get_execution_eligibility ---
    def test_engine_evaluate_transition_with_registry(self) -> None:
        self.registry.register_strategy("eng1", "Eng1", status="walkforward")
        d = self.promotion.evaluate_transition_with_registry(self.registry, "eng1", "paper")
        self.assertTrue(d.allowed)

    def test_engine_get_execution_eligibility(self) -> None:
        self.registry.register_strategy("eng2", "Eng2", status="live")
        e = self.promotion.get_execution_eligibility(self.registry, "eng2")
        self.assertTrue(e.executable)
        self.assertEqual(e.lifecycle_state, "live")
