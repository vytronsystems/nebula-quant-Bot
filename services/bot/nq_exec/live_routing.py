# NEBULA-QUANT v1 | Phase 76 — Live Routing
# Route orders by deployment stage: live → production credentials; else → testnet/paper. Fail-closed.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RoutingDecision:
    use_production: bool
    use_testnet: bool
    use_paper: bool
    reason: str
    stage: str


def route_by_stage(stage: str | None) -> RoutingDecision:
    """
    Deterministic routing by stage. Fail-closed: unknown or missing stage → paper.
    - live → production credentials
    - paper, backtest, or any other → testnet/paper (no production)
    """
    if not stage or not stage.strip():
        return RoutingDecision(
            use_production=False,
            use_testnet=True,
            use_paper=True,
            reason="missing_stage_fail_closed",
            stage="",
        )
    s = stage.strip().lower()
    if s == "live":
        return RoutingDecision(
            use_production=True,
            use_testnet=False,
            use_paper=False,
            reason="stage_live",
            stage=s,
        )
    return RoutingDecision(
        use_production=False,
        use_testnet=True,
        use_paper=True,
        reason="stage_not_live",
        stage=s,
    )


def select_adapter_key(stage: str | None) -> str:
    """Returns 'production' or 'testnet' or 'paper' for adapter lookup. Fail-closed to non-live."""
    d = route_by_stage(stage)
    if d.use_production:
        return "production"
    if d.use_paper:
        return "paper"
    return "testnet"
