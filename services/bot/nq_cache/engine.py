# NEBULA-QUANT v1 | nq_cache engine

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from nq_cache.models import CacheEntry, CachePolicy, CacheResult, CacheStats
from nq_cache.namespace import DEFAULT_NAMESPACE
from nq_cache.policy import DEFAULT_CACHE_POLICY, CacheModuleConfigLike, policy_from_config


class CacheError(Exception):
    """Raised on invalid key, namespace, TTL, or policy configuration."""


def cache_engine_from_config(
    config: CacheModuleConfigLike,
    clock: Callable[[], float] | None = None,
) -> CacheEngine:
    """Build CacheEngine from a config (e.g. AppConfig.cache from nq_config)."""
    return CacheEngine(policy=policy_from_config(config), clock=clock)


class CacheEngine:
    """
    Deterministic in-memory cache with namespace separation, TTL, and bounded eviction.
    Clock is injectable for tests. Eviction is oldest-created first when max_entries is set.
    """

    def __init__(
        self,
        policy: CachePolicy | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._policy = policy or DEFAULT_CACHE_POLICY
        self._clock = clock or time.monotonic
        self._store: dict[tuple[str, str], CacheEntry] = {}
        self._creation_order: list[tuple[str, str]] = []
        self._stats = CacheStats()

    def _validate_key(self, key: str) -> None:
        if key is None or not isinstance(key, str) or not key.strip():
            raise CacheError("key must be a non-empty string")

    def _validate_namespace(self, namespace: str | None) -> str:
        if namespace is not None and not namespace.strip():
            raise CacheError("namespace must be non-empty when provided")
        ns = (namespace or DEFAULT_NAMESPACE).strip()
        return ns

    def _ttl_seconds(
        self, ttl_seconds: float | None, namespace: str
    ) -> float | None:
        if ttl_seconds is not None:
            if ttl_seconds < 0:
                raise CacheError("ttl_seconds must be non-negative")
            return ttl_seconds
        return self._policy.default_ttl_seconds

    def _make_entry(
        self, key: str, namespace: str, value: Any, ttl_seconds: float | None
    ) -> CacheEntry:
        now = self._clock()
        expires = (now + ttl_seconds) if ttl_seconds is not None else None
        return CacheEntry(
            key=key,
            namespace=namespace,
            value=value,
            created_at_monotonic=now,
            expires_at_monotonic=expires,
            metadata={},
        )

    def _evict_one(self) -> None:
        """Evict oldest entry by creation order. Deterministic."""
        if not self._creation_order or self._policy.max_entries is None:
            return
        if len(self._store) < self._policy.max_entries:
            return
        ns_key = self._creation_order.pop(0)
        if ns_key in self._store:
            del self._store[ns_key]
            self._stats.evictions += 1

    def _ensure_capacity(self) -> None:
        if self._policy.max_entries is None:
            return
        while len(self._store) >= self._policy.max_entries and self._creation_order:
            self._evict_one()

    def _remove_expired(self, ns: str, key: str) -> bool:
        """If entry exists and is expired, remove it and return True."""
        ns_key = (ns, key)
        entry = self._store.get(ns_key)
        if entry is None:
            return False
        if entry.expires_at_monotonic is not None and self._clock() >= entry.expires_at_monotonic:
            del self._store[ns_key]
            if ns_key in self._creation_order:
                self._creation_order.remove(ns_key)
            self._stats.expirations += 1
            return True
        return False

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: float | None = None,
        namespace: str | None = None,
    ) -> None:
        self._validate_key(key)
        ns = self._validate_namespace(namespace)
        if not self._policy.allow_none_values and value is None:
            raise CacheError("policy does not allow caching None")
        ttl = self._ttl_seconds(ttl_seconds, ns)
        ns_key = (ns, key)
        is_new = ns_key not in self._store
        if not is_new and ns_key in self._creation_order:
            self._creation_order.remove(ns_key)
        if is_new:
            self._ensure_capacity()
        entry = self._make_entry(key, ns, value, ttl)
        self._store[ns_key] = entry
        self._creation_order.append(ns_key)
        self._stats.sets += 1

    def get(
        self,
        key: str,
        namespace: str | None = None,
    ) -> CacheResult:
        self._validate_key(key)
        ns = self._validate_namespace(namespace)
        ns_key = (ns, key)
        if self._remove_expired(ns, key):
            self._stats.misses += 1
            return CacheResult(hit=False, value=None, expired=True, namespace=ns, key=key)
        entry = self._store.get(ns_key)
        if entry is None:
            self._stats.misses += 1
            return CacheResult(hit=False, value=None, expired=False, namespace=ns, key=key)
        self._stats.hits += 1
        return CacheResult(
            hit=True,
            value=entry.value,
            expired=False,
            namespace=ns,
            key=key,
        )

    def delete(self, key: str, namespace: str | None = None) -> None:
        self._validate_key(key)
        ns = self._validate_namespace(namespace)
        ns_key = (ns, key)
        if ns_key in self._store:
            del self._store[ns_key]
            if ns_key in self._creation_order:
                self._creation_order.remove(ns_key)
            self._stats.deletes += 1

    def clear(self, namespace: str | None = None) -> None:
        if namespace is None:
            self._store.clear()
            self._creation_order.clear()
            return
        ns = self._validate_namespace(namespace)
        to_remove = [nk for nk in self._store if nk[0] == ns]
        for nk in to_remove:
            del self._store[nk]
            if nk in self._creation_order:
                self._creation_order.remove(nk)

    def has(self, key: str, namespace: str | None = None) -> bool:
        result = self.get(key, namespace)
        return result.hit

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl_seconds: float | None = None,
        namespace: str | None = None,
    ) -> Any:
        self._validate_key(key)
        ns = self._validate_namespace(namespace)
        result = self.get(key, namespace)
        if result.hit:
            return result.value
        value = factory()
        if not self._policy.allow_none_values and value is None:
            return None
        self.set(key, value, ttl_seconds=ttl_seconds, namespace=namespace)
        return value

    def stats(self) -> CacheStats:
        return CacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            expirations=self._stats.expirations,
            sets=self._stats.sets,
            deletes=self._stats.deletes,
            evictions=self._stats.evictions,
            size=len(self._store),
        )

    def keys(self, namespace: str | None = None) -> list[str] | list[tuple[str, str]]:
        if namespace is None:
            return list(self._store.keys())
        ns = self._validate_namespace(namespace)
        return [k for (n, k) in self._store if n == ns]

    def size(self, namespace: str | None = None) -> int:
        if namespace is None:
            return len(self._store)
        ns = self._validate_namespace(namespace)
        return sum(1 for (n, _) in self._store if n == ns)
