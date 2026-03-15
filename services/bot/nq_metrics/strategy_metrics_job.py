# NEBULA-QUANT v1 | Phase 74 — Compute strategy metrics from trades and persist to strategy_metrics

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from nq_metrics.engine import MetricsEngine
from nq_metrics.models import TradePerformance


def _dsn() -> str:
    return os.getenv("PG_DSN", "postgresql://nebula:nebula123@localhost:5432/trading")


def _row_to_trade_performance(row: dict[str, Any]) -> TradePerformance:
    """Map DB trade row to TradePerformance. Safe defaults for nulls."""
    opened = row.get("opened_at")
    closed = row.get("closed_at")
    holding_sec = 0.0
    if opened and closed:
        if hasattr(opened, "timestamp"):
            t0 = opened.timestamp()
        else:
            t0 = 0.0
        if hasattr(closed, "timestamp"):
            t1 = closed.timestamp()
        else:
            t1 = 0.0
        holding_sec = max(0.0, t1 - t0)
    entry = float(row.get("entry_price") or 0)
    exit_p = float(row.get("exit_price") or 0)
    qty = float(row.get("qty") or 0)
    pnl = float(row.get("pnl_usd") or 0)
    pnl_pct = (pnl / (entry * qty) * 100.0) if entry and qty else 0.0
    return TradePerformance(
        trade_id=str(row.get("id", "")),
        symbol=str(row.get("symbol", "")),
        entry_price=entry,
        exit_price=exit_p,
        qty=qty,
        pnl=pnl,
        pnl_pct=pnl_pct,
        holding_time=holding_sec,
        metadata={},
    )


def compute_and_persist_strategy_metrics() -> int:
    """
    For each row in strategy_deployment, load trades for that instrument (symbol),
    compute WinRate, PnL, Trades, Days, Profit Factor, Max Drawdown via MetricsEngine,
    then upsert into strategy_metrics. Returns number of deployments updated.
    """
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError:
        return 0

    dsn = _dsn()
    engine = MetricsEngine()
    updated = 0

    with psycopg.connect(dsn, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, instrument FROM strategy_deployment WHERE enabled = true"
            )
            deployments = cur.fetchall()

        for dep in deployments:
            deployment_id = dep["id"]
            instrument = dep.get("instrument") or ""

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, symbol, entry_price, exit_price, qty, pnl_usd, opened_at, closed_at FROM trades WHERE symbol = %s ORDER BY opened_at",
                    (instrument,),
                )
                rows = cur.fetchall()

            trades = [_row_to_trade_performance(dict(r)) for r in rows]
            result = engine.compute_metrics(trades=trades, initial_equity=0.0)

            days_count = 0
            if rows:
                seen = set()
                for r in rows:
                    opened = r.get("opened_at")
                    if opened:
                        d = opened.date() if hasattr(opened, "date") else opened
                        seen.add(str(d))
                days_count = len(seen)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO strategy_metrics (
                        id, deployment_id, computed_at, win_rate, pnl, trades_count, days_count,
                        profit_factor, max_drawdown, meta
                    ) VALUES (
                        gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (deployment_id) DO UPDATE SET
                        computed_at = EXCLUDED.computed_at,
                        win_rate = EXCLUDED.win_rate,
                        pnl = EXCLUDED.pnl,
                        trades_count = EXCLUDED.trades_count,
                        days_count = EXCLUDED.days_count,
                        profit_factor = EXCLUDED.profit_factor,
                        max_drawdown = EXCLUDED.max_drawdown,
                        meta = EXCLUDED.meta
                    """,
                    (
                        deployment_id,
                        datetime.now(timezone.utc),
                        float(result.win_rate),
                        float(sum(t.pnl for t in trades)),
                        result.total_trades,
                        days_count,
                        float(result.profit_factor),
                        float(result.max_drawdown),
                        None,
                    ),
                )
            updated += 1

        conn.commit()

    return updated


def run_metrics_job() -> dict[str, Any]:
    """Entry point: compute and persist; return summary."""
    try:
        n = compute_and_persist_strategy_metrics()
        return {"ok": True, "deployments_updated": n}
    except Exception as e:
        return {"ok": False, "error": str(e)}
