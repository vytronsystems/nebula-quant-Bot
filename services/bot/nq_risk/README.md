# nq_risk — Deterministic Risk Decision Engine

**NEBULA-QUANT v1** risk decision engine. This module evaluates order intents against configured risk limits and context, returning **ALLOW**, **REDUCE**, or **BLOCK** decisions with explicit reason codes. It does **not** execute trades and does **not** talk to brokers; it is purely a decision layer.

## Purpose

- **Evaluate** proposed orders (`RiskOrderIntent`) in the context of account equity and strategy state (`RiskContext`).
- **Enforce** risk limits (`RiskLimits`) such as max risk per trade, daily risk budgets, and stop distance.
- **Produce** deterministic `RiskDecisionResult` objects with standardized decision types and reason codes.
- **Fail closed** when intent, context, or limits are missing or malformed.

## Responsibilities

- Provide domain models (`RiskOrderIntent`, `RiskContext`, `RiskLimits`, `RiskDecisionType`, `RiskDecisionResult`).
- Evaluate intents via rule-based logic (`evaluate_risk`) that:
  - Validates required fields (strategy_id, symbol, side, quantity/notional, prices, account_equity).
  - Checks lifecycle executability (paper/live only when lifecycle state is present).
  - Computes risk-per-trade and compares to limits.
  - Enforces daily strategy/account risk budgets and optional stop distance limits.
- Expose a simple `RiskEngine` with `evaluate_order_intent(...)` used by pipeline orchestrators and higher layers.

## Public interfaces

- Models:
  - `RiskOrderIntent`
  - `RiskContext`
  - `RiskLimits`
  - `RiskDecisionType` (`allow`, `reduce`, `block`)
  - `RiskDecisionResult`
- Engine:
  - `RiskEngine(policy: RiskPolicy | None = None)`
  - `RiskEngine.evaluate_order_intent(intent, context, limits=None) -> RiskDecisionResult`
- Rules:
  - `evaluate_risk(intent, context, limits) -> RiskDecisionResult` (pure function).
- Config helpers:
  - `DEFAULT_RISK_LIMITS`
  - `risk_limits_from_config(app_config_section)`
  - Constants like `MAX_RISK_PER_TRADE`, `MAX_DAILY_DRAWDOWN`, `MAX_CONCURRENT_POSITIONS`.

## Inputs and outputs

- **Inputs**:
  - `RiskOrderIntent`: strategy_id, symbol, side, entry_price, stop_loss_price, requested_quantity and/or requested_notional, optional timestamp and metadata.
  - `RiskContext`: account_equity, strategy_id, optional daily realized PnL (strategy/account), strategy_lifecycle_state, symbol, metadata.
  - `RiskLimits`: configuration values for max risk per trade %, daily budgets, stop distance %, etc.
- **Outputs**:
  - `RiskDecisionResult` with:
    - `decision`: `ALLOW`, `REDUCE`, or `BLOCK`.
    - `reason_codes`: list of machine-consumable strings (e.g. `missing_strategy_id`, `risk_per_trade_exceeded`).
    - `message`: human-readable summary.
    - Optional `approved_quantity` / `approved_notional` for `REDUCE`.
    - Optional `risk_amount` / `risk_pct`.

## Pipeline role

`nq_risk` sits directly after strategy signal generation in the pipeline:

`nq_data → nq_data_quality → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_guardrails → nq_exec → ...`

Every candidate trade from `nq_strategy` should be evaluated by `nq_risk` before it is allowed to proceed to backtest/paper/live execution or portfolio allocation.

## Determinism guarantees

- `evaluate_risk` is pure and deterministic: same `intent`, `context`, and `limits` produce the same `RiskDecisionResult`.
- All thresholds (max risk %, stop distance %, daily budgets) are explicit and documented in code.
- No randomness, I/O, or external services in the risk evaluation path.
- Metadata defaults are normalized in `__post_init__` to avoid `None` vs `{}` differences.

## Fail-closed behavior

- If any of `intent`, `context`, or `limits` is `None`, the engine returns a `BLOCK` decision with `reason_codes=["missing_input"]`.
- Missing or invalid required fields (e.g. empty strategy_id/symbol, non-positive equity, non-positive prices, missing quantity/notional) cause `BLOCK` with appropriate reason codes.
- Non-executable lifecycle (`strategy_lifecycle_state` present but not `paper` or `live`) yields `BLOCK` with `non_executable_lifecycle`.
- Negative quantity or notional, or malformed side, also produce `BLOCK` results.
- Risk that exceeds limits may produce `REDUCE` (when resizable) or `BLOCK` (when not), always with explicit reason codes.

## Integration notes

- **Upstream**:
  - `nq_strategy` (and later `nq_portfolio`) should construct `RiskOrderIntent` and `RiskContext` and pass them to `RiskEngine.evaluate_order_intent`.
- **Downstream**:
  - `nq_guardrails` and `nq_exec` should respect risk decisions:
    - ALLOW → may proceed, subject to guardrails.
    - REDUCE → order should be resized to `approved_quantity` / `approved_notional`.
    - BLOCK → order should not be sent.
- **Configuration**:
  - `nq_config` can provide risk limits via `risk_limits_from_config`.
  - Defaults (`DEFAULT_RISK_LIMITS`) give conservative behavior when explicit config is absent.

