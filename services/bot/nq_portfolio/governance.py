# NEBULA-QUANT v1 | nq_portfolio — portfolio risk engine (final approval gate before nq_exec)

from __future__ import annotations

from nq_portfolio.models import (
    OrderIntent,
    PortfolioDecision,
    PortfolioDecisionType,
    PortfolioLimits,
    PortfolioState,
    PositionSnapshot,
    StrategyAllocation,
)

# Execution-compatible lifecycle states only
EXECUTION_LIFECYCLE_STATES = frozenset({"paper", "live"})

# Drawdown formula (mandatory): abs(min(daily_pnl, 0)) / max(portfolio_equity, 1e-9)
def _portfolio_drawdown_ratio(portfolio_equity: float, daily_pnl: float) -> float:
    return abs(min(daily_pnl, 0.0)) / max(portfolio_equity, 1e-9)


def _strategy_drawdown_ratio(portfolio_equity: float, strategy_daily_pnl: float) -> float:
    return abs(min(strategy_daily_pnl, 0.0)) / max(portfolio_equity, 1e-9)


def _get_allocation(state: PortfolioState, strategy_id: str) -> StrategyAllocation | None:
    for a in state.strategy_allocations:
        if a.strategy_id == strategy_id:
            return a
    return None


def _positions_by_strategy(positions: list[PositionSnapshot]) -> dict[str, list[PositionSnapshot]]:
    out: dict[str, list[PositionSnapshot]] = {}
    for p in positions:
        out.setdefault(p.strategy_id, []).append(p)
    return out


def _total_used_capital(positions: list[PositionSnapshot]) -> float:
    return sum(p.notional_value for p in positions)


def evaluate_order_intent(
    order_intent: OrderIntent | None,
    portfolio_state: PortfolioState | None,
    limits: PortfolioLimits | None,
) -> PortfolioDecision:
    """
    Deterministic portfolio approval gate. Returns ALLOW, THROTTLE, or BLOCK.
    Fail-closed: any ambiguity, missing data, or inconsistent state -> BLOCK.
    """
    # Fail-closed: missing inputs
    if order_intent is None or portfolio_state is None or limits is None:
        return PortfolioDecision(
            decision=PortfolioDecisionType.BLOCK,
            reason_codes=["missing_input"],
            message="Portfolio gate: missing order_intent, portfolio_state, or limits",
            throttle_ratio=None,
            metadata=None,
        )

    reason_codes: list[str] = []
    throttle_domains: list[str] = []
    throttle_ratio: float | None = None
    recommended_notional: float | None = None
    recommended_quantity: float | None = None

    sid = order_intent.strategy_id
    if not sid or not order_intent.symbol:
        return PortfolioDecision(
            decision=PortfolioDecisionType.BLOCK,
            reason_codes=["malformed_intent"],
            message="Portfolio gate: strategy_id or symbol missing",
            throttle_ratio=None,
            metadata=None,
        )

    allocation = _get_allocation(portfolio_state, sid)
    if allocation is None:
        return PortfolioDecision(
            decision=PortfolioDecisionType.BLOCK,
            reason_codes=["missing_allocation"],
            message=f"Portfolio gate: no allocation for strategy {sid!r}",
            throttle_ratio=None,
            metadata=None,
        )

    if not allocation.strategy_enabled:
        return PortfolioDecision(
            decision=PortfolioDecisionType.BLOCK,
            reason_codes=["strategy_disabled"],
            message=f"Portfolio gate: strategy {sid!r} is disabled",
            throttle_ratio=None,
            metadata=None,
        )

    if allocation.strategy_lifecycle_state not in EXECUTION_LIFECYCLE_STATES:
        return PortfolioDecision(
            decision=PortfolioDecisionType.BLOCK,
            reason_codes=["lifecycle_not_executable"],
            message=f"Portfolio gate: strategy {sid!r} lifecycle {allocation.strategy_lifecycle_state!r} not executable (paper/live only)",
            throttle_ratio=None,
            metadata=None,
        )

    equity = max(portfolio_state.portfolio_equity, 0.0)
    if equity <= 0:
        return PortfolioDecision(
            decision=PortfolioDecisionType.BLOCK,
            reason_codes=["invalid_equity"],
            message="Portfolio gate: portfolio_equity must be positive",
            throttle_ratio=None,
            metadata=None,
        )

    positions = portfolio_state.open_positions or []
    by_strategy = _positions_by_strategy(positions)
    total_used = _total_used_capital(positions)
    strategy_positions = by_strategy.get(sid, [])
    strategy_used = _total_used_capital(strategy_positions)

    # Requested notional/quantity (use for throttle recommendations)
    req_notional = max(order_intent.requested_notional or 0.0, 0.0)
    req_qty = max(order_intent.requested_quantity or 0.0, 0.0)

    # --- Capital usage (portfolio): current and projected (with new order)
    portfolio_usage_pct = total_used / equity if equity else 0.0
    projected_usage_pct = (total_used + req_notional) / equity if equity else 0.0
    if portfolio_usage_pct >= limits.max_portfolio_capital_usage_pct or projected_usage_pct >= limits.max_portfolio_capital_usage_pct:
        reason_codes.append("portfolio_capital_overflow")
    elif portfolio_usage_pct >= limits.warning_capital_usage_pct or projected_usage_pct >= limits.warning_capital_usage_pct:
        throttle_domains.append("portfolio_capital")
        if throttle_ratio is None:
            throttle_ratio = 1.0
        # Reduce so we stay under warning
        headroom = limits.warning_capital_usage_pct * equity - total_used
        if req_notional > 0 and headroom < req_notional and throttle_ratio > (headroom / req_notional):
            throttle_ratio = max(0.0, headroom / req_notional)
            recommended_notional = headroom
            recommended_quantity = (headroom / (req_notional / req_qty)) if req_qty else 0.0

    # --- Capital usage (strategy): current and projected
    alloc_cap = max(allocation.allocated_capital, 1e-9)
    strategy_usage_pct = strategy_used / alloc_cap
    projected_strategy_pct = (strategy_used + req_notional) / alloc_cap
    if strategy_usage_pct >= limits.max_strategy_capital_usage_pct or projected_strategy_pct >= limits.max_strategy_capital_usage_pct:
        reason_codes.append("strategy_capital_overflow")
    elif strategy_usage_pct >= limits.warning_capital_usage_pct or projected_strategy_pct >= limits.warning_capital_usage_pct:
        throttle_domains.append("strategy_capital")
        if throttle_ratio is None:
            throttle_ratio = 1.0
        headroom = limits.warning_capital_usage_pct * alloc_cap - strategy_used
        if req_notional > 0 and headroom < req_notional and (throttle_ratio is None or throttle_ratio > max(0.0, headroom / req_notional)):
            r = max(0.0, headroom / req_notional)
            if throttle_ratio is None or r < throttle_ratio:
                throttle_ratio = r
                recommended_notional = headroom
                recommended_quantity = (headroom / (req_notional / req_qty)) if req_qty else 0.0

    # --- Open positions total
    n_total = len(positions)
    if n_total >= limits.max_open_positions_total:
        reason_codes.append("open_positions_overflow")
    elif limits.max_open_positions_total > 0 and n_total >= limits.max_open_positions_total * limits.warning_open_positions_pct:
        throttle_domains.append("open_positions")

    # --- Open positions per strategy
    n_strat = len(strategy_positions)
    if n_strat >= (allocation.max_positions or limits.max_open_positions_per_strategy):
        reason_codes.append("strategy_positions_overflow")
    elif (allocation.max_positions or limits.max_open_positions_per_strategy) > 0:
        cap_pos = allocation.max_positions or limits.max_open_positions_per_strategy
        if n_strat >= cap_pos * limits.warning_open_positions_pct:
            throttle_domains.append("strategy_positions")

    # --- Daily drawdown (portfolio)
    dd = _portfolio_drawdown_ratio(equity, portfolio_state.daily_pnl)
    if dd >= limits.max_daily_drawdown_pct:
        reason_codes.append("daily_drawdown_breach")
    elif dd >= limits.warning_drawdown_pct:
        throttle_domains.append("drawdown")

    # --- Strategy drawdown
    strat_daily = portfolio_state.strategy_daily_pnl.get(sid, 0.0)
    sd = _strategy_drawdown_ratio(equity, strat_daily)
    if sd >= limits.max_strategy_drawdown_pct:
        reason_codes.append("strategy_drawdown_breach")
    elif sd >= limits.warning_drawdown_pct:
        throttle_domains.append("strategy_drawdown")

    # --- Decision
    if reason_codes:
        return PortfolioDecision(
            decision=PortfolioDecisionType.BLOCK,
            reason_codes=reason_codes,
            message="Portfolio gate: " + "; ".join(reason_codes),
            throttle_ratio=None,
            metadata=None,
        )

    if throttle_domains and throttle_ratio is not None and throttle_ratio < 1.0:
        return PortfolioDecision(
            decision=PortfolioDecisionType.THROTTLE,
            reason_codes=[f"near_limit_{d}" for d in throttle_domains],
            message="Portfolio gate: near limits; reduced size recommended",
            throttle_ratio=throttle_ratio,
            metadata={
                "recommended_notional": recommended_notional,
                "recommended_quantity": recommended_quantity,
                "applied_warning_domains": throttle_domains,
            },
        )

    if throttle_domains:
        # Near limits but no numeric throttle computed; still THROTTLE with ratio 1.0
        return PortfolioDecision(
            decision=PortfolioDecisionType.THROTTLE,
            reason_codes=[f"near_limit_{d}" for d in throttle_domains],
            message="Portfolio gate: near limits",
            throttle_ratio=1.0,
            metadata={
                "recommended_notional": req_notional,
                "recommended_quantity": req_qty,
                "applied_warning_domains": throttle_domains,
            },
        )

    return PortfolioDecision(
        decision=PortfolioDecisionType.ALLOW,
        reason_codes=[],
        message="Portfolio gate: allowed",
        throttle_ratio=None,
        metadata=None,
    )


class PortfolioRiskEngine:
    """Deterministic portfolio approval gate (final gate before nq_exec)."""

    def __init__(self, limits: PortfolioLimits | None = None) -> None:
        from nq_portfolio.config import DEFAULT_PORTFOLIO_LIMITS
        self._limits = limits if limits is not None else DEFAULT_PORTFOLIO_LIMITS

    def evaluate(
        self,
        order_intent: OrderIntent | None,
        portfolio_state: PortfolioState | None,
        limits: PortfolioLimits | None = None,
    ) -> PortfolioDecision:
        """Evaluate order intent against portfolio state. Uses instance limits if limits not provided."""
        return evaluate_order_intent(
            order_intent,
            portfolio_state,
            limits if limits is not None else self._limits,
        )
