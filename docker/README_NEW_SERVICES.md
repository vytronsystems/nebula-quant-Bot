# Adding Control Plane and Web to Docker Stack

Current `docker-compose.yml` runs: postgres, redis, grafana, postgres-exporter, bot, prometheus, alertmanager.

## When Dockerfiles are ready

1. **Control plane** (port 8081):
   - Build from `services/control-plane` (Maven/Java 21). Set env `PG_DSN` (or equivalent) to postgres URL if it needs DB. Health: `GET /api/health`.
   - Add to compose:
   ```yaml
   control-plane:
     build: ../services/control-plane
     ports: ["8081:8081"]
     environment:
       # PG_DSN if needed
     depends_on: [postgres]
     networks: [nqnet]
   ```

2. **Web** (port 3001; 3000 is Grafana):
   - Build from `apps/web` (Node, next build && next start). For server-side API calls to control plane, set `NEXT_PUBLIC_CONTROL_PLANE_URL=http://control-plane:8081` or similar.
   - Add to compose:
   ```yaml
   web:
     build: ../apps/web
     ports: ["3001:3000"]
     environment:
       NEXT_PUBLIC_CONTROL_PLANE_URL: http://localhost:8081
     depends_on: [control-plane]
     networks: [nqnet]
   ```

3. Run: `docker compose up -d` (after adding the service blocks and Dockerfiles).

## Migration

- Ensure `003_evidence_backbone.sql` has been applied (`docker/scripts/nq-db-migrate.sh`) so control plane and bot can use evidence tables.
