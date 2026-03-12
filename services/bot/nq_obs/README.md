# nq_obs — Observability Integration Layer

**NEBULA-QUANT v1** observability integration layer. This module gathers outputs from core modules (registry, execution, guardrails, portfolio, promotion, experiments), normalizes them into observability inputs, and bridges into `nq_metrics` for reporting. It does **not** compute metrics itself, does **not** execute trades, and does **not** persist data.

## Purpose

- **Gather** strategy, execution, guardrail, portfolio, promotion, and experiment signals into a single normalized structure.
- **Normalize** these signals to `StrategyObservabilitySeed` and `SystemObservabilityBuilderInput`.
- **Build** `ObservabilityInput` for `nq_metrics`.
- **Generate** `SystemObservabilityReport` via `nq_metrics.observability.generate_observability_report`.

## Responsibilities

- Provide adapters that:
  - Build strategy seeds from the strategy registry (`build_strategy_seeds_from_registry`).
  - Normalize execution outcomes, guardrail decisions, portfolio decisions, promotion decisions, and experiment summaries.
- Provide builders that:
  - Convert normalized inputs to `ObservabilityInput` for `nq_metrics`.
- Provide an `ObservabilityEngine` that orchestrates gather → build → report, with **no side effects** on upstream modules.

## Public interfaces

- Models:
  - `StrategyObservabilitySeed`
  - `ObservabilityGatherResult`
  - `SystemObservabilityBuilderInput`
- Adapters:
  - `build_strategy_seeds_from_registry(registry_engine, strategy_ids)`
  - `normalize_execution_outcomes(execution_events)`
  - `normalize_guardrail_decisions(guardrail_results)`
  - `normalize_portfolio_decisions(portfolio_decisions)`
  - `normalize_promotion_decisions(promotion_decisions)`
  - `normalize_experiment_summary(experiment_result)`
- Builders:
  - `seed_to_health_input(StrategyObservabilitySeed) -> StrategyHealthInput`
  - `build_observability_input(SystemObservabilityBuilderInput | None) -> ObservabilityInput`
- Engine:
  - `ObservabilityEngine.gather(...) -> SystemObservabilityBuilderInput`
  - `ObservabilityEngine.build_observability_input(builder_input) -> ObservabilityInput`
  - `ObservabilityEngine.generate_report(...) -> SystemObservabilityReport`

## Inputs and outputs

- **Inputs** (all optional, dict/list-like, tolerant of empty values):
  - `registry_engine`: Strategy registry engine (from `nq_strategy_registry`).
  - `strategy_ids`: List of strategy ids to include.
  - `execution_events`: List of execution results or events (e.g. `ExecutionResult`-like).
  - `guardrail_results`: Guardrail evaluation results.
  - `portfolio_decisions`: Portfolio decision records.
  - `promotion_decisions`: Promotion decision records.
  - `experiment_result`: Experiment report or summary.
- **Intermediate outputs**:
  - `StrategyObservabilitySeed` list and `SystemObservabilityBuilderInput`.
- **Final outputs**:
  - `ObservabilityInput` (for `nq_metrics`).
  - `SystemObservabilityReport` from `nq_metrics`.

## Pipeline role

`nq_obs` sits **outside** the main trading decision pipeline and in the **operations / observability** layer:

`... → nq_exec → nq_metrics → nq_experiments → nq_portfolio → nq_promotion`  
`                ↓`  
`             nq_obs → nq_metrics (observability)`

It **does not** change pipeline outcomes; it only observes and summarizes them.

## Determinism guarantees

- Normalization functions (`normalize_*`) are pure and deterministic given the same input lists.
- `build_observability_input` produces the same `ObservabilityInput` for the same `SystemObservabilityBuilderInput`.
- `ObservabilityEngine.generate_report` is deterministic assuming the underlying `nq_metrics` engine is deterministic; it does not introduce randomness or I/O.
- `build_strategy_seeds_from_registry` uses registry “truth” and returns consistent seeds and codes for a given registry state.

## Fail-closed behavior

- Missing or malformed inputs are treated conservatively:
  - Registry lookups that fail yield no seeds and error codes instead of fabricating data.
  - Normalization functions handle `None` and unexpected shapes without raising, defaulting counts to zero and lists to empty.
  - `build_observability_input(None)` returns an `ObservabilityInput` with metadata indicating omission, not fabricated metrics.
- No write operations are performed against upstream modules; all inputs are treated as read-only views.

## Integration notes

- **Upstream**:
  - `nq_strategy_registry` is used for strategy lifecycle and enablement truth; registry data overrides caller-supplied lifecycle when available.
  - `nq_exec`, `nq_guardrails`, `nq_portfolio`, `nq_promotion`, `nq_experiments` supply events/results.
- **Downstream**:
  - `nq_metrics` consumes `ObservabilityInput` to generate `SystemObservabilityReport`.
  - `nq_reporting`, dashboards, and SRE layers can consume the report for operational visibility.
- **Ownership**:
  - `nq_obs` does **not** own metrics definitions or storage; it only builds inputs and delegates to `nq_metrics`.
  - This separation keeps observability architecture explicit and auditable.

