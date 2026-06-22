---
name: research-to-architecture-adr
description: Convert research, proposal, benchmark, or side-chat synthesis documents into long-lived architecture design updates and ADR candidates. Use when Codex needs to propagate non-authoritative research into architecture docs, produce an impact map, decide ADR boundaries, update an ADR index, or run consistency review across architecture, SRS, roadmap, technical design, contracts, and traceability.
---

# Research to Architecture ADR

## Overview

Use this skill to promote stable research/proposal claims into architecture design and ADRs without copying research prose wholesale. The workflow keeps proposal documents as evidence inputs and preserves repository authority boundaries.

For reusable tables and report templates, read `references/propagation-workflow.md` when the task asks for an impact map, ADR candidate analysis, consistency review, validation commands, or final propagation report.

## Operating Rules

- Treat research, proposal, benchmark, and side-chat content as non-authoritative input.
- Inspect governing documents before editing: SRS, architecture design, technical design, roadmap, ADR index and existing ADRs, executable contracts, and traceability files when relevant.
- Read only relevant sections after heading or search inspection unless full-document context is needed.
- Always produce a visible impact map before mutating long-lived docs unless the user already supplied an equivalent map.
- Promote each stable claim to the smallest owning artifact:
  - Architecture design owns boundaries, viewpoints, major components, runtime/data flows, and current-vs-target labels.
  - ADRs own durable decisions, options, consequences, and traceability.
  - Technical design owns realization details, modules, schemas, persistence, and integration mechanics.
  - SRS owns WHAT-level requirements, constraints, acceptance criteria, interfaces, and traceability.
  - Roadmap owns runnable increments, gates, dependencies, and backlog mirrors.
  - Executable contracts own payload and wire schema truth.
- Do not edit SRS, roadmap, technical design, contracts, or traceability unless the user explicitly includes them as targets.
- Ask the user before creating new ADRs when multiple plausible decision boundaries exist.
- Respect the active collaboration mode. If the environment is plan-only, produce a decision-complete plan instead of editing.

## Workflow

1. **Load context**
   - Read the proposal/research input.
   - Read the target architecture document and relevant existing sections.
   - Read the ADR index and nearby ADRs for naming, status, traceability, and style.
   - Read SRS, roadmap, technical design, executable contracts, and traceability only as needed to avoid authority drift.

2. **Create the impact map**
   - For each proposal point, assign target document, target section/artifact, authority type, and action.
   - Mark actions as `promote`, `defer`, `ADR`, `SRS`, `technical design`, `roadmap`, `contract`, or `do not promote`.
   - Show or summarize the impact map before edits when the task requires mutation.
   - Report follow-ups outside the requested edit scope instead of silently editing extra documents.

3. **Update architecture design**
   - Add or refine boundaries, system context, component relationships, runtime/data flows, provider/integration boundaries, and state labels.
   - Keep architecture at viewpoint level. Do not add detailed implementation module placement, exhaustive field schemas, or requirement tables.
   - Label current state, target state, future state, and transition state explicitly.
   - Track these four states when relevant: current implemented behavior, target proposed behavior, transition/migration behavior, and future optional behavior.

4. **Create or update ADRs**
   - Use an ADR when the proposal chooses a durable direction among meaningful alternatives.
   - Keep each ADR focused on one decision boundary.
   - Inspect the existing ADR index and filenames before choosing an ADR number or slug.
   - Use the next available sequence number; do not reuse existing ADR IDs.
   - Include status, context, decision, considered options, consequences, and traceability.
   - Update the ADR index when creating, renaming, or materially revising ADRs.

5. **Run consistency review**
   - Check stale terminology, duplicate authority, broken links, missing traceability, and current-vs-target drift.
   - Check that architecture and ADRs do not contradict SRS, roadmap, technical design, or executable contracts.
   - Run `git diff --check` on changed Markdown files and report changed-file scope.

## ADR Boundary Heuristics

Create separate ADRs when decisions have different reversibility, owners, risk posture, or downstream implementation constraints. Prefer one ADR when the choices are inseparable and would be confusing if approved independently.

Examples:
- Tool Gateway policy boundary and generic web evidence trust model are usually separate decisions.
- A diagram update that only reflects an already-approved requirement usually does not need a new ADR.
- Provider selection strategy may need an ADR only when it constrains production sourcing or licensing posture.

## Output Expectations

For planning-only requests, output:
- impact map,
- ADR candidates and decision-boundary questions,
- proposed architecture sections,
- consistency review plan.

For implementation requests, deliver:
- architecture updates,
- dedicated ADRs where justified,
- ADR index update,
- validation results,
- follow-up list for SRS, roadmap, technical design, contracts, or traceability items outside scope.