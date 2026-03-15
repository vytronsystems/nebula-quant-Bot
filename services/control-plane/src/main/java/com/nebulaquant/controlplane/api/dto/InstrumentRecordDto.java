package com.nebulaquant.controlplane.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record InstrumentRecordDto(
    UUID id,
    String venue,
    String symbol,
    String assetType,
    boolean active,
    String createdAt,
    String updatedAt,
    Map<String, Object> meta
) {
    public static String formatInstant(Instant i) {
        return i == null ? null : i.toString();
    }
}
