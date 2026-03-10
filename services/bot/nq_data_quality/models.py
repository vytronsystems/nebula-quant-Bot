# NEBULA-QUANT v1 | nq_data_quality models

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DataQualityIssue:
    """Single data quality finding (skeleton)."""

    issue_type: str
    severity: str
    timestamp: float
    description: str
    symbol: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DataQualityResult:
    """Aggregate validation result (skeleton)."""

    valid: bool
    issues: list[DataQualityIssue]
    issue_count: int
    symbol: str
    timeframe: str
    metadata: dict[str, Any] = field(default_factory=dict)
