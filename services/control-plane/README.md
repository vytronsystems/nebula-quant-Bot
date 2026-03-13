# NEBULA-QUANT Control Plane

Spring Boot 3 / Java 21 service. Responsibilities: auth/session/MFA boundary, operator/executive APIs, instrument registry APIs, artifact/evidence APIs, live approval APIs, risk policy APIs, venue configuration APIs, dashboard aggregation APIs. Does not migrate quant engines into Java (Python remains quant core).

## Build and run

- Requires Java 21 and Maven.
- `mvn spring-boot:run` or `mvn package && java -jar target/control-plane-*.jar`
- Health: `GET /api/health` (no auth) and `GET /actuator/health`.

## Package structure

- `config`: SecurityConfig (auth foundation; MFA points in auth package).
- `health`: HealthController.
- `auth`: MfaSupport (reauth for sensitive actions).
- `drools`: DroolsSkeleton (rules to be wired).
- `api`: InstrumentRegistryController, ArtifactRegistryController (stubs; wire to Python/DB later).
