# Phase 59 — Security Cleanup and Packaging Stabilization

## Objective
Make the current repo safe and runnable from the root without fragile import behavior.

## Tasks
- Remove hardcoded secrets from tracked configuration.
- Create `.env.example` patterns.
- Refactor alertmanager/docker config to consume environment variables.
- Fix test import path issues so root-level test execution works without manual path hacks.
- Ensure `scripts` can be imported or tested consistently.

## Required outputs
- passing test suite from repo root
- updated env loading strategy
- security audit artifact
