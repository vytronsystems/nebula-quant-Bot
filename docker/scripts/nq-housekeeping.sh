#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== HOUSEKEEPING (retención 1 año) =="
docker compose exec -T postgres psql -U nebula -d trading -v ON_ERROR_STOP=1 -c "\
delete from decision_snapshots where created_at < now() - interval '365 days';
delete from bot_errors where created_at < now() - interval '365 days';
delete from bot_runs where started_at < now() - interval '365 days';
"
echo "OK: housekeeping done"
