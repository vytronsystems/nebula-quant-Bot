-- 002_phase1_hardening.sql (idempotente)

-- 1) Tabla de errores para auditoría operativa
create table if not exists bot_errors (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  bot_run_id uuid null,
  component varchar(64) not null,
  severity varchar(16) not null default 'ERROR',
  error_type varchar(128) not null,
  message text not null,
  detail text null,
  meta json null
);

create index if not exists ix_bot_errors_created_at on bot_errors(created_at desc);
create index if not exists ix_bot_errors_bot_run_id on bot_errors(bot_run_id);

-- 2) Índices útiles
create index if not exists ix_bot_runs_started_at on bot_runs(started_at desc);
create index if not exists ix_decision_snapshots_created_at on decision_snapshots(created_at desc);

-- 3) Tabla de control (circuit breaker básico persistente)
create table if not exists bot_state (
  key varchar(64) primary key,
  value json not null,
  updated_at timestamp without time zone not null default now()
);

-- 4) Guardrails: retención (1 año) se hará por housekeeping script (ver scripts/nq-housekeeping.sh)
