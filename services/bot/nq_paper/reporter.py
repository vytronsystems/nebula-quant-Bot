# NEBULA-QUANT v1 | nq_paper reporter — summary for weekly audit / dashboards

from __future__ import annotations

from typing import Any

from nq_paper.models import PaperSessionResult


def build_paper_summary(result: PaperSessionResult) -> dict[str, Any]:
    """
    Build a dictionary of paper trading summary for weekly audit,
    dashboards, and promotion decisions toward live trading.
    """
    summary = result.summary
    closed_count = len(result.trades)
    return {
        "session_id": result.session_id,
        "started_ts": result.started_ts,
        "ended_ts": result.ended_ts,
        "cash": result.account_state.cash,
        "equity": result.account_state.equity,
        "total_trades": summary.get("total_trades", closed_count),
        "closed_trades": closed_count,
        "open_positions": len(result.positions),
        "net_pnl": summary.get("net_pnl", 0.0),
        "win_rate": summary.get("win_rate", 0.0),
        "max_drawdown": summary.get("max_drawdown", 0.0),
        "summary": summary,
        "metadata": result.metadata,
    }
