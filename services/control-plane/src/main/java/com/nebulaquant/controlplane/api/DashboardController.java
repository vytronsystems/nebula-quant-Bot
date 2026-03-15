package com.nebulaquant.controlplane.api;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Phase 81 — UI Backend Integration.
 * Aggregate endpoint for Operator Cockpit and Executive Dashboard.
 * Use GET /api/deployments, /api/metrics, /api/binance/positions, /api/instruments for data.
 */
@RestController
@RequestMapping("/api")
public class DashboardController {

    @GetMapping("/dashboard")
    public ResponseEntity<Map<String, String>> dashboard() {
        return ResponseEntity.ok(Map.of(
            "deployments", "/api/deployments",
            "metrics", "/api/metrics",
            "positions", "/api/binance/positions",
            "instruments", "/api/instruments",
            "recommendations", "/api/recommendations",
            "alerts", "/api/alerts"
        ));
    }
}
