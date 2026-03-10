# nq_guardrails

**NEBULA-QUANT v1** — Risk protection layer (skeleton).

## Purpose

`nq_guardrails` is a **system-level safety controller** responsible for preventing catastrophic losses and unsafe trading conditions. It does **not** execute trades; it only evaluates risk conditions and returns safety signals (allowed / blocked, plus reasons and metadata).

## Examples of risk protections

Typical guardrails (placeholders in this skeleton):

- **Max drawdown stop** — Halt trading when account drawdown exceeds a limit.
- **Daily loss limit** — Stop new risk when daily PnL loss exceeds a threshold.
- **Volatility shutdown** — Pause or reduce exposure when volatility spikes (e.g. VIX or realized vol).
- **Strategy disable** — Disable specific strategies based on health or performance.
- **Execution pause** — Pause order submission when execution layer or market is abnormal.
- **Abnormal market conditions** — Detect and react to circuit breakers, illiquidity, or bad data.

## Integration with the trading pipeline

The main pipeline remains:

`nq_data → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_exec`

Guardrails sit **alongside** this pipeline as infrastructure:

- The orchestrator or main loop can call `GuardrailsEngine.run_guardrails()` before allowing new trades or after each decision cycle.
- If `GuardrailResult.allowed` is `False`, the system should not open new positions or may pause execution.
- Reports from `reporter.build_guardrail_report()` can be sent to monitoring and logs.

This module is skeleton-only: no external APIs, no broker connectivity, no database persistence. All rule functions return safe placeholder results until wired to real account, market, and execution feeds.
