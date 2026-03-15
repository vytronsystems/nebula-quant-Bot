package com.nebulaquant.controlplane.api;

import com.nebulaquant.controlplane.domain.DatasetVersion;
import com.nebulaquant.controlplane.repository.DatasetVersionRepository;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/datasets")
public class DatasetVersionController {

    private final DatasetVersionRepository repository;

    public DatasetVersionController(DatasetVersionRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public ResponseEntity<List<DatasetVersion>> list(@RequestParam(required = false) String datasetId) {
        if (datasetId != null && !datasetId.isBlank())
            return ResponseEntity.ok(repository.findByDatasetIdOrderByCreatedAtDesc(datasetId.trim()));
        return ResponseEntity.ok(repository.findAll());
    }

    @PostMapping
    public ResponseEntity<DatasetVersion> create(@RequestBody Map<String, Object> payload) {
        DatasetVersion e = new DatasetVersion();
        e.setDatasetId(payload.get("datasetId") != null ? payload.get("datasetId").toString() : "");
        e.setVersion(payload.get("version") != null ? payload.get("version").toString() : "1");
        e.setSnapshotPath(payload.get("snapshotPath") != null ? payload.get("snapshotPath").toString() : null);
        e.setMeta((Map<String, Object>) payload.get("meta"));
        e.prePersist();
        return ResponseEntity.status(HttpStatus.CREATED).body(repository.save(e));
    }
}
