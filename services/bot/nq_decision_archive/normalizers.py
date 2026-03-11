# NEBULA-QUANT v1 | nq_decision_archive — decision normalization

from __future__ import annotations

from typing import Any

from nq_decision_archive.models import (
    DecisionArchiveError,
    DecisionRecord,
    DecisionSourceType,
)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Get attribute or dict key; do not mutate."""
    if hasattr(obj, key):
        return getattr(obj, key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _ensure_list(val: Any, name: str) -> list[str]:
    if val is None:
        return []
    if not isinstance(val, list):
        raise DecisionArchiveError(f"{name} must be a list or None, got {type(val).__name__}")
    return [str(x) for x in val if x is not None]


def _normalize_outcome(val: Any, allowed_vals: set[str]) -> str:
    """Normalize outcome string to canonical value; fail closed if invalid."""
    if val is None:
        raise DecisionArchiveError("decision outcome is required")
    s = str(val).strip().lower()
    if s not in allowed_vals:
        raise DecisionArchiveError(f"invalid decision outcome: {val!r}")
    return s


def normalize_risk_decision(
    payload: Any,
    archive_id: str,
    source_id: str | None = None,
    timestamp: float | None = None,
) -> DecisionRecord:
    """
    Normalize nq_risk decision (RiskDecisionResult or dict) to DecisionRecord.
    Expects decision (allow/reduce/block), reason_codes; optional strategy_id, symbol.
    Fails closed on missing critical fields.
    """
    if payload is None:
        raise DecisionArchiveError("risk payload must not be None")
    decision = _get(payload, "decision")
    if decision is None:
        raise DecisionArchiveError("risk decision must have 'decision'")
    outcome_val = _get(decision, "value") if hasattr(decision, "value") else (
        decision if isinstance(decision, str) else _get(decision, "name")
    )
    outcome = _normalize_outcome(outcome_val, {"allow", "reduce", "block"})
    reason_codes = _ensure_list(_get(payload, "reason_codes"), "reason_codes")
    ts = timestamp
    if ts is None:
        ts = _get(payload, "timestamp")
        if ts is not None and isinstance(ts, (int, float)):
            ts = float(ts)
        else:
            raise DecisionArchiveError("risk decision requires timestamp or caller-provided timestamp")
    strategy_id = _get(payload, "strategy_id")
    if strategy_id is not None:
        strategy_id = str(strategy_id).strip() or None
    symbol = _get(payload, "symbol")
    if symbol is not None:
        symbol = str(symbol).strip() or None
    metadata = _get(payload, "metadata")
    if metadata is not None and not isinstance(metadata, dict):
        metadata = {}
    return DecisionRecord(
        archive_id=archive_id,
        source_module="nq_risk",
        source_type=DecisionSourceType.RISK.value,
        decision_type="risk_eval",
        decision_outcome=outcome,
        strategy_id=strategy_id,
        symbol=symbol,
        timestamp=float(ts),
        reason_codes=list(reason_codes),
        source_id=source_id,
        metadata=metadata or {},
    )


def normalize_guardrails_decision(
    payload: Any,
    archive_id: str,
    source_id: str | None = None,
    timestamp: float | None = None,
) -> DecisionRecord:
    """
    Normalize nq_guardrails result (GuardrailResult or dict with allowed/reason/signals) to DecisionRecord.
    Maps allowed True -> allow, False -> block. Reason codes from signals (severity + message) or reason.
    """
    if payload is None:
        raise DecisionArchiveError("guardrails payload must not be None")
    allowed = _get(payload, "allowed")
    if allowed is None:
        raise DecisionArchiveError("guardrails payload must have 'allowed'")
    outcome = "allow" if allowed else "block"
    reason_codes: list[str] = []
    reason = _get(payload, "reason")
    if isinstance(reason, str) and reason.strip():
        reason_codes.append(reason.strip())
    signals = _get(payload, "signals")
    if isinstance(signals, list):
        for s in signals:
            sev = _get(s, "severity")
            msg = _get(s, "message")
            if sev or msg:
                reason_codes.append(f"{sev or 'signal'}: {msg or ''}".strip())
    ts = timestamp
    if ts is None:
        ts = _get(payload, "timestamp")
        if ts is not None and isinstance(ts, (int, float)):
            ts = float(ts)
        else:
            raise DecisionArchiveError("guardrails decision requires timestamp or caller-provided timestamp")
    strategy_id = _get(payload, "strategy_id")
    if strategy_id is not None:
        strategy_id = str(strategy_id).strip() or None
    metadata = _get(payload, "metadata")
    if metadata is not None and not isinstance(metadata, dict):
        metadata = {}
    return DecisionRecord(
        archive_id=archive_id,
        source_module="nq_guardrails",
        source_type=DecisionSourceType.GUARDRAILS.value,
        decision_type="guardrail_eval",
        decision_outcome=outcome,
        strategy_id=strategy_id,
        symbol=None,
        timestamp=float(ts),
        reason_codes=reason_codes,
        source_id=source_id,
        metadata=metadata or {},
    )


def normalize_portfolio_decision(
    payload: Any,
    archive_id: str,
    source_id: str | None = None,
    timestamp: float | None = None,
) -> DecisionRecord:
    """
    Normalize nq_portfolio decision (PortfolioDecision or dict) to DecisionRecord.
    Expects decision (allow/throttle/block), reason_codes; optional strategy_id.
    """
    if payload is None:
        raise DecisionArchiveError("portfolio payload must not be None")
    decision = _get(payload, "decision")
    if decision is None:
        raise DecisionArchiveError("portfolio decision must have 'decision'")
    outcome_val = _get(decision, "value") if hasattr(decision, "value") else (
        decision if isinstance(decision, str) else _get(decision, "name")
    )
    outcome = _normalize_outcome(outcome_val, {"allow", "throttle", "block"})
    reason_codes = _ensure_list(_get(payload, "reason_codes"), "reason_codes")
    ts = timestamp
    if ts is None:
        ts = _get(payload, "timestamp")
        if ts is not None and isinstance(ts, (int, float)):
            ts = float(ts)
        else:
            raise DecisionArchiveError("portfolio decision requires timestamp or caller-provided timestamp")
    strategy_id = _get(payload, "strategy_id")
    if strategy_id is not None:
        strategy_id = str(strategy_id).strip() or None
    symbol = _get(payload, "symbol")
    if symbol is not None:
        symbol = str(symbol).strip() or None
    metadata = _get(payload, "metadata")
    if metadata is not None and not isinstance(metadata, dict):
        metadata = {}
    return DecisionRecord(
        archive_id=archive_id,
        source_module="nq_portfolio",
        source_type=DecisionSourceType.PORTFOLIO.value,
        decision_type="portfolio_gate",
        decision_outcome=outcome,
        strategy_id=strategy_id,
        symbol=symbol,
        timestamp=float(ts),
        reason_codes=list(reason_codes),
        source_id=source_id,
        metadata=metadata or {},
    )


def normalize_promotion_decision(
    payload: Any,
    archive_id: str,
    source_id: str | None = None,
    timestamp: float | None = None,
) -> DecisionRecord:
    """
    Normalize nq_promotion decision (PromotionDecision/PromotionResult or dict) to DecisionRecord.
    Maps allowed True -> approve, False -> reject. reason_codes from blocking_issues or reason.
    """
    if payload is None:
        raise DecisionArchiveError("promotion payload must not be None")
    decision = _get(payload, "decision")
    if decision is not None:
        allowed = _get(decision, "allowed")
        blocking = _ensure_list(_get(decision, "blocking_issues"), "blocking_issues")
        reason = _get(decision, "reason")
    else:
        allowed = _get(payload, "allowed")
        blocking = _ensure_list(_get(payload, "blocking_issues"), "blocking_issues")
        reason = _get(payload, "reason")
    if allowed is None:
        raise DecisionArchiveError("promotion payload must have 'allowed' or decision.allowed")
    outcome = "approve" if allowed else "reject"
    reason_codes = list(blocking) if blocking else []
    if isinstance(reason, str) and reason.strip() and reason.strip() not in reason_codes:
        reason_codes.append(reason.strip())
    ts = timestamp
    if ts is None:
        ts = _get(payload, "evaluated_at") or _get(payload, "timestamp")
        if ts is not None and isinstance(ts, (int, float)):
            ts = float(ts)
        else:
            raise DecisionArchiveError("promotion decision requires timestamp or caller-provided timestamp")
    strategy_id = _get(payload, "strategy_id")
    if strategy_id is None and decision is None:
        pass
    if strategy_id is None and decision is not None:
        strategy_id = _get(payload, "strategy_id")
    if strategy_id is not None:
        strategy_id = str(strategy_id).strip() or None
    metadata = _get(payload, "metadata")
    if metadata is not None and not isinstance(metadata, dict):
        metadata = {}
    return DecisionRecord(
        archive_id=archive_id,
        source_module="nq_promotion",
        source_type=DecisionSourceType.PROMOTION.value,
        decision_type="promotion_eval",
        decision_outcome=outcome,
        strategy_id=strategy_id,
        symbol=None,
        timestamp=float(ts),
        reason_codes=reason_codes,
        source_id=source_id,
        metadata=metadata or {},
    )


def normalize_decision(
    source_module: str,
    payload: Any,
    archive_id: str,
    source_id: str | None = None,
    timestamp: float | None = None,
) -> DecisionRecord:
    """
    Dispatch to the appropriate normalizer by source_module. Fail closed on unknown source.
    """
    mod = (source_module or "").strip().lower()
    if mod == "nq_risk" or mod == "risk":
        return normalize_risk_decision(payload, archive_id, source_id, timestamp)
    if mod == "nq_guardrails" or mod == "guardrails":
        return normalize_guardrails_decision(payload, archive_id, source_id, timestamp)
    if mod == "nq_portfolio" or mod == "portfolio":
        return normalize_portfolio_decision(payload, archive_id, source_id, timestamp)
    if mod == "nq_promotion" or mod == "promotion":
        return normalize_promotion_decision(payload, archive_id, source_id, timestamp)
    raise DecisionArchiveError(f"unsupported decision source for normalization: {source_module!r}")
