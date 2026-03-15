# Guía para probar el portal

Todo está listo para probar el portal. Sigue estos pasos.

---

## 1. Abrir el portal

- **URL:** http://localhost:3001  
- El contenedor **web-ui** está levantado; la primera carga puede tardar unos segundos (Next.js compila bajo demanda).

**Qué debes notar:** La home carga con enlaces a **Operator Cockpit** y **Executive Dashboard**. Sin errores en consola del navegador por CORS si solo navegas por las páginas estáticas.

---

## 2. Qué probar y qué cambios notar

### 2.1 Navegación básica

| Acción | Dónde | Qué notar |
|--------|--------|-----------|
| Ir al **Operator Cockpit** | Home → "Operator Cockpit" o `/operator` | Página con tarjetas: Venues, Instruments, Strategies, Paper, Live, Orders, Risk, Audit. |
| Ir al **Executive Dashboard** | Home → "Executive Dashboard" o `/executive` | Página con tarjetas: PnL, Capital, Venues, Strategies, Targets, Incidents. |
| Entrar en cada subpantalla | Clic en cada tarjeta (Venues, Instruments, etc.) | Cada ruta carga; las que llaman al control plane (Instruments, etc.) pueden mostrar "Failed to fetch" o lista vacía si el **control-plane** no está corriendo (ver más abajo). |

### 2.2 Pantallas que usan el control plane (puerto 8081)

- **Operator → Instruments** (`/operator/instruments`): llama a `GET http://localhost:8081/api/instruments` (o similar).  
  - **Si control-plane no está levantado:** verás error de red o mensaje tipo "Ensure the control plane is running (e.g. port 8081)".  
  - **Si control-plane está levantado:** lista de instrumentos (puede estar vacía) o datos según backend.

- Otras pantallas Operator/Executive que consuman APIs del control plane se comportan igual: sin control-plane, fallan las peticiones; con control-plane, responden (aunque sea vacío).

### 2.3 Binance Testnet (APIs en 8082 y vía 8081)

- **Binance API directa:** `curl -s http://localhost:8082/health`  
  - Deberías ver JSON con `"status":"NOT_CONFIGURED"` (si no hay `BINANCE_API_KEY`/`BINANCE_API_SECRET`) o `"CONNECTED"` si están configuradas las credenciales testnet.

- **Binance vía control plane:** `curl -s http://localhost:8081/api/binance/health`  
  - Solo responde si el servicio **control-plane** está corriendo. Si no: conexión rechazada. Si sí: mismo tipo de JSON (proxy a binance-api).

**Qué notar:** Con solo **binance-api** (8082) y **web-ui** (3001) levantados, el portal navega bien. Para que las pantallas que usan datos del control plane (instrumentos, etc.) y el proxy Binance funcionen, hay que tener también **control-plane** en marcha (primera vez requiere construir la imagen, ~5–10 min).

---

## 3. Resumen de servicios para “solo probar el portal”

| Servicio | Estado recomendado | Puerto |
|----------|--------------------|--------|
| **web-ui** | Up | 3001 → portal |
| **binance-api** | Up | 8082 → health/venue/market |
| **control-plane** | Opcional para APIs del portal y proxy Binance | 8081 |
| alertmanager | Up (config corregida) | 9093 |

Para levantar el **control-plane** (opcional, primera vez tarda en construir):

```bash
docker compose -f docker/docker-compose.yml up -d --build control-plane
```

---

## 4. Comprobaciones rápidas

```bash
# Portal
curl -sI http://localhost:3001 | head -1
# Esperado: HTTP/1.1 200 ...

# Binance API (sin control plane)
curl -s http://localhost:8082/health
# Esperado: {"status":"NOT_CONFIGURED",...} o {"status":"CONNECTED",...}

# Control plane (si lo levantaste)
curl -s http://localhost:8081/actuator/health 2>/dev/null || curl -s http://localhost:8081/api/binance/health
# Esperado: JSON de salud o proxy a Binance
```

---

**Resumen:** Abre http://localhost:3001, recorre Operator Cockpit y Executive Dashboard. Debes notar la navegación y las tarjetas; las pantallas que dependen del control plane mostrarán error hasta que ese servicio esté levantado. Binance se prueba por curl a 8082 (y a 8081 si el control-plane está up).
