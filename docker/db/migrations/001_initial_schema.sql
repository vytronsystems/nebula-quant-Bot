-- 001_initial_schema.sql
create extension if not exists pgcrypto;

create table if not exists bot_runs (
  id uuid primary key default gen_random_uuid(),
  started_at timestamp without time zone not null default now(),
  ended_at timestamp without time zone null,
  env varchar(32) not null default 'local',
  version varchar(64) not null default 'dev',
  status varchar(24) not null default 'running',
  meta json null
);

create table if not exists decision_snapshots (
  id uuid primary key default gen_random_uuid(),
  bot_run_id uuid null references bot_runs(id) on delete set null,
  created_at timestamp without time zone not null default now(),
  symbol varchar(16) not null default 'QQQ',
  timeframe varchar(16) not null default '5m',
  session_tag varchar(32) not null default 'regular',
  decision varchar(24) not null,
  direction varchar(8) null,
  confidence integer null,
  policy_hash varchar(64) not null,
  user_params json not null,
  derived_params json not null,
  indicators json not null,
  levels json null,
  news_context json null,
  contract json null,
  reason_code varchar(64) null,
  reason_detail text null
);

create table if not exists orders (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  broker varchar(24) not null default 'tradestation',
  account_id varchar(64) null,
  symbol varchar(32) not null,
  side varchar(8) not null,
  qty integer not null,
  order_type varchar(16) not null,
  limit_price numeric(18,6) null,
  status varchar(16) not null default 'new',
  broker_order_id varchar(64) null,
  raw_request json null,
  raw_response json null
);

create table if not exists executions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  order_id uuid null references orders(id) on delete set null,
  broker_exec_id varchar(64) null,
  qty integer not null default 0,
  price numeric(18,6) null,
  meta json null
);

create table if not exists trades (
  id uuid primary key default gen_random_uuid(),
  opened_at timestamp without time zone not null default now(),
  closed_at timestamp without time zone null,
  symbol varchar(32) not null,
  direction varchar(16) not null,
  qty integer not null,
  entry_price numeric(18,6) null,
  exit_price numeric(18,6) null,
  pnl_usd numeric(18,2) null,
  rr numeric(10,4) null,
  meta json null
);

create table if not exists errors (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  component varchar(64) not null,
  severity varchar(16) not null default 'error',
  message text not null,
  meta json null
);

create index if not exists ix_bot_runs_started_at on bot_runs(started_at desc);
create index if not exists ix_decision_snapshots_created_at on decision_snapshots(created_at desc);
create index if not exists ix_decision_snapshots_symbol_created_at on decision_snapshots(symbol, created_at desc);
