from __future__ import annotations

from typing import Any

from adapters.binance.mapper import map_account_payload_to_state
from adapters.binance.models import BinanceAccountState
from adapters.binance.validation import validate_account_payload


class BinanceAccountAdapter:
    """
    Architecture-level account adapter for Binance USDT-M Futures.

    In Phase 51 this adapter exposes normalization helpers for account,
    balances, and positions based on Binance-like payloads.
    """

    def __init__(self) -> None:
        pass

    def normalize_account_state(self, payload: dict[str, Any]) -> BinanceAccountState:
        validate_account_payload(payload)
        return map_account_payload_to_state(payload)

    def normalize_positions(self, payload: dict[str, Any]) -> list[BinanceAccountState.__annotations__["positions"][0]]:  # type: ignore[index]
        state = self.normalize_account_state(payload)
        return state.positions

    def normalize_balances(self, payload: dict[str, Any]) -> list[BinanceAccountState.__annotations__["balances"][0]]:  # type: ignore[index]
        state = self.normalize_account_state(payload)
        return state.balances

