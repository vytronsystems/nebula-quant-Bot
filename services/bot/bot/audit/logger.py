import uuid
import json
import hashlib
from datetime import datetime

import psycopg

from bot.config import PG_DSN


def _utcnow():
    return datetime.utcnow()


def _policy_hash_stub() -> str:
    raw = {"version": "v1", "risk_engine": "stub", "news_guard": "stub"}
    return hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()


def start_run(env: str = "local", version: str = "dev") -> str:
    dsn = PG_DSN
    run_id = str(uuid.uuid4())
    now = _utcnow()

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bot_runs (id, started_at, ended_at, env, version, status, meta)
                VALUES (%s, %s, NULL, %s, %s, %s, %s)
                """,
                (run_id, now, env, version, "running", json.dumps({"source": "psycopg"})),
            )
        conn.commit()

    return run_id


def end_run(run_id: str, status: str = "success") -> None:
    dsn = PG_DSN
    now = _utcnow()

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE bot_runs
                   SET ended_at = %s,
                       status   = %s
                 WHERE id = %s
                """,
                (now, status, run_id),
            )
        conn.commit()


def log_no_trade(run_id: str, symbol: str = "QQQ", timeframe: str = "5m") -> None:
    dsn = PG_DSN
    now = _utcnow()

    snap_id = str(uuid.uuid4())
    policy_hash = _policy_hash_stub()

    user_params = {"RISK_USD": 200, "MIN_RR": 3}
    derived_params = {"note": "stub"}
    indicators = {"note": "stub"}

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO decision_snapshots (
                    id, bot_run_id, created_at,
                    symbol, timeframe, session_tag,
                    decision, direction, confidence,
                    policy_hash, user_params, derived_params,
                    indicators, levels, news_context, contract,
                    reason_code, reason_detail
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                )
                """,
                (
                    snap_id, run_id, now,
                    symbol, timeframe, "regular",
                    "no_trade", None, None,
                    policy_hash,
                    json.dumps(user_params),
                    json.dumps(derived_params),
                    json.dumps(indicators),
                    None, None, None,
                    "BOOT_HEARTBEAT",
                    "Heartbeat snapshot (no trade).",
                ),
            )
        conn.commit()
