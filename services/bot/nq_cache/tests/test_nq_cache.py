# NEBULA-QUANT v1 | nq_cache tests

from __future__ import annotations

import unittest
from typing import Any

from nq_cache import (
    CacheEngine,
    CacheError,
    CachePolicy,
    DEFAULT_NAMESPACE,
    NAMESPACE_PORTFOLIO,
    NAMESPACE_RISK,
)


def make_clock(ticks: list[float]) -> tuple[list[float], Any]:
    """Returns (ticks list, clock callable). clock() returns next tick."""
    it = iter(ticks)

    def clock() -> float:
        return next(it)

    return ticks, clock


class TestSetGet(unittest.TestCase):
    def test_set_get_works_for_valid_keys(self) -> None:
        cache = CacheEngine()
        cache.set("k1", "v1")
        r = cache.get("k1")
        self.assertTrue(r.hit)
        self.assertEqual(r.value, "v1")
        self.assertFalse(r.expired)
        self.assertEqual(r.namespace, DEFAULT_NAMESPACE)
        self.assertEqual(r.key, "k1")


class TestNamespaceSeparation(unittest.TestCase):
    def test_namespace_separation(self) -> None:
        cache = CacheEngine()
        cache.set("x", "from-default", namespace=DEFAULT_NAMESPACE)
        cache.set("x", "from-risk", namespace=NAMESPACE_RISK)
        cache.set("x", "from-portfolio", namespace=NAMESPACE_PORTFOLIO)
        self.assertEqual(cache.get("x").value, "from-default")
        self.assertEqual(cache.get("x", namespace=NAMESPACE_RISK).value, "from-risk")
        self.assertEqual(cache.get("x", namespace=NAMESPACE_PORTFOLIO).value, "from-portfolio")
        self.assertEqual(cache.size(), 3)
        self.assertEqual(cache.size(DEFAULT_NAMESPACE), 1)
        self.assertEqual(cache.size(NAMESPACE_RISK), 1)


class TestMiss(unittest.TestCase):
    def test_missing_key_returns_deterministic_miss(self) -> None:
        cache = CacheEngine()
        r = cache.get("nonexistent")
        self.assertFalse(r.hit)
        self.assertIsNone(r.value)
        self.assertFalse(r.expired)
        self.assertEqual(r.key, "nonexistent")


class TestTTLExpiration(unittest.TestCase):
    def test_ttl_expiration_with_injected_clock(self) -> None:
        ticks, clock = make_clock([0.0, 0.0, 10.0])
        cache = CacheEngine(clock=clock)
        cache.set("k", "v", ttl_seconds=5.0)
        r1 = cache.get("k")
        self.assertTrue(r1.hit)
        self.assertEqual(r1.value, "v")
        r2 = cache.get("k")
        self.assertFalse(r2.hit)
        self.assertTrue(r2.expired)

    def test_expired_entries_not_returned(self) -> None:
        ticks, clock = make_clock([0.0, 100.0])
        cache = CacheEngine(clock=clock)
        cache.set("k", "v", ttl_seconds=10.0)
        r = cache.get("k")
        self.assertFalse(r.hit)
        self.assertTrue(r.expired)
        self.assertIsNone(r.value)


class TestDelete(unittest.TestCase):
    def test_delete_removes_entries(self) -> None:
        cache = CacheEngine()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.delete("a")
        self.assertFalse(cache.get("a").hit)
        self.assertTrue(cache.get("b").hit)
        self.assertEqual(cache.size(), 1)


class TestClear(unittest.TestCase):
    def test_clear_namespace_clears_only_that_namespace(self) -> None:
        cache = CacheEngine()
        cache.set("k1", "v1", namespace=NAMESPACE_RISK)
        cache.set("k2", "v2", namespace=NAMESPACE_PORTFOLIO)
        cache.clear(namespace=NAMESPACE_RISK)
        self.assertFalse(cache.get("k1", namespace=NAMESPACE_RISK).hit)
        self.assertTrue(cache.get("k2", namespace=NAMESPACE_PORTFOLIO).hit)
        self.assertEqual(cache.size(), 1)

    def test_clear_entire_cache(self) -> None:
        cache = CacheEngine()
        cache.set("a", 1, namespace=NAMESPACE_RISK)
        cache.set("b", 2, namespace=NAMESPACE_PORTFOLIO)
        cache.clear()
        self.assertFalse(cache.get("a", namespace=NAMESPACE_RISK).hit)
        self.assertFalse(cache.get("b", namespace=NAMESPACE_PORTFOLIO).hit)
        self.assertEqual(cache.size(), 0)


class TestGetOrSet(unittest.TestCase):
    def test_get_or_set_returns_cached_value_when_present(self) -> None:
        cache = CacheEngine()
        cache.set("k", "cached")
        calls: list[int] = []

        def factory() -> str:
            calls.append(1)
            return "new"

        out = cache.get_or_set("k", factory)
        self.assertEqual(out, "cached")
        self.assertEqual(len(calls), 0)

    def test_get_or_set_calls_factory_when_missing(self) -> None:
        cache = CacheEngine()
        calls: list[int] = []

        def factory() -> str:
            calls.append(1)
            return "built"

        out = cache.get_or_set("k", factory)
        self.assertEqual(out, "built")
        self.assertEqual(len(calls), 1)
        self.assertEqual(cache.get("k").value, "built")

    def test_get_or_set_does_not_cache_none_when_policy_forbids(self) -> None:
        policy = CachePolicy(allow_none_values=False)
        cache = CacheEngine(policy=policy)

        def factory() -> None:
            return None

        out = cache.get_or_set("k", factory)
        self.assertIsNone(out)
        self.assertFalse(cache.get("k").hit)


class TestMaxEntriesEviction(unittest.TestCase):
    def test_max_entries_eviction_deterministic(self) -> None:
        policy = CachePolicy(max_entries=3)
        cache = CacheEngine(policy=policy)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)
        self.assertEqual(cache.size(), 3)
        self.assertFalse(cache.get("a").hit)
        self.assertTrue(cache.get("b").hit)
        self.assertTrue(cache.get("c").hit)
        self.assertTrue(cache.get("d").hit)
        s = cache.stats()
        self.assertEqual(s.evictions, 1)


class TestStats(unittest.TestCase):
    def test_stats_update_correctly(self) -> None:
        cache = CacheEngine()
        cache.set("k1", "v1")
        cache.get("k1")
        cache.get("k1")
        cache.get("missing")
        cache.delete("k1")
        cache.set("k2", "v2")
        s = cache.stats()
        self.assertEqual(s.hits, 2)
        self.assertEqual(s.misses, 1)
        self.assertEqual(s.sets, 2)
        self.assertEqual(s.deletes, 1)
        self.assertEqual(s.size, 1)


class TestFailClosed(unittest.TestCase):
    def test_invalid_key_fails_closed(self) -> None:
        cache = CacheEngine()
        with self.assertRaises(CacheError):
            cache.set("", "v")
        with self.assertRaises(CacheError):
            cache.get("")
        with self.assertRaises(CacheError):
            cache.get("  ")

    def test_negative_ttl_fails_closed(self) -> None:
        cache = CacheEngine()
        with self.assertRaises(CacheError):
            cache.set("k", "v", ttl_seconds=-1)

    def test_set_none_when_disallowed_fails_closed(self) -> None:
        policy = CachePolicy(allow_none_values=False)
        cache = CacheEngine(policy=policy)
        with self.assertRaises(CacheError):
            cache.set("k", None)

    def test_empty_namespace_fails_closed(self) -> None:
        cache = CacheEngine()
        with self.assertRaises(CacheError):
            cache.set("k", "v", namespace="")


class TestDeterminism(unittest.TestCase):
    def test_repeated_deterministic_operations_consistent(self) -> None:
        cache = CacheEngine()
        for i in range(5):
            cache.set(f"k{i}", i)
        for i in range(5):
            r = cache.get(f"k{i}")
            self.assertTrue(r.hit)
            self.assertEqual(r.value, i)
        keys_def = sorted(cache.keys(namespace=DEFAULT_NAMESPACE))
        self.assertEqual(keys_def, ["k0", "k1", "k2", "k3", "k4"])
