#!/usr/bin/env bash
# NEBULA-QUANT — Construye todas las imágenes (bot, binance-api, control-plane).
# La primera vez tarda varios minutos (sobre todo control-plane). Ejecutar antes de run si faltan imágenes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

cd "$REPO_ROOT"
echo "== Construyendo imágenes Nebula-Quant (puede tardar varios minutos) =="
docker compose -f "$COMPOSE_FILE" build
echo "== Build listo. Ahora puedes ejecutar run_nebulaQuant.sh =="
