# NEBULA-QUANT v1 | Binance paper / shadow execution (24/7, no session boundaries)

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from adapters.binance.config import BINANCE_FUTURES_CONFIG
from adapters.binance.validation import validate_symbol


class BinancePaperError(Exception):
    """Paper/shadow layer error."""


@dataclass(slots=True)
class BinancePaperOrder:
    order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None
    stop_price: float | None
    status: str  # PENDING, FILLED, CANCELED
    client_order_id: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinancePaperFill:
    fill_id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    ts: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinancePaperPosition:
    symbol: str
    position_amt: float
    entry_price: float
    unrealized_pnl: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinancePaperAccountState:
    cash_usdt: float
    positions: list[BinancePaperPosition]
    orders: list[BinancePaperOrder]
    fills: list[BinancePaperFill]
    session_start_ts: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinancePaperSessionReport:
    session_id: str
    started_ts: float
    ended_ts: float
    initial_cash: float
    final_cash: float
    total_pnl: float
    orders_count: int
    fills_count: int
    positions_count: int
    mode: str  # "paper" | "shadow"
    intended_orders_shadow: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)


def _get_bar(bar: Any, key: str, default: Any = None) -> Any:
    if hasattr(bar, key):
        return getattr(bar, key, default)
    if isinstance(bar, dict):
        return bar.get(key, default)
    return default


def _bar_ts(bar: Any) -> float:
    ts = _get_bar(bar, "ts")
    if ts is None:
        return 0.0
    if hasattr(ts, "timestamp"):
        return float(ts.timestamp())
    return float(ts)


def _bar_close(bar: Any) -> float:
    c = _get_bar(bar, "close")
    if c is None:
        return 0.0
    return float(c)


class BinancePaperTradingEngine:
    """
    Paper and shadow execution over Binance-normalized market data.
    No real risk; no secrets. 24/7: no market open/close assumptions.
    """

    def __init__(
        self,
        mode: str = "paper",
        initial_cash_usdt: float = 100_000.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        import time
        if mode not in ("paper", "shadow"):
            raise BinancePaperError(f"mode must be 'paper' or 'shadow', got {mode!r}")
        self._mode = mode
        self._initial_cash = float(initial_cash_usdt)
        self._clock = clock or time.time
        self._session_id: str = ""
        self._started_ts: float = 0.0
        self._cash: float = 0.0
        self._positions: list[BinancePaperPosition] = []
        self._orders: list[BinancePaperOrder] = []
        self._fills: list[BinancePaperFill] = []
        self._intended_orders: list[dict[str, Any]] = []
        self._order_counter: int = 0
        self._fill_counter: int = 0

    def _next_order_id(self) -> str:
        self._order_counter += 1
        return f"paper-order-{self._order_counter}"

    def _next_fill_id(self) -> str:
        self._fill_counter += 1
        return f"paper-fill-{self._fill_counter}"

    def start_session(self, session_id: str | None = None) -> None:
        now = self._clock()
        self._session_id = session_id or f"paper-session-{int(now)}"
        self._started_ts = now
        self._cash = self._initial_cash
        self._positions = []
        self._orders = []
        self._fills = []
        self._intended_orders = []
        self._order_counter = 0
        self._fill_counter = 0

    def submit_paper_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        client_order_id: str | None = None,
    ) -> BinancePaperOrder:
        validate_symbol(symbol)
        if symbol not in BINANCE_FUTURES_CONFIG.allowed_symbols:
            raise BinancePaperError(f"symbol {symbol!r} not allowed")
        order_id = self._next_order_id()
        order = BinancePaperOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            status="PENDING",
            client_order_id=client_order_id,
            metadata={},
        )
        self._orders.append(order)
        self._intended_orders.append({
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "stop_price": stop_price,
        })

        if self._mode == "paper":
            fill_price = price if price and price > 0 else 50000.0
            fill = BinancePaperFill(
                fill_id=self._next_fill_id(),
                order_id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=fill_price,
                ts=self._clock(),
                metadata={},
            )
            self._fills.append(fill)
            order.status = "FILLED"
            amt = quantity * fill_price
            if side.upper() == "BUY":
                self._cash -= amt
            else:
                self._cash += amt
            existing = [p for p in self._positions if p.symbol == symbol]
            if existing:
                pos = existing[0]
                if (side.upper() == "BUY" and pos.position_amt >= 0) or (side.upper() == "SELL" and pos.position_amt <= 0):
                    new_amt = pos.position_amt + (quantity if side.upper() == "BUY" else -quantity)
                    avg = (pos.entry_price * abs(pos.position_amt) + fill_price * quantity) / abs(new_amt) if new_amt != 0 else pos.entry_price
                    self._positions = [p for p in self._positions if p.symbol != symbol]
                    if abs(new_amt) > 1e-9:
                        self._positions.append(BinancePaperPosition(symbol=symbol, position_amt=new_amt, entry_price=avg, unrealized_pnl=0.0, metadata={}))
                else:
                    close_qty = min(quantity, abs(pos.position_amt))
                    pnl = close_qty * (fill_price - pos.entry_price) if pos.position_amt > 0 else close_qty * (pos.entry_price - fill_price)
                    self._cash += pnl
                    new_amt = pos.position_amt + (close_qty if side.upper() == "SELL" else -close_qty)
                    self._positions = [p for p in self._positions if p.symbol != symbol]
                    if abs(new_amt) > 1e-9:
                        self._positions.append(BinancePaperPosition(symbol=symbol, position_amt=new_amt, entry_price=pos.entry_price, unrealized_pnl=0.0, metadata={}))
            else:
                self._positions.append(BinancePaperPosition(symbol=symbol, position_amt=quantity if side.upper() == "BUY" else -quantity, entry_price=fill_price, unrealized_pnl=0.0, metadata={}))

        return order

    def process_bar(self, bar: Any, strategy: Any | None = None) -> str:
        if strategy is None:
            return "hold"
        close = _bar_close(bar)
        if close <= 0:
            return "hold"
        signal = "hold"
        if callable(strategy):
            signal = strategy(bar)
        elif hasattr(strategy, "on_bar"):
            signal = strategy.on_bar(bar)
        if isinstance(signal, str):
            signal = signal.strip().lower()
        else:
            signal = getattr(signal, "value", str(signal)).strip().lower()
        return signal if signal in ("long", "short", "exit", "hold") else "hold"

    def get_session_state(self) -> BinancePaperAccountState:
        return BinancePaperAccountState(
            cash_usdt=self._cash,
            positions=list(self._positions),
            orders=list(self._orders),
            fills=list(self._fills),
            session_start_ts=self._started_ts,
            metadata={"mode": self._mode, "session_id": self._session_id},
        )

    def build_session_report(self) -> BinancePaperSessionReport:
        now = self._clock()
        total_pnl = self._cash - self._initial_cash
        return BinancePaperSessionReport(
            session_id=self._session_id,
            started_ts=self._started_ts,
            ended_ts=now,
            initial_cash=self._initial_cash,
            final_cash=self._cash,
            total_pnl=total_pnl,
            orders_count=len(self._orders),
            fills_count=len(self._fills),
            positions_count=len(self._positions),
            mode=self._mode,
            intended_orders_shadow=list(self._intended_orders),
            metadata={},
        )
