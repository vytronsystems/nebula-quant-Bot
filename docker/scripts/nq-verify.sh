#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "ERROR: $*" >&2; exit 1; }

echo "== NEBULA-QUANT | VERIFY (AUDIT) =="

command -v docker >/dev/null || fail "docker no instalado"
command -v jq >/dev/null || fail "jq no instalado"
command -v curl >/dev/null || fail "curl no instalado"

echo "== 1) docker daemon access =="
docker ps >/dev/null || fail "No tengo acceso a docker daemon (docker ps falló)"

echo "== 2) compose services up =="
docker compose ps >/dev/null || fail "docker compose ps falló"

echo "== 3) postgres schema expected =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "
select table_name, column_name
from information_schema.columns
where table_schema='public' and table_name in ('bot_runs','decision_snapshots')
order by table_name, ordinal_position;
" >/tmp/nq.schema.txt

grep -q "bot_runs" /tmp/nq.schema.txt || fail "tabla bot_runs no encontrada"
grep -q "decision_snapshots" /tmp/nq.schema.txt || fail "tabla decision_snapshots no encontrada"
grep -q "bot_runs.*started_at" /tmp/nq.schema.txt || fail "bot_runs.started_at no encontrado"
grep -q "decision_snapshots.*created_at" /tmp/nq.schema.txt || fail "decision_snapshots.created_at no encontrado"

echo "== 4) SQL checks in DB (no macros) =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "
select date_trunc('day', started_at) as day, count(*) as value
from bot_runs
where started_at > now() - interval '6 hours'
group by 1 order by 1;
" >/dev/null

docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "
select date_trunc('minute', created_at) as minute, count(*) as value
from decision_snapshots
where created_at > now() - interval '6 hours'
group by 1 order by 1
limit 5;
" >/dev/null

echo "== 5) grafana health =="
curl -fsS -u admin:admin http://localhost:3000/api/health | jq -e '.database=="ok"' >/dev/null \
  || fail "Grafana health no OK"

echo "== 6) grafana datasource Postgres-NEBULA health =="
curl -fsS -u admin:admin http://localhost:3000/api/datasources/uid/Postgres-NEBULA/health | jq -e '.status=="OK"' >/dev/null \
  || fail "Datasource Postgres-NEBULA no OK"

echo "== 7) grafana ds/query sanity (now() test) =="
FROM_MS=$(($(date +%s%N)/1000000 - 15*60*1000))
TO_MS=$(($(date +%s%N)/1000000))

curl -fsS -u admin:admin -H "Content-Type: application/json" -X POST http://localhost:3000/api/ds/query -d @- <<JSON \
| jq -e '.results.A.status==200' >/dev/null || fail "Grafana ds/query now() falló"
{
  "from": "${FROM_MS}",
  "to": "${TO_MS}",
  "queries": [
    {
      "refId": "A",
      "datasource": { "uid": "Postgres-NEBULA", "type": "grafana-postgresql-datasource" },
      "rawSql": "select now() as time, 1::int as value",
      "format": "time_series",
      "rawQuery": true
    }
  ]
}
JSON

echo "== 8) bot writing snapshots (last 5min) =="
SNAPS=$(docker compose exec -T postgres psql -U nebula -d trading -tA -v ON_ERROR_STOP=1 -c "
select count(*) from decision_snapshots where created_at > now() - interval '5 minutes';
")
# trim spaces/newlines
SNAPS="$(echo "$SNAPS" | tr -d '[:space:]')"
[ "${SNAPS:-0}" -ge 1 ] || fail "No veo snapshots en los últimos 5 minutos (count=${SNAPS:-0})"

echo "OK: VERIFY PASSED ✅"
echo "Grafana: http://localhost:3000"
