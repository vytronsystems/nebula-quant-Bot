from __future__ import annotations

from typing import Any

from nq_strategy_generation.models import (
    StrategyCandidate,
    StrategyFamily,
    StrategyGenerationError,
    StrategyParameterSet,
    StrategyTemplate,
)


MAX_CANDIDATES_PER_RUN = 64


def _get(d: dict[str, Any], key: str, default: Any = None) -> Any:
    return d.get(key, default)


def _normalize_regime(regime_context: Any) -> str:
    if regime_context is None:
        return ""
    if isinstance(regime_context, str):
        return regime_context.strip().upper()
    return str(regime_context).strip().upper()


def _regime_allows(template: StrategyTemplate, regime: str) -> bool:
    if not template.regime_constraints or not regime:
        return True
    return regime in template.regime_constraints


def _families_from_features(
    market_observations: dict[str, Any] | None,
    regime: str,
) -> list[StrategyFamily]:
    """Rule-based mapping from feature snapshot + regime to families."""
    features = market_observations or {}
    families: list[StrategyFamily] = []

    breakout_signal = bool(_get(features, "breakout_signal", False))
    relvol = float(_get(features, "relative_volume", 1.0) or 1.0)
    momentum = float(_get(features, "momentum_score", 0.0) or 0.0)
    trend = float(_get(features, "trend_strength", 0.0) or 0.0)
    mr_dist = float(_get(features, "mean_reversion_distance", 0.0) or 0.0)
    vol_pct = float(_get(features, "volatility_percentile", 0.0) or 0.0)
    session_bias = bool(_get(features, "session_bias", False))
    opening_breakout = bool(_get(features, "opening_range_breakout", False))

    # Breakout
    if breakout_signal and relvol >= 1.2 and regime in {"TRENDING_UP", "TRENDING_DOWN", "HIGH_VOLATILITY"}:
        families.append(StrategyFamily.BREAKOUT)

    # Momentum continuation
    if momentum >= 0.6 and trend >= 0.6 and regime in {"TRENDING_UP", "TRENDING_DOWN", "LOW_VOLATILITY"}:
        families.append(StrategyFamily.MOMENTUM_CONTINUATION)

    # Mean reversion
    if mr_dist >= 1.5 and regime in {"RANGE_BOUND", "LOW_VOLATILITY"}:
        families.append(StrategyFamily.MEAN_REVERSION)

    # Opening range breakout
    if session_bias and opening_breakout and relvol >= 1.2 and regime in {"TRENDING_UP", "TRENDING_DOWN", "HIGH_VOLATILITY"}:
        families.append(StrategyFamily.OPENING_RANGE_BREAKOUT)

    # Simple volatility expansion (derived from high volatility percentile)
    if vol_pct >= 0.8 and regime in {"HIGH_VOLATILITY", "MIXED"}:
        families.append(StrategyFamily.VOLATILITY_EXPANSION)

    # Deduplicate while preserving order.
    seen: set[StrategyFamily] = set()
    out: list[StrategyFamily] = []
    for f in families:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _families_from_feedback(learning_feedback: dict[str, Any] | None) -> dict[str, float]:
    """
    Influence weights by family based on internal feedback.

    Values in returned dict are deterministic weights in [0, 1] applied as
    simple allow/suppress toggles in this version.
    """
    fb = learning_feedback or {}
    weights: dict[str, float] = {}

    # Edge decay in a family suppresses it.
    decay_families = fb.get("edge_decay_families") or []
    for fam in decay_families:
        try:
            f = StrategyFamily(str(fam))
            weights[f.value] = 0.0
        except ValueError:
            continue

    # Persistent slippage issues suppress very fast breakout-style approaches.
    if fb.get("slippage_issues"):
        weights.setdefault(StrategyFamily.BREAKOUT.value, 0.0)
        weights.setdefault(StrategyFamily.OPENING_RANGE_BREAKOUT.value, 0.0)

    # Improvement candidates may explicitly boost certain families (not used
    # directly for selection here, but tracked for future versions).
    improvement_pref = fb.get("preferred_families") or []
    for fam in improvement_pref:
        try:
            f = StrategyFamily(str(fam))
            if weights.get(f.value, 1.0) > 0.0:
                weights[f.value] = 1.0
        except ValueError:
            continue

    return weights


def _is_family_allowed(
    family: StrategyFamily,
    feedback_weights: dict[str, float],
) -> bool:
    weight = feedback_weights.get(family.value, 1.0)
    return weight > 0.0


def generate_candidates_for_templates(
    templates: list[StrategyTemplate],
    parameter_sets: list[StrategyParameterSet],
    *,
    market_observations: dict[str, Any] | None,
    regime_context: Any | None,
    learning_feedback: dict[str, Any] | None,
    adaptation_context: dict[str, Any] | None = None,
) -> list[StrategyCandidate]:
    """
    Deterministically build candidate strategies from templates, parameters,
    and structured inputs.
    """
    if market_observations is not None and not isinstance(market_observations, dict):
        raise StrategyGenerationError("market_observations must be a dict or None")
    if learning_feedback is not None and not isinstance(learning_feedback, dict):
        raise StrategyGenerationError("learning_feedback must be a dict or None")

    regime = _normalize_regime(regime_context)
    feature_snapshot = dict(market_observations or {})
    requested_families = _families_from_features(market_observations, regime)
    feedback_weights = _families_from_feedback(learning_feedback)
    adaptation = adaptation_context or {}
    suppressed_families = set(adaptation.get("suppressed_families", []) or [])
    excluded_regimes = set(adaptation.get("excluded_regimes", []) or [])
    param_adj_map: dict[tuple[str, str], dict[str, Any]] = {}
    for adj in adaptation.get("parameter_adjustments", []) or []:
        fam = str(adj.get("family") or "")
        param = str(adj.get("parameter") or "")
        val = adj.get("value") or {}
        if fam and param and isinstance(val, dict):
            param_adj_map[(fam, param)] = val

    candidates: list[StrategyCandidate] = []
    for tpl in templates:
        fam = StrategyFamily(tpl.family)
        if fam not in requested_families:
            continue
        if not _is_family_allowed(fam, feedback_weights):
            continue
        if not _regime_allows(tpl, regime):
            continue
        if fam.value in suppressed_families:
            continue
        if regime and regime in excluded_regimes:
            continue

        # Match parameter sets by template prefix.
        matching_param_sets = [ps for ps in parameter_sets if ps.parameter_set_id.startswith(tpl.template_id + "-ps-")]
        # Apply any parameter range adjustments for this family.
        filtered_param_sets: list[StrategyParameterSet] = []
        for ps in matching_param_sets:
            keep = True
            for (adj_family, param), bounds in param_adj_map.items():
                if adj_family != fam.value:
                    continue
                if param not in ps.parameters:
                    continue
                v = ps.parameters[param]
                if not isinstance(v, (int, float)):
                    continue
                min_v = bounds.get("min")
                max_v = bounds.get("max")
                if min_v is not None and v < float(min_v):
                    keep = False
                    break
                if max_v is not None and v > float(max_v):
                    keep = False
                    break
            if keep:
                filtered_param_sets.append(ps)
        for idx, ps in enumerate(filtered_param_sets):
            strategy_id = f"{tpl.template_id}-{ps.parameter_set_id}"
            candidate_id = f"cand-{strategy_id}"
            rationale = f"{fam.value} candidate for regime {regime or 'UNKNOWN'} from template {tpl.template_id}"
            candidates.append(
                StrategyCandidate(
                    candidate_id=candidate_id,
                    strategy_id=strategy_id,
                    family=fam.value,
                    template_id=tpl.template_id,
                    parameter_set_id=ps.parameter_set_id,
                    regime=regime or "",
                    rationale=rationale,
                    feature_snapshot=feature_snapshot,
                    metadata={"order": idx},
                )
            )
            if len(candidates) >= MAX_CANDIDATES_PER_RUN:
                return candidates
    return candidates

