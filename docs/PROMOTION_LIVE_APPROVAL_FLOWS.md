# Promotion and Live Approval Flows

## Hybrid flows

- **Promotion** (idea → backtest → walkforward → paper → live): Governed by `nq_promotion` and evidence (backtest results, walk-forward, paper trading snapshots). Control plane will expose promotion APIs; Drools skeleton in place for approval rules.
- **Live approval**: Before enabling live trading: MFA required (see `MfaSupport.requireReauthForSensitiveAction`), governance approval, and Binance activation engine (`BinanceActivationEngine.assert_live_activation_allowed`). No live routing without explicit venue/account/reconciliation readiness (per non-negotiables).

## Control plane integration

- Sensitive actions (enable live, disable kill switch, increase venue capital, modify risk limits) must trigger reauth/MFA points defined in `services/control-plane` auth package.
- Promotion review table (`promotion_review`) and artifact_registry hold evidence for audit.
