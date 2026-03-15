# Qué falta — Estado del stack y Fase 71

**Última comprobación:** 2026-03-13

## 1. Servicios Docker

| Servicio        | Estado actual     | Acción si falta |
|-----------------|-------------------|------------------|
| **binance-api** | Up (puerto 8082)  | `docker compose -f docker/docker-compose.yml up -d binance-api` |
| **web-ui**      | Up (puerto 3001)  | `docker compose -f docker/docker-compose.yml up -d web-ui` |
| **alertmanager** | Up (config corregida) | `docker compose -f docker/docker-compose.yml restart alertmanager` |
| **control-plane** | No construido aún | `docker compose -f docker/docker-compose.yml up -d --build control-plane` (primera vez 5–10 min). Necesario para APIs del portal (instrumentos, etc.) y proxy `/api/binance/*`. |

## 2. Resumen de lo ya hecho (Fase 71)

- Config testnet: `services/bot/adapters/binance/testnet_config.py`
- Cliente testnet: `services/bot/adapters/binance/testnet_client.py`
- API FastAPI: `services/bot/binance_api.py` (puerto 8082)
- Proxy en control plane: `BinanceProxyController` → `/api/binance/*`
- Tests: `services/bot/adapters/binance/tests/test_testnet.py`
- Docs: `docs/BINANCE_TESTNET_INTEGRATION.md`
- Artefactos: `artifacts/phases/phase_71_*`, `artifacts/tests/phase_71_test_report.html`, `artifacts/audits/phase_71_audit_report.html`

## 3. Cómo dejar todo levantado

Desde la raíz del repo:

```bash
# Corregir alertmanager (ya aplicado en repo) y reiniciar
docker compose -f docker/docker-compose.yml restart alertmanager

# Levantar binance-api y control-plane (construye si hace falta)
docker compose -f docker/docker-compose.yml up -d binance-api control-plane

# Levantar web-ui si está parado
docker compose -f docker/docker-compose.yml up -d web-ui
```

Comprobar:

```bash
docker compose -f docker/docker-compose.yml ps -a
curl -s http://localhost:8082/health   # Binance API
curl -s http://localhost:8081/api/binance/health  # vía control plane
```

## 4. Opcional

- **Credenciales Binance Testnet:** para que `/health` o `/venue-overview` devuelvan `CONNECTED`, configurar `BINANCE_TESTNET=true`, `BINANCE_API_KEY` y `BINANCE_API_SECRET` (p. ej. en `.env`). Ver `docs/BINANCE_TESTNET_INTEGRATION.md`.
