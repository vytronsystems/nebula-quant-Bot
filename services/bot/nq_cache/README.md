# nq_cache

Deterministic in-process cache for NEBULA-QUANT v1. Caches read-side data to reduce repeated reconstruction or DB lookups; supports namespaces, TTL, explicit invalidation, and bounded size. Not a source of truth — misses are reported deterministically and callers refetch from the authoritative store (e.g. nq_db).

## Purpose

- **Cache** frequently accessed read-side data in memory.
- **Reduce** repeated DB reads or recomputation for stable lookups.
- **Support** explicit invalidation and bounded lifetime (TTL / max entries).
- **Remain** independent from business logic; fail closed on invalid input.

## Deterministic in-memory design

- No Redis, Memcached, or external services; standard library only.
- All behavior is deterministic given the same sequence of operations and (when used) injectable clock for tests.
- Expiration uses monotonic time; clock can be injected for reproducible tests.

## Namespace model

Cached entries are segregated by **namespace** (e.g. `strategy_registry`, `observability`, `risk`, `portfolio`, `system`). Default namespace is `default`. Operations take an optional `namespace`; `keys(namespace)` and `size(namespace)` are per-namespace; `clear(namespace)` clears only that namespace; `clear()` with no namespace clears the entire cache.

## TTL / expiration

- Optional **TTL** per `set()` or via policy `default_ttl_seconds`.
- Expiration is based on **monotonic time** (configurable via `clock` in the engine).
- When an entry is expired, it is treated as a **miss**: the entry is removed, expiration is counted, and the caller receives a miss (no value fabricated).

## Eviction policy

When **max_entries** is set and the cache is at capacity, a **new** set evicts the **oldest entry by creation time** (first inserted). Eviction is deterministic: no random eviction. Replacing an existing key does not count toward capacity for eviction (same key is updated in place).

## Cache is not source of truth

- The cache is a **performance optimization** only.
- Authoritative data lives in nq_db, nq_event_store, or domain modules.
- On **miss or expiration**, the cache returns a miss; it never fabricates data.
- Callers should refetch or recompute from the real source when they get a miss.

## Intended future integration points

- **nq_strategy_registry**: cache strategy lookup results.
- **nq_obs / nq_metrics**: cache observability snapshots or aggregates.
- **nq_portfolio / nq_promotion**: cache portfolio or promotion read models.
- **nq_db-backed read models**: cache results of expensive queries.

No deep wiring into these modules in this phase; only the cache foundation and this documentation.

## Usage example

```python
import time
from nq_cache import CacheEngine, CachePolicy, NAMESPACE_STRATEGY_REGISTRY

policy = CachePolicy(default_ttl_seconds=60.0, max_entries=1000)
cache = CacheEngine(policy=policy)

cache.set("strategy:v1", {"id": "v1", "name": "Alpha"}, ttl_seconds=30, namespace=NAMESPACE_STRATEGY_REGISTRY)
result = cache.get("strategy:v1", namespace=NAMESPACE_STRATEGY_REGISTRY)
if result.hit:
    use(result.value)

value = cache.get_or_set("expensive-key", factory=lambda: load_from_db(), ttl_seconds=60)
stats = cache.stats()
cache.clear(namespace=NAMESPACE_STRATEGY_REGISTRY)
```

## Configuration

- **CachePolicy**: `default_ttl_seconds`, `max_entries`, `allow_none_values`, `namespace_defaults`.
- **Clock**: pass `clock=your_callable` to `CacheEngine` for tests (e.g. a counter or list of monotonic values).
- **nq_config integration**: `cache_engine_from_config(app_config.cache)` or `policy_from_config(app_config.cache)` with `AppConfig` from `nq_config`.

## Fail-closed behavior

Invalid key (empty or not a string), invalid namespace, or negative TTL raise `CacheError`. The cache does not silently coerce invalid configuration or fabricate values on miss.
