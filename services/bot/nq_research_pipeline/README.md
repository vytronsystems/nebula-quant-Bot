NEBULA-QUANT v1 | `nq_research_pipeline` — Strategy Research Pipeline Orchestrator
===============================================================================

Purpose
-------

`nq_research_pipeline` activates the automated strategy research loop for NEBULA-QUANT v1.
It wires the existing research and evaluation modules into a single deterministic,
fail-closed orchestration layer that:

- discovers strategy candidates,
- evaluates them via experiments,
- backtests them,
- validates them using walk-forward analysis,
- simulates them in paper trading,
- and submits them for promotion decisions.


Pipeline Flow
-------------

The orchestrator follows the official research pipeline order:

- `nq_alpha_discovery`
- `nq_experiments`
- `nq_backtest`
- `nq_walkforward`
- `nq_paper`
- `nq_metrics`
- `nq_promotion`

All stages operate purely in memory and never call external services.


Public API
----------

### `ResearchPipelineEngine`

Main entry point for the research loop.

```python
from nq_research_pipeline import ResearchPipelineEngine

engine = ResearchPipelineEngine()
report = engine.run_research_cycle(market_data, regime_context=None)
```

#### `run_research_cycle(market_data, regime_context=None) -> ResearchCycleReport`

- **Inputs**
  - `market_data`: sequence of bar-like objects (dicts or typed models) with the
    fields required by `nq_backtest`, `nq_walkforward`, and `nq_paper`
    (e.g. `ts`, `close`, optional `symbol`, `timeframe`).
  - `regime_context`: optional contextual information about the regime or
    environment. It is accepted for future extension but not interpreted by the
    current implementation.

- **Outputs**
  - Returns a `ResearchCycleReport` summarizing the full research loop.


Data Model
----------

### `ResearchCycleReport`

Structured output for one research cycle:

- `cycle_id`: deterministic identifier derived from discovered strategy
  identifiers.
- `generated_at`: timestamp (float) taken from the injectable clock.
- `candidate_count`: number of distinct strategy candidates discovered.
- `experiment_count`: number of experiments analyzed for this cycle.
- `approved_strategies`: list of strategy identifiers that passed promotion
  checks.
- `rejected_strategies`: list of strategy identifiers that failed promotion
  checks.
- `summary`: dictionary with high-level counters:
  - `candidate_count`
  - `experiment_count`
  - `approved_count`
  - `rejected_count`


Stage Responsibilities
----------------------

The orchestration logic respects the ownership of each module:

- **Discovery (`nq_alpha_discovery`)**
  - Builds alpha hypotheses from normalized research observations.
  - The pipeline uses direct observation inputs constructed from `market_data`
    to materialize deterministic strategy candidates.

- **Experiments (`nq_experiments`)**
  - Constructs `ExperimentRecord` instances for each candidate strategy and
    runs deterministic analysis using `ExperimentEngine`.
  - Produces an `ExperimentReport` whose summary is fed into promotion checks.

- **Backtest (`nq_backtest`)**
  - Runs a safe placeholder strategy over `market_data` using `BacktestEngine`.
  - Produces a `BacktestResult` and a summarized backtest dictionary via
    `build_backtest_summary`, which is consumed by walk-forward and promotion.

- **Walkforward (`nq_walkforward`)**
  - Uses `WalkForwardEngine` to split `market_data` into train/test windows and
    evaluate pass/fail per window.
  - Produces a `WalkForwardResult` and a compact summary dictionary including
    `pass_rate` for promotion rules.

- **Paper (`nq_paper`)**
  - Runs `PaperEngine.run_session` over `market_data` with the same placeholder
    strategy.
  - Produces a `PaperSessionResult` whose `summary` is propagated into
    promotion inputs.

- **Metrics (`nq_metrics`)**
  - Converts backtest trades into `TradePerformance` records and passes them to
    `MetricsEngine.compute_metrics`.
  - Produces a `MetricsResult` used to build a compact metrics summary for
    promotion.

- **Promotion (`nq_promotion`)**
  - Builds `PromotionInput` instances per candidate strategy with:
    - `backtest_summary`
    - `walkforward_summary`
    - `paper_summary`
    - `metrics_summary`
    - `experiment_summary`
  - Uses `PromotionEngine.evaluate_promotion` to decide whether each strategy
    may transition from `walkforward` to `paper`.
  - Approved and rejected strategy identifiers are recorded in
    `ResearchCycleReport`.


Determinism and Fail-Closed Behavior
------------------------------------

- **Deterministic IDs**
  - `cycle_id` is derived solely from the sorted set of candidate strategy
    identifiers using a stable hash. Re-running the cycle with the same
    inputs yields the same `cycle_id`.

- **Injectable Clock**
  - `ResearchPipelineEngine` accepts an optional `clock` callable.
  - All timestamps in `ResearchCycleReport` and intermediate experiments use
    this clock, enabling deterministic testing.

- **No External Services**
  - The engine does not read from or write to disks, databases, or networks.
  - All inputs are supplied by the caller; all outputs are in-memory models and
    primitive types.

- **Fail-Closed**
  - Input validation is minimal but explicit: `market_data` must be a sequence
    or `None`, otherwise a `ResearchPipelineError` is raised.
  - Promotion rules (`nq_promotion`) are inherently fail-closed: missing or
    weak evidence leads to rejection rather than implicit approval.


Integration Notes
-----------------

- The orchestrator is a **pure coordination layer**. It does not implement
  discovery, simulation, or promotion logic itself; it delegates to the
  specialized modules listed above.
- `ResearchCycleReport` is intentionally compact so that higher-level reporting
  layers (`nq_reporting`, observability dashboards, CLI tools) can easily
  consume and display the status of the research pipeline.
- Future phases may:
  - enrich `summary` with additional metrics,
  - introduce configurable strategies per candidate instead of a placeholder
    strategy, and
  - integrate lifecycle registry modules to persist promotion outcomes.

