# NEBULA-QUANT v1 | nq_edge_decay — deterministic edge decay analysis rules

from __future__ import annotations

from typing import Any

from nq_edge_decay.models import (
    CATEGORY_EXECUTION_QUALITY_DECAY,
    CATEGORY_EXPERIMENT_QUALITY_DECAY,
    CATEGORY_EXPECTANCY_DECAY,
    CATEGORY_INSUFFICIENT_BASELINE,
    CATEGORY_MIXED_EDGE_DECAY,
    CATEGORY_PNL_DECAY,
    CATEGORY_SLIPPAGE_DECAY,
    CATEGORY_WIN_RATE_DECAY,
    EdgeDecayEvidence,
    EdgeDecayFinding,
    EdgeDecaySeverity,
)

# Documented thresholds; simple and testable.
PNL_DECAY_PCT_THRESHOLD = 0.10  # 10% deterioration vs baseline
WIN_RATE_DROP_THRESHOLD = 0.05  # 5 percentage points
EXPECTANCY_DROP_THRESHOLD = 0.10  # absolute drop
SLIPPAGE_WORSEN_PCT_THRESHOLD = 0.20  # 20% increase vs baseline
EXECUTION_FINDINGS_THRESHOLD = 2  # repeated findings count
EXPERIMENT_DECAY_MIN_DELTA = 1  # at least 1 more failed/degraded in recent


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _float_or_none(val: Any) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    return None


def _int_or_none(val: Any) -> int | None:
    if val is None:
        return None
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    return None


def analyze_single_input(
    inp: Any,
    finding_id_prefix: str,
    evidence_id_prefix: str,
) -> tuple[list[EdgeDecayFinding], list[EdgeDecayEvidence]]:
    """
    Analyze one edge decay input. Returns (findings, evidence).
    Deterministic: same input -> same output. Does not mutate inp.
    """
    findings: list[EdgeDecayFinding] = []
    evidence: list[EdgeDecayEvidence] = []
    ev_idx = [0]
    find_idx = [0]

    def add_ev(category: str, value: Any, description: str) -> str:
        eid = f"{evidence_id_prefix}-{ev_idx[0]}"
        ev_idx[0] += 1
        evidence.append(EdgeDecayEvidence(evidence_id=eid, category=category, value=value, description=description, metadata={}))
        return eid

    def add_finding(category: str, severity: str, title: str, description: str, rationale: str, ev_ids: list[str]) -> None:
        fid = f"{finding_id_prefix}-{find_idx[0]}"
        find_idx[0] += 1
        strategy_id = _get(inp, "strategy_id")
        if strategy_id is not None:
            strategy_id = str(strategy_id).strip() or None
        findings.append(EdgeDecayFinding(
            finding_id=fid,
            category=category,
            severity=severity,
            title=title,
            description=description,
            strategy_id=strategy_id,
            evidence_ids=list(ev_ids),
            rationale=rationale,
            metadata={},
        ))

    strategy_id = _get(inp, "strategy_id")
    strategy_id = str(strategy_id).strip() if strategy_id else None

    baseline_pnl = _float_or_none(_get(inp, "baseline_pnl"))
    recent_pnl = _float_or_none(_get(inp, "recent_pnl"))
    baseline_wr = _float_or_none(_get(inp, "baseline_win_rate"))
    recent_wr = _float_or_none(_get(inp, "recent_win_rate"))
    baseline_exp = _float_or_none(_get(inp, "baseline_expectancy"))
    recent_exp = _float_or_none(_get(inp, "recent_expectancy"))
    baseline_slip = _float_or_none(_get(inp, "baseline_slippage"))
    recent_slip = _float_or_none(_get(inp, "recent_slippage"))
    baseline_failed = _int_or_none(_get(inp, "baseline_failed_experiments"))
    recent_failed = _int_or_none(_get(inp, "recent_failed_experiments"))
    baseline_degraded = _int_or_none(_get(inp, "baseline_degraded_experiments"))
    recent_degraded = _int_or_none(_get(inp, "recent_degraded_experiments"))
    repeated_tr = _int_or_none(_get(inp, "repeated_trade_review_findings"))
    repeated_audit = _int_or_none(_get(inp, "repeated_audit_findings"))

    decay_categories: list[str] = []

    # A. PnL decay
    if baseline_pnl is not None and recent_pnl is not None:
        add_ev("recent_pnl", recent_pnl, "Recent PnL")
        add_ev("baseline_pnl", baseline_pnl, "Baseline PnL")
        if baseline_pnl > 0 and recent_pnl < baseline_pnl:
            pct_drop = (baseline_pnl - recent_pnl) / baseline_pnl
            if pct_drop >= PNL_DECAY_PCT_THRESHOLD:
                ev_ids = [evidence[-2].evidence_id, evidence[-1].evidence_id]
                add_finding(
                    CATEGORY_PNL_DECAY,
                    EdgeDecaySeverity.WARNING.value,
                    "PnL deterioration",
                    f"Recent PnL {recent_pnl} deteriorated vs baseline {baseline_pnl}.",
                    f"Recent PnL deteriorated by {pct_drop:.1%} relative to baseline.",
                    ev_ids,
                )
                decay_categories.append(CATEGORY_PNL_DECAY)
        elif baseline_pnl < 0 and recent_pnl < baseline_pnl:
            # Both negative; recent more negative
            ev_ids = [evidence[-2].evidence_id, evidence[-1].evidence_id]
            add_finding(
                CATEGORY_PNL_DECAY,
                EdgeDecaySeverity.WARNING.value,
                "PnL deterioration",
                "Recent PnL worsened vs baseline.",
                "Recent PnL is more negative than baseline.",
                ev_ids,
            )
            decay_categories.append(CATEGORY_PNL_DECAY)

    # B. Win-rate decay
    if baseline_wr is not None and recent_wr is not None:
        add_ev("recent_win_rate", recent_wr, "Recent win rate")
        add_ev("baseline_win_rate", baseline_wr, "Baseline win rate")
        drop = baseline_wr - recent_wr
        if drop >= WIN_RATE_DROP_THRESHOLD:
            ev_ids = [evidence[-2].evidence_id, evidence[-1].evidence_id]
            add_finding(
                CATEGORY_WIN_RATE_DECAY,
                EdgeDecaySeverity.WARNING.value,
                "Win rate deterioration",
                f"Recent win rate {recent_wr:.2%} dropped vs baseline {baseline_wr:.2%}.",
                f"Win rate dropped by {drop:.2%} (threshold {WIN_RATE_DROP_THRESHOLD:.2%}).",
                ev_ids,
            )
            decay_categories.append(CATEGORY_WIN_RATE_DECAY)

    # C. Expectancy decay
    if baseline_exp is not None and recent_exp is not None:
        add_ev("recent_expectancy", recent_exp, "Recent expectancy")
        add_ev("baseline_expectancy", baseline_exp, "Baseline expectancy")
        drop = baseline_exp - recent_exp
        if drop >= EXPECTANCY_DROP_THRESHOLD:
            ev_ids = [evidence[-2].evidence_id, evidence[-1].evidence_id]
            add_finding(
                CATEGORY_EXPECTANCY_DECAY,
                EdgeDecaySeverity.WARNING.value,
                "Expectancy deterioration",
                f"Recent expectancy {recent_exp} dropped vs baseline {baseline_exp}.",
                f"Expectancy dropped by {drop} (threshold {EXPECTANCY_DROP_THRESHOLD}).",
                ev_ids,
            )
            decay_categories.append(CATEGORY_EXPECTANCY_DECAY)

    # D. Slippage decay
    if baseline_slip is not None and recent_slip is not None:
        add_ev("recent_slippage", recent_slip, "Recent slippage")
        add_ev("baseline_slippage", baseline_slip, "Baseline slippage")
        if recent_slip > baseline_slip:
            denom = baseline_slip if abs(baseline_slip) >= 1e-9 else 1e-9
            pct_increase = (recent_slip - baseline_slip) / abs(denom)
            if pct_increase >= SLIPPAGE_WORSEN_PCT_THRESHOLD:
                ev_ids = [evidence[-2].evidence_id, evidence[-1].evidence_id]
                add_finding(
                    CATEGORY_SLIPPAGE_DECAY,
                    EdgeDecaySeverity.WARNING.value,
                    "Slippage deterioration",
                    f"Recent slippage {recent_slip} increased vs baseline {baseline_slip}.",
                    f"Slippage increased by {pct_increase:.1%} (threshold {SLIPPAGE_WORSEN_PCT_THRESHOLD:.1%}).",
                    ev_ids,
                )
                decay_categories.append(CATEGORY_SLIPPAGE_DECAY)

    # E. Experiment quality decay
    base_exp_total = (baseline_failed or 0) + (baseline_degraded or 0)
    recent_exp_total = (recent_failed or 0) + (recent_degraded or 0)
    if recent_exp_total > base_exp_total and (recent_exp_total - base_exp_total) >= EXPERIMENT_DECAY_MIN_DELTA:
        add_ev("recent_failed_degraded", recent_exp_total, "Recent failed+degraded experiments")
        add_ev("baseline_failed_degraded", base_exp_total, "Baseline failed+degraded experiments")
        ev_ids = [evidence[-2].evidence_id, evidence[-1].evidence_id]
        add_finding(
            CATEGORY_EXPERIMENT_QUALITY_DECAY,
            EdgeDecaySeverity.WARNING.value,
            "Experiment quality deterioration",
            f"Recent failed/degraded experiments ({recent_exp_total}) exceed baseline ({base_exp_total}).",
            "Experiment outcomes have deteriorated relative to baseline.",
            ev_ids,
        )
        decay_categories.append(CATEGORY_EXPERIMENT_QUALITY_DECAY)

    # F. Execution quality decay
    if (repeated_tr or 0) >= EXECUTION_FINDINGS_THRESHOLD or (repeated_audit or 0) >= EXECUTION_FINDINGS_THRESHOLD:
        add_ev("repeated_trade_review_findings", repeated_tr or 0, "Repeated trade review findings")
        add_ev("repeated_audit_findings", repeated_audit or 0, "Repeated audit findings")
        ev_ids = [e.evidence_id for e in evidence[-2:]]
        add_finding(
            CATEGORY_EXECUTION_QUALITY_DECAY,
            EdgeDecaySeverity.INFO.value,
            "Execution quality concerns",
            f"Repeated trade review findings: {repeated_tr or 0}, audit findings: {repeated_audit or 0}.",
            "Repeated execution or audit findings may indicate execution-quality decay.",
            ev_ids,
        )
        decay_categories.append(CATEGORY_EXECUTION_QUALITY_DECAY)

    # G. Mixed edge decay
    if len(decay_categories) >= 2:
        ev_ids = [f.evidence_ids[0] for f in findings[-len(decay_categories):] if f.evidence_ids]
        add_finding(
            CATEGORY_MIXED_EDGE_DECAY,
            EdgeDecaySeverity.CRITICAL.value,
            "Multiple edge decay signals",
            f"Multiple decay categories observed: {', '.join(decay_categories)}.",
            "Multiple decay signals were observed simultaneously; edge may be materially deteriorating.",
            ev_ids[:3],
        )

    # H. Insufficient baseline (when critical comparison needed but baseline missing)
    if strategy_id and not findings and (
        recent_pnl is not None or recent_wr is not None or recent_exp is not None
    ):
        if (recent_pnl is not None and baseline_pnl is None) or (recent_wr is not None and baseline_wr is None):
            add_ev("insufficient_baseline", None, "Baseline missing for comparison")
            add_finding(
                CATEGORY_INSUFFICIENT_BASELINE,
                EdgeDecaySeverity.INFO.value,
                "Insufficient baseline",
                "Baseline metrics missing; cannot assess decay.",
                "Insufficient baseline information for safe comparison.",
                [evidence[-1].evidence_id],
            )

    return findings, evidence