# NEBULA-QUANT v1 | Observability Architecture (nq_metrics + nq_obs)

## Roles

- **nq_metrics**: observability and system metrics engine. Owns observability models, health classification and report generation.
- **nq_obs**: observability integration layer. Gathers outputs from other modules, normalizes them, and builds `ObservabilityInput` for `nq_metrics`.

## Observability models (in nq_metrics)

Key types:
- `MetricRecord`: normalized metric entry.
- `StrategyHealthSnapshot`: per-strategy health view (status, executions, PnL, drawdown, slippage).
- `ExecutionQualitySnapshot`: aggregated execution quality (attempted/approved/blocked/throttled, fills, slippage).
- `ControlDecisionSnapshot`: aggregated guardrail/portfolio/promotion counts.
- `SystemObservabilityReport`: top-level report combining strategies, execution quality, controls, experiment summary and totals.
- `StrategyHealthInput` and `ObservabilityInput`: input types to generate reports.

`nq_metrics.observability` provides deterministic functions such as `classify_strategy_health`, `build_*_snapshot` and `generate_observability_report`.

## Integration and normalization (nq_obs)

`nq_obs` provides:

- `StrategyObservabilitySeed`: normalized per-strategy seed based on registry truth and optional metrics.
- `SystemObservabilityBuilderInput`: normalized container for system-wide metrics (strategy seeds, execution/control counts, experiment summary).
- Adapters:
  - `normalize_execution_outcomes` — maps execution results into counts and averages.
  - `normalize_guardrail_decisions` — maps guardrail results into allow/block counts.
  - `normalize_portfolio_decisions` — maps portfolio decisions into allow/block/throttle counts.
  - `normalize_promotion_decisions` — maps promotion decisions into allow/reject/invalid-lifecycle counts.
  - `normalize_experiment_summary` — extracts experiment summary from experiments outputs.
  - `build_strategy_seeds_from_registry` — builds strategy seeds from `nq_strategy_registry` lifecycle truth.
- Builders:
  - `seed_to_health_input` — converts `StrategyObservabilitySeed` to `StrategyHealthInput`.
  - `build_observability_input` — converts `SystemObservabilityBuilderInput` to `ObservabilityInput`.
- Engine:
  - `ObservabilityEngine.gather(...)` — gathers & normalizes module outputs.
  - `ObservabilityEngine.build_observability_input(...)` — builds `ObservabilityInput`.
  - `ObservabilityEngine.generate_report(...)` — calls `nq_metrics.generate_observability_report`.

## Observability flow

Module outputs / state  
→ `nq_obs` adapters (`normalize_*`, `build_strategy_seeds_from_registry`)  
→ `SystemObservabilityBuilderInput`  
→ `build_observability_input` → `ObservabilityInput`  
→ `nq_metrics.generate_observability_report`  
→ `SystemObservabilityReport`

Observability is **read-only** and deterministic. Missing inputs do not fabricate values; instead, zero/None/empty values or explicit omission metadata are used.

## Weekly audit readiness

`SystemObservabilityReport` exposes:
- Per-strategy health (status, lifecycle_state, executions, drawdown/PnL where provided).
- Execution quality (attempted/approved/blocked/throttled, fills, slippage aggregates).
- Control layer decisions (guardrail allows/blocks, portfolio allows/blocks/throttles, promotion rejections, invalid lifecycles).
- Experiment summary and system totals (e.g. total executable strategies, total blocked/throttled attempts).

This makes it straightforward to build weekly audit views using only `nq_obs` + `nq_metrics`, without changing trading decisions.
