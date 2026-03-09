#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== NEBULA-QUANT | STATUS =="

echo "== docker compose ps =="
docker compose ps

echo
echo "== health (containers) =="
# Works across compose versions: parse STATUS column textually
docker compose ps --format json | jq -r '
  .[] | "\(.Name)\t\(.State)\t\(.Health // "n/a")"
' 2>/dev/null || {
  # fallback
  docker compose ps
}

echo
echo "== postgres: quick counts (last 24h) =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "
select
  (select count(*) from bot_runs where started_at > now() - interval '24 hours') as bot_runs_24h,
  (select count(*) from decision_snapshots where created_at > now() - interval '24 hours') as snapshots_24h;
"

echo
echo "== last 10 decision_snapshots =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "
select created_at, symbol, timeframe, decision, reason_code
from decision_snapshots
order by created_at desc
limit 10;
"

echo
echo "== grafana health =="
curl -fsS -u admin:admin http://localhost:3000/api/health | jq .

echo
echo "== grafana datasource health (Postgres-NEBULA) =="
curl -fsS -u admin:admin http://localhost:3000/api/datasources/uid/Postgres-NEBULA/health | jq .

echo
echo "OK: status completo"
