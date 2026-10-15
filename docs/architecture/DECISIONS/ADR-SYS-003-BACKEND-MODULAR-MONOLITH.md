# ADR-SYS-003: Backend as a modular monolith

| Field | Value |
|---|---|
| Status | Proposed (stub) |
| Date | 2026-10-12 |
| Owner | Software Architect Assistant; decision by Phan Duy |
| Blocks | Overview §4.2 citation; the placeholder agent container's fate |
| Depends on | None |

## Context

The [overview](../SYSTEM_OVERVIEW_AND_BOUNDARIES.md) draws one Backend holding application services, the Investment Core modules and the Agent in-process. It currently cites Frontend ADR-001 for this, which only covers the frontend. Compose and Helm both run the agent container only as a placeholder health check on port 7000.

## Decision to make

Whether the Backend is one deployable with internal module boundaries, which modules exist, and when the Agent may be moved into its own service.

## Options to evaluate

- A. One deployable with enforced module boundaries; the Agent in-process and movable (current overview).
- B. The Agent as a separate service now.
- Triggers for moving the Agent out: scheduled or background agent runs, agent load slowing the API, a separate owning team, or a managed agent runtime.

## Decision

Not yet decided.

## Follow-ups

- Decide whether to remove or keep the placeholder `agent` container in compose and Helm.
