#!/usr/bin/env bash
# NEBULA-QUANT — Muestra el estado de los contenedores del stack.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

cd "$REPO_ROOT"
docker compose -f "$COMPOSE_FILE" ps -a
