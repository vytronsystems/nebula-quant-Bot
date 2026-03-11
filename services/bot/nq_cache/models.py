# NEBULA-QUANT v1 | nq_cache models

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CacheEntry:
    """Single cached value with optional TTL."""

    key: str
    namespace: str
    value: Any
    created_at_monotonic: float
    expires_at_monotonic: float | None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class CachePolicy:
    """Cache behavior: TTL, capacity, and value rules."""

    default_ttl_seconds: float | None = None
    max_entries: int | None = None
    allow_none_values: bool = False
    namespace_defaults: dict[str, dict[str, Any]] | None = None


@dataclass(slots=True)
class CacheResult:
    """Result of a get: hit/miss, value, and metadata."""

    hit: bool
    value: Any | None
    expired: bool
    namespace: str
    key: str


@dataclass(slots=True)
class CacheStats:
    """Counters for cache operations and current size."""

    hits: int = 0
    misses: int = 0
    expirations: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    size: int = 0
