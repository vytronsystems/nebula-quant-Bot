# nq_learning

Deterministic learning-analysis module for NEBULA-QUANT v1. Consumes structured findings from nq_audit and nq_trade_review, aggregates them into patterns, and produces lessons and improvement candidates. **Analysis infrastructure only** — no trading decisions, no auto-tuning, no ML.

## Purpose

- **Consume** audit findings and trade-review findings (list of finding-like dicts with category, severity, optional related_strategy_id, related_module).
- **Aggregate** by category, by (category + strategy), by (category + module); count and severity distribution.
- **Produce** deterministic LearningPattern, LearningLesson, and ImprovementCandidate.
- **Support** future integration with nq_improvement and nq_reporting.

## Input model

**LearningInput**:

- **audit_findings**: list of finding-like dicts (e.g. from nq_audit reports); each must have `category` and `severity`; may have `related_strategy_id` or `strategy_id`, `related_module`.
- **trade_review_findings**: list of finding-like dicts (e.g. from nq_trade_review reports); same shape.
- **metadata**: optional dict.

Findings without a valid `category` are skipped. Malformed critical input (e.g. non-list) raises **LearningError**.

## Pattern model

**LearningPattern**: pattern_id, category, count, related_strategy_id, related_module, severity_distribution (e.g. {"info": 1, "warning": 2}), metadata. Patterns are produced for (category), (category, strategy_id), (category, module).

## Lesson model

**LearningLesson**: lesson_id, title, description, priority (low/medium/high/critical), related_categories, related_strategy_id, related_module, metadata. Lessons are derived only from patterns with count >= 2 (recurring). Title/description are deterministic from pattern category and strategy/module.

## Improvement-candidate model

**ImprovementCandidate**: candidate_id, title, description, priority, source_patterns, related_strategy_id, related_module, metadata. Derived from the same recurring patterns; title/description follow documented rules (e.g. "Review entry rules for strategy X", "Investigate slippage conditions").

## Priority rules

- **CRITICAL**: pattern has at least one finding with severity "critical".
- **HIGH**: pattern has at least two "warning" findings or any "critical".
- **MEDIUM**: pattern count >= 3 and not HIGH/CRITICAL.
- **LOW**: otherwise.

Same inputs always yield the same priority.

## Intended future integration

- **nq_improvement**: consume improvement candidates.
- **nq_reporting**: publish learning reports.
- **nq_scheduler** / **nq_orchestrator**: trigger learning runs.
- **nq_audit** / **nq_trade_review**: pass findings into LearningInput.

No wiring in this phase; API is ready.

## Simple usage example

```python
from nq_learning import LearningEngine, LearningInput

engine = LearningEngine()
input_data = LearningInput(
    audit_findings=[
        {"category": "repeated_blocked_decisions", "severity": "warning", "related_strategy_id": "s1"},
        {"category": "repeated_blocked_decisions", "severity": "warning", "related_strategy_id": "s1"},
    ],
    trade_review_findings=[
        {"category": "poor_entry_quality", "severity": "warning", "strategy_id": "s1"},
    ],
)
report = engine.run_learning(input_data)
print(report.summary.total_patterns, report.summary.total_lessons)
for p in report.patterns:
    print(p.category, p.count, p.severity_distribution)
for c in report.improvement_candidates:
    print(c.priority, c.title)
```
