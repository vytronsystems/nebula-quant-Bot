#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/tmp/nebula-quant"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/phase1-one.log"

echo "=== START phase1-one $(date -Iseconds) ===" >"$LOG"

set -x
{
  echo "== A) UP stack =="
  cd docker
  docker compose up -d --build
  docker compose ps
  cd ..

  echo
  echo "== B) VERIFY (AUDIT) =="
  ./scripts/nq-verify.sh

  echo
  echo "== C) PROM targets audit dump =="
  curl -fsS http://localhost:9090/api/v1/targets > /tmp/nq.prom.targets.json
  echo "OK: saved /tmp/nq.prom.targets.json"

  echo
  echo "=== END phase1-one $(date -Iseconds) ==="
} >>"$LOG" 2>&1

echo "EXIT=0" > "$LOG_DIR/phase1-one.exit"
tail -n 120 "$LOG"
