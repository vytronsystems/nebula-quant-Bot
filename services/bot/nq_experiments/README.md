# nq_experiments

**NEBULA-QUANT v1** — Experiment tracking and research comparison layer (skeleton).

## Purpose

`nq_experiments` is the **experiment tracking and research comparison layer**. It records and compares research experiments: backtest runs, walk-forward runs, parameter sets, strategy versions, metrics snapshots, experiment notes, and status. It does **not** execute strategies, connect to brokers, or call external APIs; it only manages experiment definitions, in-memory results, and reporting.

## How it supports research and experiment tracking

- **Register experiments:** Store experiment_id, strategy_id, version, type (e.g. backtest), status, parameters, metrics, notes.
- **Update status/metrics:** Progress experiments from pending → running → completed/failed and attach metrics snapshots.
- **Compare experiments:** `comparison.compare_experiments()` and `build_metric_deltas()` support baseline vs candidate comparison for research decisions.
- **Registry view:** `build_registry_result()` exposes total, active, completed, failed counts for dashboards and governance.

## How it fits the institutional validation lifecycle

Experiments align with the pipeline (research → backtest → walk-forward → paper → live). This module records each run (backtest, walk-forward, etc.) so that parameter sets, strategy versions, and metrics can be compared and audited before promoting a strategy. It does not run the pipeline; it tracks the outcomes.

## Why this skeleton exists before persistent experiment storage

The API and in-memory storage provide a stable interface for the rest of the platform. Database persistence and historical querying can be added in a later iteration without changing the public API (ExperimentsEngine, ExperimentRecord, comparison, reporter).
