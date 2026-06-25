---
name: research-to-architecture-adr
description: Support high-level project architecture work from research, proposals, benchmark reports, specs, source evidence, and side-chat synthesis. Use when Codex needs to brainstorm architecture solution options, review architecture design work, convert non-authoritative research into architecture updates and ADR candidates, produce architecture impact maps, decide ADR boundaries, route lower-level realization work to $technical-design-manager, update an ADR index, or run consistency review across architecture, SRS, roadmap, technical design, contracts, specs, source code, and traceability.
---

# Research to Architecture ADR

## Overview

Use this skill as a project architecture assistant for brainstorming, decision support, architecture review, and promotion of stable research/proposal claims into architecture design and ADRs. The workflow keeps proposal documents as evidence inputs and preserves repository authority boundaries.

For reusable tables and report templates, read `references/propagation-workflow.md` when the task asks for an impact map, architecture option analysis, viewpoint mapping, ADR candidate analysis, architecture review, consistency review, validation commands, or final propagation report.

## Architecture Scope Principles

- Work at architecture abstraction: stakeholders, concerns, viewpoints, system/domain boundaries, major components, integration ownership, runtime/data/deployment flows, quality attributes, risks, and ADR-worthy decisions.
- Keep architecture distinct from realization. Architecture answers what system shape, boundary, responsibility split, and decision record should exist; `$technical-design-manager` handles how modules, schemas, code paths, persistence, and domain interfaces realize those boundaries.
- Prefer high-signal diagrams, viewpoint tables, option matrices, and decision summaries over implementation walkthroughs.
- Label current, target, transition, and future state whenever architecture and implementation maturity differ.
- Treat security, operations, data, API, and implementation details as architecture concerns only when they affect durable boundaries, quality attributes, trust boundaries, or decision records.

## Operating Rules

- Treat research, proposal, benchmark, and side-chat content as non-authoritative input.
- Inspect governing documents before editing or reviewing: SRS, architecture design, technical design, roadmap, ADR index and existing ADRs, executable contracts, relevant specs, source evidence, tests, and traceability files when relevant.
- Read only relevant sections after heading or search inspection unless full-document context is needed.
- Use the project methodology first, with ISO 42010-aligned viewpoints, C4-style diagrams, arc42-style section routing, and ADR practice as supporting heuristics. Do not claim formal standards conformance unless the target document already does.
- For brainstorming and review tasks, produce options, tradeoffs, risks, and feedback without editing unless the user asks for updates.
- Always produce a visible impact map before mutating long-lived docs unless the user already supplied an equivalent map.
- Promote each stable claim to the smallest owning artifact:
  - Architecture design owns stakeholders, concerns, viewpoints, boundaries, major components, runtime/data/deployment flows, risks, and current/target/transition/future-state labels.
  - ADRs own durable decisions, drivers, options, lifecycle status, consequences, and traceability.
  - Technical design owns realization details, modules, schemas, persistence, and integration mechanics.
  - SRS owns WHAT-level requirements, constraints, acceptance criteria, interfaces, and traceability.
  - Roadmap owns runnable increments, gates, dependencies, and backlog mirrors.
  - Specs own delivery-scoped intent, plans, tasks, and verification evidence.
  - Executable contracts own payload and wire schema truth.
- Do not edit SRS, roadmap, technical design, contracts, specs, source code, tests, or traceability unless the user explicitly includes them as targets.
- Ask the user before creating new ADRs when multiple plausible decision boundaries exist.
- When content is out of architecture/ADR scope, route it to the correct owner and report the follow-up rather than forcing it into architecture prose.
- Respect the active collaboration mode. If the environment is plan-only, produce a decision-complete plan instead of editing.

## Out of Scope and Companion Routing

- Use `$technical-design-manager` for technical realization: modules, package structure, code paths, class responsibilities, persistence mechanics, detailed interfaces, executable implementation sync, and `TECHNICAL_DESIGN.md` updates.
- Route new or changed WHAT-level obligations to SRS.
- Route sequencing, delivery phases, gates, and backlog mirrors to roadmap or Spec Kit artifacts under `specs/`.
- Route payload and wire schema truth to executable contracts such as OpenAPI or JSON Schema.
- Route code, tests, migrations, and implementation tasks to implementation planning or coding workflows.
- Route deep security assessment to security review skills or threat modeling, while keeping only architecture-significant trust boundaries and security decisions here.
- Route operational procedures, recovery steps, and support workflows to runbooks or operations policy; keep only architecture-level operations boundaries and quality scenarios here.

## Workflow

1. **Load context**
   - Identify the task mode: brainstorm, review, promote, architecture update, ADR, consistency check, or mixed.
   - Read the proposal/research/spec/source input relevant to that mode.
   - Read the target architecture document and relevant existing sections.
   - Read the ADR index and nearby ADRs for naming, status, traceability, and style.
   - Read SRS, roadmap, technical design, executable contracts, specs, source files, tests, and traceability only as needed to avoid authority drift.

2. **Create the impact map**
   - For each proposal point or architecture concern, assign target document, target section/artifact, authority type, and action.
   - Mark actions as `promote`, `defer`, `ADR`, `SRS`, `technical design`, `roadmap`, `contract`, or `do not promote`.
   - Map stakeholder concerns and architecture viewpoints when the update affects boundaries, flows, data, deployment, operations, or quality attributes.
   - Mark out-of-scope details with the correct companion owner, especially `$technical-design-manager` for realization detail.
   - Show or summarize the impact map before edits when the task requires mutation.
   - Report follow-ups outside the requested edit scope instead of silently editing extra documents.

3. **Update architecture design**
   - Add or refine stakeholders, concerns, viewpoint scope, system context, component relationships, runtime/data/deployment flows, provider/integration boundaries, risk notes, and state labels.
   - Keep architecture at viewpoint level. Do not add detailed implementation module placement, exhaustive field schemas, or requirement tables.
   - Label current state, target state, future state, and transition state explicitly.
   - Track these four states when relevant: current implemented behavior, target proposed behavior, transition/migration behavior, and future optional behavior.
   - Prefer compact C4-style Mermaid diagrams and viewpoint tables when they make the architecture clearer than prose.

4. **Create or update ADRs**
   - Use an ADR when the proposal chooses a durable direction among meaningful alternatives.
   - Keep each ADR focused on one decision boundary.
   - Inspect the existing ADR index and filenames before choosing an ADR number or slug.
   - Use the next available sequence number; do not reuse existing ADR IDs.
   - Include status, context, decision, considered options, consequences, and traceability.
   - Treat accepted or rejected ADRs as stable history; create a superseding ADR instead of silently rewriting the old decision unless the user explicitly asks for a correction.
   - Update the ADR index when creating, renaming, or materially revising ADRs.

5. **Run consistency review**
   - Check stale terminology, duplicate authority, broken links, missing traceability, and current-vs-target drift.
   - Check that architecture and ADRs do not contradict SRS, roadmap, technical design, specs, source evidence, executable contracts, or traceability.
   - Check diagram quality, viewpoint fit, ADR boundary fit, and whether claims are promoted to the smallest owning artifact.
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
- architecture options and tradeoff assessment when brainstorming,
- review findings ordered by severity when reviewing,
- ADR candidates and decision-boundary questions,
- proposed architecture sections,
- out-of-scope routing and companion-skill follow-ups,
- consistency review plan.

For implementation requests, deliver:
- architecture updates,
- dedicated ADRs where justified,
- ADR index update,
- validation results,
- follow-up list for `$technical-design-manager`, SRS, roadmap, specs, contracts, code, tests, security review, operations, or traceability items outside scope.
