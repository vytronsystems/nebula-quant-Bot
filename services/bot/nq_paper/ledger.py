# NEBULA-QUANT v1 | nq_paper ledger — paper bookkeeping (real, in-memory)

from __future__ import annotations

from typing import Any

from nq_paper.models import PaperAccountState, PaperPosition, PaperTrade


def open_paper_position(
    symbol: str = "",
    side: str = "long",
    qty: float = 0.0,
    price: float = 0.0,
    ts: float = 0.0,
    **kwargs: Any,
) -> PaperPosition:
    """
    Open a paper position. In-memory only; deterministic.
    Caller is responsible for updating cash (deduct cost for long, add proceeds for short).
    """
    qty = qty if qty > 0 else 0.0
    return PaperPosition(
        symbol=symbol or "QQQ",
        side=side,
        qty=qty,
        avg_price=price,
        opened_ts=ts,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        metadata=dict(kwargs.get("metadata", {})),
    )


def close_paper_position(
    position: PaperPosition | None,
    exit_price: float = 0.0,
    exit_ts: float = 0.0,
    reason: str = "",
    strategy_id: str = "",
    trade_id: str = "",
    **kwargs: Any,
) -> PaperTrade | None:
    """
    Close a paper position and return a PaperTrade (gross pnl; caller applies commission).
    Safe on None. Deterministic.
    """
    if position is None or position.qty <= 0:
        return None
    if position.side == "long":
        pnl_gross = (exit_price - position.avg_price) * position.qty
    else:
        pnl_gross = (position.avg_price - exit_price) * position.qty
    entry_value = position.avg_price * position.qty
    pnl_pct = (pnl_gross / entry_value * 100.0) if entry_value else 0.0
    tid = trade_id or f"pt_{int(exit_ts)}"
    return PaperTrade(
        trade_id=tid,
        symbol=position.symbol,
        side=position.side,
        qty=position.qty,
        entry_ts=position.opened_ts,
        entry_price=position.avg_price,
        exit_ts=exit_ts,
        exit_price=exit_price,
        status="closed",
        pnl=pnl_gross,
        pnl_pct=pnl_pct,
        reason=reason or "signal",
        strategy_id=strategy_id,
        metadata=dict(kwargs.get("metadata", {})),
    )


def update_account_state(
    cash: float = 0.0,
    positions: list[PaperPosition] | None = None,
    closed_trades: list[PaperTrade] | None = None,
    ts: float = 0.0,
    **kwargs: Any,
) -> PaperAccountState:
    """
    Build paper account state from cash, open positions (with unrealized_pnl set), and closed trades.
    Equity = cash + sum(position value) where value = avg_price * qty + unrealized_pnl.
    Safe on empty input.
    """
    positions = positions or []
    closed_trades = closed_trades or []
    position_value = sum(p.avg_price * p.qty + getattr(p, "unrealized_pnl", 0.0) for p in positions)
    equity = cash + position_value
    used_buying_power = sum(p.avg_price * p.qty for p in positions)
    available_buying_power = max(0.0, equity - used_buying_power)
    return PaperAccountState(
        cash=cash,
        equity=equity,
        used_buying_power=used_buying_power,
        available_buying_power=available_buying_power,
        open_positions=list(positions),
        closed_trades=list(closed_trades),
        updated_ts=ts,
        metadata=dict(kwargs.get("metadata", {})),
    )
