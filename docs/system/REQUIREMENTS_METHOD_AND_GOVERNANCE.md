# Requirements Method and Governance

> **Status**: Draft 0.1 — filled for the Phase 1 SRS pilot per [documentation methodology](../study-hub/project-documentation-and-specification-methodology.md) Section 12.2, Phase 1.

## Purpose

Defines how requirements are authored, approved, changed, traced, and retired across the master system SRS and subordinate domain SRS documents.

## 1. Document Control

| Field | Value |
|-------|-------|
| Owner | Chief of Staff drafts; Phan approves |
| Status | Draft 0.1 |
| Date | 2026-10-16 |
| Applies to | [Master System SRS](SYSTEM_REQUIREMENTS_SPECIFICATION.md), subordinate domain SRSs, pitches and spec-kit slices under `specs/` |

## 2. Requirement Authoring Standards

### 2.1 Layers (one home per fact)

| Layer | Artifact | Answers | Owner |
|-------|----------|---------|-------|
| L0 Product truth | [Product Specification](PRODUCT_SPECIFICATION.md), [IA map](CONCEPTUAL_IA_MAP.md), [Journeys](USER_JOURNEYS_WITH_WIREFRAMES.md) | What the product is | Phan / Chief of Staff |
| L1 Requirements | Master System SRS + domain SRSs | What must be true, testably (ID, priority, pointer) | Chief of Staff drafts, Phan approves |
| L1.5 Pitch | One page per feature (`specs/pitches/<feature>.md`) | Why now, how much time | Chief of Staff |
| L2 Slice | spec-kit `spec.md` → plan → tasks | What one 1–2 week slice delivers | Slice owner; built by Coding Orchestrator |

Each layer links down by ID and never restates the layer above.

### 2.2 Rules

1. **One home per fact.** SRS lines point to the Spec (and IA map, Journeys, ADRs) by section or ID; they never copy domain text.
2. **No technical detail in the Spec.** Mechanisms live in ADRs, technical design and slices.
3. **EARS sentences.** One requirement per line using one pattern: Ubiquitous ("The system SHALL …"), State ("While …"), Event ("When …"), Optional ("Where …"), Unwanted ("If … then …"). End with `→` pointers.
4. **Stable IDs.** Keep `SR-x.y.z` / `SNR-x.y.z` (domain SRSs: `FR-` / `NFR-`). Never renumber; deprecate instead.
5. **Priorities** P0–P3 mirror Spec §5.3 for the phase in question.
6. **Acceptance lives in slices** as Given/When/Then, one scenario per testable behaviour; unresolved points are marked `[NEEDS CLARIFICATION]` and block planning.
7. **Draft marking.** Lines that are not final carry *(draft)* in the title and an "initial draft" note on the group.

### 2.3 Pitch template (L1.5)

```markdown
# Pitch: <feature>   Spec §5.3 row: "<quoted>"   Priority: P0
## Problem (user words, Spec § link)
## Value / why now
## Appetite (weeks) and slice split (S1, S2…)
## Solution sketch (IA zones, no tech)
## Rabbit holes
## No-gos
## SRS IDs covered
## Open questions → [NEEDS CLARIFICATION]
```

### 2.4 Slice header template (top of each spec-kit `spec.md`)

```markdown
# Slice: <name>            ID: specs/NNN-<slug>   Status: draft|clarified|planned|implemented|verified
| Field | Value |
|---|---|
| SRS IDs | SR-…, SNR-… |
| Spec § | §… (link only) |
| Journey step | J-TFI-… / W… |
| IA zone | Z1–Z4 (Designer) |
| ADRs | ADR-… (Software Architect Assistant) or none |
| Pitch | link or "quick slice (≤2 days)" |
| Appetite | ≤ 2 weeks |
| Out of scope | … |
```

A quick slice (≤ 2 days) may skip the pitch but never the header.

## 3. Change Classification and Approval Path

- Classes follow methodology Section 10.3: **Major** (breaking, retired requirements, structural baseline), **Minor** (additive, clarifications, new allocations), **Patch** (editorial, reference-only).
- Flow: trigger → classification → impact map (point → target doc/section → action) → **Phan approval** → baseline update → downstream sync → verification closeout.
- No long-lived document edit without an approved plan; no commit or push unless Phan approves that exact write in the same message.

## 4. Traceability Obligations

- **Scope:** only P0 and P1 requirements are registered in `specs/spec-traceability.yaml`; P2/P3 are traced when they enter a slice.
- Every slice header lists the SRS IDs it delivers.
- A registry row is added when a slice first references an ID; status moves `analyzed → planned → implemented → verified`.
- A slice is done only when all its IDs are `verified` (see [Verification and Traceability Strategy](../testing/VERIFICATION_AND_TRACEABILITY_STRATEGY.md)).

## 5. Versioning and Baseline Management

- The SRS uses SemVer (Major/Minor/Patch as in §3) and records each change in its Revision History.
- A baseline is taken at each phase cut (Spec §5.3 phases).
- Retired requirements stay listed as deprecated with the version that retired them.

## 6. Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| Phan | Approves plans, SRS baselines and every commit |
| Chief of Staff | Drafts SRS lines and pitches; ranks features |
| Researcher | Method research and benchmarks |
| Software Architect Assistant | ADRs and architecture boundaries cited by SRS lines |
| Designer | IA zones and Journey references in slice headers |
| Coding Orchestrator | Builds and tests slices; produces verification evidence |
| Task Keeper | Maintains the traceability registry |

## 7. Revision History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.0 | 2026-04-03 | GitHub Copilot | Skeleton created |
| 0.1 | 2026-10-16 | Chief of Staff (approved by Phan) | Filled all planned sections for the Phase 1 SRS pilot: layers, EARS rules, pitch and slice header templates, change flow, P0+P1 trace scope, roles |
