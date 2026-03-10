from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Sequence

from nq_portfolio.config import DEFAULT_PORTFOLIO_CASH
from nq_portfolio.exposure import (
    build_exposure_summary,
    compute_gross_exposure,
    compute_long_exposure,
    compute_net_exposure,
    compute_short_exposure,
)
from nq_portfolio.models import (
    PortfolioAllocation,
    PortfolioDecision,
    PortfolioPosition,
    PortfolioSnapshot,
)


# NEBULA-QUANT v1 | nq_portfolio — portfolio engine (skeleton)


class PortfolioEngine:
    """
    In-memory portfolio management engine.

    Skeleton responsibilities:
    - maintain a minimal in-memory view of positions and allocations
    - compute basic exposure metrics
    - provide a fail-closed PortfolioDecision for new position requests
    """

    def __init__(
        self,
        cash: float = DEFAULT_PORTFOLIO_CASH,
        positions: Optional[Sequence[PortfolioPosition]] = None,
        allocations: Optional[Sequence[PortfolioAllocation]] = None,
    ) -> None:
        self._cash: float = float(cash)
        self._positions: list[PortfolioPosition] = list(positions or [])
        self._allocations: list[PortfolioAllocation] = list(allocations or [])

    @property
    def positions(self) -> Sequence[PortfolioPosition]:
        return tuple(self._positions)

    @property
    def allocations(self) -> Sequence[PortfolioAllocation]:
        return tuple(self._allocations)

    @property
    def cash(self) -> float:
        return self._cash

    def build_snapshot(self) -> PortfolioSnapshot:
        """
        Build a PortfolioSnapshot from current in-memory state.

        Safe behavior:
        - Works with empty positions/allocations.
        """
        positions: list[PortfolioPosition] = list(self._positions)
        allocations: list[PortfolioAllocation] = list(self._allocations)

        gross = compute_gross_exposure(positions)
        net = compute_net_exposure(positions)
        long_exposure = compute_long_exposure(positions)
        short_exposure = compute_short_exposure(positions)
        equity = self._cash + net

        return PortfolioSnapshot(
            cash=self._cash,
            equity=equity,
            gross_exposure=gross,
            net_exposure=net,
            long_exposure=long_exposure,
            short_exposure=short_exposure,
            positions=positions,
            allocations=allocations,
            updated_ts=datetime.utcnow(),
            metadata={"engine": "nq_portfolio", "version": "skeleton"},
        )

    def evaluate_new_position(
        self,
        requested_position: PortfolioPosition,
    ) -> PortfolioDecision:
        """
        Evaluate a requested new/adjusted position.

        Skeleton behavior:
        - Fail-closed: by default, does not allow new risk.
        - Does not mutate internal state.
        """
        return self.build_decision(
            allowed=False,
            reason="nq_portfolio skeleton: new positions disabled by default",
            requested_position=requested_position,
        )

    def update_position(self, position: PortfolioPosition) -> None:
        """
        Update or insert a position in the in-memory state.

        Skeleton behavior:
        - Upsert by position_id.
        - No external side effects or persistence.
        """
        for idx, existing in enumerate(self._positions):
            if existing.position_id == position.position_id:
                self._positions[idx] = position
                return
        self._positions.append(position)

    def close_position(self, position_id: str) -> None:
        """
        Remove a position from in-memory state by id.

        Safe behavior:
        - No error if the position does not exist.
        """
        self._positions = [
            p for p in self._positions if p.position_id != position_id
        ]

    def build_decision(
        self,
        allowed: bool,
        reason: str,
        requested_position: Optional[PortfolioPosition] = None,
    ) -> PortfolioDecision:
        """
        Helper to build a PortfolioDecision from basic inputs.

        For now, adjusted_qty and adjusted_weight simply mirror the
        requested position data when provided; otherwise they default to 0.0.
        """
        adjusted_qty = requested_position.qty if requested_position else 0.0
        adjusted_weight = requested_position.weight if requested_position else 0.0

        # Expose a minimal snapshot of current exposure at decision time
        exposures = build_exposure_summary(self._positions)

        return PortfolioDecision(
            allowed=allowed,
            reason=reason,
            adjusted_qty=adjusted_qty,
            adjusted_weight=adjusted_weight,
            metadata={"exposure": exposures},
        )

