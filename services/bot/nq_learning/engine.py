# NEBULA-QUANT v1 | nq_learning engine

from __future__ import annotations

from collections.abc import Callable

from nq_learning.aggregators import aggregate_patterns
from nq_learning.lessons import improvement_candidates_from_patterns, lessons_from_patterns
from nq_learning.models import (
    LearningInput,
    LearningPriority,
    LearningReport,
    LearningSummary,
)


class LearningEngine:
    """
    Deterministic learning analysis engine.
    Consumes audit and trade-review findings, aggregates patterns, derives lessons and improvement candidates.
    Injectable clock and counter-based or caller-supplied learning_id.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._learning_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_learning_id(self) -> str:
        self._learning_counter += 1
        return f"learning-{self._learning_counter}"

    def run_learning(
        self,
        input_data: LearningInput,
        learning_id: str | None = None,
        generated_at: float | None = None,
    ) -> LearningReport:
        """
        Run learning analysis on input_data. Returns deterministic LearningReport.
        Fails closed on malformed critical input (non-list findings).
        """
        now = generated_at if generated_at is not None else self._now()
        if learning_id is not None:
            lid = learning_id
            self._learning_counter += 1
        else:
            lid = self._next_learning_id()

        patterns = aggregate_patterns(
            input_data.audit_findings,
            input_data.trade_review_findings,
        )
        lessons = lessons_from_patterns(patterns)
        candidates = improvement_candidates_from_patterns(patterns)

        categories_seen: set[str] = set()
        strategies_seen: set[str] = set()
        modules_seen: set[str] = set()
        for p in patterns:
            categories_seen.add(p.category)
            if p.related_strategy_id:
                strategies_seen.add(p.related_strategy_id)
            if p.related_module:
                modules_seen.add(p.related_module)

        high_c = sum(1 for c in candidates if c.priority == LearningPriority.HIGH.value)
        high_c += sum(1 for l in lessons if l.priority == LearningPriority.HIGH.value)
        crit_c = sum(1 for c in candidates if c.priority == LearningPriority.CRITICAL.value)
        crit_c += sum(1 for l in lessons if l.priority == LearningPriority.CRITICAL.value)

        summary = LearningSummary(
            total_patterns=len(patterns),
            total_lessons=len(lessons),
            total_improvement_candidates=len(candidates),
            high_priority_count=high_c,
            critical_priority_count=crit_c,
            categories_seen=sorted(categories_seen),
            strategies_seen=sorted(strategies_seen),
            modules_seen=sorted(modules_seen),
            metadata={},
        )

        return LearningReport(
            learning_id=lid,
            generated_at=now,
            summary=summary,
            patterns=patterns,
            lessons=lessons,
            improvement_candidates=candidates,
            metadata={},
        )
