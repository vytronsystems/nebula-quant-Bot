from __future__ import annotations

from typing import Any

from nq_strategy_adaptation.models import AdaptationActionType, AdaptationDirective


def _directive_id(parts: list[str]) -> str:
    """Build a deterministic directive id from structured parts."""
    key = "|".join(parts)
    # Small hash to keep ids readable but deterministic.
    import hashlib

    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    return f"dir-{digest}"


def _build_family_directive(
    action: AdaptationActionType,
    family: str,
    rationale: str,
    source_ids: list[str],
) -> AdaptationDirective:
    did = _directive_id([action.value, family, rationale] + sorted(source_ids))
    return AdaptationDirective(
        directive_id=did,
        action_type=action.value,
        target_family=family,
        rationale=rationale,
        source_ids=sorted(source_ids),
        metadata={},
    )


def _build_regime_directive(
    action: AdaptationActionType,
    family: str,
    regime: str,
    rationale: str,
    source_ids: list[str],
) -> AdaptationDirective:
    did = _directive_id([action.value, family, regime, rationale] + sorted(source_ids))
    return AdaptationDirective(
        directive_id=did,
        action_type=action.value,
        target_family=family,
        target_regime=regime,
        rationale=rationale,
        source_ids=sorted(source_ids),
        metadata={},
    )


def _build_param_directive(
    family: str,
    parameter: str,
    value: dict[str, Any],
    rationale: str,
    source_ids: list[str],
) -> AdaptationDirective:
    did = _directive_id(
        [AdaptationActionType.ADJUST_PARAMETER_RANGE.value, family, parameter, str(sorted(value.items())), rationale]
        + sorted(source_ids)
    )
    return AdaptationDirective(
        directive_id=did,
        action_type=AdaptationActionType.ADJUST_PARAMETER_RANGE.value,
        target_family=family,
        target_parameter=parameter,
        value=value,
        rationale=rationale,
        source_ids=sorted(source_ids),
        metadata={},
    )


def apply_adaptation_rules(normalized: dict[str, Any]) -> list[AdaptationDirective]:
    """
    Apply deterministic adaptation rules to normalized feedback facts.

    The normalized dict is expected to contain keys from adapters:
    - slippage (trade reviews)
    - edge decay
    - experiments
    - learning
    - improvement_plan
    - audit
    """
    directives: list[AdaptationDirective] = []

    # A. Slippage suppression
    tr = normalized.get("trade_review", {})
    if tr.get("slippage_issues"):
        src = tr.get("source_ids", [])
        for fam in ("breakout", "opening_range_breakout"):
            directives.append(
                _build_family_directive(
                    AdaptationActionType.SUPPRESS_FAMILY,
                    fam,
                    "Suppressed due to repeated slippage issues in trade reviews.",
                    src,
                )
            )

    # B. Edge decay suppression
    ed = normalized.get("edge_decay", {})
    for fam in sorted(ed.get("decayed_families", [])):
        directives.append(
            _build_family_directive(
                AdaptationActionType.REDUCE_PRIORITY,
                fam,
                "Reduced priority due to detected edge decay.",
                ed.get("source_ids", []),
            )
        )

    # C. Successful experiment reinforcement
    ex = normalized.get("experiments", {})
    for fam in sorted(ex.get("reinforced_families", [])):
        directives.append(
            _build_family_directive(
                AdaptationActionType.PREFER_FAMILY,
                fam,
                "Preferred due to repeated successful experiments.",
                ex.get("source_ids", []),
            )
        )

    # D. Regime specialization
    au = normalized.get("audit", {})
    for fam, regime in au.get("regime_successes", []):
        directives.append(
            _build_regime_directive(
                AdaptationActionType.REQUIRE_REGIME,
                fam,
                regime,
                "Family shows strong performance in this regime; specialize.",
                au.get("source_ids", []),
            )
        )
    for fam, regime in au.get("regime_failures", []):
        directives.append(
            _build_regime_directive(
                AdaptationActionType.EXCLUDE_REGIME,
                fam,
                regime,
                "Family performs poorly in this regime; exclude.",
                au.get("source_ids", []),
            )
        )

    # E. Parameter adjustment
    # Use trade review poor entry/exit counts as simple triggers.
    poor_entry = int(tr.get("poor_entry_count", 0) or 0)
    poor_exit = int(tr.get("poor_exit_count", 0) or 0)
    if poor_entry >= 3:
        directives.append(
            _build_param_directive(
                family="breakout",
                parameter="lookback_bars",
                value={"min": 20, "max": 40},
                rationale="Widen breakout lookback due to poor entries.",
                source_ids=tr.get("source_ids", []),
            )
        )
    if poor_exit >= 3:
        directives.append(
            _build_param_directive(
                family="momentum_continuation",
                parameter="momentum_threshold",
                value={"min": 0.5, "max": 0.9},
                rationale="Adjust momentum threshold due to poor exits.",
                source_ids=tr.get("source_ids", []),
            )
        )

    # F. Promotion rejection feedback (via improvement plan flags)
    ip = normalized.get("improvement_plan", {})
    for fam in sorted(ip.get("flagged_families", [])):
        directives.append(
            _build_family_directive(
                AdaptationActionType.FLAG_FOR_REVIEW,
                fam,
                "Flagged for manual review due to repeated issues.",
                ip.get("source_ids", []),
            )
        )

    # Deterministic ordering by directive_id.
    directives.sort(key=lambda d: d.directive_id)
    return directives

