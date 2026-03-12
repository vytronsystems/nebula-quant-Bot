from __future__ import annotations

from typing import Any

from adapters.binance.models import BinanceKline, BinanceOrderBookSnapshot, BinanceTicker, BinanceAdapterError


def normalize_kline(symbol: str, raw: list[Any]) -> BinanceKline:
    """
    Normalize a Binance kline array into BinanceKline.

    Expected raw format (subset of Binance kline stream /klines):
    [
      openTime, open, high, low, close, volume,
      closeTime, quoteAssetVolume, numberOfTrades, ...
    ]
    """
    try:
        open_time = int(raw[0])
        open_price = float(raw[1])
        high = float(raw[2])
        low = float(raw[3])
        close = float(raw[4])
        volume = float(raw[5])
        close_time = int(raw[6])
        trades = int(raw[8])
        return BinanceKline(
            symbol=symbol,
            interval="",  # interval can be attached by caller if needed
            open_time=open_time,
            close_time=close_time,
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume,
            trades=trades,
            metadata={},
        )
    except Exception as exc:  # noqa: BLE001
        raise BinanceAdapterError(f"failed to normalize kline: {exc}") from exc


def normalize_ticker(raw: dict[str, Any]) -> BinanceTicker:
    """Normalize a Binance 24hr ticker payload."""
    try:
        return BinanceTicker(
            symbol=str(raw["symbol"]),
            last_price=float(raw.get("lastPrice", 0) or 0),
            price_change_percent=float(raw.get("priceChangePercent", 0) or 0),
            volume=float(raw.get("volume", 0) or 0),
            metadata={},
        )
    except Exception as exc:  # noqa: BLE001
        raise BinanceAdapterError(f"failed to normalize ticker: {exc}") from exc


def normalize_order_book(raw: dict[str, Any]) -> BinanceOrderBookSnapshot:
    """Normalize a Binance order book snapshot payload (/depth)."""
    try:
        symbol = str(raw.get("symbol", ""))
        last_update_id = int(raw.get("lastUpdateId", 0) or 0)
        bids = [(float(p), float(q)) for p, q in raw.get("bids", [])]
        asks = [(float(p), float(q)) for p, q in raw.get("asks", [])]
        return BinanceOrderBookSnapshot(
            symbol=symbol,
            last_update_id=last_update_id,
            bids=bids,
            asks=asks,
            metadata={},
        )
    except Exception as exc:  # noqa: BLE001
        raise BinanceAdapterError(f"failed to normalize order book: {exc}") from exc

