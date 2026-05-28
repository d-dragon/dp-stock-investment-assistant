---
description: Documentation, specification, markdown, and diagram conventions for repo docs and instruction files
applyTo: "docs/**,specs/**,.github/instructions/*.md,.github/copilot-instructions.md"
---

# Documentation and Specification Conventions

## Agent-First Operating Rules
- Treat [docs/study-hub/project-documentation-and-specification-methodology.md](../../docs/study-hub/project-documentation-and-specification-methodology.md) as the canonical source for documentation architecture, standards stance, glossary, notation policy, and the full spec-driven lifecycle.
- Use [docs/](../../docs/) for long-lived baselines such as SRS, architecture, technical design, ADRs, policy, and runbooks. Use [specs/](../../specs/) for delivery-scoped Spec Kit artifacts such as spec, plan, tasks, review, evidence, and temporary design exploration. Use [.specify/](../../.specify/) for Spec Kit runtime, configuration, template, extension, and governance material. Do not confuse [specs/](../../specs/) with [.specify/](../../.specify/).
- Before editing docs or specs, read the governing artifacts for the slice you are touching: the relevant SRS, ADR, technical design, feature spec or plan or review when present, [.specify/memory/constitution.md](../../.specify/memory/constitution.md), and [specs/spec-traceability.yaml](../../specs/spec-traceability.yaml) when traceability or sync status is in scope.
- Prefer updating an existing authority document before creating a sibling. Create a new long-lived document only when the current one cannot absorb the content cleanly.
- Promote content from [specs/](../../specs/) into [docs/](../../docs/) only after the behavior is implemented, verified, and stable enough to become reusable repository knowledge.
- Treat executable contracts such as [docs/openapi.yaml](../../docs/openapi.yaml) or JSON Schema as the source of truth for schema and payload shape. Prose should explain intent, ownership, and constraints rather than restating contracts line by line.
- If code, specs, contracts, and long-lived docs disagree, fix the authoritative artifact and the dependent references instead of preserving conflicting descriptions in parallel.

## Agentic Workflow Integration
- This instruction complements [.github/copilot-instructions.md](../copilot-instructions.md), the methodology document, and the custom agent catalog under [.github/agents/](../agents/). Do not duplicate their full prompts or workflow narratives here.
- Treat `docs/spec-driven development (SDD)/spec-kit HOW-TO.md` as the operational SDD guide for how this repository actually uses Spec Kit, including command normalization, hook expectations, governed artifact locations, and discovery of the [Documentation Spec Maintainer Agent](../agents/documentation.spec-maintainer.agent.md).
- Align documentation work with the repository's Spec Kit operating chain: `speckit.constitution`, `speckit.specify`, `speckit.clarify`, `speckit.plan`, `speckit.tasks`, `speckit.verify.run`, and `speckit.sync`. Documentation should reflect or support that workflow, not invent a second lifecycle.
- When a request is primarily documentation, traceability, or Copilot customization maintenance, prefer the [Documentation Spec Maintainer Agent](../agents/documentation.spec-maintainer.agent.md) as the entry point and keep its edits aligned with this instruction and the Spec-Kit HOW-TO.
- When updating long-lived docs because of a delivered feature, use the verified feature artifacts in [specs/](../../specs/) and the traceability registry as your primary inputs rather than inferring intent from code alone.
- When a feature is still planned or partially implemented, label future-state or mixed-state documentation explicitly rather than documenting planned behavior as settled fact.
- When editing Copilot customization files in [.github/instructions/](../instructions/) or [.github/copilot-instructions.md](../copilot-instructions.md), keep rules short, self-contained, broadly applicable, and non-conflicting with repository-wide instructions, path-specific instructions, and custom agent profiles.
- Front-load the highest-value rules in customization files. Copilot code review may only consume the early portion of a custom instruction file.

## Artifact Lifecycles and Promotion
- Long-lived artifacts in [docs/](../../docs/) own stable system and domain knowledge. Delivery-scoped artifacts in [specs/](../../specs/) own feature detail, sequencing, verification evidence, and temporary exploration.
- [.specify/](../../.specify/) holds Spec Kit runtime and configuration state, templates, extensions, presets, and governance artifacts. It is not the repo-governed feature evidence area.
- Treat Step 17 of the repository's SDD lifecycle as the documentation sync phase: once a feature is verified, update the smallest long-lived document that should permanently own the new knowledge.
- Promote only stable, reusable, or cross-feature content. Keep transient rollout notes, active task sequencing, or one-off analysis in [specs/](../../specs/) unless they become part of the enduring operating model.
- When stable behavior changes, update the governing long-lived docs, traceability links, and any affected downstream references in the same change when practical.

## Authority Boundaries and Reconciliation
- Requirements belong in SRS documents, not in ADRs.
- Decisions belong in ADRs, not in SRS or technical design docs.
- Realization details belong in technical design docs, not in ADRs or the master SRS.
- Schemas and payload shapes belong in executable contracts such as OpenAPI or JSON Schema.
- Runbooks own operational procedures, rollout, recovery, reconciliation, and support workflows.
- Study and analysis documents inform decisions but are not long-lived authority baselines.
- The master system SRS owns system outcomes and cross-domain qualities. Domain SRS documents may specialize domain-local behavior without contradicting the master baseline.
- ADRs own decision rationale and consequences. Technical design owns how a domain realizes approved requirements. Executable contracts own schema shape. Runbooks own operational truth.
- When artifacts disagree, reconcile the authoritative source for that concern, then update references, specs, or supporting prose so the repository returns to one consistent story.
- Use [specs/spec-traceability.yaml](../../specs/spec-traceability.yaml) and the repository's sync workflow when long-lived docs, specs, and verified implementation appear to have drifted apart.

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
- For customization files, keep frontmatter accurate (`description`, `applyTo`, and `excludeAgent` when intentionally needed) and avoid conflicting instructions across scopes.
- Prefer operational guidance over methodology duplication in instruction files; point to canonical sources when detail already exists elsewhere.

## Synchronization Rules
- When implementation changes stable behavior, update the appropriate long-lived document in the same change when practical.
- When a feature spec produces stable, reusable knowledge, promote it into the smallest existing `docs/` artifact that can own it after verification.
- When promoting diagrams from `specs/` to `docs/`, normalize them to the destination document's notation policy.
- Use repository-relative Markdown links for cross-document references, and prefer section-level anchors when a specific subsection, requirement family, or traceability point is the real authority.
- Point each cross-reference to the authoritative artifact for that concern: SRS for requirements, ADRs for decisions, technical design for realization, executable contracts for schema shape, runbooks for operational procedures, and verified feature specs for delivery evidence.
- Keep bidirectional references where they materially improve traceability: architecture docs should link to governing ADRs and related technical design, technical design should link to governing ADRs, allocated SRS items, and owned contracts, and SRS documents should link to downstream design, specs, or verification artifacts when those links are stable.
- When documents are renamed, split, promoted, retired, or significantly restructured, update inbound and outbound links in the same change set so no stale baseline remains referenced.
- When a feature's requirement coverage or verification state changes, update the relevant traceability artifacts and reverse traces in the same change when practical.
- If code, contracts, specs, and long-lived docs disagree, reconcile the authoritative source instead of duplicating conflicting descriptions.

## Common Documentation Tasks

### Add or Update Architecture Design
1. Confirm the change belongs in a long-lived architecture document rather than a feature spec. If the content is still feature-scoped or speculative, keep it in [specs/](../../specs/) until it stabilizes.
2. Read the governing ADRs, allocated SRS items, and the relevant feature spec or plan or review when the architecture change is driven by a delivered feature.
3. Keep the document at architecture level: describe system or domain boundaries, major building blocks, runtime interaction views, and viewpoint-specific concerns without drifting into detailed implementation.
4. Use C4-style Mermaid views where they clarify context, container, component, deployment, or runtime flow relationships.
5. Link the architecture document to its governing ADRs, related technical design documents, relevant contracts, and relevant operations policy.
6. Label current, planned, and transition state explicitly when the architecture is partially implemented or evolving.

### Add or Update an ADR
1. Confirm the change is an architecture-significant decision rather than a requirement update or technical design elaboration.
2. Link the ADR to the driving spec, plan, architecture concern, or implementation follow-up when that trace materially helps future readers.
3. Keep the ADR focused on the decision, drivers, consequences, affected stakeholders, and traceability.
4. Move sustained architecture description to architecture docs and sustained realization detail to technical design docs.
5. Use tables first; add a simple Mermaid diagram only when it materially improves the decision record.

### Add or Update Technical Design
1. Confirm the document stays within one domain or bounded context and identify the governing ADRs, SRS items, and source specs it realizes.
2. If the design realizes an active feature, link the relevant spec, plan, review, or verification evidence instead of rewriting delivery history in prose.
3. Describe how the domain realizes allocated requirements, including internal boundaries, internal components, runtime behavior, persistence or state behavior, and domain-specific constraints that do not belong in system architecture.
4. Explain domain-owned interfaces and link to executable contracts or schemas, but do not duplicate payload or schema definitions that already live in machine-readable artifacts.
5. Ensure the document covers the views needed to explain scope, realization, interfaces, data or state behavior, and traceability, using diagrams and tables that stay within one abstraction level.
6. Cross-link the governing ADRs, allocated requirement IDs, owned contracts, and relevant operations or verification documents where they materially shape the design.
7. Mark planned work, deprecated sections, mixed current or future state, and known gaps explicitly instead of leaving them implicit.

### Add or Update an SRS Document
1. Confirm whether the change belongs in the master system SRS, a justified domain SRS, or still-delivery-scoped feature material. Default feature detail to [specs/](../../specs/) until it becomes stable requirement language.
2. Write stable requirement entries with IDs, type, title, SHALL or MUST statement, priority, primary owning domain, contributing domains, linked documents or contracts, and spec coverage status when applicable.
3. Keep decision rationale in ADRs, realization detail in technical design, and schema structure in executable contracts rather than duplicating those concerns inside the SRS.
4. Update change-control metadata, revision history, and cross-references to affected specs, design documents, contracts, and verification artifacts in the same change set.
5. Update or reference downstream specs, design docs, contracts, and traceability artifacts when requirement coverage changes.
6. Reconcile contradictions against the authoritative baseline instead of preserving competing requirement wording across master and domain SRS documents.

### Promote Content from Specs
1. Confirm the content is implemented, verified, and stable enough to become reusable knowledge; do not promote from clarification or planning artifacts alone.
2. Use the relevant `spec.md`, `plan.md`, `review.md`, and traceability entries as promotion inputs so the promoted text reflects verified behavior.
3. Move the content into the smallest existing long-lived document that can own it.
4. Rework diagrams and surrounding language to match the target document type instead of copying raw spec content unchanged.
5. Update inbound and outbound links, reverse traces, and status documents when the promotion changes where readers should look for authoritative guidance.

### Add or Update a Copilot Customization File
1. Choose the narrowest scope that fits: repository-wide guidance in [.github/copilot-instructions.md](../copilot-instructions.md), path-specific guidance in [.github/instructions/](../instructions/), and agent-specific behavior in [.github/agents/](../agents/).
2. Put the highest-value operational rules first and keep them self-contained.
3. Do not restate the full methodology or custom agent prompts; link to canonical docs or agent profiles when detail already exists elsewhere.
4. Keep scopes non-conflicting and use `excludeAgent` only when a file should intentionally not affect cloud agent or code review.
5. When changing instruction scope or file location, update nearby references so future agents can still find the intended authority quickly.