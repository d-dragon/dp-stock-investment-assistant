# Verification and Traceability Strategy

> **Status**: Draft 0.1 — thin first fill for the Phase 1 SRS pilot per [documentation methodology](../study-hub/project-documentation-and-specification-methodology.md) Section 12.4, Phase 3.
> **Standards Stance**: Aligned internal verification standard

## Purpose

Defines test levels, evidence expectations, release gates, and how requirements (SR-x, SNR-x, FR-x, NFR-x) are proven through feature specs, automated tests, and traceability reports.

## 1. Document Control

| Field | Value |
|-------|-------|
| Owner | Chief of Staff drafts; Phan approves |
| Status | Draft 0.1 |
| Date | 2026-10-16 |
| Related | [Master System SRS](../system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) §9, [Requirements Method and Governance](../system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md) |

## 2. Test Levels and Strategy (Unit, Integration, E2E, Performance, Security)

| Level | Purpose | Phase 1 stance |
|-------|---------|----------------|
| Unit | Behaviour of one module in isolation | Required for every slice |
| Integration | Behaviour across layers and stores | Required where a slice crosses a boundary |
| Contract | API matches the executable contract (OpenAPI) | Required when a slice changes the API |
| E2E | A Journey step works end to end ([Journeys](../system/USER_JOURNEYS_WITH_WIREFRAMES.md)) | Required for P0 Journey steps once the frontend is testable (SRS OI-3) |
| Performance | SNR-1 targets | Deferred |
| Security | SNR-3 controls | Deferred beyond input validation and owner scoping |

## 3. Evidence Expectations per Test Level

Each slice stores evidence under its `specs/NNN-<slug>/checklists/`: the command run, the result (pass/fail counts), the commit or worktree it ran on, and the SRS IDs covered.

## 4. Requirement-to-Test Traceability Policy

- Every Given/When/Then scenario in a slice maps to at least one automated test (or a recorded manual check where automation is not yet possible).
- Each test names the SRS ID it proves (in the test name, docstring or evidence table).
- Trace scope (P0 + P1) is set in [Requirements Method and Governance](../system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md) §4.

## 5. Release Gate Criteria

- All P0 SRS IDs for the phase are `verified` in the registry.
- No open `[NEEDS CLARIFICATION]` markers in the phase's slices.
- Coverage targets in §7 are met and no known contract divergence (SR-8.1.2) remains.

## 6. Traceability Tooling (spec-traceability.yaml, sync_spec_status.py)

- `specs/spec-traceability.yaml` is the registry; status gates are `analyzed → planned → implemented → verified`.
- `scripts/sync_spec_status.py` generates forward and reverse reports.
- Open item: confirm the registry and script accept master-SRS IDs (today they are agent-SRS-centric) before the first pilot slice registers SR-1.3 / SR-4.4 / SR-9.1.

## 7. Coverage Targets and Reporting

- Backend: keep SNR-6.1.3 (56% meaningful coverage, pytest).
- Frontend: target set when SRS OI-3 is resolved.
- Each slice reports coverage for touched modules in its evidence.

## 8. Revision History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.0 | 2026-04-03 | GitHub Copilot | Skeleton created |
| 0.1 | 2026-10-16 | Chief of Staff (approved by Phan) | Thin first fill of all planned sections for the Phase 1 SRS pilot |
