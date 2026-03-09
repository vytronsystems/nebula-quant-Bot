import os
import sys
import psycopg
import redis


def main() -> int:
    pg_dsn = os.getenv("PG_DSN")
    if not pg_dsn:
        print("PG_DSN missing", file=sys.stderr)
        return 2

    r_host = os.getenv("REDIS_HOST", "redis")

    # Postgres
    try:
        with psycopg.connect(pg_dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
    except Exception as e:
        print(f"postgres unhealthy: {e}", file=sys.stderr)
        return 1

    # Redis
    try:
        r = redis.Redis(host=r_host, port=6379, decode_responses=True)
        r.ping()
    except Exception as e:
        print(f"redis unhealthy: {e}", file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
