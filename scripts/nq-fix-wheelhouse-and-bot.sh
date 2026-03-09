#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOT_DIR="$ROOT/services/bot"
REQ="$BOT_DIR/requirements.txt"
WH="$BOT_DIR/wheelhouse"

echo "== NEBULA-QUANT | FIX wheelhouse + bot metrics =="
echo "ROOT=$ROOT"
echo "BOT_DIR=$BOT_DIR"
echo "REQ=$REQ"
echo "WH=$WH"
echo "USER=$(whoami)"
echo "GROUPS=$(id -nG)"

# 0) guard rails
command -v docker >/dev/null
command -v docker compose >/dev/null || true
docker ps >/dev/null

test -f "$REQ" || { echo "ERROR: no existe $REQ"; exit 1; }
mkdir -p "$WH"

echo "== 1) Sync wheelhouse OFFLINE (descarga wheels para TODOS los requirements) =="
# Nota: Esto necesita internet SOLO en este paso de "preparación offline".
# Una vez el wheelhouse esté completo, el build vuelve 100% offline.
python3 -m pip download \
  --only-binary=:all: \
  --dest "$WH" \
  -r "$REQ"

echo "== 2) Verificación: prometheus_client wheel existe =="
ls -1 "$WH" | grep -E '^prometheus_client-0\.20\.0-.*\.whl$' >/dev/null \
  || { echo "ERROR: wheel de prometheus_client==0.20.0 no fue descargado"; ls -1 "$WH" | grep -i prometheus || true; exit 1; }
echo "OK: wheel prometheus_client presente"

echo "== 3) Rebuild bot (no-cache) =="
cd "$ROOT/docker"
docker compose build --no-cache bot

echo "== 4) Up bot =="
docker compose up -d bot

echo "== 5) Wait bot healthy (hasta 90s) =="
for i in $(seq 1 45); do
  st="$(docker inspect nq-bot --format '{{.State.Status}}/{{if .State.Health}}{{.State.Health.Status}}{{else}}nohealth{{end}}' 2>/dev/null || echo unknown)"
  echo "try=$i status=$st"
  if echo "$st" | grep -q "running/healthy"; then
    echo "OK: bot healthy ✅"
    break
  fi
  sleep 2
done

echo "== 6) Smoke: prometheus scrape bot metrics (desde contenedor prometheus) =="
# No depende de exponer 8080 al host. Este es el check correcto.
docker compose exec -T prometheus sh -lc 'wget -qO- http://bot:8080/metrics | head -n 20'

echo "== DONE ✅ =="
