# NEBULA-QUANT v1 | Governance Architecture

## Governance goals

- Centralize lifecycle truth and promotion rules.
- Enforce risk and capital limits deterministically.
- Provide a clear, auditable hierarchy of decisions (risk → safety → portfolio → execution → promotion).

## Lifecycle governance

- **nq_strategy_registry** is the source of truth for strategy registration and lifecycle state (idea, research, backtest, walkforward, paper, live, disabled, retired, rejected).
- **nq_promotion** is the lifecycle promotion engine; it validates transitions using evidence from backtests, walkforward runs, paper trading and guardrails, and calls registry integration helpers before/after transitions.
- **Execution-compatible lifecycle states:** `paper`, `live` (as used by risk, portfolio and observability layers).

Lifecycle transitions follow the official path: idea → research → backtest → walkforward → paper → live → retired. Any other transition is blocked unless explicitly allowed by promotion rules.

## Risk and capital governance

Governance around risk and capital flows through several dedicated modules:

- **nq_risk** — per-trade risk decision engine (max risk per trade, daily strategy/account budgets, stop-loss sanity). Returns **ALLOW**, **REDUCE** (with approved size) or **BLOCK**.
- **nq_guardrails** — system-level safety layer (daily loss, drawdown, volatility, strategy disable flags). Returns `GuardrailResult` and can block further risk taking.
- **nq_portfolio** — portfolio-level governance gate that enforces capital usage, exposure, position count and drawdown limits; returns **ALLOW**, **THROTTLE**, or **BLOCK** before `nq_exec`.
- **nq_exec** — execution abstraction; validates orders and applies final execution rules but does not generate signals or set risk limits.

## Decision hierarchy

1. **Strategy & signals**: `nq_strategy` emits deterministic signals from data.  
2. **Risk decision**: `nq_risk` approves, reduces, or blocks trades based on risk policy.  
3. **Guardrails**: `nq_guardrails` can block trades at the system level (e.g., after large drawdowns).  
4. **Portfolio governance**: `nq_portfolio` can allow, throttle, or block based on portfolio constraints.  
5. **Execution**: `nq_exec` executes (simulated in v1) only if upstream layers permit it.  
6. **Promotion**: `nq_promotion` uses evidence from backtests, walkforward, paper and guardrails to promote or block strategies across lifecycle stages.

Each layer is deterministic, fail-closed and has a narrow, explicit responsibility. No single module replaces the others.

## Interaction with observability

- **nq_metrics** and **nq_obs** provide observability over governance decisions (risk decisions, guardrail blocks, portfolio throttles, promotion rejections) without changing behavior.
- Weekly audits can consume `SystemObservabilityReport` to understand how often each governance layer intervenes.

## Fail-closed philosophy

- Missing or inconsistent lifecycle information from registry must block promotion and execution until resolved.
- Ambiguous risk inputs (e.g., missing quantity+notional, invalid prices) must result in BLOCK at `nq_risk`.
- Guardrails default to BLOCK on ambiguous state.
- Portfolio governance does not silently exceed limits; any ambiguity defaults to BLOCK.
