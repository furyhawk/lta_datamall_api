---
mode: ask
description: "Use when preparing a release for this backend project to run a consistent release checklist covering build, runtime, config safety, and documentation updates."
---

# Release Checklist

Run a full release readiness pass for this repository.

## Inputs

- Release version or tag
- Scope of changes
- Target environment (local, staging, production)

If any input is missing, ask concise follow-up questions before proceeding.

## Checklist Workflow

1. Review changed files and summarize release scope.
2. Validate project health:
   - Run make sync if dependency files changed.
   - Run make compile.
3. Validate container workflow:
   - Run make compose-up when Podman or Docker is available.
   - Verify the health endpoint returns success.
   - Run make compose-ps and confirm services are healthy.
4. Validate configuration safety:
   - Ensure .env is not staged or committed.
   - Ensure .env.example includes any new required variables.
5. Validate docs and instructions:
   - Update README.md if commands, routes, or behavior changed.
   - Update AGENTS.md if conventions or operational workflows changed.
6. Produce a release report with:
   - Pass and fail checklist items
   - Risks or follow-ups
   - Suggested next actions before tagging

## Output Format

Return results in this order:

1. Findings by severity, with file references where relevant
2. Open questions and assumptions
3. Release readiness verdict: ready, conditionally ready, or not ready
4. Recommended next actions

## Project-Specific Notes

- Primary commands are managed through Makefile and uv.
- Backend routes live under app/api/routes.
- Runtime depends on DATAMALL_API_KEY from .env.
- Valkey cache is expected in compose-based runs.
