#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== NEBULA-QUANT | UP =="
docker compose up -d

echo "== wait containers (up to 60s) =="
deadline=$((SECONDS+60))
while true; do
  running=$(docker compose ps --format json | jq -r '.[].State' | sort | uniq -c || true)
  echo "$running" | sed 's/^/  /'
  if echo "$running" | grep -q "running"; then
    # if any is not running, keep waiting
    if echo "$running" | grep -qv "running"; then
      :
    else
      break
    fi
  fi
  if (( SECONDS > deadline )); then
    echo "ERROR: containers no están todos en running luego de 60s"
    docker compose ps
    exit 1
  fi
  sleep 3
done

echo "OK: stack arriba"
