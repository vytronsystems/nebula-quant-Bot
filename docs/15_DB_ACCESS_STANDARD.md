# NEBULA-QUANT v1 | DB Access Standard

## Objetivo
Definir el estándar institucional para acceso a base de datos en el runtime actual.

## Fuente única de DSN
- **Variable de entorno**: `PG_DSN`
- **Configuración runtime**: `bot.config.PG_DSN`
- **Formato**: `postgresql://user:pass@host:port/dbname` (compatible con psycopg 3.x)

## Estándar operativo actual
- **Driver**: psycopg directo (no SQLAlchemy en el flujo runtime)
- **Uso**: `from bot.config import PG_DSN` y `psycopg.connect(PG_DSN)`
- **Módulos que acceden a BD**: `bot.audit.logger` (start_run, end_run, log_no_trade)

## Código fuera del flujo
- `bot/db/session.py`: **DEPRECATED**. SQLAlchemy SessionLocal/engine. No se usa en producción.
- `configs/settings.DB_DSN`: Solo para session.py (deprecated). Formato SQLAlchemy `postgresql+psycopg://`.

## Reglas
1. Todo acceso a BD en runtime debe usar `bot.config.PG_DSN` y psycopg.
2. No importar `SessionLocal` ni `engine` de `bot.db.session` en código de producción.
3. Los modelos en `bot/db/models.py` documentan el esquema; la persistencia es SQL explícito.
4. El DSN se inyecta por variable de entorno en Docker; el default es para desarrollo local.
