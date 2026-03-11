# nq_experiments

**NEBULA-QUANT v1** — Experiment tracking, research comparison, and deterministic experiment analysis.

## Purpose

`nq_experiments` is the **experiment tracking and analysis layer**. It records and compares research experiments (backtest, walk-forward, paper, research), manages experiment definitions and in-memory results, and provides **deterministic experiment analysis** (validation, findings, summaries, reports). It does **not** execute strategies, connect to brokers, or call external APIs.

## Experiment record model

- **ExperimentRecord** (existing): experiment_id, strategy_id, strategy_version, experiment_type, status, parameters, metrics, notes, created_at, updated_at, owner, metadata.
- **ExperimentStatus**: pending, running, success, failed, degraded, invalid. Status `completed` is normalized to `success` for analysis.
- **ExperimentType**: backtest, walkforward, paper, research, other.

## Experiment analysis (Phase 33)

- **ExperimentEngine(clock)** — Deterministic analysis engine. `analyze_experiments(experiment_records, report_id=..., generated_at=...)` returns **ExperimentReport** (report_id, generated_at, summary, findings, experiment_records).
- **Validation** — Missing experiment_id or invalid status/type/metrics raises **ExperimentError**. Optional fields handled safely.
- **Findings** — Deterministic categories: experiment_failed, experiment_degraded, experiment_invalid, missing_metrics, weak_result, inconsistent_experiment_record. Severity: info, warning, critical.
- **ExperimentSummary** — total_experiments, successful/failed/degraded/invalid counts, strategies_seen, categories_seen.
- **Weak-result heuristics** — Negative PnL, low win rate (<0.3), negative expectancy produce weak_result findings when metrics are present. No fabrication of missing data.

## How it supports research and experiment tracking

- **Register experiments:** ExperimentsEngine.register_experiment(), update status/metrics, list/filter.
- **Compare experiments:** `comparison.compare_experiments()` and `build_metric_deltas()` for baseline vs candidate.
- **Registry view:** `build_registry_result()` for total, active, completed, failed counts.
- **Analysis view:** `ExperimentEngine.analyze_experiments()` for findings and summary suitable for nq_audit, nq_learning, nq_reporting.

## Deterministic guarantees

- Same experiment records produce the same report structure and finding set.
- Report ids: counter-based `experiment-report-{n}` or caller-supplied. Finding ids: deterministic per record and index.

## Future integration

- **nq_metrics / nq_obs:** Consume experiment summaries and metrics.
- **nq_audit / nq_learning / nq_reporting:** Consume ExperimentReport (findings, summary) for audit trails, learning inputs, and system reports.

No deep wiring in this phase; the API is ready for integration.
