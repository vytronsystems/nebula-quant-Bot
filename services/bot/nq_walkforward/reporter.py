# NEBULA-QUANT v1 | nq_walkforward reporter — summary for gates/dashboards

from typing import Any

from nq_walkforward.models import WalkForwardResult


def build_walkforward_summary(result: WalkForwardResult) -> dict[str, Any]:
    """
    Build a dictionary of summary statistics for research reviews,
    strategy approval gates, and dashboards.
    """
    return {
        "total_windows": result.total_windows,
        "passed_windows": result.passed_windows,
        "failed_windows": result.failed_windows,
        "pass_rate": result.pass_rate,
        "metadata": result.metadata,
    }
