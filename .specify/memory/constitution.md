<!--
SYNC IMPACT REPORT
==================
Version Change: 1.3.0 → 2.0.0 (MAJOR)
Bump Rationale: Replaced an agent-memory-centric constitution with a repo-wide practical
  constitution aligned to current Spec-Driven Development, layered architecture, contract
  synchronization, multi-surface delivery, and AI runtime governance. v2.1.0 adds explicit
  document-referencing rules governing how `docs/` documents are referenced during spec-kit
  phases, including anchor-level precision, lifecycle obligations, and cross-reference
  validation.

Modified Principles:
- Memory Never Stores Facts → Spec-Driven, Traceable Delivery
- RAG Never Stores Opinions → Layered Boundaries and Explicit Ownership
- Fine-Tuning Never Stores Knowledge → Evidence-Grounded Financial Intelligence
- Prompting Controls Behavior, Not Data → Prompts, Memory, and Fine-Tuning Control Behavior, Not Truth
- Tools Compute Numbers, LLM Reasons About Them → Deterministic Tools and Contracted Interfaces
- Investment Data Sources Are External → Testability and Observability Are First-Class
- Market Manipulation Safeguards Are Enforced → Secure, Simple, Reversible Change

Added Sections:
- Artifact and Documentation Boundaries
- Document Referencing in Spec-Kit Workflows
- Spec Kit Lifecycle Obligations
- Delivery Sync Gates

Removed Sections:
- None; earlier agent-specific governance was absorbed into repo-wide principles and Memory and AI Runtime Boundaries.

Template Consistency Check:
- .specify/templates/plan-template.md: ✅ updated in v2.0.0; doc-referencing rules are cross-cutting and are now captured in the constitution directly; no template structural change needed
- .specify/templates/spec-template.md: ✅ updated in v2.0.0
- .specify/templates/tasks-template.md: ✅ updated in v2.0.0
- .specify/templates/constitution-template.md: ✅ checked, no change required
- .github/prompts/speckit.constitution.prompt.md: ✅ checked, no change required

Follow-up TODOs:
- None
-->

# DP Stock Investment Assistant Constitution

> **Purpose**: This constitution defines the governing principles for the DP Stock Investment
> Assistant project. It establishes hard rules for spec-driven delivery, architecture boundaries,
> financial-AI safety, contract synchronization, and quality gates that all contributors and AI
> agents MUST follow.

---

## Core Principles

These seven principles govern practical current development across backend, agent, frontend,
data, operations, documentation, and infrastructure. They are **non-negotiable**.

### I. Spec-Driven, Traceable Delivery
Every non-trivial change MUST start from governed artifacts and named authorities. `docs/` owns
long-lived requirements, architecture, technical design, contracts, policy, and runbooks;
`specs/` owns delivery-scoped feature artifacts and verification evidence; `.specify/` owns Spec
Kit runtime files, templates, extensions, and workflows. Delivered work MUST refresh affected
traceability and long-lived artifacts before it is considered complete. Rationale: this
repository uses Spec Kit as its delivery governance engine, so unsourced or unsynchronized work
creates drift across code, contracts, and docs.

### II. Layered Boundaries and Explicit Ownership
Implementation MUST respect ownership boundaries across frontend, backend, agent, data,
operations, and IaC surfaces. Backend request flow MUST remain `routes -> services ->
repositories -> database`; cross-cutting dependencies MUST be injected via factories,
protocols, or immutable context objects; cross-domain behavior MUST be implemented in the owning
surface rather than through ad-hoc reach-through. Rationale: the current codebase already
depends on blueprint, service, repository, and factory patterns, and preserving those seams
keeps change reviewable and testable.

### III. Evidence-Grounded Financial Intelligence
Financial outputs MUST be grounded in approved external sources, governed internal data stores,
retrieved documents with provenance, or deterministic tool output. The assistant MUST NOT invent
prices, metrics, forecasts, or investment certainty, and all outputs MUST remain informational
rather than manipulative. Rationale: in this finance domain, unsourced or hype-driven output is
a safety failure.

### IV. Prompts, Memory, and Fine-Tuning Control Behavior, Not Truth
Prompt assets, memory, and fine-tuning MAY shape behavior, structure, routing, and
personalization, but they MUST NOT become hidden fact stores. Memory retains preferences and
session context only; retrieval retains sourced documents; fine-tuning reinforces format or tone
rather than factual content. Rationale: the repository's current prompt-system and memory work
assumes this separation, and governance must keep it explicit.

### V. Deterministic Tools and Contracted Interfaces
Deterministic tools MUST fetch or compute facts; the model interprets them. Public interfaces
such as REST endpoints, streaming responses, WebSocket events, and machine-readable contracts
MUST remain explicit, version-aware, and synchronized with implementation. Rationale: the
project relies on OpenAPI, route registration, streaming surfaces, and auditable tool results;
opaque interface drift is operational risk.

### VI. Testability and Observability Are First-Class
Every material behavior MUST be verifiable and diagnosable. Focused tests, health endpoints,
structured logging, prompt or request trace metadata, and explicit degraded-mode outcomes MUST
make failures explainable across API, agent, data, frontend, and deployment surfaces.
Rationale: hidden state and silent failure block safe delivery in a multi-surface system.

### VII. Secure, Simple, Reversible Change
Changes MUST default to least privilege, minimal scope, backward-compatible evolution, and clear
rollback or migration paths. Complexity MUST be justified against a simpler modular or additive
alternative. Rationale: the current project spans microservice-style deployment, persistent data,
and evolving AI behavior, so irreversible or over-broad changes multiply risk.

---

## Project Operating Standards

### Golden Development Rules

These nine rules govern all day-to-day project development. Violations MUST be corrected before
merge.

#### 1. Start From Governing Artifacts
For every non-trivial task, identify the controlling SRS, architecture or technical design, ADR,
contract, runbook, or feature spec before changing code, docs, or IaC.

#### 2. Respect Artifact Lifecycles and Locations
`docs/` is the long-lived baseline, `specs/` is the governed delivery evidence area, and
`.specify/` is runtime and tooling support. Stable knowledge is promoted from `specs/` to `docs/`
only after verification.

#### 3. Keep Contracts and Sync Artifacts Current
When stable behavior changes, update `docs/openapi.yaml`, `specs/spec-traceability.yaml`,
`specs/spec-sync-status.md`, affected reverse-trace documents, and impacted technical design or
runbook artifacts in the same delivery cycle when relevant.

#### 4. Protect Secrets and Privileged Access
Secrets MUST NOT appear in source, logs, docs, or test fixtures. Use environment variables,
approved secret stores, and least-privilege credentials for local and production access.

#### 5. Validate With Executable Evidence First
Prefer focused tests, diagnostics, type or lint checks, schema validation, or health checks over
manual inspection. Docs-only work MUST at least pass the file diagnostics available in the
environment.

#### 6. Log and Expose Safe Operational State
Use structured logging, safe user-visible errors, health probes, and machine-detectable degraded
states. Silent failures and raw internal errors on public surfaces are prohibited.

#### 7. Preserve Architecture Seams
Routes handle transport concerns, services own business logic, repositories own persistence, and
factories or immutable context objects own dependency wiring. Do not bypass those seams with
ad-hoc shortcuts.

#### 8. Prefer Additive Migration and Backward-Compatible Rollout
Use aliases, migration scripts, versioning, fallback lineages, or staged rollout when public,
persisted, or prompt-governed behavior changes.

#### 9. Keep Changes Small, Focused, and Reviewable
Each change set MUST stay scoped to one logical outcome, include its required doc or contract or
test updates, and justify any unavoidable complexity against a simpler alternative.

### Artifact and Documentation Boundaries

- `docs/` is authoritative for long-lived requirements, architecture, technical design, ADRs,
  policy, runbooks, and executable contracts.
- `specs/` is authoritative for governed feature delivery artifacts, review evidence, and sync
  status.
- `.specify/` is the project-local Spec Kit runtime and configuration area and MUST NOT be used
  as the canonical store for governed feature delivery evidence.
- If code, specs, contracts, and long-lived docs disagree, fix the authoritative artifact first,
  then reconcile dependent references.

### Document Referencing in Spec-Kit Workflows

Cross-references between spec-kit artifacts (in `specs/`) and long-lived documents (in `docs/`)
MUST be precise and durable. Vague or unanchored references reduce traceability and break
agentic workflow context.

#### Cross-Reference Precision Rules

1. **Use section-level anchors, not document-level paths alone.** Every reference to a `docs/`
   document from a spec, plan, task, or review artifact MUST include an anchor pointing to the
   specific section, requirement ID, or heading that contains the governing content. For example,
   `docs/domains/agent/TECHNICAL_DESIGN.md#35-prompt-realization-and-guardrails` is valid;
   `docs/domains/agent/TECHNICAL_DESIGN.md` alone is not sufficient for non-trivial references.
2. **Anchor precision applies to all spec-kit phases.** `speckit.specify`, `speckit.plan`,
   `speckit.tasks`, implementation, verification, and sync artifacts MUST all use anchor-level
   references when linking to long-lived documents. Generic document-level references are
   permitted only when the entire document is the authority for the referenced concern.
3. **Repository-relative paths.** Use paths relative to the repository root (e.g.,
   `docs/domains/agent/TECHNICAL_DESIGN.md`) rather than absolute or ambiguous labels, so
   references remain valid across branches and agent sessions.
4. **Anchor validity is a sync responsibility.** When a section heading, requirement ID, or
   anchor label changes in a `docs/` document, every inbound cross-reference from `specs/`,
   other `docs/` files, and customization files MUST be updated in the same change set or in an
   immediately following maintenance change.

#### Lifecycle Obligations by Spec-Kit Phase

| Spec-Kit phase | Document-referencing obligation |
|----------------|--------------------------------|
| `speckit.specify` | The `## Governance Context` section MUST identify governing `docs/` documents with section-level anchors for every referenced authority. |
| `speckit.plan` | The Constitution Check MUST list which `docs/` documents are affected and whether their section anchors or requirement IDs will need updates. |
| `speckit.tasks` | Task descriptions MUST include explicit cross-reference validation or anchor-checking steps when feature work references or changes `docs/` documents. |
| `speckit.implement` | Code or documentation changes that modify section headings, requirement IDs, or anchor labels in `docs/` MUST be paired with updates to all inbound references. |
| `speckit.verify.run` | Verification MUST check that cross-references between `specs/` artifacts and `docs/` documents resolve to valid, non-broken anchors. |
| Steps 15-17 (sync) | The traceability-refresh and documentation-sync steps MUST validate all cross-references and flag any stale or broken anchors for correction. |

#### Agentic Workflow Guidance

- When contributing to a spec-kit artifact that references a `docs/` document, always read the
  target section first to confirm the reference is accurate and the anchor resolves to the
  intended content.
- When renaming a section heading in a `docs/` document, use grep or equivalent search to find
  all inbound references across `specs/`, other `docs/` files, and `.github/` customization
  files before committing the rename.
- Placeholder or template-style references such as `[link to relevant design doc]` MUST NOT
  survive into a published spec, plan, or task artifact. Every reference MUST be resolved to a
  concrete file path and section anchor before the artifact leaves draft status.

### Memory and AI Runtime Boundaries

These boundaries govern prompt-system, memory, and agent-runtime work so personalization,
control-plane logic, and factual data remain separated.

#### Long-Term Memory (LTM) — Allowed
- User risk profile and investment preferences
- Investment goals, time horizon, and sector interests
- Output style, language, and verbosity preferences
- Stable workspace or personalization defaults

#### Short-Term Memory (STM) — Allowed
- Current conversation context and approved assumptions
- Active routing or tool-selection state
- In-progress analysis state that is bounded to the request or conversation
- Temporary session continuity metadata

#### Explicitly Prohibited in Memory
These items MUST stay in retrieval, tools, or governed data stores rather than LTM or STM:
- Real-time or historical prices
- Financial ratios, valuations, and calculated metrics
- Raw filings, news bodies, or sourced document text used as evidence
- Forecasts, price targets, or analytical conclusions
- Investment recommendations presented as durable stored truth

#### Retrieval, Prompts, and Fine-Tuning
- Retrieval stores sourced documents with provenance and reviewable origin.
- Prompt assets encode policy, role behavior, output contracts, and guardrails rather than facts.
- Fine-tuning or reusable prompt assets MAY reinforce structure and tone but MUST NOT become a
  hidden knowledge base.
- Deterministic tools fetch and compute facts; the model interprets, frames, and cites them.

### Architecture and Design Constraints

- Use `ModelClientFactory`, `RepositoryFactory`, `ServiceFactory`, and immutable route or socket
  context objects for dependency wiring rather than manual global coupling.
- All database access MUST flow through `src/data/repositories/`; routes and presentation layers
  MUST NOT issue ad-hoc persistence queries.
- Cross-service dependencies MUST prefer protocols and composition over inheritance except for
  established base classes.
- Application code MUST use absolute imports and preserve tool-friendly import structure.
- Health endpoints, streaming surfaces, and deployment probes MUST stay aligned across code and
  IaC.

#### SOLID Constraints

- **Single Responsibility**: one concern per layer or module.
- **Open/Closed**: extend behavior with new modules or registrations instead of unrelated edits.
- **Liskov Substitution**: implementations MUST honor their published contracts.
- **Interface Segregation**: use lean interfaces and protocols instead of broad shared surfaces.
- **Dependency Inversion**: depend on abstractions and injected collaborators, not hard-coded
  concrete implementations.

---

## Workflow and Quality Gates

### Spec Kit Lifecycle Obligations

- Non-trivial work MUST follow the repository's Spec-Driven Development chain: governed
  requirements and design inputs, `speckit.constitution`, `speckit.specify`, clarification and
  checklist steps when needed, `speckit.plan`, `speckit.tasks`, implementation, verification,
  and delivery synchronization.
- Plans MUST identify governing artifacts, affected domains, sync targets, validation strategy,
  architecture impact, and rollback or migration implications.
- Tasks MUST include tests, contract updates, traceability refresh, and long-lived doc sync work
  whenever those surfaces are affected.
- All references to `docs/` documents in spec-kit artifacts MUST use section-level anchors, not
  document-level paths alone. The lifecycle table under Document Referencing in Spec-Kit
  Workflows defines the responsibility per phase.
- Documentation-first work MAY start from documentation-focused agents or workflows, but it MUST
  obey the same artifact boundaries and sync duties.

### Verification and Delivery Gates

- REST API changes MUST update `docs/openapi.yaml` and be checked against the actual registered
  public route surface.
- Prompt or agent behavior changes MUST preserve prompt identity, fallback or degradation
  metadata, and finance-safety guardrail expectations where those surfaces exist.
- Data schema, migration, or cache behavior changes MUST include migration or initialization
  evidence and compatibility checks.
- Frontend, backend, agent, and IaC changes MUST validate the affected user or operator journey
  with the narrowest executable evidence available.
- Docs-only changes MUST pass diagnostics on the touched files and keep anchors or links current.
- Cross-references between `specs/` artifacts and `docs/` documents MUST be validated for anchor
  correctness during verification. Stale or broken section-level references are a verification
  failure, not optional cleanup.

### Pre-Merge Checklist

- [ ] Governing artifacts and affected domains are identified.
- [ ] Focused executable validation or diagnostics have been run.
- [ ] Required contracts, long-lived docs, and sync artifacts are updated.
- [ ] Cross-references in spec-kit artifacts use section-level anchors and resolve to valid targets.
- [ ] No secrets or unsafe internal details are exposed.
- [ ] Any migration, fallback, rollout, or breaking-change path is documented.
- [ ] The change remains one logical slice or explicitly justifies broader scope.

### Delivery Sync Gates

- `docs/openapi.yaml` MUST be synchronized when REST API behavior changes.
- `specs/spec-traceability.yaml` and `specs/spec-sync-status.md` MUST be synchronized when
  requirement coverage or feature verification status changes.
- Domain reverse-trace documents, such as `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`, MUST be
  updated when their requirement mappings change.
- Affected technical design, architecture, or runbook documents MUST be synchronized when stable
  behavior becomes part of the long-lived baseline.

---

## Governance

### Supremacy
This constitution supersedes project-local defaults, templates, and prompt guidance. When
conflicts arise, constitutional principles take precedence, and the authoritative source for the
specific concern MUST then be reconciled across dependent artifacts.

### Amendment Process
1. Propose the amendment with rationale, affected principles, and semantic-version bump
  reasoning.
2. Validate the proposal against current repository context, templates, runtime guidance, and any
  affected long-lived docs or contracts.
3. Update the constitution, dependent templates, and any required sync references in the same
  change.
4. Record the amendment date and any deferred follow-up items in the Sync Impact Report.

### Compliance Verification
- `/speckit.plan` MUST pass the Constitution Check before research or design is treated as ready.
- `/speckit.tasks`, implementation, review, and post-implementation verification MUST confirm
  that required tests, contracts, traceability, and long-lived doc sync tasks are present when
  relevant.
- Any approved deviation MUST be written as an explicit justification in the affected plan,
  review, ADR, or equivalent governing artifact.

### Version Control
- **MAJOR**: Breaking changes to core principles or backward-incompatible governance changes
- **MINOR**: New articles, principles, or materially expanded guidance
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

**Version**: 2.1.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-06-02
