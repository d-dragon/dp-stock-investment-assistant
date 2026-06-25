# Propagation Workflow Templates

Use these templates when converting research or proposal documents into architecture design updates and ADRs.

## Architecture Task Router

Classify the request before editing:

| Task Mode | Use When | Default Output | Default Edit Behavior |
|-----------|----------|----------------|-----------------------|
| Brainstorm | User asks for solution options, design alternatives, or tradeoff help | Options, tradeoff matrix, recommended direction, open decisions | No edits unless explicitly requested |
| Review | User asks to evaluate architecture/design work | Findings by severity, drift/misconceptions, follow-ups | No edits unless explicitly requested |
| Promote | User provides research/proposal/spec evidence to propagate | Impact map and target artifact actions | Edit only requested targets |
| Architecture Update | User asks to update architecture docs | Viewpoint-level changes, diagrams, correspondences | Architecture docs only by default |
| ADR | User asks for durable decisions or ADRs | ADR candidates, boundary questions, ADR files/index | Ask before creating ADRs when boundaries are ambiguous |
| Consistency Check | User asks for alignment/drift review | Cross-artifact consistency report | No edits unless explicitly requested |

If a request combines modes, run the impact map first and keep each output tied to its authority owner.

## Architecture Abstraction-Level Checklist

Keep architecture work at the level of:

- stakeholders, concerns, viewpoints, and scope boundaries,
- system/domain context, external actors, and external dependencies,
- major components, containers, responsibilities, and dependency direction,
- runtime, data, deployment, integration, and operations flows,
- quality attributes, risks, trust boundaries, and degraded-mode boundaries,
- durable decisions that need ADRs or ADR follow-ups.

Do not turn architecture sections into module inventories, schema definitions, code walkthroughs, implementation task lists, or delivery plans. Route those to the correct companion artifact.

## Out-of-Scope Routing Matrix

| Content Found | Do Not Put It In Architecture As | Correct Owner | Action |
|---------------|----------------------------------|---------------|--------|
| Detailed modules, packages, classes, code paths, algorithms | Architecture implementation prose | `$technical-design-manager` / `TECHNICAL_DESIGN.md` | Report technical-design follow-up |
| Persistence mechanics, indexes, cache policy details, schema fields | Architecture data-model detail | `$technical-design-manager` or executable data contracts | Report technical-design or contract follow-up |
| New WHAT-level behavior, constraints, acceptance criteria | Architecture requirement text | SRS | Report SRS follow-up |
| Sequencing, rollout phases, backlog mirrors, delivery gates | Architecture roadmap | Roadmap or `specs/` | Report roadmap/spec follow-up |
| Payloads, wire formats, API schema examples | Architecture schema authority | Executable contracts | Report contract follow-up |
| Source code edits, migrations, tests, implementation tasks | Architecture action list | Implementation workflow | Report code/test follow-up |
| Deep security vulnerabilities, exploit paths, mitigations | Architecture security audit | Security review or threat modeling | Keep only architecture-significant trust boundary or ADR |
| Operational procedures, runbooks, incident response steps | Architecture operations manual | Runbooks or operations policy | Keep only operations boundary or quality scenario |

## Companion Skill Handoff Pattern

Use this when architecture review exposes realization work:

```markdown
Use `$technical-design-manager`.
Inputs: <architecture section>, <ADR/SRS/spec/source evidence>.
Target: <TECHNICAL_DESIGN.md section/module>.
Task: Translate the approved architecture boundary into compact realization design, produce a linked impact map, prefer diagrams/tables, and report code/spec follow-ups outside scope.
```

Use the handoff pattern as a follow-up, not as an instruction to edit technical design unless the user explicitly expands the target documents.

## Impact Map

Always produce or summarize this map before mutating long-lived documents unless the user supplied an equivalent map.

| Proposal Point | Target Document | Target Section or Artifact | Authority Type | Action |
|----------------|-----------------|----------------------------|----------------|--------|
| Stable requirement or constraint | SRS | FR/NFR/CON/AC/IR section | Requirement authority | Promote as SHALL/MUST language |
| Boundary, component, or runtime relationship | Architecture design | Context, component, runtime, data, or deployment view | Architecture authority | Promote as viewpoint-level design |
| Module, schema, persistence, or integration detail | Technical design | Realization, data, interface, or runtime section | Realization authority | Promote as HOW-level design |
| Irreversible or architecture-significant choice | ADR | New or existing ADR | Decision authority | Record decision, alternatives, consequences |
| Sequencing, dependency, or delivery gate | Roadmap | Phase, milestone, backlog mirror | Planning authority | Promote as traceable delivery sequence |
| Payload or wire format | Executable contract | OpenAPI, JSON Schema, or owned contract artifact | Schema authority | Promote to machine-readable contract |
| Research rationale or external comparison | Proposal or benchmark report | Research log, benchmark matrix, reference index | Evidence input | Keep as supporting evidence |
| Detailed realization or implementation evidence | Technical design | `TECHNICAL_DESIGN.md` section/module | Realization authority | Hand off to `$technical-design-manager` unless explicitly targeted |

## Stakeholder, Concern, and Viewpoint Map

Use this map when an architecture change affects multiple audiences or views.

| Proposal Point / Concern | Stakeholder(s) | Architecture Viewpoint | Target Section | State Label | Action |
|--------------------------|----------------|------------------------|----------------|-------------|--------|
| Boundary or external dependency | Product, Security, Architecture Owners, Engineers | Context and Boundary | System context, dependency table, boundary note | Current / Target / Transition / Future | Promote or defer |
| Component ownership or dependency direction | Engineers, Architecture Owners | Logical | Building blocks, responsibility table, dependency diagram | Current / Target / Transition / Future | Promote or ADR |
| Runtime behavior or failure path | Engineers, SRE, QA | Process | Runtime sequence, degraded-mode flow, resilience note | Current / Target / Transition / Future | Promote or technical design follow-up |
| State, evidence, data, or lifecycle boundary | Data, Security, Engineers | Information and State | Data/state allocation, lifecycle table | Current / Target / Transition / Future | Promote or contract follow-up |
| Deployment or operational concern | SRE, Security, Architecture Owners | Deployment / Operations | Topology, health, observability, runbook boundary | Current / Target / Transition / Future | Promote or operations follow-up |
| Behavioral policy or guardrail | AI maintainers, Security, Product | Prompt and Behavior | Guardrail boundary, tool-risk view, behavior taxonomy | Current / Target / Transition / Future | Promote or ADR |

## Architecture Section Selection Guide

Route content to the smallest useful architecture section. Use project methodology first; use ISO 42010, C4, and arc42 as heuristics, not as claims of formal conformance.

| Content Type | Architecture Target | Useful Form |
|--------------|---------------------|-------------|
| Entity, scope, external actors, external systems | Context and Boundary view | C4-style context diagram, dependency table |
| Containers, major building blocks, ownership | Logical view | C4-style container/component sketch, responsibility table |
| Important runtime scenarios | Process view | Mermaid sequence or flowchart |
| State, memory, cache, evidence, data lifecycle | Information and State view | State/lifecycle table, data-flow diagram |
| Deployment topology, environments, probes, scaling | Deployment view | Deployment table or topology sketch |
| Operations, observability, failure/degraded behavior | Operations and Maintenance view | Quality scenario table, decision flow |
| Prompt, guardrails, tool policy, behavioral constraints | Prompt and Behavior view | Boundary diagram, risk taxonomy table |
| Durable choice among meaningful alternatives | ADR | ADR with decision, options, consequences |
| Detailed modules, schemas, algorithms, storage mechanics | Technical design | Report follow-up unless target includes technical design |

## Option Tradeoff Matrix

Use this for brainstorming and decision support before creating or updating ADRs.

| Option | Summary | Benefits | Costs / Risks | Fit to SRS / Architecture | Implementation Impact | ADR Needed? |
|--------|---------|----------|---------------|---------------------------|-----------------------|-------------|
| Option A |  |  |  |  |  | Yes / No |
| Option B |  |  |  |  |  | Yes / No |
| Recommended |  |  |  |  |  |  |

State the recommendation separately and identify what evidence would change it.

## Architecture Promotion Checklist

- Does this change alter durable system boundaries, context, major components, runtime/data flow, integration ownership, or operationally relevant constraints?
- Is the content rewritten as architecture-level guidance rather than copied from a proposal?
- Are current state, target state, future state, and transition state labeled where mixed?
- Is the current implemented behavior separated from target proposed behavior?
- Is transition/migration behavior separated from future optional behavior?
- Are implementation details kept for technical design rather than architecture?
- Are links added to governing ADRs, SRS IDs, roadmap milestones, or benchmark evidence only when materially useful?
- Does every diagram stay within one viewpoint and one abstraction level?
- Are C4-style context/container/component/dynamic/deployment diagrams used only where they clarify the architecture?
- Are low-level realization details routed to `$technical-design-manager` instead of embedded in architecture?

## ADR Candidate Checklist

Create an ADR when at least one is true:
- The project chooses one durable direction among meaningful alternatives.
- The decision constrains future implementation choices.
- The decision affects ownership, trust boundaries, provider strategy, security posture, deployment, or operational cost.
- Future maintainers will need the decision drivers and rejected options.

Avoid an ADR when:
- The change is only a wording cleanup.
- The content is an implementation detail better owned by technical design.
- The decision is already covered by an existing ADR.
- The proposal is still exploratory and not ready for durable commitment.

## ADR Naming and Index Rules

- Inspect existing ADR filenames and the ADR index before creating a new ADR.
- Use the next available sequence number in the local ADR series.
- Keep filenames stable, uppercase prefix if the repo already uses it, and a concise hyphenated slug.
- Do not reuse an existing ADR number or create parallel index entries for the same decision.
- Update the ADR index in the same change whenever creating, renaming, or materially revising ADRs.
- Link ADRs to relevant architecture sections, SRS IDs, roadmap milestones, benchmark reports, or proposal inputs only when the trace is useful.

## ADR Lifecycle Checklist

| Status | Meaning | Skill Behavior |
|--------|---------|----------------|
| Proposed | Decision is ready for review but not accepted | Create or update when the user asks for candidate ADRs |
| Accepted | Decision is approved and governs future work | Treat as stable decision history; do not rewrite materially without explicit correction scope |
| Superseded | Later ADR replaces this decision | Create a new ADR and update the index/linkage |
| Rejected | Decision was considered and rejected | Preserve rationale to avoid repeat debate |

Ask the user before creating ADRs when multiple decision boundaries are plausible, when status is unclear, or when superseding an accepted ADR may be required.

## Architecture Review Checklist

Use findings-first style for review tasks:

- Boundary accuracy: system, domain, external provider, and data boundaries match governing docs and current evidence.
- Viewpoint fit: content belongs in architecture, not SRS, technical design, roadmap, contract, spec, or runbook.
- Decision coverage: durable choices have ADRs or documented ADR follow-ups.
- Abstraction level: architecture sections avoid module inventories, code walkthroughs, schema fields, and delivery task lists.
- Companion routing: technical realization work is handed off to `$technical-design-manager`; requirements, roadmap, contracts, code, tests, security, and operations work are routed to their owners.
- Current/target drift: implemented, transition, target, and future-state claims are labeled correctly.
- Duplicate authority: requirements, schemas, implementation details, and delivery sequencing are not duplicated in architecture.
- Diagram quality: Mermaid/C4-style diagrams have clear scope, one abstraction level, readable labels, and no stale terminology.
- Traceability: useful links to SRS IDs, ADRs, roadmap items, technical design, contracts, specs, or source evidence are present and not excessive.
- Consistency: architecture and ADRs do not contradict SRS, technical design, roadmap, specs, source evidence, executable contracts, or traceability.

## Consistency Review Checklist

- One owning authority exists for each promoted claim.
- SRS owns requirements; ADRs own decisions; architecture owns boundaries; technical design owns realization; executable contracts own schemas; roadmap owns sequencing.
- Proposal and benchmark documents are cited as evidence inputs, not overriding authority.
- New architecture and ADR language does not contradict SRS, roadmap, technical design, specs, code current state, tests, traceability, or executable contracts.
- Terminology is consistent across updated documents.
- Current-state, target-state, transition-state, and future-state wording is explicit where relevant.
- ADR index links resolve.
- `git diff --check` passes for changed docs.
- Changed-file scope matches the user request.

## Validation Commands

Use scoped validation whenever possible:

```powershell
git diff --check -- <changed-docs>
git diff --name-only
```

When ADRs are created, also verify:

```powershell
Test-Path <new-adr-path>
Select-String -Path <adr-index-path> -Pattern "<new-adr-id-or-slug>"
```

For untracked files, run a direct trailing-whitespace scan if normal `git diff --check` cannot see them.

## Final Report Format

Use this structure for final responses:

```markdown
Implemented the research-to-architecture propagation.

Updated:
- path/to/ARCHITECTURE_DESIGN.md: summary of architecture changes
- path/to/DECISIONS/ADR-...md: summary of decision
- path/to/DECISIONS/AGENT_ARCHITECTURE_DECISION_RECORDS.md: ADR index update

Impact summary:
- promoted to architecture: ...
- recorded as ADRs: ...
- deferred follow-ups: ...

Validation:
- git diff --check ...
- link checks ...
- consistency review result ...
```
