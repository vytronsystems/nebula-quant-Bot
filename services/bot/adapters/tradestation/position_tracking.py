# NEBULA-QUANT v1 | Phase 88 — TradeStation position tracking
# Fetch positions from TradeStation. Stub until API wired.

from __future__ import annotations

from adapters.tradestation.models import TSPosition


def get_positions(account_id: str | None = None) -> list[TSPosition]:
    """Fetch open positions. Stub: returns empty list until TS API wired."""
    return []
