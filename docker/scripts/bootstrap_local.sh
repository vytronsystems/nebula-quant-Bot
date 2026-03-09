#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKER_DIR="${ROOT}/docker"

echo "== NEBULA-QUANT | bootstrap_local =="

echo "[1/8] Validar docker compose"
cd "${DOCKER_DIR}"
docker compose config >/dev/null
echo "OK: compose parse"

echo "[2/8] Crear carpetas persistentes"
mkdir -p "${ROOT}/logs/postgres" "${ROOT}/logs/redis" "${ROOT}/logs/grafana"
echo "OK: logs folders"

echo "[3/8] Permisos Grafana (UID 472)"
# Evita fallos en VirtualBox/WSL: dejamos 775 y dueño 472 si existe sudo
if command -v sudo >/dev/null 2>&1; then
  sudo chown -R 472:472 "${ROOT}/logs/grafana" || true
  sudo chmod -R 775 "${ROOT}/logs/grafana" || true
else
  chmod -R 775 "${ROOT}/logs/grafana" || true
fi
echo "OK: grafana perms"

echo "[4/8] Levantar servicios base (postgres/redis/grafana)"
docker compose up -d --force-recreate postgres redis grafana

echo "[5/8] Esperar healthchecks (hasta 60s)"
deadline=$((SECONDS+60))
while true; do
  pg="$(docker inspect -f '{{.State.Health.Status}}' nq-postgres 2>/dev/null || echo starting)"
  rd="$(docker inspect -f '{{.State.Health.Status}}' nq-redis 2>/dev/null || echo starting)"
  gf="$(docker inspect -f '{{.State.Health.Status}}' nq-grafana 2>/dev/null || echo starting)"
  echo "health: postgres=${pg} redis=${rd} grafana=${gf}"
  if [[ "${pg}" == "healthy" && "${rd}" == "healthy" && "${gf}" == "healthy" ]]; then
    break
  fi
  if (( SECONDS > deadline )); then
    echo "ERROR: timeout esperando servicios base"
    docker compose ps || true
    exit 1
  fi
  sleep 3
done

echo "[6/8] Levantar bot (build + recreate)"
docker compose up -d --build --force-recreate bot

echo "[7/8] Esperar bot health (hasta 60s)"
deadline=$((SECONDS+60))
while true; do
  bt="$(docker inspect -f '{{.State.Health.Status}}' nq-bot 2>/dev/null || echo starting)"
  echo "health: bot=${bt}"
  if [[ "${bt}" == "healthy" ]]; then
    break
  fi
  if (( SECONDS > deadline )); then
    echo "ERROR: timeout esperando bot"
    docker compose logs --tail 120 bot || true
    exit 1
  fi
  sleep 3
done

echo "[8/8] Smoke checks rápidos"
echo "- Postgres: decision_snapshots count"
docker compose exec -T postgres psql -U nebula -d trading -c "select count(*) as decision_snapshots from decision_snapshots;" || true

echo "- Redis: ping"
docker compose exec -T redis redis-cli ping || true

echo "DONE ✅  Grafana: http://localhost:3000"
