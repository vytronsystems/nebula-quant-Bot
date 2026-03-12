# NEBULA-QUANT v1 | Module Catalog

## Module states (Phase 44 aligned)

Status legend (current codebase):
- **IMPLEMENTED**: deterministic logic and models in place, with tests and README.

All modules listed below are **IMPLEMENTED**, have **tests: YES**, and **readme: YES**.

### Core pipeline and governance modules

| module_name        | status      | tests | readme | description |
|--------------------|------------|-------|--------|-------------|
| `nq_data`          | IMPLEMENTED | YES   | YES    | Data ingestion and canonical OHLCV `Bar` feed; provider abstraction with stub provider (no external I/O in v1). |
| `nq_data_quality`  | IMPLEMENTED | YES   | YES    | Data validation and integrity checks; produces `DataQualityResult` used before strategies/risk. |
| `nq_strategy`      | IMPLEMENTED | YES   | YES    | Strategy base class, `Signal` enum, reusable rules, and `StrategyEngine` for deterministic signal generation. |
| `nq_risk`          | IMPLEMENTED | YES   | YES    | Risk decision engine evaluating `RiskOrderIntent` + `RiskContext` against `RiskLimits`; returns ALLOW/REDUCE/BLOCK. |
| `nq_backtest`      | IMPLEMENTED | YES   | YES    | Bar-by-bar backtest engine; simulates trades, builds equity curve, computes metrics, returns `BacktestResult`. |
| `nq_walkforward`   | IMPLEMENTED | YES   | YES    | Walk-forward validation engine; builds train/test windows, runs backtests, and aggregates `WalkForwardResult`. |
| `nq_paper`         | IMPLEMENTED | YES   | YES    | Paper trading engine; simulates positions and trades over bars, returns `PaperSessionResult`. |
| `nq_guardrails`    | IMPLEMENTED | YES   | YES    | System safety controller; evaluates drawdown, daily loss, volatility, strategy disable, and execution pause; fail-closed. |
| `nq_exec`          | IMPLEMENTED | YES   | YES    | Execution abstraction; validates orders, routes via in-memory adapters, returns `ExecutionResult` (simulated in v1). |
| `nq_metrics`       | IMPLEMENTED | YES   | YES    | Performance and observability metrics engine; computes trading metrics and builds observability reports. |
| `nq_experiments`   | IMPLEMENTED | YES   | YES    | Experiment registry and analysis; compares experiment runs and produces `ExperimentReport`. |
| `nq_portfolio`     | IMPLEMENTED | YES   | YES    | Portfolio governance and exposure management; portfolio-level constraints and decisions. |
| `nq_promotion`     | IMPLEMENTED | YES   | YES    | Lifecycle promotion engine; governs idea → research → backtest → walkforward → paper → live → retired. |

### Integration / observability / registry

| module_name         | status      | tests | readme | description |
|---------------------|------------|-------|--------|-------------|
| `nq_strategy_registry` | IMPLEMENTED | YES   | YES    | Strategy registration and lifecycle registry; source of truth for strategy metadata and status. |
| `nq_obs`           | IMPLEMENTED | YES   | YES    | Observability integration layer; gathers module outputs and builds `ObservabilityInput` for `nq_metrics`. |

### Audit, learning, and continuous improvement

| module_name        | status      | tests | readme | description |
|--------------------|------------|-------|--------|-------------|
| `nq_audit`         | IMPLEMENTED | YES   | YES    | Audit analysis engine; consumes system events/decisions and produces structured `AuditReport` with findings and recommendations. |
| `nq_trade_review`  | IMPLEMENTED | YES   | YES    | Trade review engine; analyzes trades and produces review findings for governance and learning. |
| `nq_learning`      | IMPLEMENTED | YES   | YES    | Learning layer; aggregates audit/review outcomes into `LearningReport` with lessons and patterns. |
| `nq_improvement`   | IMPLEMENTED | YES   | YES    | Improvement planning engine; turns audit/learning/review outputs into prioritized `ImprovementPlan`. |
| `nq_reporting`     | IMPLEMENTED | YES   | YES    | Reporting layer; builds system reports from other module outputs for external consumers and dashboards. |
| `nq_decision_archive` | IMPLEMENTED | YES   | YES    | Decision archive engine; normalizes and stores promotion/decision records for long-term audit. |

### Infrastructure, scheduling, and orchestration

| module_name        | status      | tests | readme | description |
|--------------------|------------|-------|--------|-------------|
| `nq_db`            | IMPLEMENTED | YES   | YES    | Database engine and schema layer; shared persistence foundation used by event store and other modules. |
| `nq_event_store`   | IMPLEMENTED | YES   | YES    | Append-only event store; records normalized events for audit and replay using `EventStoreEngine`. |
| `nq_cache`         | IMPLEMENTED | YES   | YES    | Deterministic in-memory cache with namespaces, TTL, and explicit invalidation; not a source of truth. |
| `nq_config`        | IMPLEMENTED | YES   | YES    | Configuration management; loads, validates, and normalizes app config for other modules. |
| `nq_scheduler`     | IMPLEMENTED | YES   | YES    | Scheduling engine; defines and runs scheduled jobs in a deterministic, fail-closed way. |
| `nq_orchestrator`  | IMPLEMENTED | YES   | YES    | Workflow orchestration engine; defines ordered workflows and runs steps with shared context. |

### Operations / reliability / governance

| module_name        | status      | tests | readme | description |
|--------------------|------------|-------|--------|-------------|
| `nq_sre`           | IMPLEMENTED | YES   | YES    | Operational reliability layer; evaluates service health, classifies incidents, and produces SRE reports. |
| `nq_runbooks`      | IMPLEMENTED | YES   | YES    | Operational runbook registry and recommendation engine; maps incidents to runbooks and generates recommendations. |
| `nq_release`       | IMPLEMENTED | YES   | YES    | Release governance; evaluates release candidates, gates, and module readiness to produce release decisions. |

### Research and regime analysis

| module_name        | status      | tests | readme | description |
|--------------------|------------|-------|--------|-------------|
| `nq_alpha_discovery` | IMPLEMENTED | YES   | YES    | Alpha discovery tooling; analyzes candidate alphas and supports ranking and selection. |
| `nq_regime`        | IMPLEMENTED | YES   | YES    | Regime detection and summaries; produces regime labels and regime-aware summaries. |
| `nq_edge_decay`    | IMPLEMENTED | YES   | YES    | Edge decay analysis; evaluates how edge/alpha decays over time and across regimes. |

### Observability and operations

| module_name        | status      | tests | readme | description |
|--------------------|------------|-------|--------|-------------|
| `nq_obs`           | IMPLEMENTED | YES   | YES    | Observability integration layer (see above); bridges module outputs to `nq_metrics`. |

> Note: Process-only modules such as `nq_architecture_gate` and `nq_qa_gate` are documented in dedicated docs (`07_AGENT_ARCHITECTURE_GATE.md`, `08_AGENT_QA_GATE.md`) and are not separate code modules under `services/bot/`.


