package com.nebulaquant.controlplane.auth;

/**
 * MFA support points: reauthentication required for enable live, disable kill switch,
 * increase venue capital ceiling, modify global risk limits (per spec).
 * Integrate with MFA provider and session validation in Phase 70+.
 */
public final class MfaSupport {
    private MfaSupport() {}

    public static boolean requireReauthForSensitiveAction(String action) {
        return "enable_live".equals(action)
            || "disable_kill_switch".equals(action)
            || "increase_venue_capital".equals(action)
            || "modify_risk_limits".equals(action);
    }
}
