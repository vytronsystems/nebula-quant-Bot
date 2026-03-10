# NEBULA-QUANT v1 | nq_walkforward splitter — placeholder windows

from typing import Any

from nq_walkforward.models import WalkForwardConfig
from nq_walkforward.config import DEFAULT_TRAIN_WINDOWS, DEFAULT_TEST_WINDOWS


def build_windows(
    start_ts: float = 0.0,
    end_ts: float = 0.0,
    symbol: str = "QQQ",
    timeframe: str = "1d",
    num_train: int | None = None,
    num_test: int | None = None,
    **kwargs: Any,
) -> list[WalkForwardConfig]:
    """
    Skeleton: build walk-forward window configs.
    Returns safe placeholder windows; does not crash on empty/default input.
    """
    _ = kwargs
    n_train = num_train if num_train is not None else DEFAULT_TRAIN_WINDOWS
    n_test = num_test if num_test is not None else DEFAULT_TEST_WINDOWS
    if n_train < 1:
        n_train = 1
    if n_test < 1:
        n_test = 1
    windows: list[WalkForwardConfig] = []
    for i in range(max(1, n_train)):
        w = WalkForwardConfig(
            train_start_ts=start_ts,
            train_end_ts=end_ts if end_ts > start_ts else start_ts + 1.0,
            test_start_ts=end_ts if end_ts > start_ts else start_ts + 1.0,
            test_end_ts=end_ts + 1.0 if end_ts > start_ts else start_ts + 2.0,
            symbol=symbol,
            timeframe=timeframe,
            window_id=f"wf_{i}",
            metadata={"skeleton": True},
        )
        windows.append(w)
        if len(windows) >= n_test:
            break
    return windows if windows else [
        WalkForwardConfig(
            train_start_ts=0.0,
            train_end_ts=1.0,
            test_start_ts=1.0,
            test_end_ts=2.0,
            symbol=symbol,
            timeframe=timeframe,
            window_id="wf_0",
            metadata={"skeleton": True},
        ),
    ]
