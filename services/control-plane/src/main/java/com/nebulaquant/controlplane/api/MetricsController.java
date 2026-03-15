package com.nebulaquant.controlplane.api;

import com.nebulaquant.controlplane.domain.StrategyMetrics;
import com.nebulaquant.controlplane.repository.StrategyMetricsRepository;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/metrics")
public class MetricsController {

    private final StrategyMetricsRepository repository;

    public MetricsController(StrategyMetricsRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public ResponseEntity<List<StrategyMetrics>> list(@RequestParam(required = false) UUID deploymentId) {
        if (deploymentId != null) {
            return repository.findByDeploymentId(deploymentId)
                .map(List::of)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.ok(List.of()));
        }
        return ResponseEntity.ok(repository.findAll());
    }

    @GetMapping("/by-deployment/{deploymentId}")
    public ResponseEntity<StrategyMetrics> getByDeployment(@PathVariable UUID deploymentId) {
        return repository.findByDeploymentId(deploymentId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
