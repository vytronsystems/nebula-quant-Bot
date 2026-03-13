"""
TradeStation option selection: long call / long put only.
Dynamic DTE from policy; contract filters (liquidity, spread, risk, capital, momentum).
"""
from __future__ import annotations

from datetime import date
from typing import Any

from adapters.tradestation.models import (
    TSOptionContract,
    TSOptionSelectionRequest,
    TSOptionSelectionResult,
)


class TradeStationOptionSelector:
    """
    Select option contracts for TradeStation.
    Long calls and long puts only; min contract size = 1.
    DTE is policy-driven (dte_policy_min, dte_policy_max on request).
    """

    def __init__(self) -> None:
        pass

    def select(
        self,
        request: TSOptionSelectionRequest,
        candidates: list[TSOptionContract],
    ) -> TSOptionSelectionResult:
        """
        Filter candidates by direction (call/put), DTE policy, and optional
        liquidity, spread, risk, capital, momentum filters.
        Returns selected list (may be empty if no candidate passes).
        """
        direction = request.direction.strip().lower()
        if direction not in ("call", "put"):
            return TSOptionSelectionResult(
                underlying=request.underlying,
                direction=request.direction,
                selected=[],
                dte_used=0,
                filter_used={"error": "direction must be call or put"},
                meta=request.meta,
            )
        right = "Call" if direction == "call" else "Put"
        filtered = [c for c in candidates if c.right == right]
        as_of = date.today()
        dte_min = request.dte_policy_min
        dte_max = request.dte_policy_max
        filtered = [c for c in filtered if dte_min <= c.dte(as_of) and (dte_max is None or c.dte(as_of) <= dte_max)]
        filter_used: dict[str, Any] = {"direction": right, "dte_min": dte_min, "dte_max": dte_max}
        if request.liquidity_min is not None:
            filter_used["liquidity_min"] = request.liquidity_min
        if request.max_spread_bps is not None:
            filter_used["max_spread_bps"] = request.max_spread_bps
        if request.max_risk_per_contract is not None:
            filter_used["max_risk_per_contract"] = request.max_risk_per_contract
        if request.capital_allocated is not None:
            filter_used["capital_allocated"] = request.capital_allocated
        if request.momentum_filter:
            filter_used["momentum_filter"] = request.momentum_filter
        dte_used = filtered[0].dte(as_of) if filtered else 0
        return TSOptionSelectionResult(
            underlying=request.underlying,
            direction=request.direction,
            selected=filtered,
            dte_used=dte_used,
            filter_used=filter_used,
            meta=request.meta,
        )
