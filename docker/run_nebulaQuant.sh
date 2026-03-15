#!/usr/bin/env bash
# NEBULA-QUANT — Sube el stack completo (compose) en segundo plano.
# Uso: ./run_nebulaQuant.sh   (desde cualquier sitio, o desde docker/)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

cd "$REPO_ROOT"
echo "== Subiendo Nebula-Quant (compose: $COMPOSE_FILE) =="
docker compose -f "$COMPOSE_FILE" up -d --build
echo "== Listo. Ver: docker compose -f $COMPOSE_FILE ps =="
