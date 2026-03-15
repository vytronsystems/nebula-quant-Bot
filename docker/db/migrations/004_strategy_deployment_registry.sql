-- 004_strategy_deployment_registry.sql — Phase 72: persistent registry for strategy deployments
-- Tracks: strategy name, version, instrument, venue, environment (testnet/production), stage (backtest, paper, live)
-- Multiple strategies per instrument supported.

create table if not exists strategy_deployment (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  updated_at timestamp without time zone not null default now(),
  strategy_name varchar(128) not null,
  strategy_version varchar(64) not null,
  instrument varchar(64) not null,
  venue varchar(32) not null,
  environment varchar(24) not null default 'testnet',
  stage varchar(24) not null default 'backtest',
  enabled boolean not null default true,
  meta json null
);

create index if not exists ix_strategy_deployment_instrument on strategy_deployment(instrument);
create index if not exists ix_strategy_deployment_venue on strategy_deployment(venue);
create index if not exists ix_strategy_deployment_stage on strategy_deployment(stage);
create index if not exists ix_strategy_deployment_environment on strategy_deployment(environment);
create unique index if not exists uq_strategy_deployment_lookup
  on strategy_deployment(strategy_name, strategy_version, instrument, venue);

comment on table strategy_deployment is 'Registry of strategy deployments: name, version, instrument, venue, environment, stage (backtest/paper/live)';
