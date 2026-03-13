"""Instrument registry service: CRUD and activation logging (DB)."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from nq_instrument_registry.models import ActivationLogEntry, InstrumentRecord


def _dsn() -> str:
    return os.getenv("PG_DSN", "postgresql://nebula:nebula123@localhost:5432/trading")


def _utcnow() -> datetime:
    return datetime.utcnow()


class InstrumentRegistryService:
    """Query and update instrument_registry and instrument_activation_log."""

    def list_instruments(
        self,
        venue: str | None = None,
        active_only: bool = True,
    ) -> list[InstrumentRecord]:
        rows = []
        with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                if venue:
                    if active_only:
                        cur.execute(
                            "SELECT venue, symbol, asset_type, active, created_at, updated_at, meta FROM instrument_registry WHERE venue = %s AND active = true ORDER BY symbol",
                            (venue,),
                        )
                    else:
                        cur.execute(
                            "SELECT venue, symbol, asset_type, active, created_at, updated_at, meta FROM instrument_registry WHERE venue = %s ORDER BY symbol",
                            (venue,),
                        )
                else:
                    if active_only:
                        cur.execute(
                            "SELECT venue, symbol, asset_type, active, created_at, updated_at, meta FROM instrument_registry WHERE active = true ORDER BY venue, symbol",
                        )
                    else:
                        cur.execute(
                            "SELECT venue, symbol, asset_type, active, created_at, updated_at, meta FROM instrument_registry ORDER BY venue, symbol",
                        )
                rows = cur.fetchall()
        return [
            InstrumentRecord(
                venue=r["venue"],
                symbol=r["symbol"],
                asset_type=r["asset_type"] or "spot",
                active=r["active"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                meta=r["meta"],
            )
            for r in rows
        ]

    def get_instrument(self, venue: str, symbol: str) -> InstrumentRecord | None:
        with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT venue, symbol, asset_type, active, created_at, updated_at, meta FROM instrument_registry WHERE venue = %s AND symbol = %s",
                    (venue, symbol),
                )
                r = cur.fetchone()
        if not r:
            return None
        return InstrumentRecord(
            venue=r["venue"],
            symbol=r["symbol"],
            asset_type=r["asset_type"] or "spot",
            active=r["active"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            meta=r["meta"],
        )

    def add_instrument(
        self,
        venue: str,
        symbol: str,
        asset_type: str = "spot",
        active: bool = True,
        meta: dict[str, Any] | None = None,
    ) -> InstrumentRecord:
        now = _utcnow()
        with psycopg.connect(_dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO instrument_registry (venue, symbol, asset_type, active, created_at, updated_at, meta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (venue, symbol) DO UPDATE SET
                      asset_type = EXCLUDED.asset_type,
                      active = EXCLUDED.active,
                      updated_at = EXCLUDED.updated_at,
                      meta = COALESCE(EXCLUDED.meta, instrument_registry.meta)
                    """,
                    (venue, symbol, asset_type, active, now, now, json.dumps(meta) if meta else None),
                )
                cur.execute(
                    "INSERT INTO instrument_activation_log (venue, symbol, action, meta) VALUES (%s, %s, 'add', %s)",
                    (venue, symbol, json.dumps(meta) if meta else None),
                )
            conn.commit()
        return self.get_instrument(venue, symbol) or InstrumentRecord(venue=venue, symbol=symbol, asset_type=asset_type, active=active, created_at=now, updated_at=now, meta=meta)

    def set_active(self, venue: str, symbol: str, active: bool, meta: dict[str, Any] | None = None) -> InstrumentRecord | None:
        now = _utcnow()
        action = "activate" if active else "deactivate"
        with psycopg.connect(_dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE instrument_registry SET active = %s, updated_at = %s WHERE venue = %s AND symbol = %s",
                    (active, now, venue, symbol),
                )
                if cur.rowcount == 0:
                    return None
                cur.execute(
                    "INSERT INTO instrument_activation_log (venue, symbol, action, meta) VALUES (%s, %s, %s, %s)",
                    (venue, symbol, action, json.dumps(meta) if meta else None),
                )
            conn.commit()
        return self.get_instrument(venue, symbol)

    def list_activation_log(
        self,
        venue: str | None = None,
        symbol: str | None = None,
        limit: int = 100,
    ) -> list[ActivationLogEntry]:
        rows = []
        with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                if venue and symbol:
                    cur.execute(
                        "SELECT venue, symbol, action, created_at, meta FROM instrument_activation_log WHERE venue = %s AND symbol = %s ORDER BY created_at DESC LIMIT %s",
                        (venue, symbol, limit),
                    )
                elif venue:
                    cur.execute(
                        "SELECT venue, symbol, action, created_at, meta FROM instrument_activation_log WHERE venue = %s ORDER BY created_at DESC LIMIT %s",
                        (venue, limit),
                    )
                else:
                    cur.execute(
                        "SELECT venue, symbol, action, created_at, meta FROM instrument_activation_log ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                rows = cur.fetchall()
        return [
            ActivationLogEntry(
                venue=r["venue"],
                symbol=r["symbol"],
                action=r["action"],
                created_at=r["created_at"],
                meta=r["meta"],
            )
            for r in rows
        ]
