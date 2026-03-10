# NEBULA-QUANT v1 | nq_paper engine — real bar-by-bar paper simulation

from __future__ import annotations

from typing import Any, Sequence

from nq_paper.config import (
    DEFAULT_PAPER_COMMISSION,
    DEFAULT_PAPER_INITIAL_CAPITAL,
    DEFAULT_PAPER_QTY,
    DEFAULT_PAPER_SLIPPAGE_BPS,
)
from nq_paper.ledger import close_paper_position, open_paper_position, update_account_state
from nq_paper.metrics import (
    compute_paper_basic_stats,
    compute_paper_drawdown,
    compute_paper_net_pnl,
    compute_paper_win_rate,
)
from nq_paper.models import (
    PaperAccountState,
    PaperPosition,
    PaperSessionResult,
    PaperTrade,
)


def _get_bar_attr(bar: Any, key: str, default: Any = None) -> Any:
    if isinstance(bar, dict):
        return bar.get(key, default)
    return getattr(bar, key, default)


def _bar_ts(bar: Any) -> float:
    ts = _get_bar_attr(bar, "ts")
    if ts is None:
        return 0.0
    if hasattr(ts, "timestamp"):
        return float(ts.timestamp())
    return float(ts)


def _bar_close(bar: Any) -> float:
    c = _get_bar_attr(bar, "close")
    if c is None:
        return 0.0
    return float(c)


def _normalize_signal(signal: Any) -> str:
    if signal is None:
        return "hold"
    s = signal
    if hasattr(s, "value"):
        s = s.value
    elif hasattr(s, "name"):
        s = s.name
    s = str(s).strip().lower()
    if s in ("long", "short", "exit", "hold"):
        return s
    return "hold"


def _apply_slippage_bps(price: float, side: str, is_entry: bool, bps: float) -> float:
    if bps <= 0:
        return price
    mult = 1.0 + (bps / 10_000.0)
    if side == "long":
        return price * mult if is_entry else price / mult
    return price / mult if is_entry else price * mult


class PaperEngine:
    """
    Real paper trading engine: bar-by-bar simulation, strategy signals,
    in-memory positions and trades, account state, session result.
    """

    def __init__(
        self,
        initial_capital: float | None = None,
        commission: float | None = None,
        slippage_bps: float | None = None,
        qty: float | None = None,
        strategy_id: str = "",
        **kwargs: Any,
    ) -> None:
        self._initial_capital = initial_capital or DEFAULT_PAPER_INITIAL_CAPITAL
        self._commission = commission if commission is not None else DEFAULT_PAPER_COMMISSION
        self._slippage_bps = slippage_bps if slippage_bps is not None else DEFAULT_PAPER_SLIPPAGE_BPS
        self._qty = qty if qty is not None else DEFAULT_PAPER_QTY
        self._strategy_id = strategy_id or ""
        self._session_id = kwargs.get("session_id", "paper_session_0")
        self._closed_trades: list[PaperTrade] = []
        self._position: PaperPosition | None = None
        self._cash: float = self._initial_capital
        self._equity_curve: list[tuple[float, float]] = []

    def run_session(
        self,
        bars: Sequence[Any] | None = None,
        strategy: Any = None,
        session_id: str | None = None,
    ) -> PaperSessionResult:
        """
        Run a paper session over bars with the given strategy.
        Empty bars or no strategy returns safe empty session result.
        """
        if session_id is not None:
            self._session_id = session_id
        self._closed_trades = []
        self._position = None
        self._cash = self._initial_capital
        self._equity_curve = []

        bar_list = list(bars or [])
        if not bar_list or strategy is None:
            return self._build_session_result(start_ts=0.0, end_ts=0.0)

        started_ts = _bar_ts(bar_list[0])
        ended_ts = _bar_ts(bar_list[-1])
        trade_counter = 0

        for bar in bar_list:
            ts = _bar_ts(bar)
            close = _bar_close(bar)
            if close <= 0:
                continue

            # Mark to market current position
            self._update_positions(close)
            equity = self._cash
            if self._position is not None:
                equity += self._position.avg_price * self._position.qty + self._position.unrealized_pnl
            self._equity_curve.append((ts, equity))

            signal = _normalize_signal(
                strategy(bar) if callable(strategy) else getattr(strategy, "on_bar", lambda b: "hold")(bar)
            )

            # Close position on EXIT or opposite signal
            if self._position is not None:
                if signal == "exit" or (signal == "short" and self._position.side == "long") or (signal == "long" and self._position.side == "short"):
                    trade = self._close_position(bar, close, reason="signal")
                    if trade:
                        trade_counter += 1
                        self._closed_trades.append(
                            PaperTrade(
                                trade_id=f"{self._session_id}_{trade_counter}",
                                symbol=trade.symbol,
                                side=trade.side,
                                qty=trade.qty,
                                entry_ts=trade.entry_ts,
                                entry_price=trade.entry_price,
                                exit_ts=trade.exit_ts,
                                exit_price=trade.exit_price,
                                status=trade.status,
                                pnl=trade.pnl - 2 * self._commission,
                                pnl_pct=trade.pnl_pct,
                                reason=trade.reason,
                                strategy_id=self._strategy_id or trade.strategy_id,
                                metadata=trade.metadata,
                            )
                        )

            # Open new position if flat
            if self._position is None:
                if signal == "long":
                    fill = _apply_slippage_bps(close, "long", True, self._slippage_bps)
                    cost = fill * self._qty + self._commission
                    if cost <= self._cash:
                        self._cash -= cost
                        self._position = open_paper_position(
                            symbol=_get_bar_attr(bar, "symbol") or "QQQ",
                            side="long",
                            qty=self._qty,
                            price=fill,
                            ts=ts,
                        )
                elif signal == "short":
                    fill = _apply_slippage_bps(close, "short", True, self._slippage_bps)
                    self._cash += fill * self._qty - self._commission
                    self._position = open_paper_position(
                        symbol=_get_bar_attr(bar, "symbol") or "QQQ",
                        side="short",
                        qty=self._qty,
                        price=fill,
                        ts=ts,
                    )

        return self._build_session_result(start_ts=started_ts, end_ts=ended_ts)

    def _process_signal(self, bar: Any, signal: str, close: float) -> None:
        """Handled inline in run_session for clarity; kept for API compatibility."""
        pass

    def _update_positions(self, mark_price: float) -> None:
        """Mark open position to market (set unrealized_pnl)."""
        if self._position is None:
            return
        if self._position.side == "long":
            self._position.unrealized_pnl = (mark_price - self._position.avg_price) * self._position.qty
        else:
            self._position.unrealized_pnl = (self._position.avg_price - mark_price) * self._position.qty

    def _close_position(self, bar: Any, exit_price: float, reason: str = "signal") -> PaperTrade | None:
        """Close current position at exit_price (with slippage); update cash; return trade (gross)."""
        if self._position is None:
            return None
        exit_fill = _apply_slippage_bps(exit_price, self._position.side, False, self._slippage_bps)
        trade = close_paper_position(
            self._position,
            exit_price=exit_fill,
            exit_ts=_bar_ts(bar),
            reason=reason,
            strategy_id=self._strategy_id,
        )
        if trade is None:
            return None
        if self._position.side == "long":
            self._cash += exit_fill * self._position.qty - self._commission
        else:
            self._cash -= exit_fill * self._position.qty + self._commission
        self._position = None
        return trade

    def _build_session_result(
        self,
        start_ts: float = 0.0,
        end_ts: float = 0.0,
    ) -> PaperSessionResult:
        """Build PaperSessionResult from current state and metrics."""
        closed = getattr(self, "_closed_trades", [])
        position = getattr(self, "_position", None)
        cash = getattr(self, "_cash", self._initial_capital)
        curve = getattr(self, "_equity_curve", [])
        positions_list = [position] if position is not None else []

        state = update_account_state(
            cash=cash,
            positions=positions_list,
            closed_trades=closed,
            ts=end_ts,
        )
        basic = compute_paper_basic_stats(closed)
        net_pnl = compute_paper_net_pnl(closed)
        win_rate = compute_paper_win_rate(closed)
        max_dd = compute_paper_drawdown(curve) if curve else 0.0
        summary = {
            "total_trades": basic["total_trades"],
            "closed_trades": len(closed),
            "net_pnl": net_pnl,
            "win_rate": win_rate,
            "max_drawdown": max_dd,
            **basic,
        }
        return PaperSessionResult(
            session_id=getattr(self, "_session_id", "paper_session_0"),
            started_ts=start_ts,
            ended_ts=end_ts,
            trades=closed,
            positions=positions_list,
            account_state=state,
            summary=summary,
            metadata={"engine": "nq_paper", "version": "real"},
        )
