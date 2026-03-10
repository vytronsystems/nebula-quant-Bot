# NEBULA-QUANT v1 | nq_data_quality checks (placeholder implementations)

from typing import Any

from nq_data_quality.models import DataQualityIssue


def check_missing_candles(data: list[Any] | None) -> list[DataQualityIssue]:
    """Placeholder: detect missing candles. Skeleton returns empty list."""
    return []


def check_duplicate_candles(data: list[Any] | None) -> list[DataQualityIssue]:
    """Placeholder: detect duplicate candles. Skeleton returns empty list."""
    return []


def check_timestamp_gaps(data: list[Any] | None) -> list[DataQualityIssue]:
    """Placeholder: detect timestamp gaps. Skeleton returns empty list."""
    return []


def check_negative_prices(data: list[Any] | None) -> list[DataQualityIssue]:
    """Placeholder: detect negative prices. Skeleton returns empty list."""
    return []


def check_ohlc_integrity(data: list[Any] | None) -> list[DataQualityIssue]:
    """Placeholder: detect inconsistent OHLC (e.g. O>H, L>C). Skeleton returns empty list."""
    return []


def check_volume_anomalies(data: list[Any] | None) -> list[DataQualityIssue]:
    """Placeholder: detect zero/abnormal volume. Skeleton returns empty list."""
    return []
