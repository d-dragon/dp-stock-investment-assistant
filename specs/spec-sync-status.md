# Spec Sync Status

> **Document Version**: 1.5
> **Generated**: 2026-07-01 04:02:48Z
> **Status**: Active
> **Traceability Manifest Version**: 1

## Baseline

- SRS: [docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md)
- SRS version: `2.7`
- SRS last updated: `2026-06-03`

## Summary

| Feature | Mapping | Coverage | Derived Status | Sync Status | Tasks |
|---------|---------|----------|----------------|-------------|-------|
| [agent-session-with-stm-wiring](agent-session-with-stm-wiring/spec.md#requirements-mandatory) | `mapped` | `partial` | `verified` | `current` | `32/32` |
| [stm-phase-cde](stm-phase-cde/spec.md#requirements-mandatory) | `mapped` | `partial` | `verified` | `current` | `56/56` |
| [001-stm-domain-service-refactor](001-stm-domain-service-refactor/plan.md) | `unmapped` | `n/a` | `unmapped` | `unmapped` | `n/a` |
| [spec-driven-development-pilot](spec-driven-development-pilot/plan.md#summary) | `mapped` | `partial` | `implemented` | `current` | `42/42` |
| [prompt-system-milestone1](prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory) | `mapped` | `partial` | `implemented` | `current` | `42/42` |
| [prompt-system-milestone2](prompt-system-milestone2/spec.md#governance-context-mandatory) | `mapped` | `partial` | `implemented` | `current` | `45/45` |

## Revision History

| Version | Date | Summary |
|---------|------|---------|
| `1.0` | `2026-03-19` | Added embedded report metadata and anchor-aware evidence links for forward spec sync reporting. |
| `1.1` | `2026-03-31` | Synchronized stm-phase-cde from clarified planning state to verified implementation state and expanded evidence links. |
| `1.2` | `2026-06-03` | Updated prompt-system-milestone1 mapping_status to implemented, added tasks.md/checklists/verify-tasks-report.md/review.md to evidence paths. Task completion 42/42, tests 29/29. |
| `1.3` | `2026-06-04` | Added prompt-system-milestone2 (M2) feature entry — mapping_status planned, spec.md and quality checklist as evidence paths. SRS v2.7 baseline reused. |
| `1.4` | `2026-06-04` | Updated prompt-system-milestone2 (M2) feature entry — mapping_status implemented, all design and delivery artifacts added to evidence paths. PromptAssembler, route-skill assets, and agent wiring delivered. |
| `1.5` | `2026-07-01` | Normalized feature mapping_status values back to mapped, aligned legacy STM feature baselines to SRS v2.7, and expanded M2 evidence paths for regenerated sync reports. |

## agent-session-with-stm-wiring

- Title: STM Domain Model Refactor and Service-Layer Restructuring
- Path: [specs/agent-session-with-stm-wiring](agent-session-with-stm-wiring/spec.md#requirements-mandatory)
- Mapping status: `mapped`
- Coverage status: `partial`
- Derived status: `verified`
- Sync status: `current`
- Sync gate enforced: `yes`
- spec.md status field: `Verified`
- Task completion: `32/32`
- Linked SRS items: `FR-3.1.1, FR-3.1.2, FR-3.1.3, FR-3.1.4, FR-3.1.5, FR-3.1.6, FR-3.1.7, FR-3.1.8, FR-3.2.1, FR-3.2.2, FR-3.2.3, FR-3.2.4, FR-3.2.5, FR-3.2.6, FR-3.2.7, FR-3.2.8, FR-3.2.9, FR-3.2.10, FR-3.4.1, FR-3.4.2, FR-3.4.3, FR-3.4.4, FR-3.4.5, FR-3.4.6, FR-3.4.7, FR-5.1.2, FR-5.1.5, FR-5.1.8, FR-5.2.2, FR-5.2.6, FR-7.1.2, FR-7.1.3, NFR-2.3.1, NFR-2.3.2, NFR-4.1.3, NFR-4.1.4, AC-2.1, AC-2.2, AC-2.5, AC-2.6, AC-2.7, AC-4.2, AC-6.1, AC-7.1, AC-7.2, AC-7.3, IR-1.5, IR-1.6, IR-1.7`
- Evidence:
  - [Feature requirements](agent-session-with-stm-wiring/spec.md#requirements-mandatory)
  - [Phase B service refactor scope](agent-session-with-stm-wiring/spec.md#phase-b-service-layer-refactor)
  - [User Story 1 delivery phase](agent-session-with-stm-wiring/tasks.md#phase-3-user-story-1-conversation-scoped-agent-memory-priority-p1--mvp)
  - [Service-layer chat flow phase](agent-session-with-stm-wiring/tasks.md#phase-5-user-story-4-service-layer-conversation-aware-chat-flow-priority-p4)
  - [Analysis report](agent-session-with-stm-wiring/analysis.md)
  - [Delivery plan](agent-session-with-stm-wiring/plan.md)
  - [Task checklist](agent-session-with-stm-wiring/tasks.md)
  - [Verification review](agent-session-with-stm-wiring/review.md)
  - [Post-implementation verdict](agent-session-with-stm-wiring/review.md#verdict)
  - [Final re-run verdict](agent-session-with-stm-wiring/review.md#final-re-run-verdict)
  - [Analyze marker](agent-session-with-stm-wiring/.analyze-done)
  - [Verify marker](agent-session-with-stm-wiring/.verify-done)

## stm-phase-cde

- Title: STM Phase C-E — Management API, Runtime Consistency, and Test Realignment
- Path: [specs/stm-phase-cde](stm-phase-cde/spec.md#requirements-mandatory)
- Mapping status: `mapped`
- Coverage status: `partial`
- Derived status: `verified`
- Sync status: `current`
- Sync gate enforced: `yes`
- spec.md status field: `Verified`
- Task completion: `56/56`
- Linked SRS items: `FR-3.1.3, FR-3.2.2, FR-3.2.3, FR-3.2.6, FR-3.2.7, FR-3.2.8, FR-3.2.10, FR-5.1.7, FR-5.1.8, FR-5.3.1, FR-5.3.2, FR-5.3.3, FR-5.3.4, FR-5.3.5, FR-5.3.6, FR-5.4.1, FR-5.4.2, FR-5.4.3, FR-5.4.4, FR-5.4.5, FR-5.4.6, FR-5.4.7, FR-5.4.8, FR-5.5.1, FR-5.5.2, FR-5.5.3, FR-5.5.4, FR-5.5.5, FR-5.5.6, FR-5.6.1, FR-5.6.2, FR-5.6.3, FR-5.6.4, FR-5.6.5, FR-7.1.1, FR-7.1.2, FR-7.1.3, FR-7.1.4, FR-7.1.5, FR-7.2.1, FR-7.2.2, FR-7.2.3, FR-7.2.4, FR-7.2.5, FR-7.3.1, FR-7.3.2, FR-7.3.3, FR-7.3.4, FR-7.3.5, FR-7.3.6, NFR-1.4.1, NFR-1.4.2, NFR-1.4.3, NFR-1.4.4, NFR-2.3.2, NFR-2.4.1, NFR-2.4.2, NFR-2.4.3, NFR-2.4.4, NFR-2.4.5, NFR-2.5.1, NFR-2.5.2, NFR-2.5.3, NFR-2.5.4, NFR-6.1.3, AC-2.2, AC-2.5, AC-2.6, AC-5.1, AC-5.2, AC-5.3, AC-5.4, AC-5.5, AC-5.6, AC-5.7, AC-6.1, AC-6.2, AC-6.3, AC-6.4, AC-6.5, AC-6.6, AC-7.1, AC-7.2, AC-7.3, AC-7.4, AC-7.5, IR-1.8, IR-1.9, IR-1.10, IR-1.11, IR-1.12, IR-1.13`
- Evidence:
  - [Feature requirements](stm-phase-cde/spec.md#requirements-mandatory)
  - [Delivery plan](stm-phase-cde/plan.md)
  - [Task checklist](stm-phase-cde/tasks.md)
  - [Validation runbook](stm-phase-cde/quickstart.md)
  - [Verification review](stm-phase-cde/review.md)
  - [Implementation sync status](stm-phase-cde/review.md#implementation-sync-status)
  - [Analyze marker](stm-phase-cde/.analyze-done)
  - [Verify marker](stm-phase-cde/.verify-done)

## 001-stm-domain-service-refactor

- Title: Legacy STM domain service refactor planning artifact
- Path: [specs/001-stm-domain-service-refactor](001-stm-domain-service-refactor/plan.md)
- Mapping status: `unmapped`
- Coverage status: `n/a`
- Derived status: `unmapped`
- Sync status: `unmapped`
- Sync gate enforced: `no`

## spec-driven-development-pilot

- Title: Spec-driven development pilot
- Path: [specs/spec-driven-development-pilot](spec-driven-development-pilot/plan.md#summary)
- Mapping status: `mapped`
- Coverage status: `partial`
- Derived status: `implemented`
- Sync status: `current`
- Sync gate enforced: `yes`
- Task completion: `42/42`
- Linked SRS items: `FR-3.1.1, FR-3.1.2, FR-3.1.4, FR-3.1.6, FR-3.1.7, FR-3.1.8`
- Evidence:
  - [STM implementation summary](spec-driven-development-pilot/plan.md#summary)
  - [Session-aware invocation pattern](spec-driven-development-pilot/plan.md#3-agent-session-aware-invocation-pattern)
  - [STM task checklist](spec-driven-development-pilot/tasks.md)
  - [Session-aware conversation phase](spec-driven-development-pilot/tasks.md#phase-3-us1--session-aware-conversation-p1--5-6-sp)
  - [Runtime integration phase](spec-driven-development-pilot/tasks.md#phase-9-stm-runtime-integration--agent-migration-critical--5-6-sp)
  - [STM quickstart](spec-driven-development-pilot/quickstart.md)

## prompt-system-milestone1

- Title: Prompt Compiler Path — Milestone M1 (Prompt Runtime Parity)
- Path: [specs/prompt-system-milestone1](prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory)
- Mapping status: `mapped`
- Coverage status: `partial`
- Derived status: `implemented`
- Sync status: `current`
- Sync gate enforced: `yes`
- spec.md status field: `Implemented`
- Task completion: `42/42`
- Linked SRS items: `FR-1.4.5, FR-1.4.6, FR-1.4.8, FR-1.4.16, NFR-5.2.5, NFR-5.2.6, NFR-5.2.7, NFR-5.2.8, NFR-5.2.9, NFR-6.2.3, AC-8.1, AC-8.2`
- Evidence:
  - [Feature specification](prompt-system-milestone1/spec.md#user-scenarios--testing-mandatory)
  - [Implementation plan](prompt-system-milestone1/plan.md)
  - [Task checklist](prompt-system-milestone1/tasks.md)
  - [Quality gate checklist](prompt-system-milestone1/checklists/spec-plan-quality.md)
  - [Post-implementation verification report](prompt-system-milestone1/verify-tasks-report.md)
  - [Verification review](prompt-system-milestone1/review.md)

## prompt-system-milestone2

- Title: Prompt Compiler Path — Milestone M2 (Route-Aware Skills)
- Path: [specs/prompt-system-milestone2](prompt-system-milestone2/spec.md#governance-context-mandatory)
- Mapping status: `mapped`
- Coverage status: `partial`
- Derived status: `implemented`
- Sync status: `current`
- Sync gate enforced: `yes`
- spec.md status field: `Implemented`
- Task completion: `45/45`
- Linked SRS items: `FR-1.4.7, FR-1.4.11, FR-1.4.16, NFR-5.2.8, AC-8.5, AC-8.8, AC-8.11`
- Evidence:
  - [Feature specification](prompt-system-milestone2/spec.md#governance-context-mandatory)
  - [Quality gate checklist](prompt-system-milestone2/checklists/requirements.md)
  - [Implementation plan](prompt-system-milestone2/plan.md)
  - [Task checklist](prompt-system-milestone2/tasks.md)
  - [Research notes](prompt-system-milestone2/research.md)
  - [Data model](prompt-system-milestone2/data-model.md)
  - [Quickstart validation](prompt-system-milestone2/quickstart.md)
  - [Prompt assembler contract](prompt-system-milestone2/contracts/prompt-assembler-interface.md)
  - [Route skill asset contract](prompt-system-milestone2/contracts/route-skill-asset-schema.md)
  - [Verification review](prompt-system-milestone2/review.md)

## Status Semantics

- `derived status` is computed from spec-kit artifacts, with a pre-planning `clarified` stage recognized from a spec header of `Status: Clarified`.
- `sync status` reports whether the feature-to-SRS mapping is current against the manifest SRS baseline.
- `coverage status` shows whether the feature covers all, some, or none of the linked SRS scope.

## Operational Rule

- Update `spec-traceability.yaml` when a feature gains or changes SRS scope.
- Update `tasks.md` and workflow markers during delivery.
- Regenerate this report with `python scripts/sync_spec_status.py --gate` whenever either side changes.

