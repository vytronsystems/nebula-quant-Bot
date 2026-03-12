NEBULA-QUANT v1 | `nq_strategy_generation` — Automatic Strategy Generation Framework
====================================================================================

Purpose
-------

`nq_strategy_generation` is the dedicated layer that transforms:

- **market feature observations**,
- **regime context**, and
- **internal research feedback**

into deterministic **strategy templates**, **parameter sets**, and **strategy
candidates** ready for:

- `nq_experiments`
- `nq_backtest`
- `nq_research_pipeline`
- and later, `nq_reporting`.

This module does **not** import or depend on external public strategies. All
strategies are generated internally from NEBULA-QUANT's own signals and
feedback.


Supported Input Sources
-----------------------

- **Market feature observations** (examples):
  - `trend_strength`
  - `momentum_score`
  - `volatility_percentile`
  - `relative_volume`
  - `breakout_signal`
  - `mean_reversion_distance`
  - `session_bias`
  - `opening_range_breakout`

- **Regime context** (examples):
  - `TRENDING_UP`
  - `TRENDING_DOWN`
  - `RANGE_BOUND`
  - `HIGH_VOLATILITY`
  - `LOW_VOLATILITY`
  - `MIXED`

- **Internal learning feedback** (examples):
  - edge decay findings per family
  - persistent slippage issues
  - improvement candidates influencing preferred families


Strategy Families
-----------------

The module currently supports the following families via the `StrategyFamily`
enum:

- `BREAKOUT`
- `MOMENTUM_CONTINUATION`
- `MEAN_REVERSION`
- `OPENING_RANGE_BREAKOUT`
- `PULLBACK_CONTINUATION`
- `REVERSAL`
- `VOLATILITY_EXPANSION`
- `SESSION_BIAS`

Not all families have concrete templates yet; new templates can be added
explicitly to `templates.py` as the research program evolves.


Template Philosophy
-------------------

Templates in `templates.py` are:

- **static and deterministic**: defined as pure data structures with no hidden
  randomness or external calls;
- **explicit**: each template describes:
  - `entry_conditions`
  - `exit_conditions`
  - `stop_loss_rule`
  - `take_profit_rule`
  - `sizing_rule`
  - `regime_constraints`
- **auditable**: template IDs and fields are stable and easily inspected.

Minimum templates included:

- Breakout (`breakout_template`)
- Momentum continuation (`momentum_continuation_template`)
- Mean reversion (`mean_reversion_template`)
- Opening range breakout (`opening_range_breakout_template`)
- Pullback continuation (`pullback_continuation_template`)


Parameter Expansion Philosophy
------------------------------

Parameter expansion in `parameter_expansion.py` is:

- **deterministic**: uses sorted keys and a fixed cartesian product order;
- **bounded**: controlled by `MAX_PARAMETER_SETS_PER_TEMPLATE` and optional
  per-call caps;
- **family-specific**: each strategy family defines a small grid, e.g.:

  - Breakout
    - `lookback_bars`: `[10, 20, 30]`
    - `relvol_min`: `[1.2, 1.5]`
    - `stop_atr`: `[1.0, 1.5]`
    - `target_atr`: `[2.0, 2.5]`

  - Mean reversion
    - `zscore_threshold`: `[1.5, 2.0]`
    - `stop_atr`: `[1.0]`
    - `target_to_mean`: `[True]`

The resulting set of `StrategyParameterSet` instances per template is always
bounded and reproducible.


Deterministic Guarantees
------------------------

- **Report IDs**
  - `StrategyGenerationEngine` builds `report_id` as a stable hash of:
    - normalized `market_observations`,
    - `regime_context`, and
    - normalized `learning_feedback`.
  - Re-running with the same inputs yields the same `report_id`.

- **Candidate IDs**
  - Each `StrategyCandidate` has:
    - `strategy_id = "{template_id}-{parameter_set_id}"`
    - `candidate_id = "cand-{strategy_id}"`
  - These IDs depend only on template and parameter IDs plus deterministic
    matching logic, not on runtime counters.

- **Candidate Ordering**
  - Templates are iterated in a fixed order (`build_all_templates()`).
  - Parameter sets are built deterministically per template.
  - Candidates are created by iterating templates and their matching parameter
    sets in order, capped by `MAX_CANDIDATES_PER_RUN`.

- **Fail-Closed Validation**
  - Non-dict `market_observations` or `learning_feedback` raise
    `StrategyGenerationError`.
  - Empty or missing inputs produce a valid empty
    `StrategyGenerationReport` (no candidates).


Public API
----------

### `StrategyGenerationEngine`

```python
from nq_strategy_generation import StrategyGenerationEngine

engine = StrategyGenerationEngine()
report = engine.generate_strategies(
    market_observations={"trend_strength": 0.8, "momentum_score": 0.7},
    regime_context="TRENDING_UP",
    learning_feedback={"slippage_issues": False},
)
```

#### `generate_strategies(market_observations, regime_context=None, learning_feedback=None, report_id=None, generated_at=None)`

- **Inputs**
  - `market_observations: dict | None`
  - `regime_context: Any | None` (string or enum-like)
  - `learning_feedback: dict | None`
  - Optional `report_id` and `generated_at` for callers that need to override
    defaults (e.g., tests).

- **Outputs**
  - `StrategyGenerationReport` containing:
    - `templates: list[StrategyTemplate]`
    - `parameter_sets: list[StrategyParameterSet]`
    - `candidates: list[StrategyCandidate]`
    - `summary: StrategyGenerationSummary`


Integration with `nq_research_pipeline`
---------------------------------------

`nq_strategy_generation` is designed to plug into `nq_research_pipeline` as the
upstream source of **strategy candidates**:

- The research pipeline can:
  - call `StrategyGenerationEngine.generate_strategies(...)`,
  - extract `StrategyCandidate` identifiers and metadata, and
  - register corresponding experiments in `nq_experiments`.

- When no candidates are generated:
  - downstream modules must receive empty inputs and produce valid empty
    reports (fail-closed, not error-prone).

The current phase keeps this integration optional so existing research pipeline
behavior remains backward compatible while enabling deterministic strategy
generation where configured.

