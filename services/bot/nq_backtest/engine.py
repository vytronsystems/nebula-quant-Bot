# NEBULA-QUANT v1 | nq_backtest engine — real bar-by-bar simulation

from __future__ import annotations

from typing import Any, Callable, Sequence

from nq_backtest.config import (
    DEFAULT_COMMISSION,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_QTY,
    DEFAULT_SLIPPAGE_BPS,
)
from nq_backtest.metrics import (
    compute_max_drawdown,
    compute_net_pnl,
    compute_sharpe_like,
    compute_win_rate,
)
from nq_backtest.models import (
    BacktestConfig,
    BacktestResult,
    EquityPoint,
    TradeRecord,
)


def _get_bar_attr(bar: Any, key: str, default: Any = None) -> Any:
    """Get attribute from bar (object or dict)."""
    if isinstance(bar, dict):
        return bar.get(key, default)
    return getattr(bar, key, default)


def _bar_ts(bar: Any) -> float:
    """Numeric timestamp for bar (seconds)."""
    ts = _get_bar_attr(bar, "ts")
    if ts is None:
        return 0.0
    if hasattr(ts, "timestamp"):
        return float(ts.timestamp())
    return float(ts)


def _bar_close(bar: Any) -> float:
    """Close price as float."""
    c = _get_bar_attr(bar, "close")
    if c is None:
        return 0.0
    return float(c)


def _normalize_signal(signal: Any) -> str:
    """Normalize strategy output to 'long'|'short'|'exit'|'hold'."""
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
    """Apply adverse slippage in basis points. Deterministic."""
    if bps <= 0:
        return price
    mult = 1.0 + (bps / 10_000.0)  # adverse: pay more on buy, get less on sell
    if side == "long":
        if is_entry:
            return price * mult  # buy higher
        return price / mult  # sell lower
    else:  # short
        if is_entry:
            return price / mult  # sell higher
        return price * mult  # cover higher


class BacktestEngine:
    """
    Real backtest engine: bar-by-bar simulation with strategy callback,
    in-memory trade recording, equity curve, and metrics.
    """

    def __init__(
        self,
        config: BacktestConfig | None = None,
        **kwargs: Any,
    ) -> None:
        if config is not None:
            self._config = config
        else:
            self._config = BacktestConfig(
                symbol=kwargs.get("symbol", "QQQ"),
                timeframe=kwargs.get("timeframe", "1d"),
                initial_capital=kwargs.get("initial_capital", DEFAULT_INITIAL_CAPITAL),
                commission_per_trade=kwargs.get(
                    "commission_per_trade", DEFAULT_COMMISSION
                ),
                slippage_bps=kwargs.get("slippage_bps", DEFAULT_SLIPPAGE_BPS),
                start_ts=float(kwargs.get("start_ts", 0)),
                end_ts=float(kwargs.get("end_ts", 0)),
                qty=float(kwargs.get("qty", DEFAULT_QTY)),
            )

    def run(
        self,
        bars: Sequence[Any] | None = None,
        strategy: Any = None,
    ) -> BacktestResult:
        """
        Run backtest over bars with the given strategy.
        bars: bar-like objects with ts, close (and optionally open, high, low, volume, symbol, timeframe).
        strategy: callable(bar) -> signal, or object with on_bar(bar) -> signal. Signals: LONG, SHORT, EXIT, HOLD.
        Returns BacktestResult; empty bars or no strategy yields safe empty result.
        """
        self._validate_inputs(bars, strategy)
        self._simulate(bars or (), strategy)
        return self._build_result()

    def _validate_inputs(
        self,
        bars: Sequence[Any] | None,
        strategy: Any,
    ) -> None:
        """Validate config and inputs. No raise on empty; engine must handle empty safely."""
        # Config is always set in __init__. Bars/strategy can be empty; _simulate handles it.
        pass

    def _simulate(
        self,
        bars: Sequence[Any],
        strategy: Any,
    ) -> None:
        """Bar-by-bar simulation: strategy signal -> open/close position, record trades, build equity curve."""
        cfg = self._config
        start_ts = cfg.start_ts
        end_ts = cfg.end_ts
        use_time_bounds = start_ts > 0 or end_ts > 0
        if end_ts <= 0:
            end_ts = float("inf")

        self._trades: list[TradeRecord] = []
        self._equity_curve: list[EquityPoint] = []
        cash = cfg.initial_capital
        position_side: str | None = None  # "long" | "short" | None
        entry_ts: float = 0.0
        entry_fill_price: float = 0.0
        position_qty: float = 0.0
        peak_equity = cash

        def strategy_signal(bar: Any) -> str:
            if strategy is None:
                return "hold"
            if callable(strategy):
                return _normalize_signal(strategy(bar))
            if hasattr(strategy, "on_bar"):
                return _normalize_signal(strategy.on_bar(bar))
            return "hold"

        for bar in bars:
            ts = _bar_ts(bar)
            if use_time_bounds and (ts < start_ts or ts > end_ts):
                continue
            close = _bar_close(bar)
            if close <= 0:
                continue

            signal = strategy_signal(bar)
            comm = cfg.commission_per_trade
            bps = cfg.slippage_bps
            qty = cfg.qty

            # Close position if signal is EXIT or opposite direction
            if position_side is not None:
                if signal == "exit" or (signal == "short" and position_side == "long") or (signal == "long" and position_side == "short"):
                    exit_fill = _apply_slippage_bps(close, position_side, False, bps)
                    if position_side == "long":
                        pnl_raw = (exit_fill - entry_fill_price) * position_qty
                    else:
                        pnl_raw = (entry_fill_price - exit_fill) * position_qty
                    pnl_net = pnl_raw - 2 * comm
                    cash += exit_fill * position_qty - comm
                    entry_value = entry_fill_price * position_qty
                    pnl_pct = (pnl_net / entry_value * 100.0) if entry_value else 0.0
                    self._trades.append(
                        TradeRecord(
                            entry_ts=entry_ts,
                            exit_ts=ts,
                            side=position_side,
                            entry_price=entry_fill_price,
                            exit_price=exit_fill,
                            qty=position_qty,
                            pnl=pnl_net,
                            pnl_pct=pnl_pct,
                            reason="signal",
                        )
                    )
                    position_side = None
                    position_qty = 0.0

            # Open new position if flat and signal is long/short
            if position_side is None:
                if signal == "long":
                    entry_fill_price = _apply_slippage_bps(close, "long", True, bps)
                    cost = entry_fill_price * qty + comm
                    if cost <= cash:
                        cash -= cost
                        position_side = "long"
                        position_qty = qty
                        entry_ts = ts
                elif signal == "short":
                    entry_fill_price = _apply_slippage_bps(close, "short", True, bps)
                    cash += entry_fill_price * qty - comm  # short sale proceeds
                    position_side = "short"
                    position_qty = qty
                    entry_ts = ts

            # Equity at bar close (mark-to-market)
            if position_side is None:
                equity = cash
            elif position_side == "long":
                equity = cash + position_qty * close
            else:
                equity = cash + (entry_fill_price - close) * position_qty
            if equity > peak_equity:
                peak_equity = equity
            drawdown = peak_equity - equity
            self._equity_curve.append(EquityPoint(ts=ts, equity=equity, drawdown=drawdown))

        # Ensure at least one equity point if we had any bars
        if not self._equity_curve and bars:
            self._equity_curve.append(
                EquityPoint(ts=0.0, equity=cfg.initial_capital, drawdown=0.0)
            )
        elif not self._equity_curve:
            self._equity_curve.append(
                EquityPoint(ts=cfg.start_ts, equity=cfg.initial_capital, drawdown=0.0)
            )

    def _build_result(self) -> BacktestResult:
        """Build BacktestResult from collected trades and equity curve."""
        cfg = self._config
        trades = getattr(self, "_trades", [])
        equity_curve = getattr(self, "_equity_curve", [])

        wins = sum(1 for t in trades if t.pnl > 0)
        losses = len(trades) - wins
        win_rate = compute_win_rate(trades)
        net_pnl = compute_net_pnl(trades)
        gross_pnl = 0.0
        for t in trades:
            if t.side == "long":
                gross_pnl += (t.exit_price - t.entry_price) * t.qty
            else:
                gross_pnl += (t.entry_price - t.exit_price) * t.qty
        max_drawdown = compute_max_drawdown(equity_curve)
        sharpe_like = compute_sharpe_like(equity_curve)

        return BacktestResult(
            config=cfg,
            total_trades=len(trades),
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            max_drawdown=max_drawdown,
            sharpe_like=sharpe_like,
            trades=trades,
            equity_curve=equity_curve,
            metadata={"engine": "nq_backtest", "version": "real"},
        )
