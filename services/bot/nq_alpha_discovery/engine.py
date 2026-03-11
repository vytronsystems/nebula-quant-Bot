# NEBULA-QUANT v1 | nq_alpha_discovery — alpha discovery engine

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from nq_alpha_discovery.extractors import (
    extract_from_audit,
    extract_from_experiment,
    extract_from_learning,
    extract_from_trade_review,
    normalize_direct_observations,
)
from nq_alpha_discovery.models import (
    AlphaDiscoveryReport,
    AlphaDiscoverySummary,
    AlphaEvidence,
    AlphaHypothesis,
    AlphaHypothesisPriority,
    AlphaObservation,
)
from nq_alpha_discovery.ranking import rank_hypotheses


def _assign_priority(observations: list[AlphaObservation]) -> str:
    """Deterministic priority from observation count and severities."""
    n = len(observations)
    severities = [o.severity.lower() for o in observations]
    has_critical = "critical" in severities
    has_warning = "warning" in severities or "high" in severities
    if n >= 2 and has_critical:
        return AlphaHypothesisPriority.CRITICAL.value
    if has_critical:
        return AlphaHypothesisPriority.HIGH.value
    if n >= 2 and has_warning:
        return AlphaHypothesisPriority.HIGH.value
    if n >= 2:
        return AlphaHypothesisPriority.MEDIUM.value
    return AlphaHypothesisPriority.LOW.value


def _confidence_score(observations: list[AlphaObservation]) -> float:
    """Deterministic 0.0-1.0 score from count and severity."""
    n = len(observations)
    base = min(1.0, 0.15 * n + 0.1)
    severities = [o.severity.lower() for o in observations]
    if "critical" in severities:
        base = min(1.0, base + 0.25)
    if "warning" in severities or "high" in severities:
        base = min(1.0, base + 0.1)
    return round(base, 2)


class AlphaDiscoveryEngine:
    """
    Deterministic alpha discovery engine. Extracts observations from supported
    sources, groups them, builds hypotheses with rationale and evidence linkage,
    ranks by priority, and produces AlphaDiscoveryReport.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._report_counter = 0
        self._hypothesis_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_report_id(self) -> str:
        self._report_counter += 1
        return f"alpha-discovery-report-{self._report_counter}"

    def _next_hypothesis_id(self) -> str:
        self._hypothesis_counter += 1
        return f"hyp-{self._hypothesis_counter}"

    def generate_hypotheses(
        self,
        learning_report: Any = None,
        experiment_report: Any = None,
        audit_report: Any = None,
        trade_review_reports: Any = None,
        observations: Any = None,
        report_id: str | None = None,
        generated_at: float | None = None,
    ) -> AlphaDiscoveryReport:
        """
        Extract observations from all provided sources, group by (category, strategy_id, module),
        build one hypothesis per group with rationale and evidence_ids, rank, and return report.
        """
        now = generated_at if generated_at is not None else self._now()
        if report_id is not None:
            rid = report_id
            self._report_counter += 1
        else:
            rid = self._next_report_id()

        all_observations: list[AlphaObservation] = []
        all_evidence: list[AlphaEvidence] = []
        obs_to_ev: dict[str, str] = {}

        def merge(obs_list: list[AlphaObservation], ev_list: list[AlphaEvidence]) -> None:
            for o, e in zip(obs_list, ev_list):
                all_observations.append(o)
                all_evidence.append(e)
                obs_to_ev[o.observation_id] = e.evidence_id

        o1, e1 = extract_from_learning(learning_report)
        merge(o1, e1)
        o2, e2 = extract_from_experiment(experiment_report)
        merge(o2, e2)
        o3, e3 = extract_from_audit(audit_report)
        merge(o3, e3)
        o4, e4 = extract_from_trade_review(trade_review_reports)
        merge(o4, e4)
        o5, e5 = normalize_direct_observations(observations)
        merge(o5, e5)

        groups: dict[tuple[str, str | None, str | None], list[AlphaObservation]] = defaultdict(list)
        for obs in all_observations:
            key = (obs.category, obs.strategy_id or "", obs.module or "")
            groups[key].append(obs)

        hypotheses: list[AlphaHypothesis] = []
        for (category, strategy_id, module), group in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
            if not group:
                continue
            strat = strategy_id if strategy_id else None
            mod = module if module else None
            evidence_ids = [obs_to_ev[o.observation_id] for o in group if o.observation_id in obs_to_ev]
            title = f"Potential alpha: {category}"
            if strat:
                title += f" (strategy {strat})"
            desc = group[0].description if group and group[0].description else f"Recurring pattern from {len(group)} observation(s)."
            rationale = f"Based on {len(group)} observation(s): " + "; ".join(o.title for o in group[:5])
            if len(group) > 5:
                rationale += f" (+{len(group) - 5} more)"
            hid = self._next_hypothesis_id()
            hypotheses.append(AlphaHypothesis(
                hypothesis_id=hid,
                title=title,
                description=desc,
                category=category,
                related_strategy_id=strat,
                related_module=mod,
                priority=_assign_priority(group),
                confidence_score=_confidence_score(group),
                evidence_ids=list(evidence_ids),
                rationale=rationale,
                metadata={},
            ))

        hypotheses = rank_hypotheses(hypotheses)

        low_c = sum(1 for h in hypotheses if h.priority == AlphaHypothesisPriority.LOW.value)
        med_c = sum(1 for h in hypotheses if h.priority == AlphaHypothesisPriority.MEDIUM.value)
        high_c = sum(1 for h in hypotheses if h.priority == AlphaHypothesisPriority.HIGH.value)
        crit_c = sum(1 for h in hypotheses if h.priority == AlphaHypothesisPriority.CRITICAL.value)
        categories_seen = sorted(set(h.category for h in hypotheses))
        strategies_seen = sorted(set(h.related_strategy_id for h in hypotheses if h.related_strategy_id))
        modules_seen = sorted(set(h.related_module for h in hypotheses if h.related_module))

        summary = AlphaDiscoverySummary(
            total_observations=len(all_observations),
            total_hypotheses=len(hypotheses),
            low_count=low_c,
            medium_count=med_c,
            high_count=high_c,
            critical_count=crit_c,
            categories_seen=categories_seen,
            strategies_seen=strategies_seen,
            modules_seen=modules_seen,
            metadata={},
        )

        return AlphaDiscoveryReport(
            report_id=rid,
            generated_at=now,
            summary=summary,
            hypotheses=hypotheses,
            metadata={"report_type": "alpha_discovery"},
        )
