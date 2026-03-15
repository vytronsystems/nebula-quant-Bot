# NEBULA-QUANT v1 | Phase 78 — Capital Allocation Engine
# Adjust risk per strategy from momentum, pnl stability, drawdown, volatility.

from __future__ import annotations

from typing import Any

from nq_capital_allocation.models import AllocationInput, AllocationResult


class CapitalAllocationEngine:
    """Dynamically allocate capital/risk across strategies from inputs."""

    def allocate(self, inputs: list[AllocationInput]) -> list[AllocationResult]:
        if not inputs:
            return []
        raw_weights = []
        for inp in inputs:
            w = self._score(inp)
            raw_weights.append((inp.strategy_id, w, inp))
        total = sum(w for _, w, _ in raw_weights) or 1.0
        results = []
        for strategy_id, w, inp in raw_weights:
            weight = w / total
            risk_pct = min(1.0, weight * 1.2)
            results.append(AllocationResult(
                strategy_id=strategy_id,
                weight=weight,
                risk_pct=risk_pct,
                reason="momentum_drawdown_volatility",
                metadata=inp.metadata,
            ))
        return results

    def _score(self, inp: AllocationInput) -> float:
        s = 1.0
        if inp.momentum is not None and inp.momentum > 0:
            s += 0.2 * min(1.0, inp.momentum)
        if inp.pnl_stability is not None and inp.pnl_stability > 0:
            s += 0.1 * min(1.0, inp.pnl_stability)
        if inp.drawdown is not None and inp.drawdown > 0:
            s -= 0.3 * min(1.0, inp.drawdown / 0.2)
        if inp.volatility is not None and inp.volatility > 0:
            s -= 0.1 * min(1.0, inp.volatility)
        return max(0.05, s)
