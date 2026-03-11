# nq_improvement

Deterministic improvement-planning layer for NEBULA-QUANT v1. Consumes structured outputs from nq_learning, nq_audit, and nq_trade_review and produces a consolidated **ImprovementPlan** with prioritized, deduplicated actions. **Planning only** — no automatic execution, no strategy/config mutation, no state changes.

## Purpose

- **Consume** LearningReport (improvement_candidates, lessons, patterns), AuditReport (findings, recommendations), and TradeReviewReport(s) (findings, recommendations).
- **Generate** structured ImprovementAction items (title, description, priority, type, strategy/module, source_ids).
- **Prioritize** deterministically from source severity and category (CRITICAL/HIGH/MEDIUM/LOW).
- **Consolidate** actions with the same (related_strategy_id, related_module, improvement_type) to avoid duplicate noise while preserving traceability (source_ids, source_categories).
- **Produce** ImprovementPlan with summary and ordered actions for orchestration or human review.

## Supported sources

| Source          | Input                    | Typical data used                          |
|-----------------|--------------------------|--------------------------------------------|
| nq_learning     | LearningReport           | improvement_candidates, lessons, patterns  |
| nq_audit        | AuditReport              | findings (warning/critical), recommendations |
| nq_trade_review | TradeReviewReport / list | findings, recommendations                  |

## Action model

**ImprovementAction**: action_id, title, description, priority (low/medium/high/critical), improvement_type (strategy_review, module_review, execution_review, risk_review, portfolio_review, promotion_review, etc.), related_strategy_id, related_module, source_categories, source_ids, rationale, metadata.

**ImprovementType** (examples): STRATEGY_REVIEW, MODULE_REVIEW, EXECUTION_REVIEW, RISK_REVIEW, PORTFOLIO_REVIEW, PROMOTION_REVIEW, OBSERVABILITY_REVIEW, etc.

## Prioritization

- **CRITICAL**: from critical findings or critical learning candidates.
- **HIGH**: from warning findings or high-priority learning items.
- **MEDIUM**: from recommendations or moderate recurrence.
- **LOW**: from informational or isolated items.

Priorities are normalized (e.g. "warn" → high) and merged when consolidating (max priority wins). Rule-based only; no ML or fuzzy scoring.

## Deduplication / consolidation

Actions are grouped by (related_strategy_id, related_module, improvement_type). One representative action per group; priority is the maximum in the group; source_ids and source_categories are merged. Ordering is deterministic (priority descending, then title, strategy, module).

## Deterministic guarantees

- Same inputs produce the same action set and ordering.
- Plan ids: counter-based `improvement-plan-{n}` or caller-supplied.
- Action ids: renumbered after consolidation as `action-1`, `action-2`, ... for stable output.

## Future integration

- **nq_scheduler** / **nq_orchestrator**: trigger plan generation and optionally run review workflows.
- **nq_reporting**: include improvement plan in system reports.
- Human review: consume ImprovementPlan.actions for ticketing or runbooks.

No wiring in this phase; API is ready.

## Simple usage example

```python
from nq_improvement import ImprovementEngine

engine = ImprovementEngine()
plan = engine.generate_improvement_plan(
    learning_report=my_learning_report,
    audit_report=my_audit_report,
    trade_review_reports=[tr1, tr2],
)
print(plan.plan_id, plan.summary.total_actions)
for a in plan.actions:
    print(a.priority, a.improvement_type, a.title)
```
