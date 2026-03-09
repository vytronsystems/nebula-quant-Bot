#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== DB MIGRATE =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "create extension if not exists pgcrypto;"
for f in ./db/migrations/*.sql; do
  echo "== applying: $f =="
  docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -f - < "$f"
done
echo "OK: migrations applied"
