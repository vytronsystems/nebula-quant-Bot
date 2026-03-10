# NEBULA-QUANT v1 | nq_paper reporter — summary for weekly audit / dashboards

from typing import Any

from nq_paper.models import PaperSessionResult


def build_paper_summary(result: PaperSessionResult) -> dict[str, Any]:
    """
    Build a dictionary of paper trading summary statistics for weekly audit,
    dashboards, and promotion decisions toward live trading.
    """
    return {
        "session_id": result.session_id,
        "started_ts": result.started_ts,
        "ended_ts": result.ended_ts,
        "total_trades": len(result.trades),
        "open_positions": len(result.positions),
        "cash": result.account_state.cash,
        "equity": result.account_state.equity,
        "summary": result.summary,
        "metadata": result.metadata,
    }
