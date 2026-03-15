package com.nebulaquant.controlplane.api;

import com.nebulaquant.controlplane.domain.Alert;
import com.nebulaquant.controlplane.repository.AlertRepository;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/alerts")
public class AlertsController {

    private final AlertRepository repository;

    public AlertsController(AlertRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public ResponseEntity<List<Alert>> list() {
        return ResponseEntity.ok(repository.findAll());
    }

    @PostMapping
    public ResponseEntity<Alert> create(@RequestBody Map<String, Object> payload) {
        Alert e = new Alert();
        e.setChannel(payload.get("channel") != null ? payload.get("channel").toString() : "dashboard");
        e.setSeverity(payload.get("severity") != null ? payload.get("severity").toString() : "info");
        e.setTitle(payload.get("title") != null ? payload.get("title").toString() : "");
        e.setBody(payload.get("body") != null ? payload.get("body").toString() : null);
        e.setTriggerType(payload.get("triggerType") != null ? payload.get("triggerType").toString() : null);
        e.setMeta((Map<String, Object>) payload.get("meta"));
        e.prePersist();
        return ResponseEntity.status(HttpStatus.CREATED).body(repository.save(e));
    }
}
