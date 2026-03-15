"""
Binance Futures Testnet REST client.
Uses testnet only when BINANCE_TESTNET=true. Fail-closed on missing creds or errors.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any

from adapters.binance.testnet_config import BinanceTestnetConfig, VenueConnectionStatus, get_binance_testnet_config
from adapters.binance.models import BinanceAdapterError


class BinanceTestnetClientError(BinanceAdapterError):
    """Raised when Testnet client fails (config, network, or response)."""
    def __init__(self, message: str, status: VenueConnectionStatus = "ERROR") -> None:
        super().__init__(message)
        self.status = status


def _sign(secret: str, query: str) -> str:
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()


def _get(
    base_url: str,
    path: str,
    params: dict[str, str] | None = None,
    api_key: str | None = None,
    api_secret: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any] | list[Any]:
    import requests
    params = dict(params or {})
    if api_key and api_secret:
        params["timestamp"] = str(int(time.time() * 1000))
    qs = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    url = f"{base_url}{path}?{qs}" if qs else f"{base_url}{path}"
    if api_key and api_secret:
        sig = _sign(api_secret, qs)
        url = f"{url}&signature={sig}"
    headers = {"X-MBX-APIKEY": api_key} if api_key else {}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        status = "DEGRADED" if e.response.status_code in (401, 403) else "ERROR"
        raise BinanceTestnetClientError(f"HTTP {e.response.status_code}: {e.response.text[:200]}", status=status) from e
    except requests.exceptions.RequestException as e:
        raise BinanceTestnetClientError(f"Request failed: {e}", status="ERROR") from e


class BinanceTestnetClient:
    """
    Binance Futures Testnet REST client.
    Only uses testnet base URL. No order submission (read-only for Phase 71).
    """

    def __init__(self, config: BinanceTestnetConfig | None = None) -> None:
        self._config = config or get_binance_testnet_config()
        if not self._config.testnet:
            raise BinanceTestnetClientError(
                "BINANCE_TESTNET must be true; live Binance is forbidden.",
                status="NOT_CONFIGURED",
            )
        if not self._config.is_configured:
            raise BinanceTestnetClientError(
                "BINANCE_API_KEY and BINANCE_API_SECRET required for Testnet.",
                status="NOT_CONFIGURED",
            )

    @property
    def connection_status(self) -> VenueConnectionStatus:
        return self._config.connection_status()

    def ping(self) -> dict[str, Any]:
        """GET /fapi/v1/ping — public."""
        return _get(self._config.rest_base_url, "/fapi/v1/ping", timeout=5.0)

    def get_account(self) -> dict[str, Any]:
        """GET /fapi/v2/account — signed. Wallet balance, positions."""
        return _get(
            self._config.rest_base_url,
            "/fapi/v2/account",
            api_key=self._config.api_key,
            api_secret=self._config.api_secret,
        )

    def get_ticker_price(self, symbol: str = "BTCUSDT") -> dict[str, Any]:
        """GET /fapi/v1/ticker/price — public."""
        return _get(
            self._config.rest_base_url,
            "/fapi/v1/ticker/price",
            params={"symbol": symbol},
        )

    def get_order_book(self, symbol: str = "BTCUSDT", limit: int = 10) -> dict[str, Any]:
        """GET /fapi/v1/depth — public."""
        return _get(
            self._config.rest_base_url,
            "/fapi/v1/depth",
            params={"symbol": symbol, "limit": str(limit)},
        )

    def get_recent_trades(self, symbol: str = "BTCUSDT", limit: int = 10) -> list[dict[str, Any]]:
        """GET /fapi/v1/trades — public."""
        out = _get(
            self._config.rest_base_url,
            "/fapi/v1/trades",
            params={"symbol": symbol, "limit": str(limit)},
        )
        return out if isinstance(out, list) else []

    def get_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "5m",
        limit: int = 100,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[list[Any]]:
        """GET /fapi/v1/klines — public. Returns list of [open_time, open, high, low, close, volume, ...]."""
        params: dict[str, str] = {"symbol": symbol, "interval": interval, "limit": str(min(limit, 1500))}
        if start_time is not None:
            params["startTime"] = str(start_time)
        if end_time is not None:
            params["endTime"] = str(end_time)
        out = _get(self._config.rest_base_url, "/fapi/v1/klines", params=params)
        return out if isinstance(out, list) else []

    def get_open_orders(self, symbol: str = "BTCUSDT") -> list[dict[str, Any]]:
        """GET /fapi/v1/openOrders — signed."""
        out = _get(
            self._config.rest_base_url,
            "/fapi/v1/openOrders",
            params={"symbol": symbol},
            api_key=self._config.api_key,
            api_secret=self._config.api_secret,
        )
        return out if isinstance(out, list) else []

    def get_position_risk(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """GET /fapi/v2/positionRisk — signed. Optional symbol filter."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        out = _get(
            self._config.rest_base_url,
            "/fapi/v2/positionRisk",
            params=params or {},
            api_key=self._config.api_key,
            api_secret=self._config.api_secret,
        )
        return out if isinstance(out, list) else []


def get_venue_status_safe() -> tuple[VenueConnectionStatus, str]:
    """
    Safe venue status for UI. Never raises.
    Returns (status, message).
    """
    try:
        cfg = get_binance_testnet_config()
        if not cfg.testnet:
            return "NOT_CONFIGURED", "BINANCE_TESTNET is not true"
        if not cfg.api_key or not cfg.api_secret:
            return "NOT_CONFIGURED", "BINANCE_API_KEY or BINANCE_API_SECRET missing"
        client = BinanceTestnetClient(cfg)
        client.ping()
        return "CONNECTED", "Testnet OK"
    except BinanceTestnetClientError as e:
        return e.status, str(e)
    except Exception as e:
        return "ERROR", str(e)
