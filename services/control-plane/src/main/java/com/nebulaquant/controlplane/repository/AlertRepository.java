package com.nebulaquant.controlplane.repository;

import com.nebulaquant.controlplane.domain.Alert;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface AlertRepository extends JpaRepository<Alert, UUID> {
}
