# Qué falta para que la UI traiga datos reales

La UI (Operator / Executive) ya existe. **Instruments** está conectado de punta a punta (control plane lee Postgres, UI llama al control plane y muestra la tabla). El resto de pantallas siguen como placeholders hasta que se conecten sus APIs.

---

## 1. Control Plane sirviendo datos

**Hecho para Instruments:**

- `GET /api/instruments` lee de la tabla `instrument_registry` (JPA + Postgres), con filtros `venue` y `activeOnly`.
- CORS habilitado para orígenes de la UI (localhost:3000, 3001, 3002).

**Pendiente para otras pantallas:**

- `GET /api/artifacts` sigue devolviendo `[]`; conectar a `artifact_registry` o al filesystem.
- **Venues / dashboard:** Exponer un endpoint que lea `venue_account_snapshot` y/o use la lógica de `nq_cross_venue` (p. ej. leyendo Postgres desde Java).

---

## 2. Que el Control Plane esté levantado y accesible

**Falta:**

- Tener **Java 21 y Maven** instalados.
- Desde la raíz del repo: construir y arrancar el control plane, por ejemplo:
  ```bash
  cd services/control-plane && mvn spring-boot:run
  ```
- Que escuche en **http://localhost:8081** (o la URL que uses en el frontend).
- Si la UI corre en otro origen (p. ej. `http://localhost:3000`), configurar **CORS** en el control plane para ese origen.

---

## 3. UI llamando al Control Plane

**Hecho para Instruments:**

- Variable de entorno `NEXT_PUBLIC_CONTROL_PLANE_URL` (por defecto `http://localhost:8081`); ver `apps/web/.env.example` y `.env.local`.
- La pantalla **Operator → Instruments Control** hace `fetch` a `GET /api/instruments?activeOnly=false`, muestra loading/error y una tabla con venue, symbol, asset type, active, updated.

**Pendiente:** Repetir el mismo patrón (env, fetch, estado, tabla/cards) en Venues, Artifacts, Paper, etc., cuando existan los endpoints en el control plane.

---

## Resumen

| Pieza | Instruments | Otras pantallas |
|-------|-------------|------------------|
| **Backend** | Hecho: control plane lee `instrument_registry` | Pendiente: artifacts, venues, dashboard |
| **Control plane arriba** | Java 21 + Maven; `cd services/control-plane && mvn spring-boot:run`; Postgres accesible (PG_HOST=localhost o el host del compose) | Igual |
| **UI** | Hecho: Instruments Control hace fetch y muestra tabla | Pendiente: mismo patrón en Venues, etc. |

**Para ver datos en Instruments:** 1) `make up` (deja Postgres y **control plane** arriba en Docker). 2) Migración 003 aplicada (tabla `instrument_registry`). 3) Abrir la UI (por ejemplo http://localhost:3001 si usas el servicio web-ui) → Operator → Instruments Control. 4) Opcional: insertar datos en `instrument_registry` o usar `nq_instrument_registry` en Python.
