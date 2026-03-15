#!/usr/bin/env bash
# NEBULA-QUANT — Development environment setup
# Run from repository root: ./scripts/setup_dev_env.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "== NEBULA-QUANT dev env setup (root: $REPO_ROOT) =="

# --- Node.js 20 LTS ---
need_node=false
if ! command -v node >/dev/null 2>&1; then
  need_node=true
elif ! node -v 2>/dev/null | grep -qE 'v20\.'; then
  echo "Node.js found but not v20.x; will try to install Node 20 LTS."
  need_node=true
fi

if [ "$need_node" = true ]; then
  echo "== Installing Node.js 20 LTS (NodeSource) =="
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
  else
    echo "ERROR: curl required to install Node.js. Install Node 20 LTS manually and re-run."
    exit 1
  fi
fi

# --- Verify node and npm ---
echo "== Verifying node and npm =="
node -v
npm -v
if ! node -v 2>/dev/null | grep -qE 'v20\.'; then
  echo "WARN: Node.js 20 LTS recommended; current: $(node -v 2>/dev/null || echo 'unknown')"
fi

# --- Frontend dependencies (apps/web) ---
if [ -d "$REPO_ROOT/apps/web" ]; then
  echo "== Installing frontend dependencies (apps/web) =="
  (cd "$REPO_ROOT/apps/web" && npm install)
else
  echo "WARN: apps/web not found; skipping frontend install."
fi

# --- Python dependencies (services/bot) ---
if [ -f "$REPO_ROOT/services/bot/requirements.txt" ]; then
  echo "== Installing Python dependencies (services/bot) =="
  if command -v pip3 >/dev/null 2>&1; then
    pip3 install --user -r "$REPO_ROOT/services/bot/requirements.txt" 2>/dev/null || \
    pip3 install -r "$REPO_ROOT/services/bot/requirements.txt" 2>/dev/null || true
  elif command -v pip >/dev/null 2>&1; then
    pip install --user -r "$REPO_ROOT/services/bot/requirements.txt" 2>/dev/null || \
    pip install -r "$REPO_ROOT/services/bot/requirements.txt" 2>/dev/null || true
  else
    echo "WARN: pip/pip3 not found; install Python dependencies manually (e.g. pip install -r services/bot/requirements.txt)."
  fi
else
  echo "WARN: services/bot/requirements.txt not found; skipping Python install."
fi

echo "== Setup complete =="
echo "Next: make up    # start Docker stack"
echo "       make ui   # start Next.js frontend (or use web-ui service)"
echo "       make backend  # start trading backend (bot)"
