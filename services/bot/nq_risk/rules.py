# NEBULA-QUANT v1 | nq_risk — deterministic risk evaluation rules

from __future__ import annotations

from nq_risk.models import (
    RiskContext,
    RiskDecisionResult,
    RiskDecisionType,
    RiskLimits,
    RiskOrderIntent,
)

EXECUTION_LIFECYCLE_STATES = frozenset({"paper", "live"})
VALID_SIDES = frozenset({"long", "short", "buy", "sell"})


def _is_long(side: str) -> bool:
    return (side or "").strip().lower() in ("long", "buy")


def _is_short(side: str) -> bool:
    return (side or "").strip().lower() in ("short", "sell")


def evaluate_risk(
    intent: RiskOrderIntent | None,
    context: RiskContext | None,
    limits: RiskLimits | None,
) -> RiskDecisionResult:
    """
    Deterministic risk evaluation. Returns ALLOW, REDUCE, or BLOCK.
    Fail-closed: missing or ambiguous inputs → BLOCK.
    """
    reason_codes: list[str] = []

    if intent is None or context is None or limits is None:
        return RiskDecisionResult(
            decision=RiskDecisionType.BLOCK,
            reason_codes=["missing_input"],
            message="risk: missing intent, context, or limits",
        )

    # --- Input validation ---
    if not (intent.strategy_id or "").strip():
        reason_codes.append("missing_strategy_id")
    if not (intent.symbol or "").strip():
        reason_codes.append("missing_symbol")
    if context.account_equity is None or context.account_equity <= 0:
        reason_codes.append("invalid_account_equity")
    if intent.requested_quantity is None and intent.requested_notional is None:
        reason_codes.append("missing_quantity_and_notional")
    if intent.requested_quantity is not None and intent.requested_quantity < 0:
        reason_codes.append("negative_quantity")
    if intent.requested_notional is not None and intent.requested_notional < 0:
        reason_codes.append("negative_notional")
    if intent.entry_price is not None and intent.entry_price <= 0:
        reason_codes.append("invalid_entry_price")
    if intent.stop_loss_price is not None and intent.stop_loss_price <= 0:
        reason_codes.append("invalid_stop_loss_price")
    side = (intent.side or "").strip().lower()
    if side and side not in VALID_SIDES:
        reason_codes.append("malformed_side")

    if reason_codes:
        return RiskDecisionResult(
            decision=RiskDecisionType.BLOCK,
            reason_codes=reason_codes,
            message="risk: " + "; ".join(reason_codes),
        )

    equity = max(context.account_equity, 1e-9)

    # --- Lifecycle consistency (optional guard; nq_risk does not own lifecycle) ---
    lifecycle = (context.strategy_lifecycle_state or "").strip().lower()
    if lifecycle and lifecycle not in EXECUTION_LIFECYCLE_STATES:
        return RiskDecisionResult(
            decision=RiskDecisionType.BLOCK,
            reason_codes=["non_executable_lifecycle"],
            message=f"risk: strategy lifecycle {lifecycle!r} not executable (paper/live only)",
        )

    # --- Stop-loss requirement ---
    if limits.require_stop_loss:
        if intent.stop_loss_price is None:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["stop_loss_required"],
                message="risk: stop loss required by policy",
            )
        if intent.entry_price is None or intent.entry_price <= 0:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["entry_price_required_for_stop"],
                message="risk: entry price required to validate stop",
            )
        entry = intent.entry_price
        stop = intent.stop_loss_price
        stop_distance_abs = abs(entry - stop)
        if stop_distance_abs < 1e-9:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["zero_stop_distance"],
                message="risk: zero or invalid stop distance",
            )
        if _is_long(intent.side) and stop >= entry:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["wrong_side_stop_long"],
                message="risk: long trade requires stop below entry",
            )
        if _is_short(intent.side) and stop <= entry:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["wrong_side_stop_short"],
                message="risk: short trade requires stop above entry",
            )
        # Stop distance % sanity
        if limits.max_stop_distance_pct is not None and limits.max_stop_distance_pct > 0:
            stop_distance_pct = stop_distance_abs / max(entry, 1e-9)
            if stop_distance_pct > limits.max_stop_distance_pct:
                return RiskDecisionResult(
                    decision=RiskDecisionType.BLOCK,
                    reason_codes=["excessive_stop_distance"],
                    message=f"risk: stop distance {stop_distance_pct:.4f} exceeds max {limits.max_stop_distance_pct}",
                )

    # --- Quantity/notional: need quantity for risk computation when stop is present ---
    qty = intent.requested_quantity
    if qty is None and intent.requested_notional is not None and intent.entry_price and intent.entry_price > 0:
        qty = intent.requested_notional / intent.entry_price
    if qty is None or qty <= 0:
        # If we require stop and risk computation, we need quantity
        if limits.require_stop_loss and intent.entry_price and intent.stop_loss_price:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["cannot_compute_risk_no_quantity"],
                message="risk: quantity or notional required for risk computation",
            )
        # No stop required and no quantity: allow with zero risk or block
        if not limits.require_stop_loss:
            return RiskDecisionResult(
                decision=RiskDecisionType.ALLOW,
                reason_codes=[],
                message="ok",
                risk_amount=0.0,
                risk_pct=0.0,
            )
        return RiskDecisionResult(
            decision=RiskDecisionType.BLOCK,
            reason_codes=["missing_quantity"],
            message="risk: quantity or notional required",
        )

    # --- Risk amount when we have entry, stop, quantity ---
    risk_amount: float | None = None
    risk_pct: float | None = None
    stop_distance_abs: float = 0.0

    if intent.entry_price and intent.entry_price > 0 and intent.stop_loss_price is not None:
        stop_distance_abs = abs(intent.entry_price - intent.stop_loss_price)
        if stop_distance_abs >= 1e-9:
            risk_amount = qty * stop_distance_abs
            risk_pct = risk_amount / equity
        else:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["zero_stop_distance"],
                message="risk: zero stop distance",
            )
    else:
        # No stop: cannot compute risk amount; if policy requires stop we already blocked
        risk_amount = None
        risk_pct = None

    # --- Daily strategy risk budget ---
    if limits.max_daily_strategy_risk_pct is not None and context.strategy_daily_realized_pnl is not None:
        daily_loss_used = abs(min(context.strategy_daily_realized_pnl, 0.0))
        budget_used_pct = daily_loss_used / equity
        if budget_used_pct >= limits.max_daily_strategy_risk_pct:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["daily_strategy_risk_budget_exceeded"],
                message=f"risk: strategy daily risk budget exceeded ({budget_used_pct:.4f} >= {limits.max_daily_strategy_risk_pct})",
                risk_amount=risk_amount,
                risk_pct=risk_pct,
            )

    # --- Daily account risk budget ---
    if limits.max_daily_account_risk_pct is not None and context.account_daily_realized_pnl is not None:
        daily_loss_used = abs(min(context.account_daily_realized_pnl, 0.0))
        budget_used_pct = daily_loss_used / equity
        if budget_used_pct >= limits.max_daily_account_risk_pct:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["daily_account_risk_budget_exceeded"],
                message=f"risk: account daily risk budget exceeded ({budget_used_pct:.4f} >= {limits.max_daily_account_risk_pct})",
                risk_amount=risk_amount,
                risk_pct=risk_pct,
            )

    # --- Max risk per trade ---
    if risk_pct is not None and risk_amount is not None and stop_distance_abs >= 1e-9:
        max_allowed_risk_amount = equity * limits.max_risk_per_trade_pct
        if risk_pct <= limits.max_risk_per_trade_pct:
            # Within limit; optional warning
            meta = {}
            if limits.warning_risk_per_trade_pct is not None and risk_pct >= limits.warning_risk_per_trade_pct:
                meta["warning_near_limit"] = True
            return RiskDecisionResult(
                decision=RiskDecisionType.ALLOW,
                reason_codes=[],
                message="ok",
                approved_quantity=qty,
                approved_notional=qty * intent.entry_price if intent.entry_price else None,
                risk_amount=risk_amount,
                risk_pct=risk_pct,
                metadata=meta,
            )
        # Exceeds limit: REDUCE if we can compute compliant quantity
        approved_qty = max_allowed_risk_amount / stop_distance_abs
        if approved_qty <= 0:
            return RiskDecisionResult(
                decision=RiskDecisionType.BLOCK,
                reason_codes=["risk_exceeds_limit_no_reduce"],
                message="risk: risk exceeds limit and approved quantity would be zero",
                risk_amount=risk_amount,
                risk_pct=risk_pct,
            )
        if qty <= approved_qty:
            # Already within limit (should not happen here but handle)
            return RiskDecisionResult(
                decision=RiskDecisionType.ALLOW,
                reason_codes=[],
                message="ok",
                approved_quantity=qty,
                approved_notional=qty * intent.entry_price if intent.entry_price else None,
                risk_amount=risk_amount,
                risk_pct=risk_pct,
            )
        approved_notional = approved_qty * intent.entry_price if intent.entry_price else None
        return RiskDecisionResult(
            decision=RiskDecisionType.REDUCE,
            reason_codes=["risk_per_trade_exceeded"],
            message="risk: size reduced to comply with max risk per trade",
            approved_quantity=approved_qty,
            approved_notional=approved_notional,
            risk_amount=risk_amount,
            risk_pct=risk_pct,
            metadata={"requested_quantity": qty, "requested_notional": qty * intent.entry_price if intent.entry_price else None},
        )

    # No stop / no risk computed: allow with zero risk if policy doesn't require stop
    if not limits.require_stop_loss:
        return RiskDecisionResult(
            decision=RiskDecisionType.ALLOW,
            reason_codes=[],
            message="ok",
            approved_quantity=qty,
            approved_notional=qty * intent.entry_price if intent.entry_price else None,
            risk_amount=risk_amount,
            risk_pct=risk_pct,
        )

    return RiskDecisionResult(
        decision=RiskDecisionType.BLOCK,
        reason_codes=["cannot_compute_risk"],
        message="risk: cannot compute risk (missing stop or entry)",
        risk_amount=risk_amount,
        risk_pct=risk_pct,
    )
