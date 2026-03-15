package com.nebulaquant.controlplane.api;

import com.nebulaquant.controlplane.api.dto.InstrumentRecordDto;
import com.nebulaquant.controlplane.domain.InstrumentRegistry;
import com.nebulaquant.controlplane.repository.InstrumentRegistryRepository;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/instruments")
public class InstrumentRegistryController {

    private final InstrumentRegistryRepository repository;

    public InstrumentRegistryController(InstrumentRegistryRepository repository) {
        this.repository = repository;
    }

    @PostMapping
    public ResponseEntity<InstrumentRecordDto> create(@RequestBody Map<String, Object> payload) {
        String venue = requiredString(payload, "venue");
        String symbol = requiredString(payload, "symbol");
        if (repository.findByVenueAndSymbol(venue, symbol).isPresent())
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        InstrumentRegistry e = new InstrumentRegistry();
        e.setId(UUID.randomUUID());
        e.setVenue(venue);
        e.setSymbol(symbol);
        e.setAssetType(optString(payload, "assetType", "spot"));
        e.setActive(optBoolean(payload, "active", true));
        e.setCreatedAt(Instant.now());
        e.setUpdatedAt(Instant.now());
        e.setMeta((Map<String, Object>) payload.get("meta"));
        InstrumentRegistry saved = repository.save(e);
        return ResponseEntity.status(HttpStatus.CREATED).body(toDto(saved));
    }

    @PatchMapping("/{id}")
    public ResponseEntity<InstrumentRecordDto> update(@PathVariable UUID id, @RequestBody Map<String, Object> payload) {
        Optional<InstrumentRegistry> opt = repository.findById(id);
        if (opt.isEmpty()) return ResponseEntity.notFound().build();
        InstrumentRegistry e = opt.get();
        if (payload.containsKey("active")) e.setActive(Boolean.TRUE.equals(payload.get("active")));
        if (payload.containsKey("meta")) e.setMeta((Map<String, Object>) payload.get("meta"));
        e.setUpdatedAt(Instant.now());
        return ResponseEntity.ok(toDto(repository.save(e)));
    }

    @GetMapping
    public ResponseEntity<List<InstrumentRecordDto>> list(
            @RequestParam(required = false) String venue,
            @RequestParam(defaultValue = "true") boolean activeOnly) {
        List<InstrumentRegistry> list;
        if (venue != null && !venue.isBlank()) {
            list = activeOnly
                ? repository.findByVenueAndActiveOrderBySymbolAsc(venue.trim(), true)
                : repository.findByVenueOrderBySymbolAsc(venue.trim());
        } else {
            list = activeOnly
                ? repository.findByActiveOrderByVenueAscSymbolAsc(true)
                : repository.findAllByOrderByVenueAscSymbolAsc();
        }
        List<InstrumentRecordDto> body = list.stream()
            .map(this::toDto)
            .collect(Collectors.toList());
        return ResponseEntity.ok(body);
    }

    private InstrumentRecordDto toDto(InstrumentRegistry e) {
        return new InstrumentRecordDto(
            e.getId(),
            e.getVenue(),
            e.getSymbol(),
            e.getAssetType() != null ? e.getAssetType() : "spot",
            e.isActive(),
            InstrumentRecordDto.formatInstant(e.getCreatedAt()),
            InstrumentRecordDto.formatInstant(e.getUpdatedAt()),
            e.getMeta()
        );
    }

    private static String requiredString(Map<String, Object> m, String key) {
        Object v = m.get(key);
        if (v == null || v.toString().isBlank()) throw new IllegalArgumentException("Missing: " + key);
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
