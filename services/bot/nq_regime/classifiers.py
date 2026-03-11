# NEBULA-QUANT v1 | nq_regime — deterministic regime classification rules

from __future__ import annotations

from typing import Any

from nq_regime.models import RegimeEvidence, RegimeInput, RegimeLabel

# Documented thresholds; no ML, no fuzzy inference.
VOL_PCT_HIGH = 75.0
VOL_PCT_LOW = 25.0
TREND_STRENGTH_THRESHOLD = 0.1
MOMENTUM_THRESHOLD = 0.2


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


def _classify_single(
    inp: RegimeInput | dict[str, Any],
    evidence_id_prefix: str,
    classification_id: str,
) -> tuple[str, list[str], float, str, list[RegimeEvidence]]:
    """
    Classify one regime input. Returns (primary_regime, secondary_regimes, confidence_score, rationale, evidence_list).
    Deterministic rule order: volatility -> trend -> momentum -> range -> mixed -> unknown.
    """
    evidence: list[RegimeEvidence] = []
    ev_idx = [0]

    def add_ev(category: str, value: Any, description: str) -> str:
        eid = f"{evidence_id_prefix}-{ev_idx[0]}"
        ev_idx[0] += 1
        evidence.append(RegimeEvidence(evidence_id=eid, category=category, value=value, description=description, metadata={}))
        return eid

    vol_pct = _float_or_none(_get(inp, "volatility_percentile"))
    vol = _float_or_none(_get(inp, "volatility"))
    ma_short = _float_or_none(_get(inp, "moving_average_short"))
    ma_long = _float_or_none(_get(inp, "moving_average_long"))
    trend_str = _float_or_none(_get(inp, "trend_strength"))
    momentum = _float_or_none(_get(inp, "momentum_score"))
    structure_hint = _get(inp, "structure_hint")
    if structure_hint is not None:
        structure_hint = str(structure_hint).strip().lower() or None

    secondary: list[str] = []
    rationale_parts: list[str] = []

    # A. Volatility classification
    if vol_pct is not None:
        add_ev("volatility_percentile", vol_pct, f"Volatility percentile {vol_pct}")
        if vol_pct >= VOL_PCT_HIGH:
            primary = RegimeLabel.HIGH_VOLATILITY.value
            rationale_parts.append(f"Volatility percentile {vol_pct} >= {VOL_PCT_HIGH} (high threshold).")
            confidence = 0.85
            return primary, secondary, confidence, " ".join(rationale_parts), evidence
        if vol_pct <= VOL_PCT_LOW:
            primary = RegimeLabel.LOW_VOLATILITY.value
            rationale_parts.append(f"Volatility percentile {vol_pct} <= {VOL_PCT_LOW} (low threshold).")
            confidence = 0.85
            return primary, secondary, confidence, " ".join(rationale_parts), evidence

    # B. Mixed: conflicting trend and momentum (check before single-signal trend return)
    if trend_str is not None and momentum is not None:
        if (trend_str >= TREND_STRENGTH_THRESHOLD and momentum <= -MOMENTUM_THRESHOLD) or (
            trend_str <= -TREND_STRENGTH_THRESHOLD and momentum >= MOMENTUM_THRESHOLD
        ):
            add_ev("trend_strength", trend_str, "Trend strength")
            add_ev("momentum_score", momentum, "Momentum score")
            primary = RegimeLabel.MIXED.value
            secondary = [RegimeLabel.TRENDING_UP.value if trend_str >= TREND_STRENGTH_THRESHOLD else RegimeLabel.TRENDING_DOWN.value]
            rationale_parts.append("Conflicting trend and momentum signals.")
            confidence = 0.5
            return primary, secondary, confidence, " ".join(rationale_parts), evidence

    # C. Trend classification (when MAs and trend_strength available)
    if ma_short is not None and ma_long is not None and trend_str is not None:
        add_ev("ma_short", ma_short, "Short moving average")
        add_ev("ma_long", ma_long, "Long moving average")
        add_ev("trend_strength", trend_str, "Trend strength")
        if ma_short > ma_long and trend_str >= TREND_STRENGTH_THRESHOLD:
            primary = RegimeLabel.TRENDING_UP.value
            rationale_parts.append("Short MA above long MA with positive trend strength.")
            confidence = 0.8
            return primary, secondary, confidence, " ".join(rationale_parts), evidence
        if ma_short < ma_long and trend_str <= -TREND_STRENGTH_THRESHOLD:
            primary = RegimeLabel.TRENDING_DOWN.value
            rationale_parts.append("Short MA below long MA with negative trend strength.")
            confidence = 0.8
            return primary, secondary, confidence, " ".join(rationale_parts), evidence

    # D. Momentum classification
    if momentum is not None:
        add_ev("momentum_score", momentum, "Momentum score")
        if momentum >= MOMENTUM_THRESHOLD:
            primary = RegimeLabel.MOMENTUM_UP.value
            rationale_parts.append(f"Momentum score {momentum} >= {MOMENTUM_THRESHOLD}.")
            confidence = 0.75
            return primary, secondary, confidence, " ".join(rationale_parts), evidence
        if momentum <= -MOMENTUM_THRESHOLD:
            primary = RegimeLabel.MOMENTUM_DOWN.value
            rationale_parts.append(f"Momentum score {momentum} <= -{MOMENTUM_THRESHOLD}.")
            confidence = 0.75
            return primary, secondary, confidence, " ".join(rationale_parts), evidence

    # E. Range-bound: structure hint or weak trend + neutral momentum
    if structure_hint in ("range", "range_bound", "ranging", "mean_reversion"):
        add_ev("structure_hint", structure_hint, "Structure hint suggests range-bound.")
        primary = RegimeLabel.RANGE_BOUND.value
        rationale_parts.append("Structure hint indicates range-bound regime.")
        confidence = 0.7
        return primary, secondary, confidence, " ".join(rationale_parts), evidence

    if trend_str is not None and momentum is not None:
        add_ev("trend_strength", trend_str, "Trend strength")
        add_ev("momentum_score", momentum, "Momentum score")
        if abs(trend_str) < TREND_STRENGTH_THRESHOLD and abs(momentum) < MOMENTUM_THRESHOLD:
            primary = RegimeLabel.RANGE_BOUND.value
            rationale_parts.append("Weak trend strength with neutral momentum suggests range-bound regime.")
            confidence = 0.65
            return primary, secondary, confidence, " ".join(rationale_parts), evidence

    # F. Unknown / fail closed
    primary = RegimeLabel.UNKNOWN.value
    rationale_parts.append("Insufficient or inconclusive inputs for classification.")
    confidence = 0.0
    if not evidence:
        add_ev("input_check", None, "No usable trend, volatility, momentum, or structure inputs.")
    return primary, secondary, confidence, " ".join(rationale_parts), evidence
