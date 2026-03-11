# nq_reporting

Deterministic reporting layer for NEBULA-QUANT v1. Collects structured outputs from nq_audit, nq_trade_review, nq_learning, and observability (nq_metrics / nq_obs), and produces unified system reports. **Report generation only** — no trading, no state changes, no execution triggers.

## Purpose

- **Collect** structured outputs from analysis modules (AuditReport, TradeReviewReport, LearningReport, observability payloads).
- **Build** deterministic summary reports per type (AuditSummaryReport, TradeReviewSummaryReport, LearningSummaryReport, ObservabilitySummaryReport).
- **Assemble** a top-level **SystemReport** with optional subreports.
- **Serialize** to dict and JSON for dashboards, monitoring, and human review.

## Supported report types

| Source            | Input                  | Output                    |
|-------------------|------------------------|---------------------------|
| nq_audit          | AuditReport            | AuditSummaryReport        |
| nq_trade_review   | list of TradeReviewReport | TradeReviewSummaryReport |
| nq_learning       | LearningReport         | LearningSummaryReport     |
| nq_metrics / nq_obs | Observability dict/object | ObservabilitySummaryReport |

## How reports are built

- **build_audit_summary(audit_report)** — Extracts total_findings, severity distribution, affected strategies/modules, recommendations from AuditReport.summary and recommendations. Does not mutate input.
- **build_trade_review_summary(trade_review_reports)** — Aggregates win/loss/breakeven rates, common issue categories, severity distribution from a list of TradeReviewReport. Accepts None or empty list.
- **build_learning_summary(learning_report)** — Maps LearningReport.summary to LearningSummaryReport (patterns, lessons, improvement candidates, priorities, categories). Accepts None for empty summary.
- **build_observability_summary(observability_report)** — Extracts system_health_score, degraded/inactive strategies, event_anomalies, metrics_summary. Accepts None.

Builders fail closed on malformed critical input (e.g. audit_report without summary when building audit summary). Missing optional sections are allowed.

## System report structure

**SystemReport**:

- **report_id** — Counter-based `system-report-{n}` or caller-supplied.
- **generated_at** — Timestamp (injectable clock or provided).
- **audit_report** — AuditSummaryReport | None
- **trade_review_report** — TradeReviewSummaryReport | None
- **learning_report** — LearningSummaryReport | None
- **observability_report** — ObservabilitySummaryReport | None
- **metadata** — Optional dict.

Order of assembly is deterministic: audit, trade_review, learning, observability.

## Deterministic guarantees

- Same inputs produce identical report structures and builder outputs.
- Serialization (report_to_dict, report_to_json) is stable; JSON uses sort_keys=True by default.
- Report ids are counter-based or caller-supplied; no random UUIDs.

## Serialization

- **report_to_dict(report)** — Returns a plain dict (dataclasses.asdict); safe for JSON.
- **report_to_json(report, sort_keys=True, indent=None)** — Returns JSON string with deterministic key order.

## Future integration

- Dashboards (e.g. Grafana) can consume JSON or dict from ReportEngine.
- Observability tools can ingest SystemReport or subreports.
- Scheduler/orchestrator can trigger report generation and pass outputs to reporting or storage.

No wiring to other modules in this phase; API is ready for integration.

## Simple usage example

```python
from nq_reporting import ReportEngine, report_to_dict, report_to_json

engine = ReportEngine()
# With optional subreports (e.g. from nq_audit, nq_trade_review, nq_learning):
system_report = engine.generate_system_report(
    audit_report=my_audit_report,
    trade_review_reports=[tr1, tr2],
    learning_report=my_learning_report,
    observability_report={"system_health_score": 0.95, "degraded_strategies": []},
)
d = report_to_dict(system_report)
json_str = report_to_json(system_report)
```
