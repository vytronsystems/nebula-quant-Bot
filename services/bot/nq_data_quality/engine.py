# NEBULA-QUANT v1 | nq_data_quality engine

from typing import Any

from nq_data_quality.models import DataQualityIssue, DataQualityResult
from nq_data_quality.checks import (
    check_missing_candles,
    check_duplicate_candles,
    check_timestamp_gaps,
    check_negative_prices,
    check_ohlc_integrity,
    check_volume_anomalies,
)


class DataQualityEngine:
    """
    Data validation and integrity layer. Validates datasets before they enter
    backtest, walk-forward, paper, or live. Does not modify data; produces validation signals only.
    """

    def __init__(self) -> None:
        pass

    def validate_dataset(
        self,
        data: list[Any] | None = None,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> DataQualityResult:
        """Run all checks, aggregate issues, return DataQualityResult. Empty dataset returns valid=True, zero issues."""
        data = data if data is not None else []
        symbol = symbol or ""
        timeframe = timeframe or ""

        if not data:
            return DataQualityResult(
                valid=True,
                issues=[],
                issue_count=0,
                symbol=symbol,
                timeframe=timeframe,
                metadata={"empty": True},
            )

        all_issues: list[DataQualityIssue] = []
        all_issues.extend(check_missing_candles(data))
        all_issues.extend(check_duplicate_candles(data))
        all_issues.extend(check_timestamp_gaps(data))
        all_issues.extend(check_negative_prices(data))
        all_issues.extend(check_ohlc_integrity(data))
        all_issues.extend(check_volume_anomalies(data))

        return DataQualityResult(
            valid=len(all_issues) == 0,
            issues=all_issues,
            issue_count=len(all_issues),
            symbol=symbol,
            timeframe=timeframe,
            metadata={"skeleton": True},
        )
