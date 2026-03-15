# NEBULA-QUANT v1 | Phase 88 — TradeStation contract lookup
# Look up option contracts by underlying, expiry, strike, right.

from __future__ import annotations

from adapters.tradestation.models import TSOptionContract


def lookup_contracts(
    underlying: str,
    expiry: str | None = None,
    strike: float | None = None,
    right: str | None = None,
) -> list[TSOptionContract]:
    """Look up option contracts. Stub: returns empty list until TS API wired."""
    return []
