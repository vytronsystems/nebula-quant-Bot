package com.nebulaquant.controlplane.api;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api/binance")
public class BinanceProxyController {

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public BinanceProxyController(
            RestTemplate restTemplate,
            @Qualifier("binanceApiBaseUrl") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }

    @GetMapping("/health")
    public ResponseEntity<Object> health() {
        return proxy("/health");
    }

    @GetMapping("/venue-overview")
    public ResponseEntity<Object> venueOverview() {
        return proxy("/venue-overview");
    }

    @GetMapping("/account")
    public ResponseEntity<Object> account() {
        return proxy("/account");
    }

    @GetMapping("/market")
    public ResponseEntity<Object> market() {
        return proxy("/market");
    }

    @GetMapping("/orderbook")
    public ResponseEntity<Object> orderbook(@RequestParam(defaultValue = "10") int limit) {
        return proxy("/orderbook?limit=" + limit);
    }

    @GetMapping("/trades")
    public ResponseEntity<Object> trades(@RequestParam(defaultValue = "10") int limit) {
        return proxy("/trades?limit=" + limit);
    }

    @GetMapping("/orders")
    public ResponseEntity<Object> orders() {
        return proxy("/orders");
    }

    @GetMapping("/positions")
    public ResponseEntity<Object> positions() {
        return proxy("/positions");
    }

    private ResponseEntity<Object> proxy(String path) {
        try {
            String url = path.startsWith("http") ? path : baseUrl + (path.startsWith("/") ? path : "/" + path);
            Object body = restTemplate.getForObject(url, Object.class);
            return ResponseEntity.ok(body != null ? body : new java.util.HashMap<String, String>());
        } catch (Exception e) {
            return ResponseEntity.status(502).body(java.util.Map.of(
                "status", "ERROR",
                "message", "Binance API unavailable: " + e.getMessage()
            ));
        }
    }
}
