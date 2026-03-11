# NEBULA-QUANT v1 | nq_obs — normalize module outputs into observability-ready structures

from __future__ import annotations

from typing import Any

from nq_obs.models import StrategyObservabilitySeed, SystemObservabilityBuilderInput


def _safe_list(x: Any) -> list[Any]:
    if x is None:
        return []
    return list(x) if isinstance(x, (list, tuple)) else []


def normalize_execution_outcomes(events: Any) -> tuple[int, int, int, int, int, int, float | None, float | None, float | None]:
    """
    Map execution outcomes to counts. Returns (attempted, approved, blocked, throttled, reject_count, fill_count, avg_req_notional, avg_eff_notional, avg_slippage).
    Does not fabricate; missing or malformed entries are skipped.
    """
    events_list = _safe_list(events)
    attempted = 0
    approved = 0
    blocked = 0
    throttled = 0
    reject_count = 0
    fill_count = 0
    notional_sum: float = 0.0
    notional_n: int = 0
    slippage_sum: float = 0.0
    slippage_n: int = 0

    for item in events_list:
        if item is None:
            continue
        status = getattr(item, "status", None) or (item.get("status") if isinstance(item, dict) else None)
        status = (status or "").strip().lower()
        attempted += 1
        fills = getattr(item, "fills", None) or (item.get("fills") if isinstance(item, dict) else None)
        fill_count += len(fills) if fills is not None else 0
        if status in ("filled", "complete", "done"):
            approved += 1
        elif status in ("rejected", "reject", "cancelled", "canceled"):
            reject_count += 1
        order = getattr(item, "order", None) or (item.get("order") if isinstance(item, dict) else None)
        if order is not None:
            qty = getattr(order, "qty", None) or order.get("qty")
            price = getattr(order, "limit_price", None) or order.get("limit_price")
            if qty is not None and price is not None:
                try:
                    notional_sum += float(qty) * float(price)
                    notional_n += 1
                except (TypeError, ValueError):
                    pass
        meta = getattr(item, "metadata", None) or (item.get("metadata") if isinstance(item, dict) else None)
        if isinstance(meta, dict) and "slippage" in meta:
            try:
                slippage_sum += float(meta["slippage"])
                slippage_n += 1
            except (TypeError, ValueError):
                pass

    avg_req = (notional_sum / notional_n) if notional_n else None
    avg_slippage = (slippage_sum / slippage_n) if slippage_n else None
    return attempted, approved, blocked, throttled, reject_count, fill_count, avg_req, None, avg_slippage


def normalize_guardrail_decisions(results: Any) -> tuple[int, int]:
    """Map guardrail results to (allow_count, block_count)."""
    lst = _safe_list(results)
    allow = 0
    block = 0
    for r in lst:
        if r is None:
            continue
        allowed = getattr(r, "allowed", None)
        if allowed is None and isinstance(r, dict):
            allowed = r.get("allowed")
        if allowed is True:
            allow += 1
        elif allowed is False:
            block += 1
        signals = getattr(r, "signals", None) or (r.get("signals") if isinstance(r, dict) else [])
        for s in _safe_list(signals):
            sev = getattr(s, "severity", None) or (s.get("severity") if isinstance(s, dict) else "")
            if (sev or "").upper() == "BLOCK":
                block += 1
                break
    return allow, block


def normalize_portfolio_decisions(decisions: Any) -> tuple[int, int, int]:
    """Map portfolio decisions to (allow_count, block_count, throttle_count)."""
    lst = _safe_list(decisions)
    allow = 0
    block = 0
    throttle = 0
    for d in lst:
        if d is None:
            continue
        dec = getattr(d, "decision", None) or (d.get("decision") if isinstance(d, dict) else None)
        if dec is None:
            allowed = getattr(d, "allowed", None) or (d.get("allowed") if isinstance(d, dict) else None)
            if allowed is True:
                allow += 1
            elif allowed is False:
                block += 1
            continue
        dec_str = (getattr(dec, "value", None) or str(dec)).lower() if dec is not None else ""
        if dec_str == "allow":
            allow += 1
        elif dec_str == "block":
            block += 1
        elif dec_str == "throttle":
            throttle += 1
    return allow, block, throttle


def normalize_promotion_decisions(results: Any) -> tuple[int, int, int]:
    """Map promotion decisions to (allow_count, reject_count, invalid_lifecycle_count)."""
    lst = _safe_list(results)
    allow = 0
    reject = 0
    invalid = 0
    for r in lst:
        if r is None:
            continue
        decision = getattr(r, "decision", r) if not isinstance(r, dict) else r.get("decision", r)
        allowed = getattr(decision, "allowed", None) if decision is not None else None
        if allowed is None and isinstance(decision, dict):
            allowed = decision.get("allowed")
        if allowed is None and isinstance(r, dict):
            allowed = r.get("allowed")
        if allowed is True:
            allow += 1
        elif allowed is False:
            reject += 1
            reason_codes = getattr(decision, "reason_codes", None) or (decision.get("reason_codes") if isinstance(decision, dict) else [])
            if reason_codes and "lifecycle" in str(reason_codes).lower():
                invalid += 1
    return allow, reject, invalid


def normalize_experiment_summary(source: Any) -> dict[str, Any] | list[Any]:
    """Extract experiment summary for nq_metrics. No fabrication; empty if absent or malformed."""
    if source is None:
        return {}
    if isinstance(source, dict):
        return dict(source)
    if isinstance(source, list):
        return list(source)
    total = getattr(source, "total_experiments", None)
    completed = getattr(source, "completed_experiments", None)
    failed = getattr(source, "failed_experiments", None)
    experiments = getattr(source, "experiments", None)
    if total is not None or completed is not None or failed is not None or experiments is not None:
        return {
            "total_experiments": total,
            "completed_experiments": completed,
            "failed_experiments": failed,
            "experiments_count": len(experiments) if experiments is not None else 0,
        }
    return {}


def build_strategy_seeds_from_registry(
    registry_engine: Any,
    strategy_ids: list[str] | None,
) -> tuple[list[StrategyObservabilitySeed], list[str]]:
    """
    Build per-strategy seeds using registry truth. Fail-closed: malformed or duplicate strategy_id skipped with reason in second return.
    Returns (seeds, reason_codes for any failures).
    """
    if registry_engine is None:
        return [], ["missing_registry_engine"]
    ids = _safe_list(strategy_ids)
    seen: set[str] = set()
    seeds: list[StrategyObservabilitySeed] = []
    reason_codes: list[str] = []

    for sid in ids:
        if not sid or not str(sid).strip():
            reason_codes.append("missing_strategy_id")
            continue
        sid = str(sid).strip()
        if sid in seen:
            reason_codes.append("duplicate_strategy_id")
            continue
        seen.add(sid)
        try:
            result = registry_engine.get_registration_record(sid)
        except Exception:
            reason_codes.append("registry_lookup_error")
            continue
        if not getattr(result, "ok", False) or getattr(result, "record", None) is None:
            reason_codes.extend(getattr(result, "reason_codes", []) or ["registry_lookup_failed"])
            continue
        record = result.record
        lifecycle = getattr(record, "lifecycle_state", None) or ""
        enabled = getattr(record, "enabled", True)
        seeds.append(
            StrategyObservabilitySeed(
                strategy_id=sid,
                lifecycle_state=lifecycle if lifecycle else None,
                enabled=enabled,
                metadata=getattr(record, "metadata", None) or {},
            )
        )

    return seeds, reason_codes
