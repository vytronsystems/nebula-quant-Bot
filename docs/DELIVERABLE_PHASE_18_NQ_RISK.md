# NEBULA-QUANT v1 | Phase 18 — Implement nq_risk Decision Engine | Deliverable

---

## 1) SUMMARY

**Implemented:**
- **models.py**: `RiskDecisionType` (ALLOW, REDUCE, BLOCK), `RiskDecisionResult` (decision, reason_codes, message, approved_quantity, approved_notional, risk_amount, risk_pct, metadata), `RiskLimits`, `RiskContext`, `RiskOrderIntent`.
- **rules.py**: Deterministic `evaluate_risk(intent, context, limits)` with: input validation (BLOCK on missing strategy_id/symbol, invalid equity, missing qty/notional, negative values, invalid entry/stop, malformed side); lifecycle consistency (BLOCK when lifecycle not paper/live when supplied); stop-loss requirement (BLOCK if required but missing; zero distance BLOCK; wrong-side stop BLOCK; excessive stop distance % BLOCK); risk amount = qty * stop_distance_abs, risk_pct = risk_amount / equity; daily strategy/account risk budget BLOCK when exceeded; max risk per trade → ALLOW with optional warning_metadata, or REDUCE with approved_quantity = max_allowed_risk_amount / stop_distance_abs, or BLOCK when approved_qty <= 0.
- **limits.py**: `DEFAULT_RISK_LIMITS` (`RiskLimits` instance); kept existing stubs.
- **engine.py**: `evaluate_order_intent(intent, context, limits=None)` returning `RiskDecisionResult`; `__init__(policy=None)` for backward compat; legacy `evaluate(signal, context)` still requires policy.
- **__init__.py**: Exports for new types and `evaluate_risk`.
- **Tests**: 16 tests in `tests/test_risk_engine.py` covering all 15 required cases plus engine API and backward compat.

**Refactored:**
- `RiskEngine.__init__` now accepts `policy: RiskPolicy | None = None`; existing callers passing policy unchanged. No breaking changes to `RiskDecision` enum or `evaluate(signal, context)` signature.

**Compatibility:**
- Backward compatible. Existing `RiskDecision` (APPROVE/REJECT/ADJUST), `RiskPolicy`, and `evaluate(signal, context)` preserved. New API is additive: `evaluate_order_intent(intent, context, limits)`.

---

## 2) FILE TREE

**Created:**
- `services/bot/nq_risk/models.py`
- `services/bot/nq_risk/rules.py`
- `services/bot/nq_risk/tests/__init__.py`
- `services/bot/nq_risk/tests/test_risk_engine.py`

**Modified:**
- `services/bot/nq_risk/__init__.py` — new exports
- `services/bot/nq_risk/engine.py` — `evaluate_order_intent`, optional policy
- `services/bot/nq_risk/limits.py` — `DEFAULT_RISK_LIMITS`, `RiskLimits` import

---

## 3) ARCHITECTURE NOTES

- **Where risk logic lives:** In **nq_risk** only: `rules.evaluate_risk()` and `RiskEngine.evaluate_order_intent()`. No risk decision logic in nq_guardrails, nq_portfolio, nq_exec, nq_promotion.
- **How risk is computed:** `risk_amount = requested_quantity * abs(entry_price - stop_loss_price)` when entry and stop are present; `risk_pct = risk_amount / max(account_equity, 1e-9)`. When only notional is supplied, quantity is derived as notional/entry when entry is present; otherwise fail-closed (BLOCK or no risk computed).
- **REDUCE:** When risk_pct exceeds max_risk_per_trade_pct, `approved_quantity = (equity * max_risk_per_trade_pct) / stop_distance_abs`; if approved_quantity > 0 and less than requested, return REDUCE with approved_quantity and approved_notional; if approved_quantity <= 0 return BLOCK.
- **Lifecycle:** If `RiskContext.strategy_lifecycle_state` is supplied and not in {paper, live}, return BLOCK with reason code `non_executable_lifecycle`. nq_risk does not own lifecycle; this is a consistency guard only.
- **Integration status:** API and logic are in place; pipeline wiring (calling `evaluate_order_intent` after nq_strategy and before guardrails) is not done in this phase. **READY_FOR_INTEGRATION**.

---

## 4) VERIFICATION RESULTS

**Commands run:**

```bash
PYTHONPATH=services/bot python3 -m unittest discover -s services/bot/nq_risk/tests -p "test_*.py" -v
# Ran 16 tests — OK

PYTHONPATH=services/bot python3 -m unittest discover -s services/bot/nq_portfolio/tests -p "test_*.py" -v
# Ran 19 tests — OK
```

**Failed checks:** None.

---

## 5) GIT STATUS

- **Branch:** `feature/nq-risk-decision-engine`
- **Commit:** `4c363ba`
- **Message:** `nq_risk: implement deterministic risk decision engine`

---

## 6) RISKS / FOLLOW-UPS

- **Pipeline wiring:** Call site after nq_strategy (and before nq_guardrails) must build `RiskOrderIntent` and `RiskContext` from strategy output and account/strategy state, then call `engine.evaluate_order_intent(intent, context, limits)` and respect ALLOW/REDUCE/BLOCK (e.g. pass REDUCE’s approved_quantity to downstream).
- **Not wired:** No automatic conversion from nq_strategy signal format to RiskOrderIntent; no persistence of limits per strategy. These can be added in a later phase.

---

## 7) ARCHITECTURE GATE RESULT

**ARCHITECTURE_APPROVED**

---

## 8) QA GATE RESULT

**QA_APPROVED**

---

## 9) INTEGRATION STATUS

**READY_FOR_INTEGRATION**
