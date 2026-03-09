#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

_have_docker_access() {
  # returns: 0 OK, 10 permission denied, 20 daemon not running, 30 unknown
  local out rc
  out="$(docker info 2>&1)" && rc=0 || rc=$?
  if [ $rc -eq 0 ]; then
    return 0
  fi
  echo "$out" | grep -qi 'permission denied.*docker\.sock' && return 10
  echo "$out" | grep -qiE 'cannot connect to the docker daemon|is the docker daemon running|connect: connection refused' && return 20
  return 30
}

_ensure_docker_or_rerun() {
_ensure_docker_or_rerun
  case $? in
    0) return 0 ;;
    10)
      echo "WARN: sin permisos a /var/run/docker.sock en esta sesión."
      echo "INFO: re-ejecutando automáticamente con newgrp docker..."
      newgrp docker -c "cd '$ROOT' && ./scripts/nq-run.sh" || exit $?
      exit 0
      ;;
    20)
      echo "ERROR: Docker daemon no está corriendo (docker info falla por daemon)."
      echo "ACCION: inicia docker y reintenta."
      exit 1
      ;;
    *)
      echo "ERROR: Docker no responde (motivo desconocido)."
      echo "SALIDA docker info:"
      docker info || true
      exit 1
      ;;
  esac
}
cd "$ROOT"

_die() { echo "ERROR: $*" >&2; exit 1; }

_have_docker_access() {
  docker ps >/dev/null 2>&1
}

# Re-ejecuta con grupo docker si no hay acceso al socket en esta sesión
if ! _have_docker_access; then
  if docker ps 2>&1 | grep -qi "permission denied.*docker.sock"; then
    if command -v sg >/dev/null 2>&1; then
      echo "== docker.sock permission denied: re-exec with 'sg docker' =="
      exec sg docker -c "$0 ${*:-}"
    else
      _die "Sin acceso a /var/run/docker.sock y no existe 'sg'. Ejecuta: newgrp docker  (o re-login) y vuelve a correr ./scripts/nq-run.sh"
    fi
  else
    _die "Docker no responde. Verifica: docker info"
  fi
fi

echo "== NEBULA-QUANT | UP =="
docker compose up -d --remove-orphans

echo "== wait containers (up to 60s) =="

mapfile -t SERVICES < <(docker compose ps --services 2>/dev/null || true)
[[ "${#SERVICES[@]}" -gt 0 ]] || _die "No pude listar servicios con 'docker compose ps --services'."

deadline=$((SECONDS + 60))

_inspect_state() {
  local cid="$1"
  local status health
  status="$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null || echo "")"
  health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$cid" 2>/dev/null || echo "")"
  printf "%s|%s" "$status" "$health"
}

_all_ready() {
  local svc cid pair st hl
  for svc in "${SERVICES[@]}"; do
    cid="$(docker compose ps -q "$svc" 2>/dev/null || true)"
    [[ -n "$cid" ]] || continue

    pair="$(_inspect_state "$cid")"
    st="${pair%%|*}"
    hl="${pair#*|}"

    [[ "$st" == "running" ]] || return 1
    if [[ -n "$hl" && "$hl" != "healthy" ]]; then
      return 1
    fi
  done
  return 0
}

while true; do
  if _all_ready; then
    echo "OK: all containers running (and healthy where applicable)"
    break
  fi

  if (( SECONDS >= deadline )); then
    echo "WARN: timeout waiting containers. Current status:"
    for svc in "${SERVICES[@]}"; do
      cid="$(docker compose ps -q "$svc" 2>/dev/null || true)"
      [[ -n "$cid" ]] || continue
      pair="$(_inspect_state "$cid")"
      st="${pair%%|*}"
      hl="${pair#*|}"
      [[ -n "$hl" ]] && echo " - $svc: $st (health=$hl)" || echo " - $svc: $st"
    done
    echo "== last 120 logs =="
    docker compose logs --tail 120 || true
    _die "Contenedores no listos antes del timeout."
  fi

  sleep 2
done

echo "== ps =="
docker compose ps

echo "== quick endpoints =="
echo "Grafana: http://localhost:3000"
