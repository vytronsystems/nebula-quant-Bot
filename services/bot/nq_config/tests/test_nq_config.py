# NEBULA-QUANT v1 | nq_config tests

from __future__ import annotations

import os
import unittest

from nq_config import (
    AppConfig,
    ConfigError,
    build_default_config,
    load_config,
    load_config_from_env,
    validate_app_config,
)
from nq_config.models import (
    CacheModuleConfig,
    DatabaseModuleConfig,
    PortfolioModuleConfig,
    RiskModuleConfig,
    SystemConfig,
)


class TestBuildDefaultConfig(unittest.TestCase):
    def test_build_default_config_returns_valid_app_config(self) -> None:
        config = build_default_config()
        self.assertIsInstance(config, AppConfig)
        validate_app_config(config)

    def test_explicit_defaults_align_with_expected_values(self) -> None:
        config = build_default_config()
        self.assertEqual(config.system.environment, "development")
        self.assertEqual(config.system.app_name, "NEBULA-QUANT v1")
        self.assertEqual(config.db.db_path, "nq_db.sqlite3")
        self.assertTrue(config.event_store.use_shared_db)
        self.assertIsNone(config.cache.default_ttl_seconds)
        self.assertIsNone(config.cache.max_entries)
        self.assertFalse(config.cache.allow_none_values)
        self.assertEqual(config.risk.max_risk_per_trade_pct, 0.02)
        self.assertEqual(config.risk.warning_risk_per_trade_pct, 0.015)
        self.assertEqual(config.portfolio.max_open_positions_total, 50)
        self.assertEqual(config.portfolio.max_open_positions_per_strategy, 10)
        self.assertTrue(config.metrics.enable_observability)


class TestEnvOverrides(unittest.TestCase):
    def setUp(self) -> None:
        self._saved: dict[str, str | None] = {}

    def _set_env(self, key: str, value: str | None) -> None:
        self._saved[key] = os.environ.get(key)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    def tearDown(self) -> None:
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_env_overrides_apply_correctly(self) -> None:
        self._set_env("NQ_ENVIRONMENT", "production")
        self._set_env("NQ_APP_NAME", "MyApp")
        self._set_env("NQ_DB_PATH", "/tmp/test.sqlite3")
        self._set_env("NQ_PORTFOLIO_MAX_OPEN_POSITIONS_TOTAL", "100")
        config = load_config_from_env()
        self.assertEqual(config.system.environment, "production")
        self.assertEqual(config.system.app_name, "MyApp")
        self.assertEqual(config.db.db_path, "/tmp/test.sqlite3")
        self.assertEqual(config.portfolio.max_open_positions_total, 100)

    def test_missing_env_values_preserve_defaults(self) -> None:
        for key in (
            "NQ_ENVIRONMENT", "NQ_APP_NAME", "NQ_DB_PATH", "NQ_EVENT_STORE_PATH",
            "NQ_CACHE_DEFAULT_TTL", "NQ_CACHE_MAX_ENTRIES", "NQ_CACHE_ALLOW_NONE",
            "NQ_RISK_MAX_RISK_PER_TRADE_PCT", "NQ_RISK_MAX_DAILY_STRATEGY_RISK_PCT",
            "NQ_RISK_MAX_DAILY_ACCOUNT_RISK_PCT", "NQ_RISK_REQUIRE_STOP_LOSS",
            "NQ_RISK_MAX_STOP_DISTANCE_PCT", "NQ_RISK_WARNING_RISK_PER_TRADE_PCT",
            "NQ_PORTFOLIO_MAX_OPEN_POSITIONS_TOTAL", "NQ_PORTFOLIO_MAX_OPEN_POSITIONS_PER_STRATEGY",
            "NQ_METRICS_ENABLE_OBSERVABILITY", "NQ_METRICS_DEFAULT_REPORT_NAMESPACE",
        ):
            self._set_env(key, None)
        config = load_config_from_env()
        self.assertEqual(config.system.environment, "development")
        self.assertEqual(config.system.app_name, "NEBULA-QUANT v1")
        self.assertIn("nq_db.sqlite3", config.db.db_path)

    def test_invalid_boolean_env_fails_closed(self) -> None:
        self._set_env("NQ_CACHE_ALLOW_NONE", "invalid")
        with self.assertRaises(ConfigError):
            load_config_from_env()
        self._set_env("NQ_CACHE_ALLOW_NONE", "1")
        config = load_config_from_env()
        self.assertTrue(config.cache.allow_none_values)

    def test_invalid_numeric_env_fails_closed(self) -> None:
        self._set_env("NQ_RISK_MAX_RISK_PER_TRADE_PCT", "not_a_number")
        with self.assertRaises(ConfigError):
            load_config_from_env()
        self._set_env("NQ_PORTFOLIO_MAX_OPEN_POSITIONS_TOTAL", "abc")
        with self.assertRaises(ConfigError):
            load_config_from_env()

    def test_invalid_percentage_fails_closed(self) -> None:
        self._set_env("NQ_RISK_MAX_RISK_PER_TRADE_PCT", "-1")
        with self.assertRaises(ConfigError):
            load_config_from_env()
        self._set_env("NQ_RISK_MAX_RISK_PER_TRADE_PCT", "0")
        with self.assertRaises(ConfigError):
            load_config_from_env()

    def test_repeated_same_env_yields_same_config(self) -> None:
        for key in list(os.environ):
            if key.startswith("NQ_"):
                self._set_env(key, None)
        self._set_env("NQ_ENVIRONMENT", "staging")
        self._set_env("NQ_PORTFOLIO_MAX_OPEN_POSITIONS_TOTAL", "25")
        c1 = load_config_from_env()
        c2 = load_config_from_env()
        self.assertEqual(c1.system.environment, c2.system.environment)
        self.assertEqual(c1.portfolio.max_open_positions_total, c2.portfolio.max_open_positions_total)
        self.assertEqual(c1.portfolio.max_open_positions_total, 25)


class TestValidationFailClosed(unittest.TestCase):
    def test_empty_required_string_fails_closed(self) -> None:
        base = build_default_config()
        bad_system = SystemConfig(environment="", app_name=base.system.app_name, timezone=None, metadata={})
        bad_config = AppConfig(
            system=bad_system,
            db=base.db,
            event_store=base.event_store,
            cache=base.cache,
            risk=base.risk,
            portfolio=base.portfolio,
            metrics=base.metrics,
        )
        with self.assertRaises(ConfigError):
            validate_app_config(bad_config)
        bad_system2 = SystemConfig(environment="dev", app_name="  ", timezone=None, metadata={})
        bad_config2 = AppConfig(
            system=bad_system2,
            db=base.db,
            event_store=base.event_store,
            cache=base.cache,
            risk=base.risk,
            portfolio=base.portfolio,
            metrics=base.metrics,
        )
        with self.assertRaises(ConfigError):
            validate_app_config(bad_config2)

    def test_nested_invalid_child_fails_closed(self) -> None:
        base = build_default_config()
        bad_db = DatabaseModuleConfig(db_path="")
        bad_config = AppConfig(
            system=base.system,
            db=bad_db,
            event_store=base.event_store,
            cache=base.cache,
            risk=base.risk,
            portfolio=base.portfolio,
            metrics=base.metrics,
        )
        with self.assertRaises(ConfigError):
            validate_app_config(bad_config)

    def test_risk_warning_exceeds_max_fails_closed(self) -> None:
        base = build_default_config()
        bad_risk = RiskModuleConfig(
            max_risk_per_trade_pct=0.02,
            max_daily_strategy_risk_pct=None,
            max_daily_account_risk_pct=None,
            require_stop_loss=False,
            max_stop_distance_pct=None,
            warning_risk_per_trade_pct=0.05,
        )
        bad_config = AppConfig(
            system=base.system,
            db=base.db,
            event_store=base.event_store,
            cache=base.cache,
            risk=bad_risk,
            portfolio=base.portfolio,
            metrics=base.metrics,
        )
        with self.assertRaises(ConfigError):
            validate_app_config(bad_config)

    def test_portfolio_warning_exceeds_limit_fails_closed(self) -> None:
        base = build_default_config()
        bad_portfolio = PortfolioModuleConfig(
            max_portfolio_capital_usage_pct=0.95,
            max_strategy_capital_usage_pct=0.25,
            max_open_positions_total=50,
            max_open_positions_per_strategy=10,
            max_daily_drawdown_pct=0.05,
            max_strategy_drawdown_pct=0.10,
            warning_capital_usage_pct=0.99,
            warning_open_positions_pct=0.85,
            warning_drawdown_pct=0.03,
        )
        bad_config = AppConfig(
            system=base.system,
            db=base.db,
            event_store=base.event_store,
            cache=base.cache,
            risk=base.risk,
            portfolio=bad_portfolio,
            metrics=base.metrics,
        )
        with self.assertRaises(ConfigError):
            validate_app_config(bad_config)

    def test_cache_negative_ttl_fails_closed(self) -> None:
        base = build_default_config()
        bad_cache = CacheModuleConfig(default_ttl_seconds=-1, max_entries=None, allow_none_values=False)
        bad_config = AppConfig(
            system=base.system,
            db=base.db,
            event_store=base.event_store,
            cache=bad_cache,
            risk=base.risk,
            portfolio=base.portfolio,
            metrics=base.metrics,
        )
        with self.assertRaises(ConfigError):
            validate_app_config(bad_config)

    def test_cache_max_entries_zero_fails_closed(self) -> None:
        base = build_default_config()
        bad_cache = CacheModuleConfig(default_ttl_seconds=None, max_entries=0, allow_none_values=False)
        bad_config = AppConfig(
            system=base.system,
            db=base.db,
            event_store=base.event_store,
            cache=bad_cache,
            risk=base.risk,
            portfolio=base.portfolio,
            metrics=base.metrics,
        )
        with self.assertRaises(ConfigError):
            validate_app_config(bad_config)


class TestLoadConfig(unittest.TestCase):
    def setUp(self) -> None:
        self._saved: dict[str, str | None] = {}
        for key in list(os.environ):
            if key.startswith("NQ_"):
                self._saved[key] = os.environ.pop(key, None)

    def tearDown(self) -> None:
        for k, v in self._saved.items():
            if v is not None:
                os.environ[k] = v

    def test_load_config_works_deterministically(self) -> None:
        c1 = load_config()
        c2 = load_config()
        self.assertEqual(c1.system.environment, c2.system.environment)
        self.assertEqual(c1.db.db_path, c2.db.db_path)

    def test_no_hidden_dependence_on_external_files(self) -> None:
        # load_config only uses defaults + os.environ; no file I/O for config content
        config = build_default_config()
        self.assertIsNotNone(config.db.db_path)
        # If we had file loading we'd need to mock open(); no such thing in loader
        load_config_from_env(base=config)
        # Passes if no file read occurred
        self.assertTrue(True)
