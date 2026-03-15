-- 006_alerts_and_datasets.sql — Phase 84 Alert System + Phase 85 Dataset Versioning

-- Alerts (dashboard, Telegram, email triggers)
create table if not exists alerts (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  channel varchar(32) not null default 'dashboard',
  severity varchar(24) not null default 'info',
  title varchar(256) not null,
  body text null,
  trigger_type varchar(64) null,
  meta json null
);

create index if not exists ix_alerts_created_at on alerts(created_at desc);
create index if not exists ix_alerts_channel on alerts(channel);

-- Dataset versioning (snapshots, identifiers, reproducibility)
create table if not exists dataset_version (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp without time zone not null default now(),
  dataset_id varchar(128) not null,
  version varchar(64) not null,
  snapshot_path varchar(512) null,
  meta json null
);

create unique index if not exists uq_dataset_version on dataset_version(dataset_id, version);
create index if not exists ix_dataset_version_created_at on dataset_version(created_at desc);
