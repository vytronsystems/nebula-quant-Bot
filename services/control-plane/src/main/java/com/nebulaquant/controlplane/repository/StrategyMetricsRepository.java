package com.nebulaquant.controlplane.repository;

import com.nebulaquant.controlplane.domain.StrategyMetrics;

import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface StrategyMetricsRepository extends JpaRepository<StrategyMetrics, UUID> {

    Optional<StrategyMetrics> findByDeploymentId(UUID deploymentId);
}
