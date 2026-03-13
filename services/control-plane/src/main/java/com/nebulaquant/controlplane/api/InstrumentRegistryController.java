package com.nebulaquant.controlplane.api;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * Instrument registry API (contract from docs/contracts/instrument_registry_api.md).
 * First implementation: stub returning empty list; Python core or DB to be wired later.
 */
@RestController
@RequestMapping("/api/instruments")
public class InstrumentRegistryController {

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> list(
            @RequestParam(required = false) String venue,
            @RequestParam(defaultValue = "true") boolean activeOnly) {
        return ResponseEntity.ok(List.of());
    }
}
