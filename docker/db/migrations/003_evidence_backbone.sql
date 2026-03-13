-- 003_evidence_backbone.sql — DB-first evidence tracking (phase/test/audit/artifact)

-- Phase execution log (each phase start/end)
create table if not exists phase_execution_log (
  id uuid primary key default gen_random_uuid(),
  phase varchar(32) not null,
  started_at timestamp without time zone not null default now(),
  ended_at timestamp without time zone null,
  status varchar(24) not null default 'running',
  details text null,
  meta json null
);

create index if not exists ix_phase_execution_log_phase on phase_execution_log(phase);
create index if not exists ix_phase_execution_log_started_at on phase_execution_log(started_at desc);

-- Artifact registry (files written per phase)
create table if not exists artifact_registry (
  id uuid primary key default gen_random_uuid(),
  phase varchar(32) not null,
  artifact_path varchar(512) not null,
  artifact_kind varchar(64) not null default 'file',
  created_at timestamp without time zone not null default now(),
  meta json null
);

create index if not exists ix_artifact_registry_phase on artifact_registry(phase);

-- Audit runs
create table if not exists audit_run (
  id uuid primary key default gen_random_uuid(),
  phase varchar(32) null,
  run_at timestamp without time zone not null default now(),
  status varchar(24) not null default 'ok',
  summary text null,
  report_path varchar(512) null,
  meta json null
);

create index if not exists ix_audit_run_phase on audit_run(phase);
create index if not exists ix_audit_run_run_at on audit_run(run_at desc);

-- Test runs
create table if not exists test_run (
  id uuid primary key default gen_random_uuid(),
  phase varchar(32) null,
  run_at timestamp without time zone not null default now(),
  total int not null default 0,
  passed int not null default 0,
  failed int not null default 0,
  report_path varchar(512) null,
  meta json null
);

create index if not exists ix_test_run_phase on test_run(phase);
create index if not exists ix_test_run_run_at on test_run(run_at desc);

-- Promotion review (lifecycle governance)
create table if not exists promotion_review (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  strategy_id varchar(64) null,
  from_stage varchar(32) not null,
  to_stage varchar(32) not null,
  decision varchar(24) not null,
  evidence_path varchar(512) null,
  meta json null
);

create index if not exists ix_promotion_review_created_at on promotion_review(created_at desc);

-- Paper trading daily snapshot
create table if not exists paper_trading_daily_snapshot (
  id uuid primary key default gen_random_uuid(),
  snapshot_date date not null,
  created_at timestamp without time zone not null default now(),
  equity numeric(18,4) null,
  open_positions json null,
  meta json null
);

create index if not exists ix_paper_trading_daily_snapshot_date on paper_trading_daily_snapshot(snapshot_date desc);

-- Venue account snapshot
create table if not exists venue_account_snapshot (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  venue varchar(32) not null,
  account_id varchar(64) null,
  balance numeric(18,4) null,
  equity numeric(18,4) null,
  meta json null
);

create index if not exists ix_venue_account_snapshot_venue_created_at on venue_account_snapshot(venue, created_at desc);

-- Instrument registry (instruments available per venue)
create table if not exists instrument_registry (
  id uuid primary key default gen_random_uuid(),
  venue varchar(32) not null,
  symbol varchar(64) not null,
  asset_type varchar(16) not null default 'spot',
  active boolean not null default true,
  created_at timestamp without time zone not null default now(),
  updated_at timestamp without time zone not null default now(),
  meta json null,
  unique(venue, symbol)
);

create index if not exists ix_instrument_registry_venue_active on instrument_registry(venue, active);

-- Instrument activation log (audit trail for add/remove/activate/deactivate)
create table if not exists instrument_activation_log (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  venue varchar(32) not null,
  symbol varchar(64) not null,
  action varchar(32) not null,
  meta json null
);

create index if not exists ix_instrument_activation_log_venue_created_at on instrument_activation_log(venue, created_at desc);
