from __future__ import annotations

from collections.abc import Callable, Sequence
import hashlib
from typing import Any

from nq_alpha_discovery import AlphaDiscoveryEngine
from nq_backtest import BacktestEngine
from nq_backtest.reporter import build_backtest_summary
from nq_experiments import ExperimentEngine
from nq_experiments.models import (
    ExperimentRecord,
    ExperimentStatus,
    ExperimentType,
)
from nq_metrics import MetricsEngine
from nq_metrics.models import TradePerformance
from nq_paper import PaperEngine
from nq_promotion import PromotionEngine
from nq_promotion.models import PromotionInput
from nq_strategy_generation import StrategyGenerationEngine
from nq_walkforward import WalkForwardEngine

from nq_research_pipeline.models import ResearchCycleReport, ResearchPipelineError


def _ensure_sequence(val: Any, name: str) -> Sequence[Any]:
    if val is None:
        return ()
    if isinstance(val, (list, tuple)):
        return val
    raise ResearchPipelineError(f"{name} must be a sequence or None, got {type(val).__name__}")


class ResearchPipelineEngine:
    """
    Deterministic research pipeline orchestrator.

    Wires the research modules in order:
    nq_alpha_discovery → nq_experiments → nq_backtest → nq_walkforward
    → nq_paper → nq_metrics → nq_promotion
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        import time

        self._clock = clock or time.time

    def _now(self) -> float:
        return float(self._clock())

    def _build_cycle_id(self, strategy_ids: list[str]) -> str:
        """Deterministic cycle_id based on strategy identifiers."""
        if not strategy_ids:
            return "research-cycle-empty"
        base = "|".join(sorted(strategy_ids))
        digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]
        return f"research-cycle-{len(strategy_ids)}-{digest}"

    def run_research_cycle(
        self,
        market_data: Sequence[Any] | None,
        regime_context: Any | None = None,
        *,
        strategy_engine: StrategyGenerationEngine | None = None,
        strategy_inputs: dict[str, Any] | None = None,
        enable_strategy_generation: bool = False,
    ) -> ResearchCycleReport:
        """
        Run a full research cycle over supplied market_data.

        - market_data: bar-like structures (dicts or objects) used by backtest/walkforward/paper.
        - regime_context: reserved for future use; not interpreted here.
        """
        bars = list(_ensure_sequence(market_data, "market_data"))

        # --- Step 1 — Discover strategies (nq_alpha_discovery or nq_strategy_generation) ---
        if enable_strategy_generation:
            sg_engine = strategy_engine or StrategyGenerationEngine(clock=self._clock)
            sg_inputs = strategy_inputs or {}
            sg_report = sg_engine.generate_strategies(
                market_observations=sg_inputs.get("market_observations"),
                regime_context=sg_inputs.get("regime_context", regime_context),
                learning_feedback=sg_inputs.get("learning_feedback"),
            )
            candidates = list(getattr(sg_report, "candidates", []) or [])
            unique_strategy_ids = [c.strategy_id for c in candidates]
        else:
            observations = [
                {
                    "category": "research_candidate",
                    "title": f"candidate-{idx}",
                    "strategy_id": f"strategy_{idx}",
                    "module": "nq_research_pipeline",
                }
                for idx, _ in enumerate(bars)
            ]
            alpha_engine = AlphaDiscoveryEngine(clock=self._clock)
            alpha_report = alpha_engine.generate_hypotheses(
                observations=observations if observations else None,
            )
            hypotheses = list(getattr(alpha_report, "hypotheses", []) or [])
            strategy_ids: list[str] = []
            for h in hypotheses:
                sid = getattr(h, "related_strategy_id", None) or getattr(h, "hypothesis_id", "")
                if sid:
                    strategy_ids.append(str(sid))
            # De-duplicate while preserving order for determinism.
            seen: set[str] = set()
            unique_strategy_ids: list[str] = []
            for sid in strategy_ids:
                if sid not in seen:
                    seen.add(sid)
                    unique_strategy_ids.append(sid)

        candidate_count = len(unique_strategy_ids)

        # --- Step 2 — Run experiments (nq_experiments) ---
        exp_engine = ExperimentEngine(clock=self._clock)
        experiment_records: list[ExperimentRecord] = []
        now_ts = self._now()
        for idx, sid in enumerate(unique_strategy_ids):
            experiment_records.append(
                ExperimentRecord(
                    experiment_id=f"exp-{sid}-{idx}",
                    strategy_id=sid,
                    strategy_version="1.0.0",
                    experiment_type=ExperimentType.RESEARCH.value,
                    status=ExperimentStatus.SUCCESS.value,
                    parameters={},
                    metrics={},
                    notes="nq_research_pipeline auto-experiment",
                    created_at=now_ts,
                    updated_at=now_ts,
                    owner="nq_research_pipeline",
                    metadata={"pipeline": "nq_research_pipeline"},
                )
            )
        experiment_report = exp_engine.analyze_experiments(experiment_records)
        experiment_summary = experiment_report.summary
        experiment_count = getattr(experiment_summary, "total_experiments", len(experiment_records))
        experiment_summary_dict = {
            "total_experiments": getattr(experiment_summary, "total_experiments", 0),
            "successful_experiments": getattr(experiment_summary, "successful_experiments", 0),
            "failed_experiments": getattr(experiment_summary, "failed_experiments", 0),
            "degraded_experiments": getattr(experiment_summary, "degraded_experiments", 0),
            "invalid_experiments": getattr(experiment_summary, "invalid_experiments", 0),
        }

        # --- Step 3 — Backtesting (nq_backtest) ---
        backtest_engine = BacktestEngine()

        def _hold_strategy(bar: Any) -> str:  # noqa: ARG001
            # Deterministic, side-effect free placeholder strategy.
            return "hold"

        backtest_result = backtest_engine.run(bars=bars, strategy=_hold_strategy)
        backtest_summary = build_backtest_summary(backtest_result)

        # --- Step 4 — Walkforward validation (nq_walkforward) ---
        walkforward_engine = WalkForwardEngine()
        walkforward_result = walkforward_engine.run(bars=bars, strategy=_hold_strategy)
        walkforward_summary = {
            "total_windows": walkforward_result.total_windows,
            "passed_windows": walkforward_result.passed_windows,
            "failed_windows": walkforward_result.failed_windows,
            "pass_rate": walkforward_result.pass_rate,
        }

        # --- Step 5 — Paper trading simulation (nq_paper) ---
        paper_engine = PaperEngine()
        paper_result = paper_engine.run_session(bars=bars, strategy=_hold_strategy)
        paper_summary = dict(getattr(paper_result, "summary", {}) or {})

        # --- Step 6 — Metrics evaluation (nq_metrics) ---
        metrics_engine = MetricsEngine()
        trades_perf: list[TradePerformance] = []
        for idx, t in enumerate(getattr(backtest_result, "trades", []) or []):
            holding_time = float(max(0.0, getattr(t, "exit_ts", 0.0) - getattr(t, "entry_ts", 0.0)))
            trades_perf.append(
                TradePerformance(
                    trade_id=f"bt-{idx}",
                    symbol=backtest_result.config.symbol,
                    entry_price=float(getattr(t, "entry_price", 0.0)),
                    exit_price=float(getattr(t, "exit_price", 0.0)),
                    qty=float(getattr(t, "qty", 0.0)),
                    pnl=float(getattr(t, "pnl", 0.0)),
                    pnl_pct=float(getattr(t, "pnl_pct", 0.0)),
                    holding_time=holding_time,
                    metadata={"source": "backtest"},
                )
            )
        metrics_result = metrics_engine.compute_metrics(trades_perf, initial_equity=backtest_result.config.initial_capital)
        metrics_summary = {
            "total_trades": metrics_result.total_trades,
            "win_rate": metrics_result.win_rate,
            "profit_factor": metrics_result.profit_factor,
            "max_drawdown": metrics_result.max_drawdown,
        }

        # --- Step 7 — Strategy promotion (nq_promotion) ---
        promotion_engine = PromotionEngine()
        approved: list[str] = []
        rejected: list[str] = []
        for sid in unique_strategy_ids:
            promotion_input = PromotionInput(
                strategy_id=sid,
                current_status="walkforward",
                backtest_summary=backtest_summary,
                walkforward_summary=walkforward_summary,
                paper_summary=paper_summary,
                guardrail_summary={},
                metrics_summary=metrics_summary,
                experiment_summary=experiment_summary_dict,
                metadata={"pipeline": "nq_research_pipeline"},
            )
            promotion_result = promotion_engine.evaluate_promotion(
                promotion_input=promotion_input,
                target_status="paper",
            )
            if promotion_result.decision.allowed:
                approved.append(sid)
            else:
                rejected.append(sid)

        cycle_id = self._build_cycle_id(unique_strategy_ids)
        generated_at = self._now()
        summary = {
            "candidate_count": candidate_count,
            "experiment_count": experiment_count,
            "approved_count": len(approved),
            "rejected_count": len(rejected),
        }

        return ResearchCycleReport(
            cycle_id=cycle_id,
            generated_at=generated_at,
            candidate_count=candidate_count,
            experiment_count=experiment_count,
            approved_strategies=approved,
            rejected_strategies=rejected,
            summary=summary,
        )

