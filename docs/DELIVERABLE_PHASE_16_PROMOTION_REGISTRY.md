# NEBULA-QUANT v1 | Phase 16 — Integrate nq_promotion with nq_strategy_registry | Deliverable

---

## 1) SUMMARY

**Implemented:**
- **nq_strategy_registry** as source of truth: added `StrategyRegistrationRecord` (strategy_id, version, lifecycle_state, enabled, metadata) and `RegistryLookupResult` (ok, record, reason_codes, message). Added `get_registration_record(strategy_id)` on `StrategyRegistryEngine` with fail-closed behavior (missing id, not found, missing/malformed lifecycle state → ok=False and reason_codes).
- **nq_promotion** as authorized transition engine: added `integration.py` with `resolve_lifecycle_from_registry`, `validate_transition_with_registry` (current state from registry only), and `check_execution_eligibility` (registered and lifecycle in {paper, live}). Added models `PromotionTransitionRequest`, `PromotionTransitionDecision`, `ExecutionEligibilityResult`. `PromotionEngine` now exposes `evaluate_transition_with_registry(registry_engine, strategy_id, target_state)` and `get_execution_eligibility(registry_engine, strategy_id)`.
- **status_map**: added `OFFICIAL_LIFECYCLE_STATES` and `EXECUTION_COMPATIBLE_STATES`; unknown target/current state and retired→active are rejected.
- **nq_strategy_registry/status**: added `STATUS_WALKFORWARD` and `EXECUTION_COMPATIBLE_STATUSES` for alignment.

**Refactored:**
- No breaking refactors. Existing `evaluate_promotion(PromotionInput, target_status)` unchanged; callers can keep using caller-provided `current_status` for evidence-based promotion. New registry-backed APIs are additive.

**Compatibility:**
- Backward compatible: `PromotionInput`, `PromotionDecision`, `PromotionResult` and `evaluate_promotion` unchanged. Downstream (e.g. nq_portfolio) can continue using their own lifecycle source until wired to registry; when ready, they call `get_execution_eligibility(registry, strategy_id)` or use registry-backed lifecycle for allocations.

---

## 2) FILE TREE

**Created:**
- `services/bot/nq_promotion/integration.py`
- `services/bot/nq_promotion/tests/__init__.py`
- `services/bot/nq_promotion/tests/test_integration.py`
- `services/bot/nq_strategy_registry/tests/__init__.py`
- `services/bot/nq_strategy_registry/tests/test_registry_lookup.py`

**Modified:**
- `services/bot/nq_promotion/__init__.py` — exports for integration and new models
- `services/bot/nq_promotion/engine.py` — `evaluate_transition_with_registry`, `get_execution_eligibility`
- `services/bot/nq_promotion/models.py` — `PromotionTransitionRequest`, `PromotionTransitionDecision`, `ExecutionEligibilityResult`
- `services/bot/nq_promotion/status_map.py` — `OFFICIAL_LIFECYCLE_STATES`, `EXECUTION_COMPATIBLE_STATES`
- `services/bot/nq_strategy_registry/__init__.py` — exports `StrategyRegistrationRecord`, `RegistryLookupResult`
- `services/bot/nq_strategy_registry/engine.py` — `get_registration_record`
- `services/bot/nq_strategy_registry/models.py` — `StrategyRegistrationRecord`, `RegistryLookupResult`
- `services/bot/nq_strategy_registry/status.py` — `STATUS_WALKFORWARD`, `EXECUTION_COMPATIBLE_STATUSES`

---

## 3) ARCHITECTURE NOTES

- **Registry ↔ promotion:** nq_strategy_registry owns registration and persisted lifecycle state (status). nq_promotion does not own storage; it calls `registry_engine.get_registration_record(strategy_id)` to get current state, then validates the requested transition with `is_transition_allowed(current, target)`. Transitions are not applied inside promotion; promotion only returns allowed/not allowed (caller or registry applies the update).
- **Lifecycle truth:** Resolved only from registry via `get_registration_record`. Caller-provided lifecycle is not used for `validate_transition_with_registry` or `check_execution_eligibility`.
- **Execution eligibility:** A strategy is executable iff it is registered and `lifecycle_state in {paper, live}`. Determined by `check_execution_eligibility(registry_engine, strategy_id)` returning `ExecutionEligibilityResult(executable=..., lifecycle_state=..., reason_codes, message)`.
- **Integration status:** API and logic are in place; downstream (nq_portfolio, nq_exec, nq_guardrails) can call the new helpers but are not yet wired in this phase. Therefore: **READY_FOR_INTEGRATION** (deterministic helper/API exposed; wiring to portfolio/exec left for a follow-up).

---

## 4) VERIFICATION RESULTS

**Commands run:**

```bash
# nq_promotion integration tests
PYTHONPATH=services/bot python3 -m unittest discover -s services/bot/nq_promotion/tests -p "test_*.py" -v
# Result: Ran 14 tests in 0.001s — OK

# nq_strategy_registry tests
PYTHONPATH=services/bot python3 -m unittest discover -s services/bot/nq_strategy_registry/tests -p "test_*.py" -v
# Result: Ran 5 tests in 0.000s — OK

# nq_portfolio tests (regression)
PYTHONPATH=services/bot python3 -m unittest discover -s services/bot/nq_portfolio/tests -p "test_*.py" -v
# Result: Ran 19 tests in 0.002s — OK
```

**Failed checks:** None.

---

## 5) GIT STATUS

- **Branch:** `feature/promotion-registry-integration`
- **Commit:** `bd1bec7`
- **Message:** `nq_promotion: integrate lifecycle governance with strategy registry`
- **Remote:** Pushed to `origin/feature/promotion-registry-integration` (tracking set).

---

## 6) RISKS / FOLLOW-UPS

- **Wiring:** nq_portfolio and nq_exec (or the step before exec) should eventually resolve lifecycle from registry (e.g. via `get_execution_eligibility` or by building `StrategyAllocation.strategy_lifecycle_state` from registry) so execution eligibility is consistent. Today nq_portfolio uses allocation-provided lifecycle; that can be fed from registry in a later change.
- **Apply transition:** Promotion only validates; the actual status update is still `registry_engine.update_strategy_status(strategy_id, new_status)`. Orchestration (e.g. after evidence checks) should call promotion to validate, then registry to update.
- **Duplicate/ambiguous:** Current storage is one record per strategy_id; if the registry later supports multiple versions per id, lookup must define behavior (e.g. latest only or explicit version) and fail closed on ambiguity.

**Next steps:** Wire execution path to use `get_execution_eligibility(registry, strategy_id)` and, where appropriate, build allocation lifecycle from registry; add/update orchestration to validate transitions via promotion before updating registry status.

---

## 7) ARCHITECTURE GATE RESULT

**ARCHITECTURE_APPROVED**

- Only nq_promotion and nq_strategy_registry touched; no pipeline change; registry remains source of truth, promotion remains transition validator; module boundaries preserved; no new external dependencies; fail-closed and deterministic behavior preserved.

---

## 8) QA GATE RESULT

**QA_APPROVED**

- Tests run and pass (14 + 5 + 19); evidence reproducible; criteria for Phase 16 (registry lookup, transition validation, execution eligibility, fail-closed, backward compat) covered by tests; no regressions observed in nq_portfolio tests.

---

## 9) INTEGRATION STATUS

**READY_FOR_INTEGRATION**

- Deterministic helper/API for “is registered?”, “current lifecycle?”, “can transition X→Y?”, “is executable?” is implemented and tested. Downstream wiring (portfolio/exec/guardrails) is not done in this phase but is straightforward via the exposed APIs.
