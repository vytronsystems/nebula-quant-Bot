package com.nebulaquant.controlplane.api;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * Artifact/evidence registry API. Returns phase artifacts from filesystem or DB;
 * first implementation: stub returning empty list.
 */
@RestController
@RequestMapping("/api/artifacts")
public class ArtifactRegistryController {

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> listByPhase(
            @RequestParam(required = false) String phase) {
        return ResponseEntity.ok(List.of());
    }
}
