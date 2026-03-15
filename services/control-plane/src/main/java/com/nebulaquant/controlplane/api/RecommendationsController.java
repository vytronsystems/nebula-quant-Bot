package com.nebulaquant.controlplane.api;

import com.nebulaquant.controlplane.domain.StrategyDeployment;
import com.nebulaquant.controlplane.domain.StrategyMetrics;
import com.nebulaquant.controlplane.repository.StrategyDeploymentRepository;
import com.nebulaquant.controlplane.repository.StrategyMetricsRepository;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/recommendations")
public class RecommendationsController {

    private static final double MIN_WIN_RATE_LIVE = 0.55;
    private static final double MIN_PROFIT_FACTOR_LIVE = 1.2;
    private static final int MIN_TRADES_LIVE = 30;
    private static final int MIN_DAYS_LIVE = 14;
    private static final double MAX_DRAWDOWN_LIVE = 0.15;
    private static final int MIN_TRADES_DATA = 5;
    private static final int MIN_DAYS_DATA = 3;

    private final StrategyDeploymentRepository deploymentRepository;
    private final StrategyMetricsRepository metricsRepository;

    public RecommendationsController(
            StrategyDeploymentRepository deploymentRepository,
            StrategyMetricsRepository metricsRepository) {
        this.deploymentRepository = deploymentRepository;
        this.metricsRepository = metricsRepository;
    }

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> list() {
        List<StrategyDeployment> deployments = deploymentRepository.findAllByOrderByInstrumentAscStrategyNameAsc();
        List<Map<String, Object>> result = new ArrayList<>();
        for (StrategyDeployment dep : deployments) {
            Optional<StrategyMetrics> opt = metricsRepository.findByDeploymentId(dep.getId());
            String recommendedState = evaluate(dep.getStage(), opt);
            String reason = reason(dep.getStage(), opt, recommendedState);
            result.add(Map.<String, Object>of(
                "deploymentId", dep.getId().toString(),
                "strategyName", dep.getStrategyName(),
                "instrument", dep.getInstrument(),
                "currentStage", dep.getStage(),
                "recommendedState", recommendedState,
                "reason", reason
            ));
        }
        return ResponseEntity.ok(result);
    }

    private static String evaluate(String stage, Optional<StrategyMetrics> opt) {
        if (opt.isEmpty()) return "requires_more_data";
        StrategyMetrics m = opt.get();
        int trades = m.getTradesCount();
        int days = m.getDaysCount();
        if (trades < MIN_TRADES_DATA || days < MIN_DAYS_DATA) return "requires_more_data";
        if (m.getMaxDrawdown() != null && m.getMaxDrawdown().doubleValue() > MAX_DRAWDOWN_LIVE) return "degraded";
        Double wr = m.getWinRate() != null ? m.getWinRate().doubleValue() : null;
        Double pf = m.getProfitFactor() != null ? m.getProfitFactor().doubleValue() : null;
        if (wr != null && wr < MIN_WIN_RATE_LIVE) return "keep_in_paper";
        if (pf != null && pf < MIN_PROFIT_FACTOR_LIVE) return "keep_in_paper";
        if (trades < MIN_TRADES_LIVE || days < MIN_DAYS_LIVE) return "keep_in_paper";
        return "ready_for_live";
    }

    private static String reason(String stage, Optional<StrategyMetrics> opt, String recommendedState) {
        if (opt.isEmpty()) return "no_metrics";
        switch (recommendedState) {
            case "requires_more_data": return "insufficient_trades_or_days";
            case "degraded": return "max_drawdown_exceeded";
            case "keep_in_paper": return "thresholds_not_met";
            case "ready_for_live": return "thresholds_met";
            default: return "unknown";
        }
    }
}
