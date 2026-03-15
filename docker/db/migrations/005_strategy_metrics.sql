-- 005_strategy_metrics.sql — Phase 74: performance metrics per deployment
-- WinRate, PnL, Trades, Days, Profit Factor, Max Drawdown

create table if not exists strategy_metrics (
  id uuid primary key default gen_random_uuid(),
  deployment_id uuid not null references strategy_deployment(id) on delete cascade,
  computed_at timestamp without time zone not null default now(),
  win_rate numeric(8,4) null,
  pnl numeric(18,4) null,
  trades_count int not null default 0,
  days_count int not null default 0,
  profit_factor numeric(12,4) null,
  max_drawdown numeric(12,4) null,
  meta json null
);

create unique index if not exists uq_strategy_metrics_deployment on strategy_metrics(deployment_id);
create index if not exists ix_strategy_metrics_computed_at on strategy_metrics(computed_at desc);

comment on table strategy_metrics is 'Computed performance metrics per strategy deployment (Phase 74 Metrics Engine)';
