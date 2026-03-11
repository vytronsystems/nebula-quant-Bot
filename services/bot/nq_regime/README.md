# nq_regime

**NEBULA-QUANT v1** — Deterministic market regime classification from structured context.

## Purpose

`nq_regime` consumes structured market context (trend, volatility, momentum, structure hints) and produces **explicit regime classifications** with rationale and evidence. It does **not** execute trades, generate live signals, replace nq_strategy/nq_risk, or invent missing values. Rule-based only; no ML or black-box inference.

## Supported input fields

**RegimeInput** (or dict): observation_id, symbol, timestamp, price, moving_average_short, moving_average_long, trend_strength, volatility, volatility_percentile, momentum_score, structure_hint, liquidity_hint, metadata.

- **Trend**: short/long MA and trend_strength drive TRENDING_UP / TRENDING_DOWN.
- **Volatility**: volatility_percentile (or volatility) drives HIGH_VOLATILITY / LOW_VOLATILITY.
- **Momentum**: momentum_score drives MOMENTUM_UP / MOMENTUM_DOWN.
- **Structure**: structure_hint (e.g. range, range_bound) or weak trend + neutral momentum → RANGE_BOUND.
- **Conflicting signals** → MIXED; insufficient data → UNKNOWN.

## Classification labels

- TRENDING_UP, TRENDING_DOWN  
- RANGE_BOUND  
- HIGH_VOLATILITY, LOW_VOLATILITY  
- MOMENTUM_UP, MOMENTUM_DOWN  
- MIXED, UNKNOWN  

## Rule-based classification (classifiers.py)

- **Volatility**: percentile ≥ 75 → HIGH_VOLATILITY; ≤ 25 → LOW_VOLATILITY (takes precedence when present).
- **Trend**: short MA > long MA and trend_strength ≥ 0.1 → TRENDING_UP; opposite → TRENDING_DOWN.
- **Momentum**: momentum_score ≥ 0.2 → MOMENTUM_UP; ≤ -0.2 → MOMENTUM_DOWN.
- **Range**: structure_hint in (range, range_bound, …) or |trend_strength| < 0.1 and |momentum| < 0.2 → RANGE_BOUND.
- **Mixed**: trend and momentum in opposite directions → MIXED.
- **Unknown**: no rule fires → UNKNOWN (confidence 0).

Each classification includes **rationale** and **evidence_ids** linking to RegimeEvidence (category, value, description).

## Deterministic guarantees

- Same inputs produce the same classifications and report structure.
- Report and classification ids are counter-based (`regime-report-{n}`, `cl-{n}`); evidence ids use `ev-{input_index}-{evidence_index}`.
- No random ids.

## Future integration

- **nq_experiments / nq_alpha_discovery**: Tag experiments or hypotheses by regime.
- **nq_edge_decay**: Use regime context for edge decay detection.
- **nq_reporting**: Expose regime labels and summaries in reports.

No deep wiring in this phase; API is ready for integration.
