package com.nebulaquant.controlplane.repository;

import com.nebulaquant.controlplane.domain.DatasetVersion;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface DatasetVersionRepository extends JpaRepository<DatasetVersion, UUID> {

    List<DatasetVersion> findByDatasetIdOrderByCreatedAtDesc(String datasetId);
}
