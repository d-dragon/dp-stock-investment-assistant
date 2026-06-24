---
name: technical-design-manager
description: Maintain long-lived domain technical design documents from governing SRS, architecture, ADRs, roadmap, research/proposals, executable contracts, Spec Kit artifacts, and source implementation evidence. Use when Codex needs to update or review TECHNICAL_DESIGN.md, sync implementation or specs to technical design, focus design changes on a specific module/component/section, produce technical-design impact maps, or run current-vs-target consistency review.
---

# Technical Design Manager

## Overview

Use this skill to maintain technical design documents as realization authority. The workflow consolidates governing documents, verified specs, and source implementation evidence into focused technical-design updates without turning the design doc into an SRS, ADR, roadmap, contract, or delivery task list.

For reusable tables and checklists, read `references/technical-design-workflow.md` when the task asks for an impact map, implementation/spec synchronization, module/component review, consistency review, validation commands, or final update report.

## Operating Rules

- Treat `TECHNICAL_DESIGN.md` as the default edit target unless the user names another technical design document.
- Keep technical design at realization level: internal components, module/package relationships, runtime behavior, data/state/cache/persistence behavior, domain-owned interfaces, implementation constraints, and current-vs-target labels.
- Use `src/` and `specs/` as evidence by default, not edit targets.
- Promote verified Spec Kit artifacts as stable input. Treat active, planned, or unverified specs as planned-state context unless the user explicitly says otherwise.
- Inspect governing artifacts before editing: SRS, architecture design, ADRs, roadmap, relevant specs, executable contracts, and source implementation evidence.
- Read only relevant sections after heading or search inspection unless full-document context is needed.
- Always produce a visible impact map before mutating long-lived technical design unless the user already supplied an equivalent map.
- Report required follow-ups for `src/`, `specs/`, SRS, architecture, ADRs, roadmap, contracts, or traceability instead of editing them, unless the user explicitly includes them as targets.
- Preserve authority boundaries: requirements belong in SRS, decisions in ADRs, sequencing in roadmap, schema truth in executable contracts, delivery detail in `specs/`, and realization in technical design.
- Respect the active collaboration mode. If the environment is plan-only, produce a decision-complete plan instead of editing.

## Workflow

1. **Load context**
   - Read the target technical design section or module.
   - Read allocated SRS items and acceptance criteria that drive the design slice.
   - Read architecture sections that define boundaries and viewpoints.
   - Read ADRs that constrain decisions, tradeoffs, and terminology.
   - Read roadmap/spec artifacts only as needed to understand delivery status and verified behavior.
   - Read implementation files under `src/` only where current-state accuracy is needed.
   - Read executable contracts when interfaces or schema ownership are involved.

2. **Create the impact map**
   - For each source point, assign evidence source, target technical-design section, authority type, and action.
   - Mark actions as `promote`, `defer`, `ADR`, `SRS`, `roadmap`, `contract`, `code follow-up`, `spec follow-up`, or `do not promote`.
   - Show or summarize the impact map before edits when the task requires mutation.
   - Keep out-of-scope follow-ups visible instead of silently editing extra artifacts.

3. **Update technical design**
   - Translate stable content into realization-level prose, diagrams, and tables.
   - Label current state, target state, transition state, and future state explicitly when mixed.
   - Prefer focused edits to the requested module, component, section, or concern.
   - Link to governing ADRs, allocated SRS IDs, executable contracts, and verified specs when the trace materially helps.
   - Do not copy proposal or spec prose wholesale; rewrite it for technical-design authority.

4. **Sync implementation and specs**
   - Implementation-to-design: update stale design when code already realizes stable behavior.
   - Spec-to-design: promote verified spec realization into technical design when it is reusable across features.
   - Design-to-implementation: report when design describes behavior not present in code.
   - Design-to-spec: report when design implies delivery scope not covered by active or verified specs.
   - Keep planned/unverified work labeled as planned or target state.

5. **Run consistency review**
   - Check stale terminology, duplicate authority, broken links, missing traceability, and current-vs-target drift.
   - Check that technical design does not contradict SRS, architecture, ADRs, roadmap, specs, source code, or executable contracts.
   - Run `git diff --check` on changed Markdown files and report changed-file scope.

## Technical Design Scope Rules

Promote content into technical design when it explains how the domain realizes approved requirements or decisions through:

- module boundaries and responsibilities,
- class or package relationships,
- runtime call flow and orchestration,
- persistence, cache, memory, or state behavior,
- domain-owned interface behavior,
- dependency and configuration usage,
- implementation constraints and extension points,
- verified implementation/design drift discovered in `src/` or `specs/`.

Do not promote content into technical design when it is:

- a new requirement that belongs in SRS,
- an architecture-significant decision that needs an ADR,
- feature sequencing that belongs in roadmap or `specs/`,
- payload/schema truth that belongs in executable contracts,
- operational procedure that belongs in runbooks,
- one-off research rationale that belongs in proposal or benchmark documents.

## Output Expectations

For planning-only requests, output:
- technical-design impact map,
- source and authority assessment,
- proposed target sections,
- follow-up list for non-technical-design artifacts,
- consistency review plan.

For implementation requests, deliver:
- focused technical-design updates,
- implementation/spec sync assessment,
- validation results,
- follow-up list for SRS, architecture, ADRs, roadmap, contracts, traceability, `src/`, or `specs/` items outside scope.