# NEBULA-QUANT v1 | nq_paper ledger — paper bookkeeping (skeleton)

from typing import Any

from nq_paper.models import PaperPosition, PaperTrade, PaperAccountState


def open_paper_position(
    symbol: str = "",
    side: str = "long",
    qty: float = 0.0,
    price: float = 0.0,
    ts: float = 0.0,
    **kwargs: Any,
) -> PaperPosition:
    """
    Skeleton: open a paper position. Safe defaults; no external persistence.
    """
    _ = kwargs
    return PaperPosition(
        symbol=symbol or "QQQ",
        side=side,
        qty=qty if qty > 0 else 0.0,
        avg_price=price,
        opened_ts=ts,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        metadata={"skeleton": True},
    )


def close_paper_position(
    position: PaperPosition | None,
    exit_price: float = 0.0,
    exit_ts: float = 0.0,
    reason: str = "",
    **kwargs: Any,
) -> PaperTrade | None:
    """
    Skeleton: close a paper position and return a PaperTrade. Safe on None/empty.
    """
    _ = kwargs
    if position is None:
        return None
    pnl = (exit_price - position.avg_price) * position.qty if position.side == "long" else (position.avg_price - exit_price) * position.qty
    pnl_pct = (pnl / (position.avg_price * position.qty)) * 100.0 if position.qty and position.avg_price else 0.0
    return PaperTrade(
        trade_id=f"pt_{int(exit_ts)}",
        symbol=position.symbol,
        side=position.side,
        qty=position.qty,
        entry_ts=position.opened_ts,
        entry_price=position.avg_price,
        exit_ts=exit_ts,
        exit_price=exit_price,
        status="closed",
        pnl=pnl,
        pnl_pct=pnl_pct,
        reason=reason or "skeleton",
        strategy_id="",
        metadata={"skeleton": True},
    )


def update_account_state(
    cash: float = 0.0,
    positions: list[PaperPosition] | None = None,
    closed_trades: list[PaperTrade] | None = None,
    ts: float = 0.0,
    **kwargs: Any,
) -> PaperAccountState:
    """
    Skeleton: build paper account state. Safe on empty input.
    """
    _ = kwargs
    positions = positions or []
    closed_trades = closed_trades or []
    equity = cash + sum(
        (p.avg_price * p.qty + p.unrealized_pnl) for p in positions
    )
    used = sum(p.avg_price * p.qty for p in positions)
    return PaperAccountState(
        cash=cash,
        equity=equity,
        used_buying_power=used,
        available_buying_power=max(0.0, equity - used),
        open_positions=positions,
        closed_trades=closed_trades,
        updated_ts=ts,
        metadata={"skeleton": True},
    )
