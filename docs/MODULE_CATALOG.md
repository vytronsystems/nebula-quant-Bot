# NEBULA-QUANT v1 | Module Catalog

## Module states

Status legend:
- **implemented**: deterministic logic in place and used.
- **integration layer**: thin adapter/gatherer around existing modules.
- **skeleton**: basic structure/API only; logic to be deepened.
- **pending**: planned, not yet built.

### Core pipeline modules

| Module             | Status           | Notes |
|--------------------|------------------|-------|
| `nq_data`          | skeleton         | Data ingestion & canonical `Bar` feed (future external providers). |
| `nq_data_quality`  | skeleton         | Data validation & quality checks. |
| `nq_strategy`      | skeleton         | Strategy engine, signals, rules. |
| `nq_risk`          | implemented      | Risk decision engine (ALLOW/REDUCE/BLOCK per trade). |
| `nq_backtest`      | implemented      | Deterministic bar-by-bar backtest engine. |
| `nq_walkforward`   | implemented      | Train/test window orchestration over backtests. |
| `nq_paper`         | implemented      | Paper trading sessions in-memory. |
| `nq_guardrails`    | implemented      | System safety controller and kill-switch. |
| `nq_exec`          | implemented      | Execution abstraction (orders/fills/results), in-memory adapters. |
| `nq_metrics`       | implemented      | Performance & observability metrics + reports. |
| `nq_experiments`   | skeleton         | Experiment registry and comparison. |
| `nq_portfolio`     | implemented      | Portfolio governance and approval gate before exec. |
| `nq_promotion`     | implemented      | Lifecycle promotion engine (idea→…→live→retired). |

### Integration / observability / registry

| Module                 | Status           | Notes |
|------------------------|------------------|-------|
| `nq_strategy_registry` | implemented      | Strategy registration & lifecycle source of truth. |
| `nq_obs`               | integration layer| Observability integration; builds `ObservabilityInput` for `nq_metrics`. |

### Research modules

| Module            | Status   | Notes |
|-------------------|----------|-------|
| `nq_research`     | pending  | Research workflows. |
| `nq_montecarlo`   | pending  | Monte Carlo analysis of strategy robustness. |
| `nq_lab`          | pending  | Strategy lab / sandbox. |
| `nq_alpha_discovery` | pending | Alpha discovery tooling. |
| `nq_regime`       | pending  | Regime detection. |
| `nq_edge_decay`   | pending  | Edge decay analysis. |

### Audit and continuous improvement

| Module             | Status   | Notes |
|--------------------|----------|-------|
| `nq_audit`         | pending  | Audit trails and controls. |
| `nq_trade_review`  | pending  | Trade-by-trade review workflows. |
| `nq_learning`      | pending  | Post-mortem learning. |
| `nq_improvement`   | pending  | Continuous improvement workflows. |
| `nq_reporting`     | pending  | Reporting layer (external consumers). |
| `nq_decision_archive` | pending | Decision and promotion archive. |

### Software factory / ops

| Module              | Status   | Notes |
|---------------------|----------|-------|
| `nq_orchestrator`   | pending  | End-to-end pipeline orchestration. |
| `nq_architecture_gate` | implemented (doc) | Architecture Gate process (see docs). |
| `nq_qa_gate`        | implemented (doc) | QA Gate process (see docs). |
| `nq_release`        | pending  | Release management. |
| `nq_gitops`         | pending  | GitOps automation. |
| `nq_alerting`       | pending  | Alerting layer (external tools). |
| `nq_sre`            | pending  | Reliability practices. |
| `nq_runbooks`       | implemented (doc) | Operational runbooks. |
| `nq_scheduler`      | pending  | Scheduling layer. |

### Data & persistence

| Module            | Status   | Notes |
|-------------------|----------|-------|
| `nq_db`           | partial  | Postgres schema and migrations for core entities. |
| `nq_cache`        | pending  | Caching layer. |
| `nq_event_store`  | pending  | Event sourcing / log store. |
| `nq_config`       | partial  | Configuration management. |

