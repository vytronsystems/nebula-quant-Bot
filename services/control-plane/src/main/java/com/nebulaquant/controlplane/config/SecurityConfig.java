package com.nebulaquant.controlplane.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Auth/session foundation. Permits actuator and API health for bootstrap;
 * authenticated endpoints to be added (operator/executive, instrument, artifact).
 * MFA support points: integrate with MFA provider in filters or auth handlers.
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health", "/api/health").permitAll()
                .requestMatchers("/api/**").authenticated()
            )
            .httpBasic(basic -> {});
        return http.build();
    }
}
