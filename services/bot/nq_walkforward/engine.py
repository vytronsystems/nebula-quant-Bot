# NEBULA-QUANT v1 | nq_walkforward engine — skeleton only

from typing import Any

from nq_walkforward.models import (
    WalkForwardConfig,
    WalkForwardResult,
    WalkForwardWindowResult,
)
from nq_walkforward.splitter import build_windows


class WalkForwardEngine:
    """
    Skeleton walk-forward engine. Validates inputs and returns a safe
    WalkForwardResult skeleton. Window execution is placeholder.
    """

    def __init__(
        self,
        windows: list[WalkForwardConfig] | None = None,
        **kwargs: Any,
    ) -> None:
        if windows is not None:
            self._windows = windows
        else:
            self._windows = build_windows(**kwargs)

    def run(self) -> WalkForwardResult:
        """Validate inputs and return a WalkForwardResult skeleton."""
        self._validate_inputs()
        return self._build_result()

    def _validate_inputs(self) -> None:
        """Skeleton: no-op. Do not raise in basic execution."""
        pass

    def _run_window(self, config: WalkForwardConfig) -> WalkForwardWindowResult:
        """Skeleton: placeholder. Returns safe window result."""
        return WalkForwardWindowResult(
            config=config,
            train_summary={"skeleton": True},
            test_summary={"skeleton": True},
            passed=True,
            notes="skeleton placeholder",
        )

    def _build_result(self) -> WalkForwardResult:
        """Build WalkForwardResult from windows (skeleton: no real run)."""
        if not self._windows:
            self._windows = build_windows()
        window_results: list[WalkForwardWindowResult] = []
        for w in self._windows:
            window_results.append(self._run_window(w))
        passed = sum(1 for r in window_results if r.passed)
        total = len(window_results)
        return WalkForwardResult(
            windows=window_results,
            total_windows=total,
            passed_windows=passed,
            failed_windows=total - passed,
            pass_rate=passed / total if total else 0.0,
            metadata={"skeleton": True},
        )
