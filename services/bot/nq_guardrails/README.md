# nq_guardrails — Safety and Kill-Switch Layer (Real Engine)

## Purpose

`nq_guardrails` is a **system-level safety controller** that evaluates account, market, strategy, and execution conditions and returns **allowed / blocked** decisions. It does **not** execute trades; it only produces deterministic safety signals. Fail-closed: any **BLOCK** severity signal forces `allowed=False`.

## What Is Implemented

- **Account-state checks**: `check_max_drawdown(account, context)` — BLOCK if drawdown ≥ limit; `check_daily_loss(account, context)` — BLOCK if daily loss (as fraction of equity) ≥ limit. Missing fields are tolerated (no crash).
- **Market-condition checks**: `check_volatility_spike(market, context)` — WARN if volatility ≥ threshold, BLOCK if ≥ extreme threshold.
- **Strategy-health checks**: `check_strategy_disable(strategy_health, context)` — BLOCK if `strategy_enabled` is False.
- **Execution-state checks**: `check_execution_pause(execution_state, context)` — BLOCK if `execution_enabled` is False.
- **Severity convention**: INFO, WARN, BLOCK. Any BLOCK → trading not allowed.
- **Engine**: `GuardrailsEngine.run_guardrails(account, positions, volatility, strategy_health, execution_state, context)` runs all domains, merges signals, applies fail-closed, updates `GuardrailsState` (trading_enabled, last_shutdown_reason, active_signals, updated_ts), returns `GuardrailResult`.
- **State**: `GuardrailsState` holds trading_enabled, last_shutdown_reason, active_signals, updated_ts; in-memory only, no persistence.
- **Reporter**: `build_guardrail_report(result)` returns dict with allowed, reason, issue_count (WARN+BLOCK), signals (signal_type, severity, message, timestamp), metadata.

## Current Limitations

- **No persistence**: State is in-memory only; no DB or file.
- **Input shape**: Expects dict-like inputs (e.g. account with drawdown, daily_pnl, equity; market with volatility; strategy_health with strategy_enabled; execution_state with execution_enabled). Missing keys are safe (no violation).
- **No broker or live**: Pure evaluation; no exchange or execution connectivity.
- **Thresholds**: Config defaults (MAX_DRAWDOWN_LIMIT, DAILY_LOSS_LIMIT, VOLATILITY_THRESHOLD, EXTREME_VOLATILITY_THRESHOLD, MAX_OPEN_POSITIONS); context can override per call.

## Assumptions

- Caller supplies account, market, strategy_health, execution_state (or empty dicts). Engine is tolerant of missing fields.
- Fail-closed: when in doubt, block. Any BLOCK signal implies allowed=False.

## Relationship: Paper, Guardrails, Execution Safety

- **Paper trading** runs strategies with simulated fills; guardrails can be evaluated before or during paper sessions to simulate real-world kill-switches.
- **Guardrails** sit alongside the pipeline: the orchestrator or main loop should call `run_guardrails()` before allowing new trades or after each cycle. If `allowed` is False, the system should not open new positions and may pause execution.
- **Live execution** (nq_exec) should respect guardrail results; no live orders when guardrails block.

## Future Versions

- Optional persistence of guardrail decisions and state for audit.
- Tighter integration with nq_risk and nq_paper (e.g. account state from paper session).
- Additional rules (e.g. max open positions, liquidity, data quality).
