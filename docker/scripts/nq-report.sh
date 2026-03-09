#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUTDIR="${1:-./reports}"
mkdir -p "$OUTDIR"
TS="$(date +%Y%m%d-%H%M%S)"

echo "== REPORT: last 24h snapshots summary =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "\
copy (
  select
    date_trunc('hour', created_at) as hour,
    symbol,
    timeframe,
    decision,
    count(*) as n
  from decision_snapshots
  where created_at >= now() - interval '24 hours'
  group by 1,2,3,4
  order by 1,2,3,4
) to stdout with csv header" > "$OUTDIR/snapshots_24h_$TS.csv"

echo "== REPORT: last 24h bot_runs =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "\
copy (
  select
    started_at, ended_at, env, version, status
  from bot_runs
  where started_at >= now() - interval '24 hours'
  order by started_at desc
) to stdout with csv header" > "$OUTDIR/bot_runs_24h_$TS.csv"

echo "OK: reports written to $OUTDIR"
