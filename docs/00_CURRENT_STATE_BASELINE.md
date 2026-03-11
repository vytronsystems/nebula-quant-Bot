# NEBULA-QUANT v1 | Current State Baseline

## Date
2026-03-10

## Validated state (up to Phase 19)
- **Phase 1** closed: Docker Compose, Bot, Postgres, Redis, Prometheus, Grafana, Alertmanager, `/metrics`, `nq-verify.sh`, core tables and migrations.
- **Phase 2 (Trading Core)** advanced:
  - **Skeletons**: `nq_data`, `nq_data_quality`, `nq_strategy`, `nq_experiments`.
  - **Implemented engines**: `nq_backtest`, `nq_walkforward`, `nq_paper`, `nq_guardrails`, `nq_exec`, `nq_risk`, `nq_portfolio`, `nq_promotion`, `nq_metrics` (metrics + observability), `nq_strategy_registry` (registry), `nq_obs` (observability integration).

## Pipeline

nq_data → nq_data_quality → nq_strategy → nq_risk → nq_backtest → nq_walkforward → nq_paper → nq_guardrails → nq_exec → nq_metrics → nq_experiments → nq_portfolio → nq_promotion

`nq_promotion` evaluates lifecycle transitions; `nq_obs` + `nq_metrics` provide observability; `nq_risk`, `nq_guardrails`, `nq_portfolio` and `nq_exec` form the pre-execution and execution control stack.

## Known gaps
- Orchestration layer for end-to-end runs is still pending.
- Persistence/export of observability reports and audit artefacts is not implemented.
- Research/audit modules from the catalog (e.g. `nq_research`, `nq_audit`, `nq_montecarlo`, `nq_lab`) remain planned.
- No real external data or broker integrations are active by default; all external I/O must be explicitly approved.

## Notes
Architecture and module documentation (`PROJECT_STATE.md`, `MODULE_CATALOG.md`, `ARCHITECTURE.md`, `PIPELINE.md`, `RISK_ARCHITECTURE.md`, `OBSERVABILITY_ARCHITECTURE.md`, `GOVERNANCE.md`, `DEVELOPMENT_PHASES.md`) reflect the current validated state.
