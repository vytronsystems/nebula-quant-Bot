# NEBULA-QUANT v1 | nq_config integration tests (core modules from AppConfig)

from __future__ import annotations

import tempfile
import unittest

from nq_config import build_default_config


class TestNqDbFromAppConfig(unittest.TestCase):
    def test_nq_db_initializes_from_app_config(self) -> None:
        from nq_config.models import DatabaseModuleConfig
        from nq_db import engine_from_config

        with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
            config = DatabaseModuleConfig(db_path=tmp.name)
            engine = engine_from_config(config)
            self.assertIsNotNone(engine)
            row = engine.fetch_one("SELECT 1")
            self.assertIsNotNone(row)
            self.assertEqual(list(row.values()), [1])
            engine.close()

    def test_nq_db_from_app_config_fails_closed_on_empty_path(self) -> None:
        from nq_db import engine_from_config
        from nq_db.engine import DatabaseError

        class BadConfig:
            db_path = ""

        with self.assertRaises(DatabaseError):
            engine_from_config(BadConfig())


class TestNqEventStoreFromAppConfig(unittest.TestCase):
    def test_nq_event_store_initializes_from_app_config(self) -> None:
        from nq_config.models import EventStoreConfig
        from nq_event_store import EventStoreRepository, engine_from_config

        with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
            config = EventStoreConfig(db_path=tmp.name, use_shared_db=False)
            store = engine_from_config(config)
            repo = EventStoreRepository(store.engine)
            self.assertEqual(repo.fetch_all(), [])
            store.close()

    def test_nq_event_store_fails_closed_when_db_path_none(self) -> None:
        from nq_event_store import engine_from_config
        from nq_event_store.engine import EventStoreError

        class BadConfig:
            db_path = None

        with self.assertRaises(EventStoreError):
            engine_from_config(BadConfig())


class TestNqCacheFromAppConfig(unittest.TestCase):
    def test_nq_cache_initializes_from_app_config(self) -> None:
        from nq_cache import cache_engine_from_config

        config = build_default_config()
        cache = cache_engine_from_config(config.cache)
        cache.set("k", "v")
        r = cache.get("k")
        self.assertTrue(r.hit)
        self.assertEqual(r.value, "v")

    def test_nq_cache_policy_from_config_matches_app_config(self) -> None:
        from nq_cache import policy_from_config

        config = build_default_config()
        policy = policy_from_config(config.cache)
        self.assertEqual(policy.default_ttl_seconds, config.cache.default_ttl_seconds)
        self.assertEqual(policy.max_entries, config.cache.max_entries)
        self.assertEqual(policy.allow_none_values, config.cache.allow_none_values)


class TestNqRiskLimitsFromAppConfig(unittest.TestCase):
    def test_nq_risk_limits_derived_from_app_config(self) -> None:
        from nq_risk import risk_limits_from_config

        config = build_default_config()
        limits = risk_limits_from_config(config.risk)
        self.assertEqual(limits.max_risk_per_trade_pct, config.risk.max_risk_per_trade_pct)
        self.assertEqual(limits.warning_risk_per_trade_pct, config.risk.warning_risk_per_trade_pct)

    def test_repeated_same_config_yields_same_limits(self) -> None:
        from nq_risk import risk_limits_from_config

        config = build_default_config()
        a = risk_limits_from_config(config.risk)
        b = risk_limits_from_config(config.risk)
        self.assertEqual(a.max_risk_per_trade_pct, b.max_risk_per_trade_pct)


class TestNqPortfolioLimitsFromAppConfig(unittest.TestCase):
    def test_nq_portfolio_limits_derived_from_app_config(self) -> None:
        from nq_portfolio import portfolio_limits_from_config

        config = build_default_config()
        limits = portfolio_limits_from_config(config.portfolio)
        self.assertEqual(limits.max_open_positions_total, config.portfolio.max_open_positions_total)
        self.assertEqual(limits.warning_capital_usage_pct, config.portfolio.warning_capital_usage_pct)

    def test_repeated_same_config_yields_same_limits(self) -> None:
        from nq_portfolio import portfolio_limits_from_config

        config = build_default_config()
        a = portfolio_limits_from_config(config.portfolio)
        b = portfolio_limits_from_config(config.portfolio)
        self.assertEqual(a.max_open_positions_total, b.max_open_positions_total)


class TestNqMetricsFromAppConfig(unittest.TestCase):
    def test_nq_metrics_config_integration(self) -> None:
        from nq_metrics import default_report_namespace, observability_enabled

        config = build_default_config()
        self.assertTrue(observability_enabled(config.metrics))
        self.assertEqual(default_report_namespace(config.metrics), config.metrics.default_report_namespace)


class TestLegacyDefaultInitialization(unittest.TestCase):
    def test_nq_db_legacy_no_arg_initialization(self) -> None:
        from nq_db import DatabaseEngine

        with tempfile.NamedTemporaryFile(suffix=".sqlite3") as tmp:
            engine = DatabaseEngine(db_path=tmp.name)
            self.assertIsNotNone(engine.fetch_one("SELECT 1"))
            engine.close()

    def test_nq_cache_legacy_no_arg_initialization(self) -> None:
        from nq_cache import CacheEngine

        cache = CacheEngine()
        cache.set("x", 1)
        self.assertEqual(cache.get("x").value, 1)

    def test_nq_risk_default_limits_unchanged(self) -> None:
        from nq_risk import DEFAULT_RISK_LIMITS

        self.assertEqual(DEFAULT_RISK_LIMITS.max_risk_per_trade_pct, 0.02)

    def test_nq_portfolio_default_limits_unchanged(self) -> None:
        from nq_portfolio.config import DEFAULT_PORTFOLIO_LIMITS

        self.assertEqual(DEFAULT_PORTFOLIO_LIMITS.max_open_positions_total, 50)
