# nq_audit

Deterministic audit analysis module for NEBULA-QUANT v1. Analyzes recorded system behavior (decisions, execution outcomes, strategy health, event streams) and produces structured audit reports with findings and recommendations. **Analysis infrastructure only** — no trading logic, no mutation of source records.

## Purpose

- **Consume** historical inputs from repositories/modules (events, decision records, execution records, strategy health, control/experiment summaries, registry).
- **Analyze** decisions and outcomes, strategy lifecycle, and event concentrations.
- **Produce** structured audit reports with explicit findings and severity.
- **Recommend** deterministic, finding-grounded next steps for review workflows.

## Input model

Audit runs on an **AuditInput** dataclass:

- **events**: list of event dicts (e.g. from nq_event_store); may include `event_type`, `aggregate_id`, `aggregate_type`, `payload`.
- **decision_records**: list of decision dicts; may include `module`, `strategy_id`, `action`, `outcome`, `blocked`, `throttled`, `promotion_rejected`, `category`.
- **execution_records**: list of execution dicts; may include `strategy_id`, `module`, `success`/`failed`, `outcome`.
- **strategy_health**: list of health dicts; may include `strategy_id`, `status`, `health`, `degraded`, `inactive`.
- **control_summary**: optional dict (e.g. `inconsistent_strategies`, `lifecycle_issues`).
- **experiment_summary**: optional dict.
- **registry_records**: optional list (e.g. `strategy_id`, `executable`, `lifecycle_state`).
- **metadata**: optional dict.

Optional sections may be missing or empty; analyzers skip them or return empty findings. Critical malformed input (e.g. non-list where a list is required) raises **AuditError** (fail-closed).

## Finding model

Each **AuditFinding** has:

- **finding_id**, **category**, **severity** (info / warning / critical), **title**, **description**
- **related_strategy_id**, **related_module** (optional)
- **metadata** (optional)

Categories are fixed and documented (e.g. `repeated_blocked_decisions`, `excessive_throttling`, `repeated_promotion_rejections`, `degraded_strategy_detected`, `inactive_strategy_detected`, `execution_failure_pattern`, `lifecycle_inconsistency_detected`, `event_concentration`).

## Severity model

- **INFO**: minor anomalies, noteworthy status, or event concentration.
- **WARNING**: repeated issues (e.g. blocked/throttle/reject counts above warning threshold), degraded strategy, lifecycle inconsistency.
- **CRITICAL**: severe repeated patterns (counts above critical threshold).

Thresholds are documented in the code (e.g. blocked: warning ≥2, critical ≥5). Same inputs always yield the same severity.

## Deterministic analysis philosophy

- Same **AuditInput** and clock/caller-supplied ids produce the same **AuditReport**.
- No randomness; no hidden external services or file I/O in the analysis path.
- Malformed critical input raises **AuditError**; optional sections are handled safely with no fabricated data.

## Recommendation generation philosophy

Recommendations are derived **only** from findings: one or more concrete suggestions per relevant finding (e.g. “Review strategy X due to repeated blocked decisions”, “Investigate module nq_exec due to repeated execution failures”). No speculation beyond the finding fields.

## Intended future integration points

- **nq_scheduler**: trigger periodic audit jobs.
- **nq_orchestrator**: run audit as a workflow step.
- **nq_reporting**: publish audit report.
- **nq_trade_review** / **nq_learning**: consume findings for review or learning pipelines.

No deep wiring in this phase; the API is designed for these integrations.

## Simple usage example

```python
from nq_audit import AuditEngine, AuditInput

engine = AuditEngine()
input_data = AuditInput(
    decision_records=[
        {"module": "nq_risk", "strategy_id": "s1", "blocked": True},
        {"module": "nq_risk", "strategy_id": "s1", "blocked": True},
    ],
    execution_records=[],
    strategy_health=[],
)
report = engine.run_audit(input_data)
assert report.summary.total_findings >= 1
assert report.summary.warning_count >= 1
for f in report.findings:
    print(f.category, f.severity, f.title)
for r in report.recommendations:
    print(r)
```
