# NEBULA-QUANT v1 | nq_trade_review findings and recommendations

from __future__ import annotations

from nq_trade_review.models import TradeReviewFinding, TradeReviewFindingSeverity


# Category identifiers (deterministic, documented).
CATEGORY_POOR_ENTRY = "poor_entry_quality"
CATEGORY_POOR_EXIT = "poor_exit_quality"
CATEGORY_RR_UNDERPERFORMANCE = "rr_underperformance"
CATEGORY_EXCESSIVE_SLIPPAGE = "excessive_slippage"
CATEGORY_MISSING_CONTROLS = "missing_trade_controls"
CATEGORY_INCONSISTENT_RECORD = "inconsistent_trade_record"
CATEGORY_INCOMPLETE_RECORD = "incomplete_trade_record"


def make_finding(
    finding_id: str,
    category: str,
    severity: TradeReviewFindingSeverity,
    title: str,
    description: str,
    trade_id: str,
    strategy_id: str | None = None,
    metadata: dict | None = None,
) -> TradeReviewFinding:
    """Build a TradeReviewFinding with string severity."""
    return TradeReviewFinding(
        finding_id=finding_id,
        category=category,
        severity=severity.value,
        title=title,
        description=description,
        trade_id=trade_id,
        strategy_id=strategy_id,
        metadata=metadata or {},
    )


def recommendations_from_findings(findings: list[TradeReviewFinding]) -> list[str]:
    """Derive deterministic recommendations from findings; grounded in findings only."""
    out: list[str] = []
    for f in findings:
        if f.severity not in (TradeReviewFindingSeverity.WARNING.value, TradeReviewFindingSeverity.CRITICAL.value):
            continue
        tid = f.trade_id
        if "entry" in f.category and "quality" in f.category:
            out.append(f"Review entry discipline for trade {tid} due to entry deviation.")
        elif "exit" in f.category and "quality" in f.category:
            out.append(f"Review exit execution for trade {tid} due to exit deviation.")
        elif "slippage" in f.category:
            out.append(f"Investigate slippage conditions for trade {tid}.")
        elif "incomplete" in f.category:
            out.append(f"Trade {tid} record is incomplete; ensure stop-loss and target are recorded.")
        elif "inconsistent" in f.category:
            out.append(f"Trade {tid} record is inconsistent; correct prices or controls.")
        elif "missing_trade_controls" in f.category:
            out.append(f"Trade {tid} record is missing trade controls; ensure stop-loss and target are recorded.")
        elif "rr_underperformance" in f.category:
            out.append(f"Expected RR was not achieved; review exit execution for trade {tid}.")
    return out
