# NEBULA-QUANT v1 | nq_data_quality reporter

from typing import Any

from nq_data_quality.models import DataQualityResult


def build_data_quality_report(result: DataQualityResult) -> dict[str, Any]:
    """Build dictionary for dashboards and logging. Skeleton only."""
    return {
        "valid": result.valid,
        "issue_count": result.issue_count,
        "symbol": result.symbol,
        "timeframe": result.timeframe,
        "issues": [
            {
                "issue_type": i.issue_type,
                "severity": i.severity,
                "timestamp": i.timestamp,
                "description": i.description,
                "symbol": i.symbol,
            }
            for i in result.issues
        ],
        "metadata": result.metadata,
    }
