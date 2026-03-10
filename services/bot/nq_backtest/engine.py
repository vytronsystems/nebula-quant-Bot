# NEBULA-QUANT v1 | nq_backtest engine — skeleton only

from typing import Any

from nq_backtest.config import (
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_COMMISSION,
    DEFAULT_SLIPPAGE_BPS,
)
from nq_backtest.models import (
    BacktestConfig,
    BacktestResult,
    TradeRecord,
    EquityPoint,
)


class BacktestEngine:
    """
    Skeleton backtest engine. Validates inputs and returns a BacktestResult skeleton.
    Simulation logic is placeholder; no runtime errors in basic execution.
    """

    def __init__(
        self,
        config: BacktestConfig | None = None,
        **kwargs: Any,
    ) -> None:
        if config is not None:
            self._config = config
        else:
            self._config = BacktestConfig(
                symbol=kwargs.get("symbol", "QQQ"),
                timeframe=kwargs.get("timeframe", "1d"),
                initial_capital=kwargs.get("initial_capital", DEFAULT_INITIAL_CAPITAL),
                commission_per_trade=kwargs.get("commission_per_trade", DEFAULT_COMMISSION),
                slippage_bps=kwargs.get("slippage_bps", DEFAULT_SLIPPAGE_BPS),
                start_ts=float(kwargs.get("start_ts", 0)),
                end_ts=float(kwargs.get("end_ts", 0)),
            )

    def run(self, bars: Any = None) -> BacktestResult:
        """
        Validate inputs and return a BacktestResult skeleton.
        bars: optional; not used in skeleton (placeholder for future data feed).
        """
        self._validate_inputs()
        self._simulate()
        return self._build_result()

    def _validate_inputs(self) -> None:
        """Skeleton: no-op or light checks. Do not raise in basic execution."""
        pass

    def _simulate(self) -> None:
        """Skeleton: placeholder. No real simulation."""
        pass

    def _build_result(self) -> BacktestResult:
        """Build and return a BacktestResult skeleton."""
        return BacktestResult(
            config=self._config,
            total_trades=0,
            wins=0,
            losses=0,
            win_rate=0.0,
            gross_pnl=0.0,
            net_pnl=0.0,
            max_drawdown=0.0,
            sharpe_like=0.0,
            trades=[],
            equity_curve=[
                EquityPoint(ts=self._config.start_ts, equity=self._config.initial_capital, drawdown=0.0),
            ],
            metadata={"skeleton": True},
        )
