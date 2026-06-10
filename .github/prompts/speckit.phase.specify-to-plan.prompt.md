---
description: Transition from a completed Spec Kit feature specification into an implementation plan for this repository's governed SDD workflow.
argument-hint: feature=example-feature
agent: speckit.plan
---

Use this prompt when the feature specification is ready and the next step is to produce or refresh `plan.md` for the same feature.

Repository-specific planning rules:

- Treat [docs/spec-driven development (SDD)/spec-kit HOW-TO.md](../../docs/spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md) as the operational guide for this repository's Spec Kit lifecycle, especially the sections covering:
  - governed artifacts under `specs/`
  - the `specify -> clarify -> plan -> tasks -> implement -> verify` flow
  - synchronization targets after delivery
- Read [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md) before planning and carry its rules into the plan.
- Governed delivery artifacts belong in `specs/<feature>/`. Do not move feature work into `.specify/`.
- Prefer concrete repository paths, validation steps, and sync targets over generic plan boilerplate.

Planning handoff instructions:

1. Read `specs/${input:feature:example-feature}/spec.md`.
2. If present, read existing planning context for that feature:
   - `specs/${input:feature:example-feature}/plan.md`
   - `specs/${input:feature:example-feature}/research.md`
   - `specs/${input:feature:example-feature}/data-model.md`
   - `specs/${input:feature:example-feature}/quickstart.md`
   - `specs/${input:feature:example-feature}/contracts/`
   - `specs/${input:feature:example-feature}/checklists/requirements.md`
3. Read `specs/spec-traceability.yaml` and `specs/spec-sync-status.md` when requirement mapping, coverage, or downstream sync targets are relevant.
4. Follow the governance context and source authorities declared inside the feature spec instead of inventing a new source list.
5. Produce or refresh `specs/${input:feature:example-feature}/plan.md` with:
   - implementation summary
   - technical context
   - constitution check
   - concrete source paths to create or modify
   - test and verification strategy
   - required sync targets in `docs/`, `specs/`, contracts, and config
   - any follow-up artifacts that the plan phase should create or refresh, including `research.md`, `data-model.md`, and `quickstart.md`
6. Keep open questions explicit. If the spec leaves a planning-critical gap, mark it clearly instead of guessing.

Quality bar for this repository:

- Plans must be specific enough that `speckit.tasks` can generate phased, dependency-aware tasks without reinterpreting intent.
- Plans must name real code paths under `src/`, `frontend/`, `tests/`, `config/`, `IaC/`, or `docs/` when those paths are affected.
- Plans must preserve traceability and note any required updates to:
  - `specs/spec-traceability.yaml`
  - `specs/spec-sync-status.md`
  - `docs/openapi.yaml`
  - affected architecture or technical design docs

Concrete example feature:

- Use `specs/example-feature/` as the placeholder reference for how this repository structures a feature specification and implementation plan.
- When invoked without a different `feature=` argument, assume `example-feature`.

Expected result:

- A repository-scoped implementation plan aligned to the current feature spec, ready for `speckit.tasks`.
