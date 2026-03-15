#!/usr/bin/env bash
# NEBULA-QUANT — Baja el stack (detiene y elimina contenedores).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

cd "$REPO_ROOT"
echo "== Bajando Nebula-Quant =="
docker compose -f "$COMPOSE_FILE" down
echo "== Stack detenido =="
