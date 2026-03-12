NEBULA-QUANT v1 | `nq_strategy_adaptation` — Adaptive Strategy Improvement Layer
================================================================================

Purpose
-------

`nq_strategy_adaptation` converts internal feedback into **deterministic
adaptation directives** that guide future strategy generation and research
without mutating live strategies or bypassing governance.

This module operates purely at the **research refinement** level and:

- does **not** auto-approve strategies,
- does **not** modify live trading behavior,
- does **not** use probabilistic or opaque optimization.

Instead, it produces explicit, auditable directives that can be consumed by:

- `nq_strategy_generation`
- `nq_research_pipeline`
- `nq_experiments`


Supported Feedback Sources
--------------------------

The engine accepts structured inputs (duck-typed) from:

- `LearningReport`
- `ImprovementPlan`
- `EdgeDecayReport`
- `TradeReviewReport` or `list[TradeReviewReport]`
- `AuditReport`
- `ExperimentReport`

Adapters in `adapters.py` normalize these into simple, stable facts such as:

- presence of slippage issues
- edge decay by family
- experiment successes/failures
- regime-specific strengths/weaknesses
- improvement-plan flags


Directive Model
---------------

Key models (in `models.py`):

- `AdaptationActionType`
  - `SUPPRESS_FAMILY`
  - `PREFER_FAMILY`
  - `EXCLUDE_REGIME`
  - `REQUIRE_REGIME`
  - `ADJUST_PARAMETER_RANGE`
  - `REDUCE_PRIORITY`
  - `INCREASE_PRIORITY`
  - `FLAG_FOR_REVIEW`

- `AdaptationDirective`
  - `directive_id`: deterministic identifier derived from action, targets, and sources.
  - `action_type`: one of `AdaptationActionType`.
  - `target_family`: strategy family affected (if any).
  - `target_parameter`: parameter name (for range adjustments).
  - `target_regime`: regime identifier (for specialization).
  - `value`: additional structured value (e.g. range dict).
  - `rationale`: human-readable explanation.
  - `source_ids`: list of originating report IDs.
  - `metadata`: reserved for future use.

- `StrategyAdaptationSummary`
  - `total_directives`
  - `suppressed_families`
  - `preferred_families`
  - `excluded_regimes`
  - `parameter_adjustments`

- `StrategyAdaptationReport`
  - `report_id` (deterministic)
  - `generated_at`
  - `directives: list[AdaptationDirective]`
  - `summary: StrategyAdaptationSummary`


Adaptation Philosophy
---------------------

Rules in `rules.py` are:

- **explicit**: all conditions are spelled out and rely on normalized facts;
- **deterministic**: there is no randomness or model-based scoring;
- **bounded**: directive count and types are controlled and auditable.

Examples:

- **Slippage suppression**
  - If trade reviews indicate repeated slippage issues:
    - `SUPPRESS_FAMILY` for `breakout` and `opening_range_breakout`.

- **Edge decay suppression**
  - If edge decay is reported for a family:
    - `REDUCE_PRIORITY` for that family.

- **Successful experiments**
  - If experiments repeatedly succeed for a family:
    - `PREFER_FAMILY` for that family.

- **Regime specialization**
  - If audit findings show strong performance for `(family, regime)`:
    - `REQUIRE_REGIME` for that pair.
  - If audit findings show poor performance:
    - `EXCLUDE_REGIME` for that pair.

- **Parameter adjustment**
  - If trade reviews show poor entries:
    - `ADJUST_PARAMETER_RANGE` for breakout `lookback_bars`.
  - If trade reviews show poor exits:
    - `ADJUST_PARAMETER_RANGE` for momentum `momentum_threshold`.

- **Promotion / improvement plan feedback**
  - Families flagged in `ImprovementPlan`:
    - `FLAG_FOR_REVIEW`.


Deterministic Guarantees
------------------------

- **Report IDs**
  - `StrategyAdaptationEngine` builds `report_id` from a hash of the normalized
    feedback facts:
    - top-level keys sorted,
    - values stringified in a stable way.
  - Same feedback → same `report_id`.

- **Directive IDs**
  - Each directive’s `directive_id` is derived from:
    - `action_type`,
    - target fields,
    - structured `value` (if any),
    - sorted `source_ids`.
  - Implemented via a small `sha256` hash; deterministic across runs.

- **Ordering**
  - Directives are **sorted by `directive_id`** before returning, ensuring
    stable ordering for identical inputs.

- **Fail-closed**
  - Malformed critical inputs (e.g. scalar in place of trade review list) raise
    `StrategyAdaptationError`.
  - All-empty inputs produce a valid empty `StrategyAdaptationReport` with
    zero directives.


Public API
----------

### `StrategyAdaptationEngine`

```python
from nq_strategy_adaptation import StrategyAdaptationEngine

engine = StrategyAdaptationEngine()
report = engine.generate_adaptation_report(
    learning_report=learning_report,
    improvement_plan=improvement_plan,
    edge_decay_report=edge_decay_report,
    trade_review_reports=trade_reviews,
    audit_report=audit_report,
    experiment_report=experiment_report,
)
```

Returns a `StrategyAdaptationReport` suitable for feeding into strategy
generation and research orchestration.


Integration with Strategy Generation and Research Pipeline
----------------------------------------------------------

- **`nq_strategy_generation`**
  - `StrategyGenerationEngine.generate_strategies(...)` can optionally accept
    an `adaptation_report`.
  - When provided, adaptation directives are applied **before** candidate
    generation to:
    - suppress certain families,
    - prefer others,
    - exclude regimes,
    - filter parameter sets by adjusted ranges.

- **`nq_research_pipeline`**
  - Higher-level orchestration may:
    - run `StrategyAdaptationEngine` on recent feedback,
    - pass the resulting `StrategyAdaptationReport` into
      `StrategyGenerationEngine`,
    - then continue through experiments, backtest, walk-forward, paper,
      metrics, and promotion.

This keeps the adaptive loop **explicit and inspectable**, with all decisions
recorded as structured directives instead of hidden heuristics.

