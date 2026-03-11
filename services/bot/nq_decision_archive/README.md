# nq_decision_archive

**NEBULA-QUANT v1** — Deterministic decision-history archival and query for control modules.

## Purpose

`nq_decision_archive` stores, normalizes, and exposes structured decision history from nq_risk, nq_guardrails, nq_portfolio, and nq_promotion. It does **not** make decisions, replace nq_event_store or nq_db, execute trades, or mutate source decisions. It provides a stable contract for audit and reporting.

## Supported decision sources

| Source         | Normalizer                    | Canonical outcomes        |
|----------------|-------------------------------|---------------------------|
| nq_risk        | normalize_risk_decision        | allow, reduce, block      |
| nq_guardrails  | normalize_guardrails_decision  | allow, block              |
| nq_portfolio   | normalize_portfolio_decision  | allow, throttle, block    |
| nq_promotion   | normalize_promotion_decision  | approve, reject           |

## Normalization

- Source-specific payloads (dict or object) are mapped to a stable **DecisionRecord**: archive_id, source_module, source_type, decision_type, decision_outcome, strategy_id, symbol, timestamp, reason_codes, source_id, metadata.
- Outcome aliases are normalized to canonical values (e.g. allowed=True → allow, allowed=False → block/reject).
- Reason fields and signals are normalized to `reason_codes: list[str]`.
- Missing optional fields are left empty/None. Missing critical fields (e.g. decision outcome, timestamp when not provided by caller) raise **DecisionArchiveError**; no guessing.

## Query model

**DecisionQuery**: strategy_id, source_module, decision_outcome, start_time, end_time, limit.  
**Repository**: `list_records(query)`, `list_by_strategy(strategy_id)`, `list_by_module(source_module)`, `list_by_outcome(decision_outcome)`.  
Results are returned in deterministic order (timestamp, then archive_id).

## Summary and report

- **DecisionArchiveSummary**: total_records, by_module, by_outcome, strategies_seen, reason_code_counts.
- **DecisionArchiveReport**: report_id, generated_at, records, summary, metadata. Report ids: `decision-archive-report-{n}` or caller-supplied.

## Deterministic guarantees

- Same input payloads produce the same normalized records.
- Archive and report ids are counter-based or caller-provided; no random ids.
- Ordering of records and summary keys is deterministic.

## Future integration

- **nq_audit / nq_reporting**: Consume archived decisions for audit trails and system reports.
- **Dashboards**: Query by strategy, module, outcome, or time window for visibility.
- Orchestration will call the archive after control modules produce decisions; no deep wiring in this phase.
