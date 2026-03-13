# Control Plane Spec

Create `services/control-plane/` as Spring Boot 3 service.

## Responsibilities
- auth/session/MFA boundary
- operator APIs
- executive APIs
- instrument registry APIs
- artifact/evidence APIs
- live approval APIs
- risk policy APIs
- venue configuration APIs
- dashboard aggregation APIs

## Important
Do not migrate quant engines into Java.
Java orchestrates and governs.
Python computes quant logic.

## Drools responsibilities
- promotion approval rules
- live activation rules
- risk movement policies
- venue enable/disable rules
- DTE eligibility decision support policies
