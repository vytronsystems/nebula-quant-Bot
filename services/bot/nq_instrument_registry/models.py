"""DTOs for instrument registry and activation log (API and UI contracts)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class InstrumentRecord:
    """Single instrument in the registry (Binance pair or TradeStation underlying)."""
    venue: str
    symbol: str
    asset_type: str
    active: bool
    created_at: datetime
    updated_at: datetime
    meta: dict[str, Any] | None = None

    def to_api(self) -> dict[str, Any]:
        return {
            "venue": self.venue,
            "symbol": self.symbol,
            "asset_type": self.asset_type,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "meta": self.meta,
        }


@dataclass
class ActivationLogEntry:
    """One activation/deactivation event (audit trail)."""
    venue: str
    symbol: str
    action: str
    created_at: datetime
    meta: dict[str, Any] | None = None

    def to_api(self) -> dict[str, Any]:
        return {
            "venue": self.venue,
            "symbol": self.symbol,
            "action": self.action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "meta": self.meta,
        }
