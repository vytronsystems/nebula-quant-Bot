# NEBULA-QUANT — Development Environment Setup

Standardized setup for local development. All commands are run from the **repository root**:

```bash
~/projects/nebula-quant
```

## Prerequisites

- **Docker** and **Docker Compose** (for `make up`, `make backend`)
- **Bash** (for `scripts/setup_dev_env.sh`)
- On Linux: **curl** (used by the setup script to install Node.js 20 if needed)

## Quick start

### 1. One-time setup: install tools and dependencies

From the repo root:

```bash
make setup
```

This runs `scripts/setup_dev_env.sh`, which:

- Installs **Node.js 20 LTS** (if missing or not v20)
- Verifies **node** and **npm**
- Installs **frontend dependencies** in `apps/web` (`npm install`)
- Installs **Python dependencies** for `services/bot` if `pip`/`pip3` is available

### 2. Start the Docker stack (Postgres, Redis, Grafana, bot, Prometheus, Alertmanager, web-ui)

```bash
make up
```

This runs `docker compose -f docker/docker-compose.yml up -d` from the repo root. It starts:

- Postgres, Redis, Grafana (port **3000**), postgres-exporter, **bot** (port 8080), Prometheus (9090), Alertmanager (9093), **control-plane** (port **8081**), **web-ui** (port **3001**)

The **control plane** stays up with the stack so the UI (Operator → Instruments Control) can load data from `http://localhost:8081`. The Next.js app in Docker is at **http://localhost:3001** (Grafana remains at http://localhost:3000).

### 3. Run the Next.js frontend locally (optional)

For frontend development with hot reload, run the UI on the host instead of in Docker:

```bash
make ui
```

This runs `npm run dev` in `apps/web`. The app will be at **http://localhost:3000**. Stop with Ctrl+C.

If you use `make up`, the **web-ui** service also runs the frontend in a container on port **3001**; you can use either `make ui` (port 3000) or the container (port 3001), but not both on the same port.

## Makefile reference (all from repo root)

| Command       | Description |
|--------------|-------------|
| `make setup` | Run `scripts/setup_dev_env.sh` (Node 20, npm deps in apps/web, Python deps in services/bot) |
| `make up`    | Start full Docker stack in background (`docker compose up -d`) |
| `make down`  | Stop and remove containers (`docker compose down`) |
| `make logs`  | Stream Docker Compose logs (`docker compose logs -f`) |
| `make ui`    | Start Next.js frontend locally (`npm run dev` in apps/web) |
| `make backend` | Start only the trading backend (bot) container |
| `make test`  | Run test suite (root `tests/` + `services/bot` tests) |

## Ports

| Service    | Port (host) | Notes |
|-----------|-------------|--------|
| Grafana   | 3000        | Existing |
| **Web UI** (Docker) | 3001 | Next.js when run via `make up` |
| Bot       | 8080        | Metrics / health |
| Prometheus| 9090        | |
| Alertmanager | 9093     | |
| Postgres  | 5432        | |
| Redis     | 6379        | |

## Control plane (para que la UI muestre datos)

Con **`make up`** el **control plane** ya sube en Docker (puerto 8081) y se queda arriba con el resto del stack. No hace falta arrancarlo a mano.

Para que **Operator → Instruments Control** muestre datos:

1. **`make up`** — deja Postgres, control plane y el resto arriba.
2. Aplica la migración 003 si no está aplicada: desde `docker/`: `./scripts/nq-db-migrate.sh`.
3. La UI (en navegador) llama a `http://localhost:8081` por defecto. Abre **Operator → Instruments Control**. Si la tabla sale vacía es que no hay filas en `instrument_registry` (inserta datos de prueba o usa el servicio Python `nq_instrument_registry`).

Si prefieres correr el control plane en local (sin Docker): Java 21 + Maven y `cd services/control-plane && mvn spring-boot:run`, con Postgres accesible (p. ej. `PG_HOST=localhost`).

## Troubleshooting

- **Node not found after setup**: Ensure the script completed; on some systems you may need to install Node 20 manually (e.g. from nodejs.org or via nvm) and then run `make setup` again for npm/Python installs.
- **make up fails**: Run from repo root (`~/projects/nebula-quant`) and ensure Docker is running. Compose file path is `docker/docker-compose.yml`.
- **Port in use**: If 3001 is in use, change the `web-ui` port mapping in `docker/docker-compose.yml` (e.g. `"3002:3000"`).
