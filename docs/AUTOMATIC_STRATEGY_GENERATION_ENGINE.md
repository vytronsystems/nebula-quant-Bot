# NEBULA-QUANT v1  
## Automatic Strategy Generation Engine

Version: 1.0  
Status: Institutional Research Architecture  
Owner: NEBULA-QUANT Research Layer  

---

# 1. Purpose

This document defines how **NEBULA-QUANT automatically generates trading strategies**.

The system does **not** depend on external public strategy repositories as a primary research source.  
Instead, it generates strategy candidates internally from:

- market observations
- regime context
- experiment feedback
- trade review findings
- audit findings
- learning and improvement outputs
- edge decay signals

This document establishes the architecture used to transform those signals into **deterministic strategy candidates** suitable for:

- experiments
- backtesting
- walkforward validation
- paper trading
- promotion decisions

---

# 2. Core Principle

NEBULA-QUANT does **not generate random strategies**.

It generates strategies by applying **deterministic templates** to structured market and research observations.

The research engine must be:

- deterministic
- auditable
- traceable
- fail-closed
- bounded in candidate expansion

---

# 3. Inputs to Strategy Generation

The strategy generation engine consumes structured information from the following layers.

## 3.1 Market Observations

From:

```text
nq_data
nq_data_quality
Examples of structured features:

trend_strength

momentum_score

volatility_percentile

relative_volume

breakout_signal

mean_reversion_distance

session_bias

opening_range_state

intraday_extension

These features are converted into strategy generation observations.

3.2 Regime Context
From:

nq_regime
Examples:

TRENDING_UP

TRENDING_DOWN

RANGE_BOUND

HIGH_VOLATILITY

LOW_VOLATILITY

MIXED

Regime context constrains which strategy families may be generated.

3.3 Internal Learning Feedback
From:

nq_learning
nq_experiments
nq_trade_review
nq_audit
nq_edge_decay
nq_improvement
Examples of internal feedback:

repeated poor entry quality

recurring slippage issues

weak experiment outcomes

edge decay warnings

repeated promotion rejection

repeated execution-quality problems

This feedback does not directly create strategies, but it influences:

which strategy families are preferred

which families should be deprioritized

which parameter ranges should be avoided

4. Generation Pipeline
The automatic strategy generation workflow is:

Market Data
→ Feature Extraction
→ Regime Classification
→ Strategy Family Selection
→ Strategy Template Selection
→ Parameter Expansion
→ Candidate Generation
→ Experiments
→ Backtest
→ Walkforward
→ Paper
→ Promotion
This process is deterministic for the same inputs.

5. Strategy Families
The initial system supports a fixed set of strategy families.

5.1 Breakout
Use when:

breakout_signal is true

relative_volume is elevated

regime is directional

Typical regime:

TRENDING_UP

TRENDING_DOWN

5.2 Momentum Continuation
Use when:

momentum_score is strong

trend_strength is positive or negative in a persistent way

regime is trending

Typical regime:

TRENDING_UP

TRENDING_DOWN

5.3 Mean Reversion
Use when:

price is far from mean

momentum is weak or exhausted

regime is range bound

Typical regime:

RANGE_BOUND

5.4 Opening Range Breakout
Use when:

opening range is defined

session bias is strong

volume confirms participation

Typical regime:

TRENDING_UP

TRENDING_DOWN

HIGH_VOLATILITY

5.5 Pullback Continuation
Use when:

trend is established

price retraces without invalidating structure

momentum resumes

Typical regime:

TRENDING_UP

TRENDING_DOWN

6. Strategy Templates
A strategy candidate is built from a template.

Each template defines:

entry conditions

exit conditions

stop-loss rule

take-profit rule

sizing rule

regime constraints

Example: Breakout Template
{
  "family": "BREAKOUT",
  "entry_conditions": {
    "break_recent_high": true,
    "relative_volume_min": 1.5,
    "momentum_score_min": 0.4
  },
  "exit_conditions": {
    "time_stop_bars": 12
  },
  "stop_loss_rule": {
    "atr_multiple": 1.0
  },
  "take_profit_rule": {
    "atr_multiple": 2.0
  },
  "regime_constraints": [
    "TRENDING_UP"
  ]
}
Templates must remain explicit and auditable.

7. Parameter Expansion
Each template is expanded into a bounded number of parameter sets.

Example for BREAKOUT:

lookback_bars = [10, 20, 30]

relative_volume_min = [1.2, 1.5]

stop_atr = [1.0, 1.5]

target_atr = [2.0, 2.5]

Example for MEAN_REVERSION:

zscore_threshold = [1.5, 2.0]

stop_atr = [1.0]

mean_reversion_window = [10, 20]

Parameter expansion must be:

deterministic

bounded

documented

reproducible

The system must not generate unbounded combinatorial explosions.

8. Candidate Generation
A StrategyCandidate must include:

strategy_id

family

template_id

parameter_set_id

regime

rationale

feature snapshot

metadata

Example:

{
  "strategy_id": "breakout_qqq_001",
  "family": "BREAKOUT",
  "template_id": "template-breakout-01",
  "parameter_set_id": "params-breakout-03",
  "regime": "TRENDING_UP",
  "rationale": "Breakout signal with elevated relative volume and positive trend strength.",
  "feature_snapshot": {
    "relative_volume": 1.9,
    "momentum_score": 0.52,
    "trend_strength": 0.63
  }
}
Candidates must be deterministic for identical inputs.

9. Role of Internal Feedback
Internal feedback modifies candidate generation rules.

Examples:

9.1 Slippage degradation
If trade review repeatedly shows slippage problems:

deprioritize fast breakout candidates

reduce preference for highly reactive intraday setups

9.2 Edge decay
If a family shows repeated decay:

reduce candidate generation for that family

require stronger evidence before regeneration

9.3 Improvement candidates
If nq_improvement recommends:

“review entry rules”

“review exit discipline”

the generator may bias toward:

wider stop/target families

less timing-sensitive entries

regime-restricted strategies

Feedback must be applied explicitly and deterministically.

10. Interaction with nq_alpha_discovery
nq_alpha_discovery generates alpha hypotheses.
nq_strategy_generation converts those hypotheses and other structured signals into concrete strategy candidates.

Relationship:

nq_alpha_discovery
→ AlphaHypothesis
→ nq_strategy_generation
→ StrategyCandidate
This preserves a separation between:

idea generation

strategy construction

11. Interaction with nq_research_pipeline
nq_research_pipeline must consume generated candidates.

Workflow:

nq_strategy_generation
→ StrategyCandidate[]
→ nq_experiments
→ nq_backtest
→ nq_walkforward
→ nq_paper
→ nq_promotion
This means automatic strategy generation is part of the institutional research loop, not a side tool.

12. Promotion Principle
A generated strategy does not go live because it exists.

It must pass:

experiments

backtesting

walkforward validation

paper trading

promotion governance

Possible promotion outcomes:

APPROVED_FOR_LIVE
REMAIN_IN_PAPER
RETURN_TO_RESEARCH
REJECT_STRATEGY
If a strategy fails:

it returns to the research loop

13. Determinism Requirements
The strategy generation engine must guarantee:

same observations → same strategy families

same templates → same parameter expansion

same inputs → same candidate IDs

same research inputs → same candidate ordering

No hidden randomness is allowed.

14. Fail-Closed Requirements
The engine must fail closed when:

critical market observations are malformed

regime information is contradictory beyond supported rules

required template fields are missing

parameter expansion rules are invalid

In these cases the system must:

raise explicit errors

or return zero candidates safely

It must not guess.

15. Future Extensions
Possible future improvements:

feature extraction engines

pattern mining layer

more advanced regime-conditioned families

adaptive family suppression based on edge decay

candidate scoring calibrated by research outcomes

These extensions must preserve determinism and auditability.

16. Summary
NEBULA-QUANT automatically generates strategies by combining:

market observations

regime context

internal research feedback

deterministic strategy templates

bounded parameter expansion

The result is a structured set of strategy candidates that enter the institutional research pipeline and are only promoted if they pass strict validation.
