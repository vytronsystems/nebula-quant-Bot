# NEBULA-QUANT v1 | nq_learning models

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LearningError(Exception):
    """Deterministic exception for invalid learning inputs or state."""


class LearningPriority(str, Enum):
    """Priority for lessons and improvement candidates."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class LearningInput:
    """Typed aggregate input for learning analysis. Findings are dict-like with category, severity, optional strategy/module."""

    audit_findings: list[dict[str, Any]] = field(default_factory=list)
    trade_review_findings: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.audit_findings is None:
            object.__setattr__(self, "audit_findings", [])
        if self.trade_review_findings is None:
            object.__setattr__(self, "trade_review_findings", [])


@dataclass(slots=True)
class LearningPattern:
    """Aggregated pattern of repeated findings."""

    pattern_id: str
    category: str
    count: int
    related_strategy_id: str | None = None
    related_module: str | None = None
    severity_distribution: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class LearningLesson:
    """Structured lesson derived from patterns."""

    lesson_id: str
    title: str
    description: str
    priority: str
    related_categories: list[str] = field(default_factory=list)
    related_strategy_id: str | None = None
    related_module: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class ImprovementCandidate:
    """Improvement candidate derived from patterns/lessons."""

    candidate_id: str
    title: str
    description: str
    priority: str
    source_patterns: list[str] = field(default_factory=list)
    related_strategy_id: str | None = None
    related_module: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class LearningSummary:
    """Summary of a learning run."""

    total_patterns: int
    total_lessons: int
    total_improvement_candidates: int
    high_priority_count: int
    critical_priority_count: int
    categories_seen: list[str] = field(default_factory=list)
    strategies_seen: list[str] = field(default_factory=list)
    modules_seen: list[str] = field(default_factory=list)
    metadata: dict[str, Any] | None = field(default_factory=dict)


@dataclass(slots=True)
class LearningReport:
    """Full deterministic learning report."""

    learning_id: str
    generated_at: float
    summary: LearningSummary
    patterns: list[LearningPattern]
    lessons: list[LearningLesson]
    improvement_candidates: list[ImprovementCandidate]
    metadata: dict[str, Any] | None = field(default_factory=dict)
