# nq_promotion — Strategy Lifecycle Governance Engine

## Purpose

`nq_promotion` is the **strategy lifecycle decision engine**. It decides whether a strategy may be **promoted** or **blocked** across the institutional pipeline:

```
research → backtest → walkforward → paper → live
```

It evaluates promotion eligibility using structured inputs: strategy registry state (current_status), backtest summary, walkforward summary, paper summary, guardrail summary, and optional metrics/experiment summaries. It does **not** execute strategies, run backtests, place orders, or connect to brokers or external APIs. It only evaluates promotion rules and returns promotion decisions.

## How It Fits the Institutional Lifecycle

- **idea** → **research**: Strategy is in hypothesis/experiment phase.
- **research** → **backtest**: Strategy has a definition and is ready for backtest.
- **backtest** → **walkforward**: Backtest meets minimum trades, win rate, profit factor, and drawdown thresholds.
- **walkforward** → **paper**: Walk-forward pass rate meets minimum.
- **paper** → **live**: Paper meets minimum trades, win rate, drawdown; **and** guardrails are clear (allowed=True).
- **any** → **disabled**: Strategy can be disabled from any stage.
- **live** → **retired**: Strategy can be retired from live.

Invalid transitions (e.g. paper → backtest, or live → research) are **blocked by default** via `status_map.py`.

## How It Uses Evidence

- **Backtest summary**: For promotion to walkforward or paper: `total_trades`, `win_rate`, `profit_factor`, `max_drawdown` are checked against config thresholds. Missing or failing any required field → blocking issue.
- **Walkforward summary**: For promotion to paper: `pass_rate` is checked. Missing → blocking.
- **Paper summary**: For promotion to live: `total_trades`/`closed_trades`, `win_rate`, `max_drawdown` are checked. Missing or failing → blocking.
- **Guardrail summary**: For promotion to live: `allowed` must be True when `ALLOW_LIVE_ONLY_IF_GUARDRAILS_CLEAR` is True. Missing or False → blocking.

All checks are **deterministic** and **in-memory**. No database or external API is called.

## Why Promotion Decisions Must Fail Closed

If evidence is missing or a threshold is not met, the engine returns `allowed=False` and lists blocking issues. This avoids promoting strategies that have not been validated to the required standard. The constitution and research framework require that nothing goes to live without backtest, walk-forward, paper, and audit; the promotion engine enforces that by requiring the corresponding summaries and thresholds before allowing the transition.

## Limitations of Current Version

- **No persistence**: Decisions are not stored; caller must record them if needed.
- **No direct integration** with nq_backtest, nq_walkforward, nq_paper, or nq_guardrails; caller supplies summary dicts.
- **Config**: Thresholds are in `config.py`; no per-strategy overrides yet.
- **Status map**: Fixed allowed transitions; extending requires editing `status_map.py`.
