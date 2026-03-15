"""Phase 71 — Binance Testnet config and client tests (degraded mode, no live)."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from adapters.binance.testnet_config import (
    BinanceTestnetConfig,
    get_binance_testnet_config,
    VenueConnectionStatus,
)
from adapters.binance.testnet_client import (
    BinanceTestnetClient,
    BinanceTestnetClientError,
    get_venue_status_safe,
)


class TestBinanceTestnetConfig(unittest.TestCase):
    def test_testnet_false_not_configured(self) -> None:
        cfg = BinanceTestnetConfig(
            api_key="key",
            api_secret="secret",
            testnet=False,
            rest_base_url="https://testnet.binancefuture.com",
            ws_base_url="wss://stream.binancefuture.com",
        )
        self.assertFalse(cfg.is_configured)
        self.assertEqual(cfg.connection_status(), "NOT_CONFIGURED")

    def test_missing_creds_not_configured(self) -> None:
        cfg = BinanceTestnetConfig(
            api_key="",
            api_secret="secret",
            testnet=True,
            rest_base_url="https://testnet.binancefuture.com",
            ws_base_url="wss://stream.binancefuture.com",
        )
        self.assertFalse(cfg.is_configured)

    def test_env_testnet_url_default(self) -> None:
        with patch.dict(os.environ, {"BINANCE_TESTNET": "true", "BINANCE_API_KEY": "k", "BINANCE_API_SECRET": "s"}, clear=False):
            cfg = get_binance_testnet_config()
            self.assertTrue(cfg.testnet)
            self.assertIn("testnet", cfg.rest_base_url.lower() or "testnet")


class TestGetVenueStatusSafe(unittest.TestCase):
    def test_not_configured_when_testnet_false(self) -> None:
        with patch.dict(os.environ, {"BINANCE_TESTNET": "false"}, clear=False):
            status, msg = get_venue_status_safe()
            self.assertEqual(status, "NOT_CONFIGURED")
            self.assertIn("BINANCE_TESTNET", msg)

    def test_not_configured_when_creds_missing(self) -> None:
        with patch.dict(os.environ, {"BINANCE_TESTNET": "true", "BINANCE_API_KEY": "", "BINANCE_API_SECRET": ""}, clear=False):
            status, msg = get_venue_status_safe()
            self.assertEqual(status, "NOT_CONFIGURED")


class TestBinanceTestnetClientFailsClosed(unittest.TestCase):
    def test_raises_when_testnet_false(self) -> None:
        cfg = BinanceTestnetConfig(
            api_key="k",
            api_secret="s",
            testnet=False,
            rest_base_url="https://testnet.binancefuture.com",
            ws_base_url="wss://x",
        )
        with self.assertRaises(BinanceTestnetClientError) as ctx:
            BinanceTestnetClient(cfg)
        self.assertEqual(ctx.exception.status, "NOT_CONFIGURED")

    def test_raises_when_creds_missing(self) -> None:
        cfg = BinanceTestnetConfig(
            api_key="",
            api_secret="s",
            testnet=True,
            rest_base_url="https://testnet.binancefuture.com",
            ws_base_url="wss://x",
        )
        with self.assertRaises(BinanceTestnetClientError):
            BinanceTestnetClient(cfg)
