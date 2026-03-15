package com.nebulaquant.controlplane.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.Map;
import java.util.UUID;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record StrategyDeploymentDto(
    UUID id,
    String createdAt,
    String updatedAt,
    String strategyName,
    String strategyVersion,
    String instrument,
    String venue,
    String environment,
    String stage,
    boolean enabled,
    Map<String, Object> meta
) {}
