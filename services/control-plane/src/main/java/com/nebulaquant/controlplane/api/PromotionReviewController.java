package com.nebulaquant.controlplane.api;

import com.nebulaquant.controlplane.domain.PromotionReview;
import com.nebulaquant.controlplane.repository.PromotionReviewRepository;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/promotion-review")
public class PromotionReviewController {

    private final PromotionReviewRepository repository;

    public PromotionReviewController(PromotionReviewRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public ResponseEntity<List<PromotionReview>> list() {
        return ResponseEntity.ok(repository.findAll());
    }

    @PostMapping
    public ResponseEntity<PromotionReview> create(@RequestBody Map<String, Object> payload) {
        PromotionReview e = new PromotionReview();
        e.setStrategyId(payload.get("strategyId") != null ? payload.get("strategyId").toString() : null);
        e.setFromStage(requiredString(payload, "fromStage"));
        e.setToStage(requiredString(payload, "toStage"));
        e.setDecision(requiredString(payload, "decision"));
        e.setEvidencePath(payload.get("evidencePath") != null ? payload.get("evidencePath").toString() : null);
        e.setMeta((Map<String, Object>) payload.get("meta"));
        e.prePersist();
        PromotionReview saved = repository.save(e);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    private static String requiredString(Map<String, Object> m, String key) {
        Object v = m.get(key);
        if (v == null || v.toString().isBlank()) throw new IllegalArgumentException("Missing or empty: " + key);
        return v.toString().trim();
    }
}
