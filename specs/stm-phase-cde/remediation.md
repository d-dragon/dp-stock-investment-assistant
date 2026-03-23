# Remediation: STM Phase C-E Analysis Findings

## Purpose

Capture the Phase 6 analysis findings that should be resolved before Phase 7 review.

## Findings

### High

1. Management contract underspecification
   - Affected artifacts:
     - `specs/stm-phase-cde/spec.md`
     - `specs/stm-phase-cde/contracts/management-api.md`
     - `specs/stm-phase-cde/checklists/readiness.md`
   - Issue:
     - Session-list and conversation-list endpoints define filters and sorting but do not enumerate list item payload fields clearly enough for direct OpenAPI translation.
   - Required remediation:
     - Add explicit list item schemas for session and conversation collection responses, including hierarchy identifiers and list-summary fields already promised in the spec.

### Medium

2. Plan metric drift
   - Affected artifact:
     - `specs/stm-phase-cde/plan.md`
   - Issue:
     - Plan still reports 38 functional requirements while the spec now contains 39 after adding FR-D08a.
   - Required remediation:
     - Refresh the scale/scope count in the plan.

3. Quickstart missing management latency verification
   - Affected artifacts:
     - `specs/stm-phase-cde/quickstart.md`
     - `specs/stm-phase-cde/tasks.md`
   - Issue:
     - Tasks T030A and T051 expect management API latency verification, but quickstart does not yet define the command or validation steps.
   - Required remediation:
     - Add management latency verification commands and expected thresholds to quickstart.

4. Runtime failure-path test coverage not explicit
   - Affected artifacts:
     - `specs/stm-phase-cde/spec.md`
     - `specs/stm-phase-cde/plan.md`
     - `specs/stm-phase-cde/tasks.md`
     - `specs/stm-phase-cde/checklists/readiness.md`
   - Issue:
     - Two runtime behaviors are still only implicit in tests/tasks:
       - concurrent archive-versus-message handling
       - delivering chat response even when metadata write fails, with drift surfaced later
   - Required remediation:
     - Add explicit test-task coverage or expand existing runtime test tasks to name both behaviors.

### Low

5. Requirements checklist drift
   - Affected artifact:
     - `specs/stm-phase-cde/checklists/requirements.md`
   - Issue:
     - Generic checklist language says the spec has no implementation details and is technology-agnostic, which no longer matches this API-contract-heavy spec.
   - Required remediation:
     - Narrow or refresh the checklist wording so it reflects what this spec actually validates.

## Recommendation

Resolve items 1 through 4 before Phase 7 review. Item 5 can be addressed in the same cleanup pass if desired.