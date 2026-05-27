---
description: Documentation, specification, markdown, and diagram conventions for repo docs and instruction files
applyTo: "docs/**,specs/**,.github/instructions/*.md,.github/copilot-instructions.md"
---

# Documentation and Specification Conventions

## Canonical Sources and Boundaries
- Treat `docs/study-hub/project-documentation-and-specification-methodology.md` as the canonical repository source for documentation architecture, standards stance, and document-type notation policy.
- Use `docs/` for stable requirements, architecture, technical design, policy, and ADR artifacts.
- Use `specs/` for delivery-scoped feature detail, planning, tasks, evidence, and temporary design exploration.
- Update an existing long-lived document before creating a sibling when the current document can absorb the content cleanly.

## Authority Boundaries
- Requirements belong in SRS documents, not in ADRs.
- Decisions belong in ADRs, not in SRS or technical design docs.
- Realization details belong in technical design docs, not in ADRs or the master SRS.
- Schemas and payload shapes belong in executable contracts such as OpenAPI or JSON Schema.
- Runbooks own operational procedures, rollout, recovery, reconciliation, and support workflows.
- Study and analysis documents inform decisions but are not long-lived authority baselines.

## Diagram and Notation Policy
- Default to Mermaid for diagrams in Markdown. Keep diagrams text-based, diffable, and review-friendly.
- Use C4-style diagrams in system architecture documents for context, container, component, and deployment views.
- Use Mermaid flowchart, sequence, state, class, ER, and interface diagrams in technical design docs when they clarify domain internals, runtime behavior, or persistence structure.
- Use Markdown tables first in ADRs. Add only simple Mermaid visuals when they materially improve decision-impact clarity.
- Use tables first in SRS, governance, and traceability documents. Add Mermaid only for scope, allocation, lifecycle, or traceability relationships that are clearer visually.
- Use lightweight Mermaid in `specs/`. When promoting a diagram into `docs/`, rewrite it to the notation policy of the target document type instead of copying it unchanged.
- Use BPMN only for operations or business-process flows with explicit human handoffs, approvals, or recovery paths.
- Keep executable contracts schema-first. Supporting diagrams may explain context, but they must not override machine-readable contract definitions.

## Diagram Quality Rules
- Keep one abstraction level per diagram. Do not mix system context, internal component design, and task sequencing in a single visual.
- Prefer several small diagrams over one dense omnibus diagram.
- Match diagram scope to document authority: architecture docs show boundaries and interactions, technical design shows realization, and specs show delivery coordination.
- Precede each non-trivial diagram with a one-sentence purpose statement or caption that names the scope.
- Label planned or future-state diagrams clearly when the behavior is not fully implemented.
- Label migration, transition, or mixed-state diagrams explicitly when implemented and planned elements appear together.
- Prefer direct labels and consistent naming for actors, systems, boundaries, and data stores; add a legend only when symbols, colors, or line styles repeat enough to need decoding.
- Keep reading direction predictable; if crossings or node count start to dominate, split the visual into smaller diagrams.
- Do not rely on color alone for meaning; diagrams must still read clearly in plain Markdown renderers.
- Pair complex visuals with a compact table or short interpretation notes when that reduces ambiguity.
- Replace stale ASCII-art diagrams with Markdown-native diagrams when the result is clearer and easier to maintain.

## Markdown and Structure
- Prefer explicit section headings, short paragraphs, and compact tables.
- Keep document control, revision history, traceability, and stakeholder sections synchronized when that document type already uses them.
- Preserve repository terminology from the canonical glossary in the methodology document.
- Use repository-relative Markdown links and keep path references consistent with the current repo structure.

## Synchronization Rules
- When implementation changes stable behavior, update the appropriate long-lived document in the same change when practical.
- When a feature spec produces stable, reusable knowledge, promote it into the smallest existing `docs/` artifact that can own it.
- When promoting diagrams from `specs/` to `docs/`, normalize them to the destination document's notation policy.
- Use repository-relative Markdown links for cross-document references, and prefer section-level anchors when a specific subsection, requirement family, or traceability point is the real authority.
- Point each cross-reference to the authoritative artifact for that concern: SRS for requirements, ADRs for decisions, technical design for realization, executable contracts for schema shape, and runbooks for operational procedures.
- Keep bidirectional references where they materially improve traceability: architecture docs should link to governing ADRs and related technical design, technical design should link to governing ADRs, allocated SRS items, and owned contracts, and SRS documents should link to downstream design, specs, or verification artifacts when those links are stable.
- When documents are renamed, split, promoted, retired, or significantly restructured, update inbound and outbound links in the same change set so no stale baseline remains referenced.
- If code, contracts, specs, and long-lived docs disagree, reconcile the authoritative source instead of duplicating conflicting descriptions.
- Resolve conflicts using the documented precedence rules: the master system SRS prevails for system outcomes and cross-domain qualities, domain SRS documents may specialize domain-local behavior without contradicting the master baseline, and executable contracts prevail for schema shape.

## Common Documentation Tasks

### Add or Update Architecture Design
1. Keep the document at architecture level: describe system or domain boundaries, major building blocks, runtime interaction views, and viewpoint-specific concerns without drifting into detailed implementation.
2. Use C4-style Mermaid views where they clarify context, container, component, deployment, or runtime flow relationships.
3. Link the architecture document to its governing ADRs, related technical design documents, and relevant contracts or operations policy.
4. Label current, planned, and transition state explicitly when the architecture is partially implemented or evolving.

### Add or Update an ADR
1. Keep the ADR focused on the decision, drivers, consequences, affected stakeholders, and traceability.
2. Move sustained architecture description to architecture docs and sustained realization detail to technical design docs.
3. Use tables first; add a simple Mermaid diagram only when it materially improves the decision record.

### Add or Update Technical Design
1. Confirm the document stays within one domain or bounded context and identify the governing ADRs, SRS items, and source specs it realizes.
2. Describe how the domain realizes allocated requirements, including internal boundaries, internal components, runtime behavior, persistence or state behavior, and domain-specific constraints that do not belong in system architecture.
3. Explain domain-owned interfaces and link to executable contracts or schemas, but do not duplicate payload or schema definitions that already live in machine-readable artifacts.
4. Ensure the document covers the views needed to explain scope, realization, interfaces, data or state behavior, and traceability, using diagrams and tables that stay within one abstraction level.
5. Cross-link the governing ADRs, allocated requirement IDs, owned contracts, and relevant operations or verification documents where they materially shape the design.
6. Mark planned work, deprecated sections, mixed current or future state, and known gaps explicitly instead of leaving them implicit.

### Add or Update an SRS Document
1. Confirm whether the change belongs in the master system SRS or a justified domain SRS; default to the master baseline for cross-domain behavior and qualities.
2. Write stable requirement entries with IDs, type, title, SHALL or MUST statement, priority, primary owning domain, contributing domains, linked documents or contracts, and spec coverage status when applicable.
3. Keep decision rationale in ADRs, realization detail in technical design, and schema structure in executable contracts rather than duplicating those concerns inside the SRS.
4. Update change-control metadata, revision history, and cross-references to affected specs, design documents, contracts, and verification artifacts in the same change set.
5. Reconcile contradictions against the authoritative baseline instead of preserving competing requirement wording across master and domain SRS documents.

### Promote Content from Specs
1. Confirm the content is stable and cross-feature before promoting it.
2. Move it into the smallest existing long-lived document that can own it.
3. Rework diagrams and surrounding language to match the target document type instead of copying raw spec content unchanged.