# NEBULA-QUANT v1 | nq_data normalization (stub)
# Raw provider output → canonical Bar.

from nq_data.models.ohlcv import Bar
from nq_data.providers.base import RawBar
from nq_data.exceptions import NormalizationError


def raw_to_bar(raw: RawBar, symbol: str, timeframe: str, source: str) -> Bar:
    """Convert one raw bar to canonical Bar. Stub: raises unless raw is already Bar-like."""
    raise NormalizationError(
        "normalize.raw_to_bar is a stub; real implementation in a later iteration"
    )
