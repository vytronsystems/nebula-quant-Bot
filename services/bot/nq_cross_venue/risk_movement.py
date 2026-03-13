"""
Controlled risk movement service hooks.
Risk movement between venues or within limits must go through approval (Drools/control plane).
This module defines the hook interface; implementation is policy-driven (Phase 66+).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskMovementRequest:
    """Request to move risk/capital (subject to approval)."""
    from_venue: str
    to_venue: str
    amount: float
    reason: str
    meta: dict[str, Any] | None = None


@dataclass
class RiskMovementResult:
    """Result of risk movement (approved/rejected by policy)."""
    approved: bool
    reason: str
    meta: dict[str, Any] | None = None


def risk_movement_hook(request: RiskMovementRequest) -> RiskMovementResult:
    """
    Hook for risk movement. Default: reject (no policy wired).
    Control plane / Drools will implement approval rules; this remains the call point.
    """
    return RiskMovementResult(approved=False, reason="risk movement not approved (no policy wired)", meta={})
