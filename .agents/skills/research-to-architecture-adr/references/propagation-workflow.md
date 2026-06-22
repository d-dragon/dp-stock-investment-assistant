# Propagation Workflow Templates

Use these templates when converting research or proposal documents into architecture design updates and ADRs.

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

## Architecture Promotion Checklist

- Does this change alter durable system boundaries, context, major components, runtime/data flow, integration ownership, or operationally relevant constraints?
- Is the content rewritten as architecture-level guidance rather than copied from a proposal?
- Are current state, target state, future state, and transition state labeled where mixed?
- Is the current implemented behavior separated from target proposed behavior?
- Is transition/migration behavior separated from future optional behavior?
- Are implementation details kept for technical design rather than architecture?
- Are links added to governing ADRs, SRS IDs, roadmap milestones, or benchmark evidence only when materially useful?

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

## Consistency Review Checklist

- One owning authority exists for each promoted claim.
- SRS owns requirements; ADRs own decisions; architecture owns boundaries; technical design owns realization; executable contracts own schemas; roadmap owns sequencing.
- Proposal and benchmark documents are cited as evidence inputs, not overriding authority.
- New architecture and ADR language does not contradict SRS, roadmap, technical design, code current state, or executable contracts.
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