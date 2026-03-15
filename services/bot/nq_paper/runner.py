# NEBULA-QUANT v1 | Automatic paper runner — runs paper sessions for deployments that meet input requirements

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from nq_paper.engine import PaperEngine
from nq_paper.models import PaperTrade


def _dsn() -> str:
    return os.getenv("PG_DSN", "postgresql://nebula:nebula123@localhost:5432/trading")


def _get_paper_deployments(conn: Any) -> list[dict[str, Any]]:
    """Return list of deployments with stage=paper and enabled=true."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, strategy_name, strategy_version, instrument, venue, environment, stage, enabled, meta
            FROM strategy_deployment
            WHERE stage = 'paper' AND enabled = true
            ORDER BY instrument, strategy_name
            """
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def _is_instrument_active(conn: Any, symbol: str) -> bool:
    """True if symbol exists in instrument_registry and is active."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM instrument_registry WHERE symbol = %s AND active = true LIMIT 1",
            (symbol,),
        )
        return cur.fetchone() is not None


def _bars_from_binance_klines(symbol: str, klines: list[list[Any]]) -> list[dict[str, Any]]:
    """Convert Binance klines [open_time, open, high, low, close, volume, ...] to bar dicts with ts, close, symbol."""
    bars = []
    for k in klines:
        if len(k) < 6:
            continue
        open_time_ms = int(k[0])
        close_price = float(k[4])
        bars.append({
            "ts": datetime.fromtimestamp(open_time_ms / 1000.0, tz=timezone.utc),
            "close": close_price,
            "symbol": symbol,
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
        })
    return bars


def _get_binance_bars(symbol: str, interval: str = "5m", limit: int = 50) -> list[dict[str, Any]]:
    """Fetch klines from Binance Testnet and return bar list. Returns [] if not configured or error."""
    try:
        from adapters.binance.testnet_config import get_binance_testnet_config
        from adapters.binance.testnet_client import BinanceTestnetClient, BinanceTestnetClientError
        cfg = get_binance_testnet_config()
        if not cfg.testnet or not cfg.is_configured:
            return []
        client = BinanceTestnetClient(cfg)
        raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return _bars_from_binance_klines(symbol, raw)
    except BinanceTestnetClientError:
        return []
    except Exception:
        return []


def _run_paper_session(
    deployment_id: str,
    instrument: str,
    venue: str,
    bars: list[dict[str, Any]],
) -> list[PaperTrade]:
    """Run one paper session for the given deployment and bars. Returns list of closed trades."""
    if not bars or len(bars) < 2:
        return []
    bar_list = list(bars)
    n = len(bar_list)

    class _Strategy:
        """Minimal strategy: long at first bar, exit at last bar."""
        def __init__(self) -> None:
            self._i = 0
        def on_bar(self, bar: Any) -> str:
            i = self._i
            self._i += 1
            if i == 0:
                return "long"
            if i == n - 1:
                return "exit"
            return "hold"

    engine = PaperEngine(
        initial_capital=100_000.0,
        strategy_id=deployment_id,
        session_id=f"paper_{deployment_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}",
    )
    result = engine.run_session(bars=bar_list, strategy=_Strategy())
    return getattr(result, "trades", []) or []


def _persist_trades(conn: Any, deployment_id: str, trades: list[PaperTrade]) -> None:
    """Insert paper trades into the trades table and notify Telegram (opened + closed)."""
    for t in trades:
        opened_at = datetime.fromtimestamp(t.entry_ts, tz=timezone.utc) if t.entry_ts else datetime.now(timezone.utc)
        closed_at = datetime.fromtimestamp(t.exit_ts, tz=timezone.utc) if t.exit_ts else datetime.now(timezone.utc)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO trades (id, opened_at, closed_at, symbol, direction, qty, entry_price, exit_price, pnl_usd, meta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    opened_at,
                    closed_at,
                    t.symbol,
                    t.side,
                    int(round(t.qty)) or 1,
                    t.entry_price,
                    t.exit_price,
                    round(t.pnl, 2),
                    {"deployment_id": deployment_id, "session": "paper_runner", "strategy_id": t.strategy_id},
                ),
            )
        _notify_telegram_trade(t)
    conn.commit()


def _notify_telegram_trade(t: PaperTrade) -> None:
    """Send Telegram: trade opened (execution) and trade closed (PnL, %). Non-fatal."""
    try:
        from bot.telegram_notify import send_trade_opened, send_trade_closed
        send_trade_opened(t.symbol, t.side, t.qty, t.entry_price)
        send_trade_closed(t.symbol, t.qty, t.pnl, t.pnl_pct)
    except Exception:
        pass


def run_paper_for_deployments() -> dict[str, Any]:
    """
    Load paper deployments that meet input requirements; for each, fetch bars (Binance),
    run paper session, persist trades. Then run strategy_metrics_job.
    Requirements: deployment stage=paper, enabled=true; instrument active in registry;
    for Binance venue, bars are fetched (if not configured, deployment is skipped).
    """
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError:
        return {"ok": False, "error": "psycopg not available", "deployments_run": 0}

    dsn = _dsn()
    deployments_run = 0
    trades_persisted = 0
    errors = []

    try:
        with psycopg.connect(dsn, row_factory=dict_row) as conn:
            deployments = _get_paper_deployments(conn)
            for dep in deployments:
                dep_id = str(dep["id"])
                instrument = (dep.get("instrument") or "").strip()
                venue = (dep.get("venue") or "").strip()
                if not instrument:
                    continue
                if not _is_instrument_active(conn, instrument):
                    continue
                bars = []
                if venue.lower() == "binance":
                    bars = _get_binance_bars(instrument, interval="5m", limit=50)
                if not bars:
                    continue
                try:
                    trades = _run_paper_session(dep_id, instrument, venue, bars)
                    if trades:
                        _persist_trades(conn, dep_id, trades)
                        trades_persisted += len(trades)
                    deployments_run += 1
                except Exception as e:
                    errors.append(f"{dep_id}: {e}")
            conn.commit()

        if deployments_run > 0 and trades_persisted >= 0:
            try:
                from nq_metrics.strategy_metrics_job import run_metrics_job
                run_metrics_job()
            except Exception as e:
                errors.append(f"metrics_job: {e}")

        return {
            "ok": len(errors) == 0,
            "deployments_run": deployments_run,
            "trades_persisted": trades_persisted,
            "errors": errors if errors else None,
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "deployments_run": deployments_run, "trades_persisted": trades_persisted}
