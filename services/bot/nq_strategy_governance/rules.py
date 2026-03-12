from __future__ import annotations

from typing import Any

from nq_strategy_governance.models import (
    StrategyGovernanceDecision,
    StrategyGovernanceFinding,
    StrategyGovernanceInput,
)


def _get(summary: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if summary is None:
        return default
    return summary.get(key, default)


def _finding(idx: int, category: str, severity: str, title: str, description: str) -> StrategyGovernanceFinding:
    return StrategyGovernanceFinding(
        finding_id=f"finding-{idx}",
        category=category,
        severity=severity,
        title=title,
        description=description,
        metadata={},
    )


def evaluate_governance(input: StrategyGovernanceInput) -> tuple[StrategyGovernanceDecision, list[StrategyGovernanceFinding], str]:
    """
    Apply explicit, deterministic governance rules to derive a final decision.

    Thresholds are intentionally conservative and simple:
    - Backtest: profit_factor >= 1.2, win_rate >= 0.5, max_drawdown <= 0.25
    - Walkforward: pass_rate >= 0.6
    - Paper: total_trades >= 30, win_rate >= 0.5, max_drawdown <= 0.2
    - Metrics: win_rate >= 0.5, expectancy >= 0.0 (if present), max_drawdown <= 0.2
    - Edge decay: significant edge decay blocks live approval
    - Audit: blocking_issues or structural_invalid flags block live approval
    """
    findings: list[StrategyGovernanceFinding] = []
    idx = 1

    # --- Backtest checks ---
    bt = input.backtest_summary or {}
    bt_pf = float(_get(bt, "profit_factor", 0.0) or 0.0)
    bt_wr = float(_get(bt, "win_rate", 0.0) or 0.0)
    bt_dd = float(_get(bt, "max_drawdown", 1.0) or 1.0)
    if bt_pf < 1.2 or bt_wr < 0.5 or bt_dd > 0.25:
        findings.append(
            _finding(
                idx,
                "backtest_weak",
                "warning",
                "Backtest below live thresholds",
                f"profit_factor={bt_pf}, win_rate={bt_wr}, max_drawdown={bt_dd}",
            )
        )
        idx += 1

    # --- Walkforward checks ---
    wf = input.walkforward_summary or {}
    wf_pass_rate = float(_get(wf, "pass_rate", 0.0) or 0.0)
    if wf_pass_rate < 0.6:
        findings.append(
            _finding(
                idx,
                "walkforward_weak",
                "warning",
                "Walkforward below live thresholds",
                f"pass_rate={wf_pass_rate}",
            )
        )
        idx += 1

    # --- Paper checks ---
    pp = input.paper_summary or {}
    pp_trades = int(_get(pp, "total_trades", 0) or 0)
    pp_wr = float(_get(pp, "win_rate", 0.0) or 0.0)
    pp_dd = float(_get(pp, "max_drawdown", 1.0) or 1.0)
    if pp_trades < 30 or pp_wr < 0.5 or pp_dd > 0.2:
        findings.append(
            _finding(
                idx,
                "paper_insufficient",
                "info",
                "Paper trading evidence insufficient for live",
                f"total_trades={pp_trades}, win_rate={pp_wr}, max_drawdown={pp_dd}",
            )
        )
        idx += 1

    # --- Metrics checks ---
    mt = input.metrics_summary or {}
    mt_wr = float(_get(mt, "win_rate", 0.0) or 0.0)
    mt_expect = float(_get(mt, "expectancy", 0.0) or 0.0)
    mt_dd = float(_get(mt, "max_drawdown", 1.0) or 1.0)
    if mt_wr < 0.5 or mt_expect < 0.0 or mt_dd > 0.2:
        findings.append(
            _finding(
                idx,
                "metrics_weak",
                "warning",
                "Metrics below live thresholds",
                f"win_rate={mt_wr}, expectancy={mt_expect}, max_drawdown={mt_dd}",
            )
        )
        idx += 1

    # --- Edge decay checks ---
    ed = input.edge_decay_summary or {}
    ed_significant = bool(_get(ed, "significant", False))
    if ed_significant:
        findings.append(
            _finding(
                idx,
                "edge_decay_blocker",
                "critical",
                "Significant edge decay",
                "Edge decay report indicates significant decay; blocks live approval.",
            )
        )
        idx += 1

    # --- Audit checks ---
    au = input.audit_summary or {}
    blocking_issues = _get(au, "blocking_issues", []) or []
    structural_invalid = bool(_get(au, "structural_invalid", False))
    if blocking_issues or structural_invalid:
        findings.append(
            _finding(
                idx,
                "audit_blocker",
                "critical",
                "Audit blocking issues",
                f"blocking_issues={blocking_issues}, structural_invalid={structural_invalid}",
            )
        )
        idx += 1

    # --- Derive decision ---
    has_critical = any(f.severity == "critical" for f in findings)
    has_backtest_fail = any(f.category == "backtest_weak" for f in findings)
    has_walkforward_fail = any(f.category == "walkforward_weak" for f in findings)
    has_paper_insufficient = any(f.category == "paper_insufficient" for f in findings)
    has_metrics_weak = any(f.category == "metrics_weak" for f in findings)

    if has_critical:
        decision = StrategyGovernanceDecision.REJECT_STRATEGY
        rationale = "Critical blockers present (edge decay and/or audit). Strategy is rejected."
    elif has_backtest_fail or has_walkforward_fail:
        decision = StrategyGovernanceDecision.RETURN_TO_RESEARCH
        rationale = "Backtest or walkforward below thresholds; strategy should return to research."
    elif has_paper_insufficient or has_metrics_weak:
        decision = StrategyGovernanceDecision.REMAIN_IN_PAPER
        rationale = "Evidence is promising but paper/metrics insufficient; remain in paper."
    else:
        decision = StrategyGovernanceDecision.APPROVED_FOR_LIVE
        rationale = "All evidence satisfies conservative thresholds. Approved for live."

    return decision, findings, rationale

