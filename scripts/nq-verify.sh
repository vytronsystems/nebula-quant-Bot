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
cd docker
docker compose ps >/dev/null || fail "docker compose ps falló"
cd ..

echo "== 3) postgres schema expected =="
cd docker
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "
select table_name, column_name
from information_schema.columns
where table_schema='public' and table_name in ('bot_runs','decision_snapshots')
order by table_name, ordinal_position;
" >/tmp/nq.schema.txt

grep -q "bot_runs" /tmp/nq.schema.txt || fail "tabla bot_runs no encontrada"
grep -q "decision_snapshots" /tmp/nq.schema.txt || fail "tabla decision_snapshots no encontrada"

echo "== 4) grafana health =="
curl -fsS -u admin:admin http://localhost:3000/api/health | jq -e '.database=="ok"' >/dev/null \
  || fail "Grafana health no OK"

echo "== 5) bot metrics on host =="
curl -fsS http://localhost:8080/metrics >/dev/null || fail "No puedo leer bot metrics en localhost:8080"

echo "== 6) prometheus scrape bot (API targets) =="
curl -fsS http://localhost:9090/api/v1/targets \
| grep -q '"scrapeUrl":"http://bot:8080/metrics".*"health":"up"\|"health":"up".*"scrapeUrl":"http://bot:8080/metrics"' \
  || fail "Prometheus NO está scrapeando bot (esperaba scrapeUrl http://bot:8080/metrics health=up)"

echo "OK: VERIFY PASSED ✅"
echo "Grafana:    http://localhost:3000"
echo "Prometheus: http://localhost:9090"
