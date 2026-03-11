# nq_alpha_discovery

**NEBULA-QUANT v1** — Deterministic alpha-hypothesis generation from structured research inputs.

## Purpose

`nq_alpha_discovery` consumes structured outputs from nq_learning, nq_experiments, nq_audit, nq_trade_review, and optional direct observations, and produces **explicit alpha hypotheses** with rationale and evidence linkage. It does **not** execute trades, modify strategies, replace nq_strategy/nq_backtest/nq_experiments, or invent unsupported signals.

## Supported input sources

| Source           | Extracted data                                      |
|------------------|-----------------------------------------------------|
| LearningReport   | patterns, lessons, improvement_candidates           |
| ExperimentReport | findings                                            |
| AuditReport      | findings, recommendations                          |
| TradeReviewReport(s) | findings, recommendations per report        |
| Direct observations | caller-supplied list (category, title, optional strategy/module) |

## Observation model

**AlphaObservation**: observation_id, source_type, category, strategy_id, module, title, description, severity, metadata.  
**AlphaEvidence**: evidence_id, source_type, source_id, category, strategy_id, module, weight, metadata.  
Observations are normalized from each source; evidence links each observation for traceability.

## Hypothesis model

**AlphaHypothesis**: hypothesis_id, title, description, category, related_strategy_id, related_module, priority (low/medium/high/critical), confidence_score (0–1), evidence_ids, rationale, metadata.

- Hypotheses are built by **grouping observations** by (category, strategy_id, module).
- One hypothesis per group; title and description are derived from category and first observation.
- **Rationale** is explicit: "Based on N observation(s): …" with observation titles.
- **evidence_ids** link to AlphaEvidence for auditability.

## Ranking / priority rules

- **CRITICAL**: ≥2 observations and at least one critical severity.
- **HIGH**: any critical, or ≥2 observations with at least one warning/high.
- **MEDIUM**: ≥2 observations.
- **LOW**: single observation.

Hypotheses are sorted by priority (critical > high > medium > low), then by confidence_score descending, then by hypothesis_id. **confidence_score** is computed from observation count and severity (simple additive rule).

## Deterministic guarantees

- Same inputs produce the same observations, hypotheses, and report structure.
- Report and hypothesis ids are counter-based (`alpha-discovery-report-{n}`, `hyp-{n}`) or caller-supplied.
- No random ids; ordering is stable.

## Future integration

- **nq_experiments / nq_backtest**: Feed hypotheses as experiment ideas or backtest candidates.
- **nq_learning / nq_reporting**: Consume hypothesis summaries for learning loops and reports.
- Orchestration will call `generate_hypotheses(...)` with reports from learning, experiments, audit, trade review; no deep wiring in this phase.
