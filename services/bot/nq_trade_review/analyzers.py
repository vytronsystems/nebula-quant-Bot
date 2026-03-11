# NEBULA-QUANT v1 | nq_trade_review deterministic analyzers

from __future__ import annotations

from nq_trade_review.findings import (
    CATEGORY_EXCESSIVE_SLIPPAGE,
    CATEGORY_INCOMPLETE_RECORD,
    CATEGORY_INCONSISTENT_RECORD,
    CATEGORY_MISSING_CONTROLS,
    CATEGORY_POOR_ENTRY,
    CATEGORY_POOR_EXIT,
    CATEGORY_RR_UNDERPERFORMANCE,
    make_finding,
)
from nq_trade_review.models import TradeReviewError, TradeReviewFinding, TradeReviewFindingSeverity, TradeReviewInput

# Thresholds (deterministic, documented).
ENTRY_DEVIATION_WARNING_PCT = 0.01
ENTRY_DEVIATION_CRITICAL_PCT = 0.05
EXIT_DEVIATION_WARNING_PCT = 0.01
EXIT_DEVIATION_CRITICAL_PCT = 0.05
SLIPPAGE_WARNING_PCT = 0.02
SLIPPAGE_CRITICAL_PCT = 0.05
RR_UNDERPERFORMANCE_WARNING_RATIO = 0.5
RR_UNDERPERFORMANCE_CRITICAL_RATIO = 0.25
OUTCOME_BREAKEVEN_TOLERANCE_PCT = 0.0001


def _side_long(t: TradeReviewInput) -> bool:
    return t.side.strip().lower() in ("long", "buy")


def _safe_float(val: float | None) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    return None


def analyze_completeness_consistency(t: TradeReviewInput) -> list[TradeReviewFinding]:
    """Missing critical fields -> incomplete; contradictory prices -> inconsistent."""
    findings: list[TradeReviewFinding] = []
    tid = t.trade_id
    sid = t.strategy_id

    missing: list[str] = []
    if not (t.symbol and t.symbol.strip()):
        missing.append("symbol")
    if not (t.side and t.side.strip()):
        missing.append("side")
    if missing:
        raise TradeReviewError(f"critical fields missing: {missing}")  # already validated in model

    if t.actual_entry_price is None and t.expected_entry_price is None:
        missing.append("entry_price")
    if t.actual_exit_price is None and t.expected_exit_price is None:
        missing.append("exit_price")
    if t.quantity is None and t.notional is None:
        missing.append("quantity_or_notional")
    if missing:
        findings.append(
            make_finding(
                f"incomplete-{tid}",
                CATEGORY_INCOMPLETE_RECORD,
                TradeReviewFindingSeverity.INFO,
                "Incomplete trade record",
                f"Trade {tid} is missing: {', '.join(missing)}.",
                trade_id=tid,
                strategy_id=sid,
                metadata={"missing": missing},
            )
        )

    if t.stop_loss_price is None and t.take_profit_price is None:
        findings.append(
            make_finding(
                f"missing-controls-{tid}",
                CATEGORY_MISSING_CONTROLS,
                TradeReviewFindingSeverity.INFO,
                "Missing trade controls",
                f"Trade {tid} has no stop-loss or take-profit recorded.",
                trade_id=tid,
                strategy_id=sid,
            )
        )

    entry = _safe_float(t.actual_entry_price) or _safe_float(t.expected_entry_price)
    sl = _safe_float(t.stop_loss_price)
    tp = _safe_float(t.take_profit_price)
    if entry is not None and sl is not None and tp is not None:
        if _side_long(t):
            if sl >= entry or tp <= entry:
                findings.append(
                    make_finding(
                        f"inconsistent-{tid}",
                        CATEGORY_INCONSISTENT_RECORD,
                        TradeReviewFindingSeverity.CRITICAL,
                        "Inconsistent trade record",
                        f"Trade {tid}: long requires stop_loss < entry < take_profit.",
                        trade_id=tid,
                        strategy_id=sid,
                    )
                )
            if sl >= tp:
                findings.append(
                    make_finding(
                        f"inconsistent-sl-tp-{tid}",
                        CATEGORY_INCONSISTENT_RECORD,
                        TradeReviewFindingSeverity.CRITICAL,
                        "Inconsistent trade record",
                        f"Trade {tid}: stop_loss must be below take_profit for long.",
                        trade_id=tid,
                        strategy_id=sid,
                    )
                )
        else:
            if sl <= entry or tp >= entry:
                findings.append(
                    make_finding(
                        f"inconsistent-{tid}",
                        CATEGORY_INCONSISTENT_RECORD,
                        TradeReviewFindingSeverity.CRITICAL,
                        "Inconsistent trade record",
                        f"Trade {tid}: short requires stop_loss > entry > take_profit.",
                        trade_id=tid,
                        strategy_id=sid,
                    )
                )
            if sl <= tp:
                findings.append(
                    make_finding(
                        f"inconsistent-sl-tp-{tid}",
                        CATEGORY_INCONSISTENT_RECORD,
                        TradeReviewFindingSeverity.CRITICAL,
                        "Inconsistent trade record",
                        f"Trade {tid}: stop_loss must be above take_profit for short.",
                        trade_id=tid,
                        strategy_id=sid,
                    )
                )

    return findings


def analyze_entry_quality(t: TradeReviewInput) -> list[TradeReviewFinding]:
    """Compare expected vs actual entry; poor_entry_quality when deviation exceeds threshold."""
    findings: list[TradeReviewFinding] = []
    expected = _safe_float(t.expected_entry_price)
    actual = _safe_float(t.actual_entry_price)
    if expected is None or actual is None or expected <= 0:
        return findings
    deviation = abs(actual - expected) / expected
    if deviation < ENTRY_DEVIATION_WARNING_PCT:
        return findings
    severity = (
        TradeReviewFindingSeverity.CRITICAL
        if deviation >= ENTRY_DEVIATION_CRITICAL_PCT
        else TradeReviewFindingSeverity.WARNING
    )
    findings.append(
        make_finding(
            f"poor-entry-{t.trade_id}",
            CATEGORY_POOR_ENTRY,
            severity,
            "Poor entry quality",
            f"Entry deviation {deviation:.4f} ({deviation*100:.2f}%) for trade {t.trade_id}.",
            trade_id=t.trade_id,
            strategy_id=t.strategy_id,
            metadata={"deviation_pct": deviation, "expected": expected, "actual": actual},
        )
    )
    return findings


def analyze_exit_quality(t: TradeReviewInput) -> list[TradeReviewFinding]:
    """Compare expected vs actual exit when both exist; poor_exit_quality when deviation exceeds threshold."""
    findings: list[TradeReviewFinding] = []
    expected = _safe_float(t.expected_exit_price)
    actual = _safe_float(t.actual_exit_price)
    if expected is None or actual is None or expected <= 0:
        return findings
    deviation = abs(actual - expected) / expected
    if deviation < EXIT_DEVIATION_WARNING_PCT:
        return findings
    severity = (
        TradeReviewFindingSeverity.CRITICAL
        if deviation >= EXIT_DEVIATION_CRITICAL_PCT
        else TradeReviewFindingSeverity.WARNING
    )
    findings.append(
        make_finding(
            f"poor-exit-{t.trade_id}",
            CATEGORY_POOR_EXIT,
            severity,
            "Poor exit quality",
            f"Exit deviation {deviation:.4f} ({deviation*100:.2f}%) for trade {t.trade_id}.",
            trade_id=t.trade_id,
            strategy_id=t.strategy_id,
            metadata={"deviation_pct": deviation, "expected": expected, "actual": actual},
        )
    )
    return findings


def _derive_expected_rr(t: TradeReviewInput) -> float | None:
    """Reward/risk from entry, stop, take_profit. Long: (tp-entry)/(entry-sl). Short: (entry-tp)/(sl-entry)."""
    entry = _safe_float(t.actual_entry_price) or _safe_float(t.expected_entry_price)
    sl = _safe_float(t.stop_loss_price)
    tp = _safe_float(t.take_profit_price)
    if entry is None or sl is None or tp is None:
        return None
    if _side_long(t):
        risk = entry - sl
        reward = tp - entry
    else:
        risk = sl - entry
        reward = entry - tp
    if risk <= 0:
        return None
    return reward / risk


def _derive_actual_rr(t: TradeReviewInput) -> float | None:
    """Actual RR from entry, exit, stop. Long: (exit-entry)/(entry-sl). Short: (entry-exit)/(sl-entry)."""
    entry = _safe_float(t.actual_entry_price) or _safe_float(t.expected_entry_price)
    exit_p = _safe_float(t.actual_exit_price) or _safe_float(t.expected_exit_price)
    sl = _safe_float(t.stop_loss_price)
    if entry is None or exit_p is None or sl is None:
        return None
    if _side_long(t):
        risk = entry - sl
        reward = exit_p - entry
    else:
        risk = sl - entry
        reward = entry - exit_p
    if risk <= 0:
        return None
    return reward / risk


def analyze_rr(t: TradeReviewInput) -> list[TradeReviewFinding]:
    """Compare actual RR to expected; rr_underperformance when actual materially below expected."""
    findings: list[TradeReviewFinding] = []
    expected = _safe_float(t.expected_rr)
    if expected is None:
        expected = _derive_expected_rr(t)
    actual = _safe_float(t.actual_rr)
    if actual is None:
        actual = _derive_actual_rr(t)
    if expected is None or actual is None or expected <= 0:
        return findings
    ratio = actual / expected
    if ratio >= RR_UNDERPERFORMANCE_WARNING_RATIO:
        return findings
    severity = (
        TradeReviewFindingSeverity.CRITICAL
        if ratio < RR_UNDERPERFORMANCE_CRITICAL_RATIO
        else TradeReviewFindingSeverity.WARNING
    )
    findings.append(
        make_finding(
            f"rr-underperform-{t.trade_id}",
            CATEGORY_RR_UNDERPERFORMANCE,
            severity,
            "RR underperformance",
            f"Trade {t.trade_id}: actual RR {actual:.4f} vs expected {expected:.4f} (ratio {ratio:.4f}).",
            trade_id=t.trade_id,
            strategy_id=t.strategy_id,
            metadata={"expected_rr": expected, "actual_rr": actual, "ratio": ratio},
        )
    )
    return findings


def analyze_slippage(t: TradeReviewInput) -> list[TradeReviewFinding]:
    """Entry slippage when expected and actual entry exist; excessive_slippage above threshold."""
    findings: list[TradeReviewFinding] = []
    expected = _safe_float(t.expected_entry_price)
    actual = _safe_float(t.actual_entry_price)
    if expected is None or actual is None or expected <= 0:
        return findings
    slippage_pct = abs(actual - expected) / expected
    if slippage_pct < SLIPPAGE_WARNING_PCT:
        return findings
    severity = (
        TradeReviewFindingSeverity.CRITICAL
        if slippage_pct >= SLIPPAGE_CRITICAL_PCT
        else TradeReviewFindingSeverity.WARNING
    )
    findings.append(
        make_finding(
            f"excessive-slippage-{t.trade_id}",
            CATEGORY_EXCESSIVE_SLIPPAGE,
            severity,
            "Excessive slippage",
            f"Entry slippage {slippage_pct:.4f} ({slippage_pct*100:.2f}%) for trade {t.trade_id}.",
            trade_id=t.trade_id,
            strategy_id=t.strategy_id,
            metadata={"slippage_pct": slippage_pct, "expected": expected, "actual": actual},
        )
    )
    return findings


def classify_outcome(t: TradeReviewInput) -> tuple[str, str]:
    """
    Return (outcome, exit_reason). Outcome: win | loss | breakeven | unknown.
    Exit_reason: stop_hit | target_hit | manual_exit | unknown_exit.
    Deterministic when entry/exit/stop/tp exist; unknown when insufficient.
    """
    entry = _safe_float(t.actual_entry_price) or _safe_float(t.expected_entry_price)
    exit_p = _safe_float(t.actual_exit_price) or _safe_float(t.expected_exit_price)
    sl = _safe_float(t.stop_loss_price)
    tp = _safe_float(t.take_profit_price)
    if entry is None or exit_p is None:
        return "unknown", "unknown_exit"
    tol = OUTCOME_BREAKEVEN_TOLERANCE_PCT * entry
    if _side_long(t):
        pnl = exit_p - entry
        if sl is not None and tp is not None:
            if abs(exit_p - sl) <= tol:
                return ("loss", "stop_hit") if pnl < -tol else ("breakeven", "stop_hit")
            if abs(exit_p - tp) <= tol:
                return ("win", "target_hit") if pnl > tol else ("breakeven", "target_hit")
        if pnl > tol:
            return "win", "manual_exit"
        if pnl < -tol:
            return "loss", "manual_exit"
        return "breakeven", "manual_exit"
    else:
        pnl = entry - exit_p
        if sl is not None and tp is not None:
            if abs(exit_p - sl) <= tol:
                return ("loss", "stop_hit") if pnl < -tol else ("breakeven", "stop_hit")
            if abs(exit_p - tp) <= tol:
                return ("win", "target_hit") if pnl > tol else ("breakeven", "target_hit")
        if pnl > tol:
            return "win", "manual_exit"
        if pnl < -tol:
            return "loss", "manual_exit"
        return "breakeven", "manual_exit"


def run_all_analyzers(t: TradeReviewInput) -> list[TradeReviewFinding]:
    """Run all analyzers and return combined findings."""
    combined: list[TradeReviewFinding] = []
    combined.extend(analyze_completeness_consistency(t))
    combined.extend(analyze_entry_quality(t))
    combined.extend(analyze_exit_quality(t))
    combined.extend(analyze_rr(t))
    combined.extend(analyze_slippage(t))
    return combined