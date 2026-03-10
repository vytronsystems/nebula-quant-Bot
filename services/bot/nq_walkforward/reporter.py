# NEBULA-QUANT v1 | nq_walkforward reporter — summary for gates/dashboards

from __future__ import annotations

from typing import Any

from nq_walkforward.models import WalkForwardResult, WalkForwardWindowResult


def _window_to_summary(w: WalkForwardWindowResult) -> dict[str, Any]:
    """Single window summary for governance review."""
    return {
        "window_id": w.config.window_id,
        "passed": w.passed,
        "train_net_pnl": w.train_summary.get("net_pnl", 0.0),
        "test_net_pnl": w.test_summary.get("net_pnl", 0.0),
        "test_drawdown": w.test_summary.get("max_drawdown", 0.0),
        "test_total_trades": w.test_summary.get("total_trades", 0),
        "notes": w.notes,
    }


def build_walkforward_summary(result: WalkForwardResult) -> dict[str, Any]:
    """
    Build a dictionary of walk-forward summary for research reviews,
    strategy approval gates, and dashboards.
    """
    return {
        "total_windows": result.total_windows,
        "passed_windows": result.passed_windows,
        "failed_windows": result.failed_windows,
        "pass_rate": result.pass_rate,
        "windows": [_window_to_summary(w) for w in result.windows],
        "metadata": result.metadata,
    }
