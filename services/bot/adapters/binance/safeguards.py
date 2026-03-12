# NEBULA-QUANT v1 | Binance live safeguards (24/7, UTC reset, rolling windows)

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from adapters.binance.config import BINANCE_FUTURES_CONFIG, BINANCE_OPERATIONAL_CONFIG

# Categories for future nq_sre / nq_runbooks integration (e.g. incident routing, runbook lookup).
SAFEGUARD_FAILURE_CATEGORIES = (
    "venue_disabled",
    "kill_switch_active",
    "leverage_cap",
    "daily_loss_limit_hit",
    "max_position_size",
    "max_notional_per_order",
    "max_open_positions",
    "order_rate_limit_hit",
    "heartbeat_stale",
    "reconciliation_required",
)


class BinanceSafeguardError(Exception):
    """Raised when a safeguard check fails (fail closed)."""


@dataclass(slots=True)
class BinanceSafeguardDecision:
    allowed: bool
    reason: str
    category: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BinanceSafeguardState:
    kill_switch_active: bool
    venue_enabled: bool
    daily_loss_so_far: float
    utc_day_key: str
    orders_in_window: int
    last_heartbeat_ts: float | None
    heartbeat_stale: bool
    metadata: dict[str, Any] = field(default_factory=dict)


def _utc_day_key(ts: float, reset_hour_utc: int) -> str:
    """Deterministic UTC day key: day rolls at reset_hour_utc (0-23)."""
    import time
    t = time.gmtime(ts)
    h = t.tm_hour
    d = t.tm_mday
    mo = t.tm_mon
    y = t.tm_year
    if h < reset_hour_utc:
        d = d - 1
        if d < 1:
            mo = mo - 1
            if mo < 1:
                mo = 12
                y = y - 1
            d = 31
    return f"{y:04d}-{mo:02d}-{d:02d}"


class BinanceLiveSafeguards:
    """
    Explicit, deterministic live safeguards for Binance.
    24/7/365: UTC-based daily reset, rolling windows, continuous kill switch.
    """

    def __init__(
        self,
        config: Any | None = None,
        venue_enabled: bool | None = None,
        kill_switch_active: bool | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        import time
        self._config = config or BINANCE_OPERATIONAL_CONFIG
        self._venue_enabled = venue_enabled if venue_enabled is not None else getattr(self._config, "binance_live_enabled", False)
        self._kill_switch = kill_switch_active if kill_switch_active is not None else False
        self._clock = clock or time.time
        self._daily_loss: float = 0.0
        self._utc_day_key: str = ""
        self._order_timestamps: list[float] = []
        self._last_heartbeat: float | None = None

    def set_heartbeat(self, ts: float | None = None) -> None:
        now = ts if ts is not None else self._clock()
        self._last_heartbeat = now

    def set_kill_switch(self, active: bool) -> None:
        self._kill_switch = active

    def record_order(self) -> None:
        self._order_timestamps.append(self._clock())

    def record_daily_loss_delta(self, delta: float) -> None:
        now = self._clock()
        key = _utc_day_key(now, getattr(self._config, "binance_reset_hour_utc", 0))
        if key != self._utc_day_key:
            self._utc_day_key = key
            self._daily_loss = 0.0
        self._daily_loss += delta

    def _trim_order_window(self) -> None:
        window_sec = getattr(self._config, "binance_rolling_window_minutes", 5) * 60.0
        cutoff = self._clock() - window_sec
        self._order_timestamps = [t for t in self._order_timestamps if t >= cutoff]

    def check_venue_enabled(self) -> BinanceSafeguardDecision:
        if not self._venue_enabled:
            return BinanceSafeguardDecision(allowed=False, reason="Binance live is disabled", category="venue_disabled", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="venue", metadata={})

    def check_kill_switch(self) -> BinanceSafeguardDecision:
        if self._kill_switch:
            return BinanceSafeguardDecision(allowed=False, reason="Kill switch is active", category="kill_switch_active", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="kill_switch", metadata={})

    def check_leverage(self, leverage: int) -> BinanceSafeguardDecision:
        max_lev = getattr(self._config, "max_leverage", None) or BINANCE_FUTURES_CONFIG.max_leverage
        if leverage > max_lev:
            return BinanceSafeguardDecision(allowed=False, reason=f"leverage {leverage} exceeds max {max_lev}", category="leverage_cap", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="leverage", metadata={})

    def check_max_daily_loss(self) -> BinanceSafeguardDecision:
        now = self._clock()
        key = _utc_day_key(now, getattr(self._config, "binance_reset_hour_utc", 0))
        if key != self._utc_day_key:
            self._utc_day_key = key
            self._daily_loss = 0.0
        max_loss = float(getattr(self._config, "binance_max_daily_loss", 5000.0))
        if self._daily_loss < -max_loss:
            return BinanceSafeguardDecision(allowed=False, reason=f"daily loss {self._daily_loss} exceeds limit -{max_loss}", category="daily_loss_limit_hit", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="daily_loss", metadata={})

    def check_max_position_size(self, position_size: float) -> BinanceSafeguardDecision:
        max_sz = float(getattr(self._config, "binance_max_position_size", 1.0))
        if position_size > max_sz:
            return BinanceSafeguardDecision(allowed=False, reason=f"position size {position_size} exceeds max {max_sz}", category="max_position_size", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="position_size", metadata={})

    def check_max_notional_per_order(self, notional: float) -> BinanceSafeguardDecision:
        max_n = float(getattr(self._config, "binance_max_notional_per_order", 100_000.0))
        if notional > max_n:
            return BinanceSafeguardDecision(allowed=False, reason=f"notional {notional} exceeds max {max_n}", category="max_notional_per_order", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="notional", metadata={})

    def check_max_open_positions(self, current_count: int) -> BinanceSafeguardDecision:
        max_pos = int(getattr(self._config, "binance_max_open_positions", 5))
        if current_count >= max_pos:
            return BinanceSafeguardDecision(allowed=False, reason=f"open positions {current_count} >= max {max_pos}", category="max_open_positions", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="open_positions", metadata={})

    def check_order_rate_limit(self) -> BinanceSafeguardDecision:
        self._trim_order_window()
        limit = int(getattr(self._config, "binance_max_order_rate_per_minute", 10))
        if len(self._order_timestamps) >= limit:
            return BinanceSafeguardDecision(allowed=False, reason=f"order rate in window ({len(self._order_timestamps)}) >= {limit}", category="order_rate_limit_hit", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="order_rate", metadata={})

    def check_heartbeat(self) -> BinanceSafeguardDecision:
        timeout = float(getattr(self._config, "binance_heartbeat_timeout_seconds", 60.0))
        now = self._clock()
        if self._last_heartbeat is None:
            return BinanceSafeguardDecision(allowed=False, reason="no heartbeat received", category="heartbeat_stale", metadata={})
        if now - self._last_heartbeat > timeout:
            return BinanceSafeguardDecision(allowed=False, reason="heartbeat stale", category="heartbeat_stale", metadata={})
        return BinanceSafeguardDecision(allowed=True, reason="ok", category="heartbeat", metadata={})

    def get_state(self) -> BinanceSafeguardState:
        now = self._clock()
        key = _utc_day_key(now, getattr(self._config, "binance_reset_hour_utc", 0))
        if key != self._utc_day_key:
            self._utc_day_key = key
            self._daily_loss = 0.0
        self._trim_order_window()
        timeout = float(getattr(self._config, "binance_heartbeat_timeout_seconds", 60.0))
        stale = self._last_heartbeat is None or (now - self._last_heartbeat > timeout)
        return BinanceSafeguardState(
            kill_switch_active=self._kill_switch,
            venue_enabled=self._venue_enabled,
            daily_loss_so_far=self._daily_loss,
            utc_day_key=key,
            orders_in_window=len(self._order_timestamps),
            last_heartbeat_ts=self._last_heartbeat,
            heartbeat_stale=stale,
            metadata={},
        )

    def assert_can_send_live(
        self,
        leverage: int = 1,
        position_size: float = 0.0,
        notional: float = 0.0,
        open_positions_count: int = 0,
    ) -> None:
        """Fail closed: raise BinanceSafeguardError if any check fails."""
        d = self.check_venue_enabled()
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_kill_switch()
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_leverage(leverage)
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_max_daily_loss()
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_max_position_size(position_size)
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_max_notional_per_order(notional)
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_max_open_positions(open_positions_count)
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_order_rate_limit()
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
        d = self.check_heartbeat()
        if not d.allowed:
            raise BinanceSafeguardError(d.reason)
