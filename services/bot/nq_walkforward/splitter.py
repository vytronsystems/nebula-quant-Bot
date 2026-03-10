# NEBULA-QUANT v1 | nq_walkforward splitter — sequential train/test windows

from __future__ import annotations

from typing import Any, Sequence

from nq_walkforward.config import DEFAULT_TEST_WINDOWS, DEFAULT_TRAIN_WINDOWS
from nq_walkforward.models import WalkForwardConfig


def _bar_ts(bar: Any) -> float:
    """Numeric timestamp for bar (seconds)."""
    if isinstance(bar, dict):
        ts = bar.get("ts")
    else:
        ts = getattr(bar, "ts", None)
    if ts is None:
        return 0.0
    if hasattr(ts, "timestamp"):
        return float(ts.timestamp())
    return float(ts)


def build_windows(
    bars: Sequence[Any],
    train_size: int | None = None,
    test_size: int | None = None,
    symbol: str = "QQQ",
    timeframe: str = "1d",
) -> list[tuple[WalkForwardConfig, list[Any], list[Any]]]:
    """
    Build sequential non-overlapping train/test windows over an ordered dataset.

    Each window has train_size bars for training and test_size bars for test.
    Advances by (train_size + test_size) per window. Skips invalid windows
    (incomplete train or test). Returns empty list if dataset is too small.
    """
    n_train = train_size if train_size is not None else DEFAULT_TRAIN_WINDOWS
    n_test = test_size if test_size is not None else DEFAULT_TEST_WINDOWS
    if n_train < 1:
        n_train = 1
    if n_test < 1:
        n_test = 1

    bar_list = list(bars)
    window_len = n_train + n_test
    if len(bar_list) < window_len:
        return []

    out: list[tuple[WalkForwardConfig, list[Any], list[Any]]] = []
    k = 0
    i = 0
    while i + window_len <= len(bar_list):
        train_bars = bar_list[i : i + n_train]
        test_bars = bar_list[i + n_train : i + window_len]
        if len(train_bars) < n_train or len(test_bars) < n_test:
            i += window_len
            continue

        train_start_ts = _bar_ts(train_bars[0])
        train_end_ts = _bar_ts(train_bars[-1])
        test_start_ts = _bar_ts(test_bars[0])
        test_end_ts = _bar_ts(test_bars[-1])

        config = WalkForwardConfig(
            train_start_ts=train_start_ts,
            train_end_ts=train_end_ts,
            test_start_ts=test_start_ts,
            test_end_ts=test_end_ts,
            symbol=symbol,
            timeframe=timeframe,
            window_id=f"wf_{k}",
            metadata={},
        )
        out.append((config, train_bars, test_bars))
        k += 1
        i += window_len

    return out
