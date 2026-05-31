---
description: "Use when the user asks for a code review, PR review, regression scan, or quality review of backend changes in this repository."
---

# Code Review Instruction

## Review Objective

Find defects and risks before merge. Prioritize behavior, correctness, reliability, and operational safety over style preferences.

## Output Contract

Return review results in this order:

1. Findings ordered by severity (critical, high, medium, low)
2. Open questions or assumptions
3. Brief change summary

If no actionable findings exist, explicitly say no findings and list residual risks or test gaps.

## Finding Format

For each finding include:

- Severity
- Impact
- Evidence with file reference
- Why it matters
- Suggested fix direction

## Repository-Specific Review Focus

### API Behavior and Compatibility

- Verify route behavior under app/api/routes is compatible with existing endpoint contracts.
- Check query alias compatibility for upstream params such as BusStopCode, ServiceNo, Date, and $skip.
- Flag any accidental payload transformation if endpoint should proxy upstream JSON directly.

### Upstream and Error Handling

- Confirm upstream failures are mapped consistently and safely.
- Ensure no secrets or sensitive payload content is leaked in error bodies.
- Validate timeout and retry assumptions for DataMall calls.

### Cache Safety

- For cache-related changes, verify key stability, TTL appropriateness, and stale-data risk.
- Confirm degraded behavior is safe when Valkey is unavailable.
- Check that cache logic is centralized in app/services/cache.py patterns.

### Configuration and Secrets

- Confirm required env vars are documented in .env.example.
- Confirm .env is not staged or committed.
- Verify new settings are wired through app/core/config.py.

### Runtime and Deployment

- Validate Docker and compose changes maintain health endpoint behavior.
- Ensure Makefile targets still reflect actual workflows.
- Check operational regressions for Podman or Docker detection logic.

### Tests and Validation

- Require at least compile-level validation for touched Python files.
- Flag missing automated tests for behavior changes.
- For major logic changes, request route-level or service-level tests.

## High-Risk Patterns To Flag Immediately

- Breaking endpoint contract changes without documentation updates
- Silent exception swallowing in request or cache paths
- Hardcoded secrets or keys
- Unbounded cache growth patterns
- Changes that bypass centralized client or cache abstractions

## Helpful References

- Architecture and commands: AGENTS.md
- Runtime and usage: README.md
- Entry wiring: app/main.py
- Upstream client: app/services/lta_client.py
- Cache layer: app/services/cache.py
