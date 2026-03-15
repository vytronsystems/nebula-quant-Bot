"""
Binance Futures Testnet configuration from environment.
No secrets in code. Fail-closed: if BINANCE_TESTNET is not true, live is never used.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

VenueConnectionStatus = Literal["CONNECTED", "DEGRADED", "NOT_CONFIGURED", "ERROR"]


@dataclass(frozen=True)
class BinanceTestnetConfig:
    """Env-based config for Binance Futures Testnet only."""

    api_key: str
    api_secret: str
    testnet: bool
    rest_base_url: str
    ws_base_url: str

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret and self.testnet)

    def connection_status(self) -> VenueConnectionStatus:
        if not self.testnet:
            return "NOT_CONFIGURED"
        if not self.api_key or not self.api_secret:
            return "NOT_CONFIGURED"
        return "CONNECTED"  # Actual status updated by client after ping


def get_binance_testnet_config() -> BinanceTestnetConfig:
    """Read config from environment. Never uses live endpoints."""
    testnet = os.getenv("BINANCE_TESTNET", "").strip().lower() in ("true", "1", "yes")
    rest = (
        os.getenv("BINANCE_FUTURES_TESTNET_BASE_URL", "").strip()
        or "https://testnet.binancefuture.com"
    )
    ws = (
        os.getenv("BINANCE_FUTURES_TESTNET_WS_URL", "").strip()
        or "wss://stream.binancefuture.com"
    )
    return BinanceTestnetConfig(
        api_key=os.getenv("BINANCE_API_KEY", "").strip(),
        api_secret=os.getenv("BINANCE_API_SECRET", "").strip(),
        testnet=testnet,
        rest_base_url=rest.rstrip("/"),
        ws_base_url=ws.rstrip("/"),
    )
