# NEBULA-QUANT v1 | nq_learning lessons and improvement candidates

from __future__ import annotations

from nq_learning.models import (
    ImprovementCandidate,
    LearningLesson,
    LearningPattern,
    LearningPriority,
)


# Minimum count to consider a pattern "recurring" for lesson generation.
RECURRING_THRESHOLD = 2


def _priority_from_pattern(p: LearningPattern) -> str:
    """Deterministic priority: CRITICAL if any critical; HIGH if multiple warning or any critical; else MEDIUM/LOW."""
    dist = p.severity_distribution or {}
    crit = dist.get("critical", 0)
    warn = dist.get("warning", 0)
    if crit >= 1:
        return LearningPriority.CRITICAL.value
    if warn >= 2 or crit >= 1:
        return LearningPriority.HIGH.value
    if p.count >= 3:
        return LearningPriority.MEDIUM.value
    return LearningPriority.LOW.value


def lessons_from_patterns(patterns: list[LearningPattern]) -> list[LearningLesson]:
    """Derive deterministic lessons from patterns. Only recurring patterns (count >= 2) produce lessons."""
    lessons: list[LearningLesson] = []
    for p in patterns:
        if p.count < RECURRING_THRESHOLD:
            continue
        priority = _priority_from_pattern(p)
        if p.related_strategy_id:
            title = f"Strategy {p.related_strategy_id} repeatedly shows {p.category} findings."
            description = f"Category {p.category} occurred {p.count} times for strategy {p.related_strategy_id}; severity distribution: {p.severity_distribution}."
        elif p.related_module:
            title = f"Module {p.related_module} shows repeated {p.category} findings."
            description = f"Category {p.category} occurred {p.count} times for module {p.related_module}; severity distribution: {p.severity_distribution}."
        else:
            title = f"Recurring category: {p.category}."
            description = f"Category {p.category} occurred {p.count} times overall; severity distribution: {p.severity_distribution}."
        lessons.append(
            LearningLesson(
                lesson_id=f"lesson-{p.pattern_id}",
                title=title,
                description=description,
                priority=priority,
                related_categories=[p.category],
                related_strategy_id=p.related_strategy_id,
                related_module=p.related_module,
                metadata={"pattern_id": p.pattern_id, "count": p.count},
            )
        )
    return lessons


def improvement_candidates_from_patterns(patterns: list[LearningPattern]) -> list[ImprovementCandidate]:
    """Derive improvement candidates from patterns. Recurring patterns (count >= 2) produce candidates."""
    candidates: list[ImprovementCandidate] = []
    for p in patterns:
        if p.count < RECURRING_THRESHOLD:
            continue
        priority = _priority_from_pattern(p)
        if "entry" in p.category and "quality" in p.category:
            title = f"Review entry rules for strategy {p.related_strategy_id or 'affected strategies'}."
            desc = f"Repeated poor entry quality ({p.count} findings); review entry discipline and execution."
        elif "exit" in p.category and "quality" in p.category:
            title = f"Review exit execution for strategy {p.related_strategy_id or 'affected strategies'}."
            desc = f"Repeated poor exit quality ({p.count} findings); review exit execution."
        elif "slippage" in p.category:
            title = f"Investigate slippage conditions for strategy {p.related_strategy_id or 'trades'}."
            desc = f"Repeated excessive slippage ({p.count} findings); investigate execution conditions."
        elif "rr_underperformance" in p.category:
            title = f"Review exit execution and RR targets for strategy {p.related_strategy_id or 'affected strategies'}."
            desc = f"RR underperformance ({p.count} findings); review exit execution and targets."
        elif "blocked" in p.category or "repeated_blocked" in p.category:
            title = f"Review risk/guardrail constraints for strategy {p.related_strategy_id or 'affected strategies'}."
            desc = f"Repeated blocked decisions ({p.count} findings); review constraints."
        elif "throttl" in p.category.lower():
            title = f"Review throttling and portfolio constraints for module {p.related_module or 'nq_guardrails'}."
            desc = f"Repeated throttling ({p.count} findings); review portfolio/risk constraints."
        elif "promotion" in p.category and "reject" in p.category:
            title = "Review promotion criteria due to repeated promotion rejections."
            desc = f"Repeated promotion rejections ({p.count} findings); review promotion criteria."
        elif "execution" in p.category and "failure" in p.category:
            title = f"Investigate execution failures for module {p.related_module or 'nq_exec'}."
            desc = f"Repeated execution failures ({p.count} findings); investigate execution layer."
        elif "degraded" in p.category or "inactive" in p.category:
            title = f"Review strategy health for strategy {p.related_strategy_id or 'affected strategies'}."
            desc = f"Strategy health findings ({p.category}, {p.count} occurrences); review strategy state."
        else:
            title = f"Review {p.category} for strategy {p.related_strategy_id or 'module ' + (p.related_module or 'general')}."
            desc = f"Recurring {p.category} ({p.count} findings); review and improve."
        candidates.append(
            ImprovementCandidate(
                candidate_id=f"improve-{p.pattern_id}",
                title=title,
                description=desc,
                priority=priority,
                source_patterns=[p.pattern_id],
                related_strategy_id=p.related_strategy_id,
                related_module=p.related_module,
                metadata={"pattern_id": p.pattern_id, "count": p.count},
            )
        )
    return candidates
