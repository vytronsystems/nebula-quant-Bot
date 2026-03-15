package com.nebulaquant.controlplane.repository;

import com.nebulaquant.controlplane.domain.StrategyDeployment;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface StrategyDeploymentRepository extends JpaRepository<StrategyDeployment, UUID> {

    List<StrategyDeployment> findByInstrumentOrderByStrategyNameAsc(String instrument);

    List<StrategyDeployment> findByVenueOrderByStrategyNameAsc(String venue);

    List<StrategyDeployment> findByStageOrderByStrategyNameAsc(String stage);

    List<StrategyDeployment> findByEnvironmentOrderByStrategyNameAsc(String environment);

    List<StrategyDeployment> findAllByOrderByInstrumentAscStrategyNameAsc();

    Optional<StrategyDeployment> findByStrategyNameAndStrategyVersionAndInstrumentAndVenue(
        String strategyName, String strategyVersion, String instrument, String venue);
}
