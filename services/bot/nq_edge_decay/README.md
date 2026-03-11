# nq_edge_decay

**NEBULA-QUANT v1** — Deterministic edge decay detection from structured performance and experiment inputs.

## Purpose

`nq_edge_decay` compares recent vs baseline (or prior window) metrics to detect **deterioration of edge quality** in a rule-based way. It does **not** execute trades, disable strategies, mutate live strategies, or replace nq_risk/nq_guardrails. Outputs are typed findings with rationale and evidence for audit, learning, improvement, and reporting.

## Supported input fields

**EdgeDecayInput** (or dict): strategy_id, window_id, baseline_window_id, recent_pnl, baseline_pnl, recent_win_rate, baseline_win_rate, recent_expectancy, baseline_expectancy, recent_slippage, baseline_slippage, recent_failed_experiments, baseline_failed_experiments, recent_degraded_experiments, baseline_degraded_experiments, repeated_trade_review_findings, repeated_audit_findings, regime_label, metadata.

## Decay categories

- **pnl_decay** — Recent PnL deteriorated vs baseline (e.g. ≥10% drop).
- **win_rate_decay** — Win rate dropped vs baseline (e.g. ≥5 pp).
- **expectancy_decay** — Expectancy dropped vs baseline (e.g. ≥0.10 absolute).
- **slippage_decay** — Slippage worsened vs baseline (e.g. ≥20% increase).
- **experiment_quality_decay** — More failed/degraded experiments in recent vs baseline.
- **execution_quality_decay** — Repeated trade review or audit findings above threshold.
- **mixed_edge_decay** — Multiple decay categories for same strategy (critical).
- **insufficient_baseline** — Baseline missing for required comparison.
- **inconsistent_edge_input** — Reserved for invalid/inconsistent input handling.

## Rule-based detection (analyzers.py)

- **Thresholds** (documented in code): PNL_DECAY_PCT_THRESHOLD=10%, WIN_RATE_DROP_THRESHOLD=5 pp, EXPECTANCY_DROP_THRESHOLD=0.10, SLIPPAGE_WORSEN_PCT_THRESHOLD=20%, EXECUTION_FINDINGS_THRESHOLD=2, EXPERIMENT_DECAY_MIN_DELTA=1.
- Each finding has **rationale** and **evidence_ids** linking to EdgeDecayEvidence (category, value, description).
- No ML or probabilistic inference; same inputs → same findings.

## Deterministic guarantees

- Same inputs produce the same findings and report structure.
- Report and finding ids are counter-based (`edge-decay-report-{n}`, `find-{input_idx}-{finding_idx}`); evidence ids use `ev-{input_idx}-{evidence_idx}`.
- No random ids.

## Future integration

- **nq_audit / nq_learning / nq_improvement / nq_reporting**: Consume EdgeDecayReport for audit trails, learning inputs, improvement planning, and system reports.
- **Regime context**: Optional regime_label on input for context; nq_regime remains owner of classification.

No deep wiring in this phase; API is ready for integration.
