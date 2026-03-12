NEBULA-QUANT v1 | `nq_strategy_governance` — Strategy Promotion Governance & Live Readiness
===========================================================================================

Purpose
-------

`nq_strategy_governance` is the final **institutional governance layer** for
strategy lifecycle in NEBULA-QUANT v1. It evaluates whether a strategy:

- is **approved for live trading**,
- should **remain in paper**,
- must **return to research**, or
- should be **rejected**.

This module:

- does **not** execute trades,
- does **not** bypass promotion governance in `nq_promotion`,
- does **not** use probabilistic or opaque optimization.

It consumes structured summaries from upstream modules and makes explicit,
deterministic decisions.


Supported Inputs
----------------

`StrategyGovernanceInput` aggregates evidence from:

- `backtest_summary` (e.g. `profit_factor`, `win_rate`, `max_drawdown`)
- `walkforward_summary` (e.g. `pass_rate`)
- `paper_summary` (e.g. `total_trades`, `win_rate`, `max_drawdown`)
- `metrics_summary` (e.g. `win_rate`, `expectancy`, `max_drawdown`)
- `edge_decay_summary` (e.g. `significant` boolean)
- `audit_summary` (e.g. `blocking_issues`, `structural_invalid`)

All summaries are treated as dict-like objects; missing or empty summaries are
handled conservatively (fail-closed).


Decision Categories
-------------------

`StrategyGovernanceDecision` enum:

- `APPROVED_FOR_LIVE`
- `REMAIN_IN_PAPER`
- `RETURN_TO_RESEARCH`
- `REJECT_STRATEGY`


Threshold Philosophy
--------------------

Thresholds in `rules.py` are **fixed, explicit, and conservative**:

- **Backtest**
  - `profit_factor >= 1.2`
  - `win_rate >= 0.5`
  - `max_drawdown <= 0.25`

- **Walkforward**
  - `pass_rate >= 0.6`

- **Paper trading**
  - `total_trades >= 30`
  - `win_rate >= 0.5`
  - `max_drawdown <= 0.2`

- **Metrics**
  - `win_rate >= 0.5`
  - `expectancy >= 0.0` (if present)
  - `max_drawdown <= 0.2`

- **Edge decay**
  - `edge_decay_summary.significant == True` → critical blocker for live.

- **Audit**
  - `audit_summary.blocking_issues` non-empty or
    `audit_summary.structural_invalid == True` → critical blocker.

Decision logic:

- **APPROVED_FOR_LIVE**
  - All above thresholds satisfied.
  - No critical blockers (edge decay or audit).

- **REMAIN_IN_PAPER**
  - Backtest and walkforward pass,
  - but paper or metrics evidence is weak/insufficient.

- **RETURN_TO_RESEARCH**
  - Backtest or walkforward below thresholds (but no critical structural
    blocker), indicating need for further research/adaptation.

- **REJECT_STRATEGY**
  - Critical blockers present (edge decay and/or audit structural issues),
  - or severe evidence of structural invalidity. Strategy should not continue
  to consume research resources in its current form.


Deterministic Guarantees
------------------------

- **Report IDs**
  - `StrategyGovernanceEngine` builds `report_id` as:
    - `strategy-governance-report-{hash}`
    - Hash includes:
      - `strategy_id`
      - stringified `backtest_summary`, `walkforward_summary`,
        `paper_summary`, `metrics_summary`, `edge_decay_summary`,
        `audit_summary`.
  - Same input → same `report_id`.

- **Findings & Ordering**
  - `StrategyGovernanceFinding.finding_id` is `finding-{index}` in a fixed
    evaluation order, yielding deterministic ordering.

- **Fail-Closed Validation**
  - `StrategyGovernanceEngine.evaluate_strategy_readiness` requires a
    `StrategyGovernanceInput` with non-empty `strategy_id`.
  - Missing or malformed critical input raises `StrategyGovernanceError`.
  - Empty summaries produce conservative outcomes (remain in paper / return to
    research / reject), never silent approval.


Public API
----------

### `StrategyGovernanceEngine`

```python
from nq_strategy_governance import (
    StrategyGovernanceEngine,
    StrategyGovernanceInput,
)

engine = StrategyGovernanceEngine()
gi = StrategyGovernanceInput(
    strategy_id="strategy_1",
    backtest_summary=backtest_summary,
    walkforward_summary=walkforward_summary,
    paper_summary=paper_summary,
    metrics_summary=metrics_summary,
    edge_decay_summary=edge_decay_summary,
    audit_summary=audit_summary,
)
report = engine.evaluate_strategy_readiness(gi)
decision = report.decision  # StrategyGovernanceDecision
```


Relationship to `nq_promotion` and `nq_research_pipeline`
---------------------------------------------------------

- `nq_promotion`:
  - Governs lifecycle transitions (idea → research → backtest → walkforward → paper → live).
  - Decides if *promotion* to a given lifecycle state is allowed based on
    upstream summaries and guardrails.

- `nq_strategy_governance`:
  - Operates **after** promotion, backtest, walkforward, paper, and metrics.
  - Makes a final, explicit readiness decision for live, paper, or research
    return, taking into account:
    - quantitative performance,
    - edge decay,
    - audit findings.

- `nq_research_pipeline`:
  - Orchestrates discovery → experiments → backtest → walkforward → paper →
    metrics → promotion.
  - Can optionally call `StrategyGovernanceEngine` at the end of the pipeline
    and update its final summary of approved vs non-approved strategies
    according to governance decisions.

In combination, these modules create a **closed, auditable lifecycle** from
research candidates to live readiness decisions, while preserving strict,
deterministic governance at each step.

