package com.nebulaquant.controlplane.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class BinanceApiConfig {

    @Value("${binance.api.url:http://localhost:8082}")
    private String binanceApiUrl;

    @Bean
    public String binanceApiBaseUrl() {
        return binanceApiUrl.endsWith("/") ? binanceApiUrl.substring(0, binanceApiUrl.length() - 1) : binanceApiUrl;
    }

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
