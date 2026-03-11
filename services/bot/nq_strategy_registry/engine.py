# NEBULA-QUANT v1 | nq_strategy_registry engine

import time
from dataclasses import replace
from typing import Any

from nq_strategy_registry.models import (
    RegistryLookupResult,
    StrategyDefinition,
    StrategyRegistrationRecord,
    StrategyRegistryResult,
)
from nq_strategy_registry.storage import (
    add_strategy,
    update_strategy,
    get_strategy_by_id,
    list_all_strategies,
)
from nq_strategy_registry.config import (
    DEFAULT_STRATEGY_OWNER,
    DEFAULT_MARKET,
    DEFAULT_TIMEFRAME,
    DEFAULT_STATUS,
)
from nq_strategy_registry.status import (
    STATUS_LIVE,
    STATUS_PAPER,
    STATUS_DISABLED,
    STATUS_RETIRED,
    STATUS_REJECTED,
)


class StrategyRegistryEngine:
    """
    Strategy lifecycle control layer. Registers and tracks strategies.
    Does not execute strategies, backtest, or connect to external systems.
    In-memory only (skeleton).
    """

    def __init__(self) -> None:
        pass

    def register_strategy(
        self,
        strategy_id: str,
        name: str,
        version: str = "1.0.0",
        status: str | None = None,
        market: str | None = None,
        instrument_type: str = "equity",
        timeframe: str | None = None,
        regime_target: str = "",
        risk_profile: str = "",
        hypothesis: str = "",
        activation_rules: dict[str, Any] | None = None,
        deactivation_rules: dict[str, Any] | None = None,
        owner: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StrategyDefinition:
        """Register a strategy. Safe defaults; no runtime errors on empty inputs."""
        now = time.time()
        definition = StrategyDefinition(
            strategy_id=strategy_id or "",
            name=name or "",
            version=version or "1.0.0",
            status=status or DEFAULT_STATUS,
            market=market or DEFAULT_MARKET,
            instrument_type=instrument_type or "equity",
            timeframe=timeframe or DEFAULT_TIMEFRAME,
            regime_target=regime_target or "",
            risk_profile=risk_profile or "",
            hypothesis=hypothesis or "",
            activation_rules=activation_rules or {},
            deactivation_rules=deactivation_rules or {},
            owner=owner or DEFAULT_STRATEGY_OWNER,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        add_strategy(definition)
        return definition

    def update_strategy_status(self, strategy_id: str, new_status: str) -> StrategyDefinition | None:
        """Update status of a strategy. Returns updated definition or None if not found."""
        existing = get_strategy_by_id(strategy_id)
        if existing is None:
            return None
        updated = replace(existing, status=new_status, updated_at=time.time())
        update_strategy(updated)
        return updated

    def get_strategy(self, strategy_id: str) -> StrategyDefinition | None:
        """Return strategy by id or None."""
        return get_strategy_by_id(strategy_id or "")

    def get_registration_record(self, strategy_id: str) -> RegistryLookupResult:
        """
        Strict lookup for lifecycle governance. Source of truth for registration and lifecycle state.
        Fail-closed: missing id, not found, malformed record, or ambiguous → ok=False with reason_codes.
        """
        if not strategy_id or not str(strategy_id).strip():
            return RegistryLookupResult(
                ok=False,
                record=None,
                reason_codes=["missing_strategy_id"],
                message="registry: strategy_id missing",
            )
        sid = str(strategy_id).strip()
        definition = get_strategy_by_id(sid)
        if definition is None:
            return RegistryLookupResult(
                ok=False,
                record=None,
                reason_codes=["strategy_not_found"],
                message=f"registry: strategy {sid!r} not found",
            )
        status = getattr(definition, "status", None)
        if not status or not isinstance(status, str) or not status.strip():
            return RegistryLookupResult(
                ok=False,
                record=None,
                reason_codes=["missing_lifecycle_state"],
                message="registry: lifecycle state missing or malformed",
            )
        lifecycle_state = status.strip().lower()
        disabled_states = {STATUS_DISABLED, STATUS_RETIRED, STATUS_REJECTED}
        enabled = lifecycle_state not in disabled_states
        record = StrategyRegistrationRecord(
            strategy_id=definition.strategy_id,
            version=getattr(definition, "version", "") or "",
            lifecycle_state=lifecycle_state,
            enabled=enabled,
            metadata=getattr(definition, "metadata", None) or {},
        )
        return RegistryLookupResult(
            ok=True,
            record=record,
            reason_codes=[],
            message="ok",
        )

    def list_strategies(
        self,
        status_filter: str | None = None,
    ) -> list[StrategyDefinition]:
        """List strategies; optional filter by status."""
        all_s = list_all_strategies()
        if not status_filter:
            return all_s
        return [s for s in all_s if s.status == status_filter]

    def build_registry_result(
        self,
        strategies: list[StrategyDefinition] | None = None,
    ) -> StrategyRegistryResult:
        """Build StrategyRegistryResult from strategy list. Safe for empty."""
        strategies = strategies if strategies is not None else list_all_strategies()
        active = sum(1 for s in strategies if s.status in (STATUS_LIVE, STATUS_PAPER))
        disabled = sum(1 for s in strategies if s.status in (STATUS_DISABLED, STATUS_RETIRED, STATUS_REJECTED))
        return StrategyRegistryResult(
            strategies=list(strategies),
            total_strategies=len(strategies),
            active_strategies=active,
            disabled_strategies=disabled,
            metadata={"skeleton": True},
        )
