#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

TS="$(date +%Y%m%d-%H%M%S)"
OUT="artifacts/smoke-$TS.log"
exec > >(tee -a "$OUT") 2>&1

echo "== NEBULA-QUANT | SMOKE | $TS =="

need_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: falta comando: $1"; exit 1; }; }
need_cmd docker
need_cmd curl
need_cmd jq
need_cmd psql || true  # opcional (usaremos psql dentro del contenedor)

echo "== 1) docker compose ps =="
docker compose ps

echo "== 2) Postgres schema check (inside container) =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "\
select table_name, column_name, data_type \
from information_schema.columns \
where table_schema='public' and table_name in ('bot_runs','decision_snapshots') \
order by table_name, ordinal_position;"

echo "== 3) Grafana health =="
curl -sS -u admin:admin http://localhost:3000/api/health | jq .

echo "== 4) Datasource exists + type check =="
curl -sS -u admin:admin http://localhost:3000/api/datasources/uid/Postgres-NEBULA | jq '{uid,name,type}' | tee /dev/stderr \
| jq -e '.type=="grafana-postgresql-datasource"' >/dev/null \
|| { echo "ERROR: datasource type no es grafana-postgresql-datasource"; exit 1; }

echo "== 5) Datasource health =="
curl -sS -u admin:admin http://localhost:3000/api/datasources/uid/Postgres-NEBULA/health | jq . \
| jq -e '.status=="OK"' >/dev/null \
|| { echo "ERROR: datasource health != OK"; exit 1; }

echo "== 6) Dashboard LIVE check (uid + SQL correct) =="
dash=$(curl -sS -u admin:admin "http://localhost:3000/api/dashboards/uid/nebula-quant-overview")
echo "$dash" | jq -e '.dashboard.uid=="nebula-quant-overview"' >/dev/null \
|| { echo "ERROR: dashboard uid nebula-quant-overview no cargado"; exit 1; }

# Validar que el panel BotRuns usa started_at
echo "$dash" | jq -r '
.dashboard.panels[]
| select(.title=="BotRuns / día" or .title=="BotRuns / dia")
| .targets[0].rawSql
' | tee /dev/stderr | grep -q "started_at" \
|| { echo "ERROR: BotRuns panel no está usando started_at"; exit 1; }

echo "== 7) ds/query: now() smoke =="
FROM_MS=$(($(date +%s%N)/1000000 - 1*60*60*1000))
TO_MS=$(($(date +%s%N)/1000000))

curl -sS -u admin:admin \
  -H "Content-Type: application/json" \
  -X POST http://localhost:3000/api/ds/query \
  -d @- <<JSON | jq -e '.results.A.status==200' >/dev/null
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

echo "== 8) ds/query: BotRuns / día =="
curl -sS -u admin:admin \
  -H "Content-Type: application/json" \
  -X POST http://localhost:3000/api/ds/query \
  -d @- <<JSON | jq -e '.results.A.status==200' >/dev/null
{
  "from": "${FROM_MS}",
  "to": "${TO_MS}",
  "queries": [
    {
      "refId": "A",
      "datasource": { "uid": "Postgres-NEBULA", "type": "grafana-postgresql-datasource" },
      "rawSql": "select date_trunc('day', started_at) as time, count(*) as value from bot_runs where \\$__timeFilter(started_at) group by 1 order by 1;",
      "format": "time_series",
      "rawQuery": true
    }
  ]
}
JSON

echo "== 9) ds/query: DecisionSnapshots / minuto =="
curl -sS -u admin:admin \
  -H "Content-Type: application/json" \
  -X POST http://localhost:3000/api/ds/query \
  -d @- <<JSON | jq -e '.results.A.status==200' >/dev/null
{
  "from": "${FROM_MS}",
  "to": "${TO_MS}",
  "queries": [
    {
      "refId": "A",
      "datasource": { "uid": "Postgres-NEBULA", "type": "grafana-postgresql-datasource" },
      "rawSql": "select date_trunc('minute', created_at) as time, count(*) as value from decision_snapshots where \\$__timeFilter(created_at) group by 1 order by 1;",
      "format": "time_series",
      "rawQuery": true
    }
  ]
}
JSON

echo "== 10) ds/query: Últimos 20 snapshots (table) =="
curl -sS -u admin:admin \
  -H "Content-Type: application/json" \
  -X POST http://localhost:3000/api/ds/query \
  -d @- <<JSON | jq -e '.results.A.status==200' >/dev/null
{
  "from": "${FROM_MS}",
  "to": "${TO_MS}",
  "queries": [
    {
      "refId": "A",
      "datasource": { "uid": "Postgres-NEBULA", "type": "grafana-postgresql-datasource" },
      "rawSql": "select created_at as \"time\", symbol, timeframe, decision, reason_code from decision_snapshots order by created_at desc limit 20;",
      "format": "table",
      "rawQuery": true
    }
  ]
}
JSON

echo "✅ SMOKE PASS: Fase 1 lista. Evidencia: $OUT"
