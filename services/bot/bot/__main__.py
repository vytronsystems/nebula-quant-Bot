import os
import time
import signal
from loguru import logger
import psycopg
import redis

from bot.utils.retry import retry
from bot.config import (
    NQ_ENV, NQ_VERSION, NQ_SYMBOL, NQ_TIMEFRAME,
    HEARTBEAT_SECONDS, SNAPSHOT_EVERY_N_HEARTBEATS,
)
from bot.audit.logger import start_run, log_no_trade, end_run

_shutdown = False


def _handle_signal(signum, frame):
    global _shutdown
    _shutdown = True
    logger.warning(f"Signal received ({signum}). Initiating graceful shutdown...")


def _start_metrics_safe(port: int = 8080):
    """
    Metrics MUST NOT crash the process.
    If prometheus_client is missing or port is taken, we log and continue.
    """
    try:
        from bot.metrics import metrics_start  # lazy import
        metrics_start(port)
        logger.success(f"Prometheus metrics enabled on :{port} (/metrics).")
        return True
    except Exception as e:
        logger.warning(f"Metrics disabled (non-fatal): {e!r}")
        return False


def _inc_heartbeat_safe():
    """
    Increment counter only if metrics are available.
    """
    try:
        from bot.metrics import HEARTBEATS_TOTAL  # lazy import
        HEARTBEATS_TOTAL.inc()
    except Exception:
        pass


def _smoke_tests(pg_dsn: str, r_host: str) -> None:
    def pg_check():
        with psycopg.connect(pg_dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT now();")
                return cur.fetchone()[0]

    now = retry(pg_check, name="postgres_check")
    logger.success(f"Postgres OK: {now}")

    def redis_check():
        r = redis.Redis(
            host=r_host,
            port=6379,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        r.ping()
        r.set("nq:boot", "ok")
        return r.get("nq:boot")

    v = retry(redis_check, name="redis_check")
    logger.success(f"Redis OK: nq:boot={v}")


def main():
    global _shutdown

    pg_dsn = os.getenv("PG_DSN", "postgresql://nebula:nebula123@postgres:5432/trading")
    r_host = os.getenv("REDIS_HOST", "redis")

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    logger.info("Booting NEBULA-QUANT bot...")
    logger.info(f"PG_DSN={pg_dsn}")
    logger.info(f"REDIS_HOST={r_host}")
    logger.info(f"NQ_ENV={NQ_ENV} NQ_VERSION={NQ_VERSION} NQ_SYMBOL={NQ_SYMBOL} NQ_TIMEFRAME={NQ_TIMEFRAME}")
    logger.info(f"HEARTBEAT_SECONDS={HEARTBEAT_SECONDS} SNAPSHOT_EVERY_N_HEARTBEATS={SNAPSHOT_EVERY_N_HEARTBEATS}")

    # metrics: safe, never fatal
    _start_metrics_safe(int(os.getenv("METRICS_PORT", "8080")))

    run_id = retry(lambda: start_run(env=NQ_ENV, version=NQ_VERSION), name="start_run")
    logger.success(f"BotRun started: {run_id}")

    status = "success"
    try:
        _smoke_tests(pg_dsn, r_host)

        hb = 0
        while not _shutdown:
            hb += 1
            logger.info("Heartbeat...")

            if SNAPSHOT_EVERY_N_HEARTBEATS > 0 and (hb % SNAPSHOT_EVERY_N_HEARTBEATS == 0):

                def persist_snapshot():
                    log_no_trade(run_id=run_id, symbol=NQ_SYMBOL, timeframe=NQ_TIMEFRAME)
                    return True

                retry(persist_snapshot, name="log_no_trade")
                logger.info("DecisionSnapshot persisted (no_trade).")

            time.sleep(HEARTBEAT_SECONDS)
            _inc_heartbeat_safe()

        status = "stopped"
        logger.warning("Graceful shutdown completed.")

    except Exception:
        status = "error"
        logger.exception("Fatal error.")
        raise
    finally:

        def finalize_run():
            end_run(run_id, status=status)
            return True

        try:
            retry(finalize_run, name="end_run")
            logger.success(f"BotRun ended: {run_id} status={status}")
        except Exception:
            logger.exception("Failed to end BotRun cleanly.")


if __name__ == "__main__":
    main()
