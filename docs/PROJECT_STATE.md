# NEBULA-QUANT v1 | Project State

## High-level system description
NEBULA-QUANT v1 is an institutional quantitative trading research & execution platform. The core of the system lives under `services/bot/` as a deterministic, fail-closed pipeline of modules with strict boundaries and no hidden side effects.

## Current pipeline (architectural truth)

nq_data  
→ nq_data_quality  
→ nq_strategy  
→ nq_risk  
→ nq_backtest  
→ nq_walkforward  
→ nq_paper  
→ nq_guardrails  
→ nq_exec  
→ nq_metrics  
→ nq_experiments  
→ nq_portfolio  
→ nq_promotion

This order is fixed from an architectural point of view and must not be changed without explicit Architecture Gate approval.

## Implemented modules (Phase 13–19)

### Core engines (deterministic behavior)
- **nq_backtest** — Bar-by-bar backtest engine with commissions/slippage, equity curve and metrics (win rate, PnL, drawdown, Sharpe-like).
- **nq_walkforward** — Train/test window engine orchestrating multiple backtests with pass/fail rules.
- **nq_paper** — Paper trading sessions, positions and trades in-memory; used for pre-live validation.
- **nq_guardrails** — System safety controller; evaluates drawdown, daily loss, volatility spikes and strategy disable rules; returns `GuardrailResult` and fails closed.
- **nq_exec** — Execution abstraction; validates orders, routes via in-memory adapters, and returns `ExecutionResult`; no direct broker integration in v1.
- **nq_risk** — Deterministic risk decision engine; evaluates `RiskOrderIntent` + `RiskContext` + `RiskLimits` and returns ALLOW / REDUCE / BLOCK with explicit risk metrics.
- **nq_portfolio** — Portfolio governance engine; final portfolio approval gate before `nq_exec` (ALLOW / THROTTLE / BLOCK) with capital usage and drawdown limits.
- **nq_metrics** — Performance and observability layer; computes trading metrics and produces `SystemObservabilityReport` from observability inputs.
- **nq_promotion** — Lifecycle governance engine; validates promotions idea → research → backtest → walkforward → paper → live → retired, strictly fail-closed.

### Integration and registry
- **nq_strategy_registry** — Source of truth for strategy registration and lifecycle state; provides `get_registration_record()` and registry summaries.
- **nq_obs** — Observability integration layer; gathers outputs from registry, exec, guardrails, portfolio, promotion and experiments and normalizes them into `ObservabilityInput` for `nq_metrics`.

### Skeleton / research modules
- **nq_data** — Skeleton data ingestion & normalization (providers, canonical `Bar` model).
- **nq_data_quality** — Skeleton data quality checks.
- **nq_strategy** — Skeleton strategy engine and signal generation.
- **nq_experiments** — Skeleton experiment registry and comparison.

## Modules still skeleton or pending
- **Skeleton**: `nq_data`, `nq_data_quality`, `nq_strategy`, `nq_experiments`.
- **Planned / pending**: research and audit modules from the catalog (e.g. `nq_research`, `nq_montecarlo`, `nq_audit`, `nq_lab`, `nq_edge_decay`, etc.).

## System maturity overview
- **Decision & execution core**: nq_risk, nq_guardrails, nq_exec, nq_portfolio and nq_promotion provide a multi-layer, fail-closed decision pipeline.
- **Validation core**: nq_backtest, nq_walkforward and nq_paper provide deterministic research and pre-live validation.
- **Observability**: nq_metrics + nq_obs provide system, strategy and control-layer observability without side effects.
- **Registry & lifecycle**: nq_strategy_registry + nq_promotion centralize lifecycle truth and promotion rules.

## Open items
- End-to-end orchestrator to run the full pipeline deterministically from data → strategy → risk → backtest/walkforward/paper → guardrails → exec → metrics/obs.
- Optional persistence/export of observability reports and audit artefacts for external weekly audit tooling.
- Progressive deepening of skeleton modules (data ingestion, strategy framework, experiment lab) and planned research/audit modules.
