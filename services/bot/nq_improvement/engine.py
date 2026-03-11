# NEBULA-QUANT v1 | nq_improvement engine

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from nq_improvement.models import (
    ImprovementAction,
    ImprovementPlan,
    ImprovementPlanSummary,
)
from nq_improvement.planners import plan_from_audit, plan_from_learning, plan_from_trade_review
from nq_improvement.prioritization import merge_priority, normalize_priority, priority_rank


def _consolidate_actions(actions: list[ImprovementAction]) -> list[ImprovementAction]:
    """Merge actions with same (related_strategy_id, related_module, improvement_type). Preserve traceability."""
    if not actions:
        return []
    groups: dict[tuple[str | None, str | None, str], list[ImprovementAction]] = defaultdict(list)
    for a in actions:
        key = (a.related_strategy_id, a.related_module, a.improvement_type)
        groups[key].append(a)
    merged: list[ImprovementAction] = []
    for key, group in sorted(groups.items(), key=lambda x: (x[0][0] or "", x[0][1] or "", x[0][2])):
        first = group[0]
        priority = first.priority
        source_ids: list[str] = []
        source_categories: list[str] = []
        for g in group:
            priority = merge_priority(priority, g.priority)
            source_ids.extend(g.source_ids)
            source_categories.extend(g.source_categories)
        merged.append(
            ImprovementAction(
                action_id=first.action_id,
                title=first.title,
                description=first.description,
                priority=normalize_priority(priority),
                improvement_type=first.improvement_type,
                related_strategy_id=first.related_strategy_id,
                related_module=first.related_module,
                source_categories=list(dict.fromkeys(source_categories)),
                source_ids=list(dict.fromkeys(source_ids)),
                rationale=first.rationale,
                metadata=first.metadata,
            )
        )
    return merged


class ImprovementEngine:
    """
    Deterministic improvement planning engine. Consumes learning, audit, and trade-review
    outputs; produces consolidated ImprovementPlan. Injectable clock and counter-based or
    caller-supplied plan_id.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._plan_counter = 0
        self._action_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_plan_id(self) -> str:
        self._plan_counter += 1
        return f"improvement-plan-{self._plan_counter}"

    def generate_improvement_plan(
        self,
        learning_report: Any = None,
        audit_report: Any = None,
        trade_review_reports: Any = None,
        plan_id: str | None = None,
        generated_at: float | None = None,
    ) -> ImprovementPlan:
        """
        Build ImprovementPlan from optional learning, audit, and trade-review sources.
        Actions are consolidated by (strategy, module, type), prioritized, and ordered.
        """
        now = generated_at if generated_at is not None else self._now()
        if plan_id is not None:
            pid = plan_id
            self._plan_counter += 1
        else:
            pid = self._next_plan_id()

        raw: list[ImprovementAction] = []
        raw.extend(plan_from_learning(learning_report, action_id_prefix="learn"))
        raw.extend(plan_from_audit(audit_report, action_id_prefix="audit"))
        raw.extend(plan_from_trade_review(trade_review_reports, action_id_prefix="trade"))

        consolidated = _consolidate_actions(raw)
        for a in consolidated:
            a.priority = normalize_priority(a.priority)
        consolidated.sort(key=lambda a: (-priority_rank(a.priority), a.title or "", a.related_strategy_id or "", a.related_module or ""))

        actions_with_ids: list[ImprovementAction] = []
        for i, a in enumerate(consolidated):
            actions_with_ids.append(
                ImprovementAction(
                    action_id=f"action-{i+1}",
                    title=a.title,
                    description=a.description,
                    priority=a.priority,
                    improvement_type=a.improvement_type,
                    related_strategy_id=a.related_strategy_id,
                    related_module=a.related_module,
                    source_categories=a.source_categories,
                    source_ids=a.source_ids,
                    rationale=a.rationale,
                    metadata=a.metadata,
                )
            )

        low_c = sum(1 for a in actions_with_ids if a.priority == "low")
        med_c = sum(1 for a in actions_with_ids if a.priority == "medium")
        high_c = sum(1 for a in actions_with_ids if a.priority == "high")
        crit_c = sum(1 for a in actions_with_ids if a.priority == "critical")
        strategies = sorted(set(a.related_strategy_id for a in actions_with_ids if a.related_strategy_id))
        modules = sorted(set(a.related_module for a in actions_with_ids if a.related_module))
        categories = sorted(set(c for a in actions_with_ids for c in a.source_categories))

        summary = ImprovementPlanSummary(
            total_actions=len(actions_with_ids),
            low_count=low_c,
            medium_count=med_c,
            high_count=high_c,
            critical_count=crit_c,
            affected_strategies=strategies,
            affected_modules=modules,
            categories_seen=categories,
            metadata={},
        )

        return ImprovementPlan(
            plan_id=pid,
            generated_at=now,
            summary=summary,
            actions=actions_with_ids,
            metadata={},
        )
