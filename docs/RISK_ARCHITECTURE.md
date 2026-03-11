# NEBULA-QUANT v1 | Risk Architecture (nq_risk)

## Role of nq_risk
`nq_risk` is the dedicated risk decision engine immediately after `nq_strategy` and before guardrails/portfolio/execution. It evaluates each proposed trade (order intent) against risk policy and returns **ALLOW**, **REDUCE**, or **BLOCK**, deterministically and fail-closed.

## Domain models

- `RiskDecisionType`: `ALLOW`, `REDUCE`, `BLOCK`.
- `RiskLimits`: max risk per trade (% of equity), optional daily strategy/account risk budgets, stop-loss requirements and maximum stop distance.
- `RiskContext`: account equity, strategy id, daily realized PnL (strategy/account), optional lifecycle state and metadata.
- `RiskOrderIntent`: strategy id, symbol, side, entry price, stop loss price, requested quantity/notional and metadata.
- `RiskDecisionResult`: outcome with decision, reason_codes, message, approved_quantity/notional (for REDUCE), and computed risk_amount/risk_pct when available.

## Risk computation

1. **Input validation**: BLOCK if critical fields are missing or invalid (strategy_id, symbol, equity, quantity/notional, prices, side).
2. **Stop-loss rules** (when required):
   - Stop loss must be present if policy requires it.
   - Long: stop below entry; Short: stop above entry.
   - Zero distance or malformed stop → `zero_stop_distance` BLOCK.
3. **Risk amount and pct**:
   - `stop_distance_abs = abs(entry_price - stop_loss_price)`.
   - `risk_amount = requested_quantity * stop_distance_abs`.
   - `risk_pct = risk_amount / max(account_equity, 1e-9)`.
4. **Per-trade limit**:
   - If `risk_pct <= max_risk_per_trade_pct` → ALLOW (with optional warning near limit).
   - If `risk_pct > max_risk_per_trade_pct` and a smaller quantity can be computed:
     - `max_allowed_risk_amount = equity * max_risk_per_trade_pct`.
     - `approved_quantity = max_allowed_risk_amount / max(stop_distance_abs, 1e-9)`.
     - If `approved_quantity > 0` and `< requested_quantity` → REDUCE with approved_quantity/notional.
   - If resizing is not possible (approved_quantity ≤ 0) → BLOCK.

## Daily risk budgets

When configured:
- **Strategy budget**: if absolute daily strategy loss / equity ≥ `max_daily_strategy_risk_pct` → BLOCK with `daily_strategy_risk_budget_exceeded`.
- **Account budget**: if absolute daily account loss / equity ≥ `max_daily_account_risk_pct` → BLOCK with `daily_account_risk_budget_exceeded`.

## Lifecycle consistency

`RiskContext.strategy_lifecycle_state`, when provided, is checked for consistency with lifecycle governance:
- Execution-compatible: `paper`, `live`.
- Any other state (e.g. `idea`, `research`, `backtest`, `walkforward`, `retired`) → BLOCK with `non_executable_lifecycle`.

`nq_risk` does not own lifecycle governance; it enforces consistency with the states defined and maintained by `nq_strategy_registry` and `nq_promotion`.

## Relationship to guardrails and portfolio

- `nq_risk` evaluates **per-trade** risk based on quantities, prices and stop distances.
- `nq_guardrails` evaluates **system-level** safety (drawdowns, daily loss, volatility, strategy disable) over account/state snapshots.
- `nq_portfolio` enforces **portfolio-level** capital and exposure constraints (capital usage, position counts, portfolio/strategy drawdown) and can ALLOW/THROTTLE/BLOCK.

The intended flow is:

Strategy signals → `nq_risk` (ALLOW/REDUCE/BLOCK) → `nq_guardrails` → `nq_portfolio` → `nq_exec`.

Each layer is deterministic, fail-closed and has a narrow responsibility.
