# NEBULA-QUANT v1 | nq_paper engine — skeleton only

from typing import Any

from nq_paper.config import DEFAULT_PAPER_INITIAL_CAPITAL
from nq_paper.models import (
    PaperTrade,
    PaperPosition,
    PaperAccountState,
    PaperSessionResult,
)
from nq_paper.ledger import update_account_state


class PaperEngine:
    """
    Skeleton paper trading engine. Accepts signal/context placeholders,
    simulates paper actions only, returns safe PaperSessionResult.
    No real fills or broker routing.
    """

    def __init__(self, initial_capital: float | None = None, **kwargs: Any) -> None:
        _ = kwargs
        self._initial_capital = initial_capital or DEFAULT_PAPER_INITIAL_CAPITAL
        self._session_id = "paper_session_0"

    def run_session(
        self,
        signals: Any = None,
        context: dict[str, Any] | None = None,
        start_ts: float = 0.0,
        end_ts: float = 0.0,
    ) -> PaperSessionResult:
        """
        Skeleton: run a paper session. Accepts placeholders; returns safe result.
        Does not crash on empty/default input.
        """
        _ = signals
        _ = context
        if end_ts <= start_ts:
            end_ts = start_ts + 1.0
        self._process_signal(None, context or {})
        self._update_positions()
        return self._build_session_result(start_ts=start_ts, end_ts=end_ts)

    def _process_signal(self, signal: Any, context: dict[str, Any]) -> None:
        """Skeleton: placeholder. No real order simulation."""
        _ = signal
        _ = context

    def _update_positions(self) -> None:
        """Skeleton: placeholder. No real position update."""

    def _close_position(self, position: PaperPosition | None, **kwargs: Any) -> PaperTrade | None:
        """Skeleton: placeholder. Returns None or stub trade."""
        _ = kwargs
        if position is None:
            return None
        return None  # skeleton: no close simulated

    def _build_session_result(
        self,
        start_ts: float = 0.0,
        end_ts: float = 0.0,
    ) -> PaperSessionResult:
        """Build safe PaperSessionResult skeleton."""
        state = update_account_state(
            cash=self._initial_capital,
            positions=[],
            closed_trades=[],
            ts=end_ts,
        )
        return PaperSessionResult(
            session_id=self._session_id,
            started_ts=start_ts,
            ended_ts=end_ts,
            trades=[],
            positions=[],
            account_state=state,
            summary={"skeleton": True, "total_trades": 0},
            metadata={"skeleton": True},
        )
