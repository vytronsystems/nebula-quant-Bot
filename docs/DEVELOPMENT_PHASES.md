# NEBULA-QUANT v1 | Development Phases

## High-level phases

- **Phase 1 — Infrastructure & skeletons**  
  Docker Compose, Bot, Postgres, Redis, Prometheus, Grafana, Alertmanager, `/metrics`, basic tables and migrations; skeletons for `nq_data`, `nq_strategy`, and related modules.

- **Phase 2 — Trading core (in progress)**  
  Deterministic engines for backtest, walkforward, paper, guardrails, execution, risk, portfolio, lifecycle governance and observability.

## Detailed recent phases (13–19)

- **Phase 13 — nq_exec execution engine**  
  Implemented `nq_exec` as a deterministic execution abstraction with `ExecutionOrder`, `ExecutionFill` and `ExecutionResult`, plus basic in-memory adapters. Fail-closed on invalid orders or disabled execution.

- **Phase 14 — nq_promotion lifecycle governance**  
  Implemented `nq_promotion` as the lifecycle engine for strategies, including allowed transitions (idea → research → backtest → walkforward → paper → live → retired), evidence checks and fail-closed promotion decisions.

- **Phase 15 — Tighten nq_portfolio**  
  Turned `nq_portfolio` into the final portfolio approval gate before `nq_exec`, with `PortfolioDecisionType` (ALLOW/THROTTLE/BLOCK), limits for capital usage and drawdowns, and a deterministic portfolio risk engine.

- **Phase 16 — Integrate nq_promotion with nq_strategy_registry**  
  Integrated `nq_promotion` with `nq_strategy_registry` so registry is the source of truth for strategy lifecycle state and registration, and promotion is the authorized transition engine.

- **Phase 17 — Observability & Metrics Layer (nq_metrics)**  
  Implemented observability models and logic in `nq_metrics` (StrategyHealthSnapshot, ExecutionQualitySnapshot, ControlDecisionSnapshot, SystemObservabilityReport, ObservabilityInput) and extended `MetricsEngine` to generate observability reports.

- **Phase 18 — nq_risk decision engine**  
  Implemented `nq_risk` as a deterministic risk decision engine with `RiskOrderIntent`, `RiskContext`, `RiskLimits` and `RiskDecisionResult`, evaluating per-trade risk and returning ALLOW/REDUCE/BLOCK.

- **Phase 19 — nq_obs integration layer**  
  Implemented `nq_obs` as the observability integration layer that gathers outputs from registry, risk, guardrails, exec, portfolio, promotion and experiments, and normalizes them into `ObservabilityInput` for `nq_metrics`.

## Current capabilities

- Deterministic validation and execution flow from strategy signals through risk, validation, paper, guardrails and execution.
- Lifecycle governance integrated with a strategy registry and promotion engine.
- Portfolio and risk governance layers before execution.
- Observability and reporting via `nq_obs` + `nq_metrics`, ready for weekly audit processes.

## Next phases (examples)

- End-to-end orchestration of the full pipeline.
- Deepening of data/strategy/experiment modules.
- Implementation of audit and research modules from the catalog.
