# NEBULA-QUANT v1 | nq_regime — regime summary builders

from __future__ import annotations

from typing import Any

from nq_regime.models import RegimeClassification, RegimeReport, RegimeSummary

CONFIDENCE_HIGH_THRESHOLD = 0.7
CONFIDENCE_LOW_THRESHOLD = 0.4


def build_regime_summary(classifications: list[RegimeClassification]) -> RegimeSummary:
    """
    Build deterministic summary from classifications. Does not mutate input.
    Counts by primary_regime, symbols_seen (sorted), high/low confidence counts.
    """
    total = len(classifications)
    by_primary: dict[str, int] = {}
    symbols_seen: set[str] = set()
    high_c = 0
    low_c = 0
    for c in classifications:
        by_primary[c.primary_regime] = by_primary.get(c.primary_regime, 0) + 1
        if c.symbol and str(c.symbol).strip():
            symbols_seen.add(str(c.symbol).strip())
        if c.confidence_score >= CONFIDENCE_HIGH_THRESHOLD:
            high_c += 1
        elif c.confidence_score < CONFIDENCE_LOW_THRESHOLD:
            low_c += 1
    return RegimeSummary(
        total_classifications=total,
        by_primary_regime=dict(sorted(by_primary.items())),
        symbols_seen=sorted(symbols_seen),
        high_confidence_count=high_c,
        low_confidence_count=low_c,
        metadata={},
    )


def build_regime_report(
    report_id: str,
    generated_at: float,
    classifications: list[RegimeClassification],
    summary: RegimeSummary | None = None,
    metadata: dict[str, Any] | None = None,
) -> RegimeReport:
    """Build RegimeReport. Does not mutate inputs."""
    if summary is None:
        summary = build_regime_summary(classifications)
    return RegimeReport(
        report_id=report_id,
        generated_at=generated_at,
        classifications=list(classifications),
        summary=summary,
        metadata=metadata or {},
    )
