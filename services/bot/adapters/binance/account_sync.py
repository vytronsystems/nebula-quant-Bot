"""
Binance account snapshot persistence and venue state history.

Transport boundary: callers provide raw account payload (from REST or stub);
this module normalizes via BinanceAccountAdapter and persists to venue_account_snapshot.
No live REST calls here (no unsafe live routing).

Integration point: a future "account state fetcher" (e.g. REST client) should:
  1. Fetch raw payload from Binance /fapi/v2/account (when live-ready and approved).
  2. Call save_snapshot_from_payload(venue="binance", account_id=..., payload).
This layer does not perform step 1.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from adapters.binance.account import BinanceAccountAdapter
from adapters.binance.models import BinanceAccountState


def _dsn() -> str:
    return os.getenv("PG_DSN", "postgresql://nebula:nebula123@localhost:5432/trading")


def _balance_equity_from_state(state: BinanceAccountState) -> tuple[float, float]:
    """Derive single balance (USDT wallet) and equity (balance + unrealized PnL) from state."""
    balance = 0.0
    for b in state.balances:
        if b.asset == "USDT":
            balance = b.balance
            break
    unrealized = sum(p.unrealized_pnl for p in state.positions)
    equity = balance + unrealized
    return balance, equity


@dataclass
class VenueAccountSnapshotRecord:
    """One row from venue_account_snapshot."""
    venue: str
    account_id: str | None
    balance: float | None
    equity: float | None
    created_at: datetime
    meta: dict[str, Any] | None


class BinanceAccountSyncService:
    """
    Persist Binance account state to venue_account_snapshot and read history.
    Transport boundary: accepts raw payload; normalizes and persists. No live fetch.
    """

    def __init__(self) -> None:
        self._adapter = BinanceAccountAdapter()

    def save_snapshot_from_payload(
        self,
        venue: str,
        account_id: str | None,
        payload: dict[str, Any],
    ) -> VenueAccountSnapshotRecord:
        """Normalize payload to BinanceAccountState, compute balance/equity, persist."""
        state = self._adapter.normalize_account_state(payload)
        return self.save_snapshot_from_state(venue, account_id, state)

    def save_snapshot_from_state(
        self,
        venue: str,
        account_id: str | None,
        state: BinanceAccountState,
    ) -> VenueAccountSnapshotRecord:
        """Persist normalized state to venue_account_snapshot."""
        import psycopg
        balance, equity = _balance_equity_from_state(state)
        meta = {
            "balances_count": len(state.balances),
            "positions_count": len(state.positions),
            "positions": [
                {"symbol": p.symbol, "position_amt": p.position_amt, "unrealized_pnl": p.unrealized_pnl}
                for p in state.positions
            ],
        }
        with psycopg.connect(_dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO venue_account_snapshot (venue, account_id, balance, equity, meta)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (venue, account_id, balance, equity, json.dumps(meta)),
                )
            conn.commit()
        return self.get_latest_snapshot(venue) or VenueAccountSnapshotRecord(
            venue=venue, account_id=account_id, balance=balance, equity=equity, created_at=datetime.utcnow(), meta=meta
        )

    def get_latest_snapshot(self, venue: str) -> VenueAccountSnapshotRecord | None:
        """Return latest snapshot for venue."""
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT venue, account_id, balance, equity, created_at, meta
                    FROM venue_account_snapshot
                    WHERE venue = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (venue,),
                )
                r = cur.fetchone()
        if not r:
            return None
        meta = r["meta"]
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except Exception:
                meta = {}
        return VenueAccountSnapshotRecord(
            venue=r["venue"],
            account_id=r["account_id"],
            balance=float(r["balance"]) if r["balance"] is not None else None,
            equity=float(r["equity"]) if r["equity"] is not None else None,
            created_at=r["created_at"],
            meta=meta,
        )

    def get_snapshot_history(self, venue: str, limit: int = 100) -> list[VenueAccountSnapshotRecord]:
        """Return recent snapshots for venue (newest first)."""
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT venue, account_id, balance, equity, created_at, meta
                    FROM venue_account_snapshot
                    WHERE venue = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (venue, limit),
                )
                rows = cur.fetchall()
        out = []
        for r in rows:
            meta = r["meta"]
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except Exception:
                    meta = {}
            out.append(
                VenueAccountSnapshotRecord(
                    venue=r["venue"],
                    account_id=r["account_id"],
                    balance=float(r["balance"]) if r["balance"] is not None else None,
                    equity=float(r["equity"]) if r["equity"] is not None else None,
                    created_at=r["created_at"],
                    meta=meta,
                )
            )
        return out
