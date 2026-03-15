package com.nebulaquant.controlplane.api;

import com.nebulaquant.controlplane.api.dto.StrategyDeploymentDto;
import com.nebulaquant.controlplane.domain.StrategyDeployment;
import com.nebulaquant.controlplane.repository.StrategyDeploymentRepository;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/deployments")
public class StrategyDeploymentController {

    private final StrategyDeploymentRepository repository;

    public StrategyDeploymentController(StrategyDeploymentRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public ResponseEntity<List<StrategyDeploymentDto>> list(
            @RequestParam(required = false) String instrument,
            @RequestParam(required = false) String venue,
            @RequestParam(required = false) String stage,
            @RequestParam(required = false) String environment) {
        List<StrategyDeployment> list;
        if (instrument != null && !instrument.isBlank()) {
            list = repository.findByInstrumentOrderByStrategyNameAsc(instrument.trim());
        } else if (venue != null && !venue.isBlank()) {
            list = repository.findByVenueOrderByStrategyNameAsc(venue.trim());
        } else if (stage != null && !stage.isBlank()) {
            list = repository.findByStageOrderByStrategyNameAsc(stage.trim());
        } else if (environment != null && !environment.isBlank()) {
            list = repository.findByEnvironmentOrderByStrategyNameAsc(environment.trim());
        } else {
            list = repository.findAllByOrderByInstrumentAscStrategyNameAsc();
        }
        List<StrategyDeploymentDto> body = list.stream().map(this::toDto).toList();
        return ResponseEntity.ok(body);
    }

    @GetMapping("/{id}")
    public ResponseEntity<StrategyDeploymentDto> get(@PathVariable UUID id) {
        return repository.findById(id)
            .map(this::toDto)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<StrategyDeploymentDto> create(@RequestBody Map<String, Object> payload) {
        StrategyDeployment e = new StrategyDeployment();
        e.setStrategyName(requiredString(payload, "strategyName"));
        e.setStrategyVersion(requiredString(payload, "strategyVersion"));
        e.setInstrument(requiredString(payload, "instrument"));
        e.setVenue(requiredString(payload, "venue"));
        e.setEnvironment(optString(payload, "environment", "testnet"));
        e.setStage(optString(payload, "stage", "backtest"));
        e.setEnabled(optBoolean(payload, "enabled", true));
        e.setMeta((Map<String, Object>) payload.get("meta"));
        e.prePersist();
        StrategyDeployment saved = repository.save(e);
        return ResponseEntity.status(HttpStatus.CREATED).body(toDto(saved));
    }

    @PatchMapping("/{id}")
    public ResponseEntity<StrategyDeploymentDto> update(@PathVariable UUID id, @RequestBody Map<String, Object> payload) {
        Optional<StrategyDeployment> opt = repository.findById(id);
        if (opt.isEmpty()) return ResponseEntity.notFound().build();
        StrategyDeployment e = opt.get();
        if (payload.containsKey("stage")) e.setStage(payload.get("stage").toString());
        if (payload.containsKey("environment")) e.setEnvironment(payload.get("environment").toString());
        if (payload.containsKey("enabled")) e.setEnabled(Boolean.TRUE.equals(payload.get("enabled")));
        if (payload.containsKey("meta")) e.setMeta((Map<String, Object>) payload.get("meta"));
        e.preUpdate();
        StrategyDeployment saved = repository.save(e);
        return ResponseEntity.ok(toDto(saved));
    }

    private StrategyDeploymentDto toDto(StrategyDeployment e) {
        return new StrategyDeploymentDto(
            e.getId(),
            e.getCreatedAt() == null ? null : e.getCreatedAt().toString(),
            e.getUpdatedAt() == null ? null : e.getUpdatedAt().toString(),
            e.getStrategyName(),
            e.getStrategyVersion(),
            e.getInstrument(),
            e.getVenue(),
            e.getEnvironment(),
            e.getStage(),
            e.isEnabled(),
            e.getMeta()
        );
    }

    private static String requiredString(Map<String, Object> m, String key) {
        Object v = m.get(key);
        if (v == null || v.toString().isBlank()) throw new IllegalArgumentException("Missing or empty: " + key);
        return v.toString().trim();
    }

    private static String optString(Map<String, Object> m, String key, String def) {
        Object v = m.get(key);
        return v == null ? def : v.toString().trim();
    }

    private static boolean optBoolean(Map<String, Object> m, String key, boolean def) {
        Object v = m.get(key);
        if (v == null) return def;
        if (v instanceof Boolean) return (Boolean) v;
        return Boolean.parseBoolean(v.toString());
    }
}
