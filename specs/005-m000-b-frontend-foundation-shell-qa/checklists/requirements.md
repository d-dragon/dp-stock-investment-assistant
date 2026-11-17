# Specification Quality Checklist: M-000 Frontend foundation shell and QA (delivery 2 of 2)

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-17
**Feature**: [spec.md](../spec.md)

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [ ] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [ ] No implementation details leak into specification

## Notes

Validation iteration 1 (2026-11-17). Items left open are intentional, except the one inventory marker.

- **Implementation details / non-technical stakeholder wording / technology-agnostic success criteria.** The generic checklist asks for a stakeholder spec with no frameworks or tools. The Product Owner required the opposite for this foundation slice: Given/When/Then, each slice's Agent constraints and T-step mapping, the B3 and B5 design tables copied from the pitch, proving commands, and a source on every requirement. `spec.md` keeps that technical content. These four boxes stay open as a known exception, not as a defect to edit out.
- **`[NEEDS CLARIFICATION]` markers.** One remains, on FR-023 (Storybook inventory: 22 stories if each M-tier case is its own story, or about 15 stories that still cover every named case). The run is headless, so the marker was not guessed away. Dark-only Storybook, the move of light theme, theme switching, the contrast script, and visual snapshots to M-001, and the folder names `features/` and `platform/` are already decided and recorded under "Clarifications" and "Source conflicts".
- **Testable requirements.** FR-001..FR-026 and SC-001..SC-012 each cite a pitch section, ADR, SRS ID, design row, or the 2026-11-17 Product Owner decision. Rows B3-D1..D9 and B5-S1..S4 are copied from the pitch. The open item is the story-file count, not which M-tier cases exist.
- **Scope.** B0, B1, B2, and B4 are dependencies under "Dependencies", delivered by `specs/004-m000-b-frontend-foundation-core`. This spec does not re-open them.

The technical-detail boxes stay open as the known exception from validation iteration 1. The story-count marker should be answered before `/speckit-plan`. It does not block reading the rest of the spec.

## Question 1: Storybook inventory size

**Context**: FR-023, and the stories table copied from `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI". The same pitch and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules" say "about 15 stories".

**What we need to know**: Is the required Storybook inventory one story per M-tier case (22), or a set of about 15 stories that still covers every named case?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A | One story per M-tier case (22): ZoneFrame 7, PriceCell 4, Delta 4, StatusBadge 4, MessageBody 3 | axe runs on every case. The "about 15" sentence stays an estimate. |
| B | About 15 stories, and every named case is still rendered inside that set | Matches the estimate. Storybook must still expose each case to the axe run, not only the default args. |
| C | ZoneFrame 7 plus one story per component for PriceCell, Delta, StatusBadge, and MessageBody, with the named cases as variants (11), and the rest of the budget left unused | Smaller catalogue. Needs an explicit rule that axe sees every variant. |
| Custom | Provide your own answer | The Product Owner names the story list. |

This specify run does not wait. The marker stays in `spec.md` until a later answer replaces it.
