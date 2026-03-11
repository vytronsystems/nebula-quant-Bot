# NEBULA-QUANT v1 | nq_trade_review engine

from __future__ import annotations

from collections.abc import Callable

from nq_trade_review.analyzers import (
    _derive_actual_rr,
    _derive_expected_rr,
    _safe_float,
    classify_outcome,
    run_all_analyzers,
)
from nq_trade_review.findings import recommendations_from_findings
from nq_trade_review.models import (
    TradeReviewFindingSeverity,
    TradeReviewInput,
    TradeReviewReport,
    TradeReviewSummary,
)


class TradeReviewEngine:
    """
    Deterministic trade review engine.
    One trade per review; produces TradeReviewReport with summary, findings, recommendations.
    Injectable clock and counter-based or caller-supplied review_id.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time
        self._clock = clock or time.monotonic
        self._review_counter = 0

    def _now(self) -> float:
        return self._clock()

    def _next_review_id(self) -> str:
        self._review_counter += 1
        return f"trade-review-{self._review_counter}"

    def run_review(
        self,
        trade: TradeReviewInput,
        review_id: str | None = None,
        generated_at: float | None = None,
    ) -> TradeReviewReport:
        """
        Run full review on a single trade. Returns deterministic TradeReviewReport.
        Fails closed on malformed critical input (TradeReviewInput __post_init__).
        """
        now = generated_at if generated_at is not None else self._now()
        if review_id is not None:
            rid = review_id
            self._review_counter += 1
        else:
            rid = self._next_review_id()

        findings = run_all_analyzers(trade)

        info_c = sum(1 for f in findings if f.severity == TradeReviewFindingSeverity.INFO.value)
        warn_c = sum(1 for f in findings if f.severity == TradeReviewFindingSeverity.WARNING.value)
        crit_c = sum(1 for f in findings if f.severity == TradeReviewFindingSeverity.CRITICAL.value)

        outcome, exit_reason = classify_outcome(trade)
        expected_rr = _safe_float(trade.expected_rr) or _derive_expected_rr(trade)
        actual_rr = _safe_float(trade.actual_rr) or _derive_actual_rr(trade)
        slippage = None
        if _safe_float(trade.expected_entry_price) and _safe_float(trade.actual_entry_price):
            exp = _safe_float(trade.expected_entry_price)
            act = _safe_float(trade.actual_entry_price)
            if exp and exp > 0:
                slippage = abs(act - exp) / exp

        status = "incomplete" if any(f.category == "incomplete_trade_record" for f in findings) else "reviewed"

        summary = TradeReviewSummary(
            trade_id=trade.trade_id,
            status=status,
            total_findings=len(findings),
            info_count=info_c,
            warning_count=warn_c,
            critical_count=crit_c,
            outcome=outcome,
            exit_reason=exit_reason,
            expected_rr=expected_rr,
            actual_rr=actual_rr,
            slippage=slippage,
            metadata={},
        )

        recommendations = recommendations_from_findings(findings)

        return TradeReviewReport(
            review_id=rid,
            generated_at=now,
            summary=summary,
            findings=findings,
            recommendations=recommendations,
            metadata={},
        )
