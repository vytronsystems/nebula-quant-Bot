# NEBULA-QUANT v1 | Module Map

## Modules and status (Phase 19)

| Module               | Status           | Notes |
|----------------------|------------------|-------|
| `nq_data`            | skeleton         | Canonical data feed (`Bar`) and provider abstraction. |
| `nq_data_quality`    | skeleton         | Data validation. |
| `nq_strategy`        | skeleton         | Strategy engine & signals. |
| `nq_strategy_registry` | implemented    | Strategy registry & lifecycle truth. |
| `nq_risk`            | implemented      | Risk decision engine (ALLOW/REDUCE/BLOCK). |
| `nq_backtest`        | implemented      | Backtest engine. |
| `nq_walkforward`     | implemented      | Walk-forward validation. |
| `nq_paper`           | implemented      | Paper trading sessions. |
| `nq_guardrails`      | implemented      | Safety and guardrail engine. |
| `nq_exec`            | implemented      | Execution abstraction. |
| `nq_metrics`         | implemented      | Metrics & observability. |
| `nq_experiments`     | skeleton         | Experiment registry. |
| `nq_portfolio`       | implemented      | Portfolio governance & approval gate. |
| `nq_promotion`       | implemented      | Lifecycle promotion engine. |
| `nq_obs`             | integration layer| Observability integration into `nq_metrics`. |

Other catalog modules (research, audit, factory, persistence) remain pending or partial as described in `MODULE_CATALOG.md`.

## Build order (completed so far)

1. `nq_data` / `nq_strategy` — skeletons.  
2. `nq_backtest`, `nq_walkforward`, `nq_paper` — validation engines.  
3. `nq_guardrails`, `nq_exec` — safety and execution.  
4. `nq_portfolio` — portfolio governance gate.  
5. `nq_promotion` + `nq_strategy_registry` — lifecycle governance and registry.  
6. `nq_risk` — risk decision engine.  
7. `nq_metrics` — observability & metrics.  
8. `nq_obs` — observability integration layer.

## Status conventions

- **implemented** — Real deterministic logic in place.
- **skeleton** — Structure & API in place; logic to be deepened.
- **integration layer** — Adapter/gatherer between modules.
- **pending/partial** — Planned or partially realized components.
