# Technical Design Workflow Templates

Use these templates when updating or reviewing technical design documents from governing docs, specs, and implementation evidence.

## Impact Map

Always produce or summarize this map before mutating long-lived technical design unless the user supplied an equivalent map.

| Source Point | Evidence Source | Target Technical Design Section | Authority Type | Action |
|--------------|-----------------|---------------------------------|----------------|--------|
| Stable implementation behavior | `src/` | Realization, runtime, data, or module section | Implementation evidence | Promote if verified and reusable |
| Verified Spec Kit realization | `specs/<feature>/review.md` or verified spec artifacts | Relevant realization section | Delivery evidence | Promote as stable design |
| Planned Spec Kit behavior | `specs/<feature>/plan.md` or `tasks.md` | Planned or target-state section only | Planned delivery context | Defer or label planned |
| Requirement allocation | SRS | Traceability or realization rationale | Requirement authority | Reference, do not restate |
| Architecture boundary | Architecture design | Module/runtime/data realization | Architecture authority | Translate into HOW-level design |
| Durable decision | ADR | Constraint, pattern, or tradeoff reference | Decision authority | Reference governing decision |
| Payload or wire format | Executable contract | Interface behavior summary | Schema authority | Link contract, avoid duplicating schema |
| Research recommendation | Proposal or benchmark report | Target-state or future-state design | Evidence input | Promote only stable claims |

## Governing Context Checklist

- Target technical design document and requested section or module are identified.
- Relevant SRS IDs, acceptance criteria, and constraints are read.
- Relevant architecture views and boundaries are read.
- Governing ADRs and ADR index are checked when decisions or terminology are involved.
- Relevant roadmap items are checked when sequencing or target state matters.
- Relevant Spec Kit artifacts are classified as verified, active, planned, or stale.
- Relevant implementation files under `src/` are inspected for current-state accuracy.
- Executable contracts are checked when interface or schema behavior is mentioned.

## Implementation and Spec Sync Checklist

| Drift Direction | Question | Default Action |
|-----------------|----------|----------------|
| Implementation to design | Does `src/` implement stable behavior not reflected in technical design? | Promote to current-state design if verified or obvious from code |
| Spec to design | Did a verified spec introduce reusable realization detail missing from technical design? | Promote to current-state or transition-state design |
| Design to implementation | Does technical design describe behavior not present in code? | Label planned/target/future or report code follow-up |
| Design to spec | Does technical design imply delivery scope not covered by active or verified specs? | Report spec follow-up or traceability gap |
| Contract to design | Does executable contract differ from prose design? | Treat contract as schema truth and report reconciliation |
| Architecture to design | Does technical design contradict architecture boundaries? | Adjust design or report architecture follow-up |

## Module and Component Update Checklist

- Name the module/component and its current responsibility.
- Identify upstream callers, downstream dependencies, data stores, and external providers.
- Separate current implementation from target or future behavior.
- Explain runtime flow using a compact sequence, flowchart, or table when prose is ambiguous.
- Explain state, persistence, cache, and lifecycle behavior when the component owns or transforms data.
- Link relevant SRS IDs, ADRs, specs, source files, and contracts only where useful.
- Avoid copying full code structure, exhaustive method lists, or schema payloads unless the design depends on them.

## State Labeling Rules

Use these labels consistently:

- **Current state**: implemented behavior confirmed by source code, verified specs, or stable docs.
- **Target state**: intended design direction accepted by governing docs but not fully implemented.
- **Transition state**: mixed behavior during migration from current to target.
- **Future state**: optional or exploratory direction that requires later approval or delivery.

Do not present target or future state as implemented behavior.

## Consistency Review Checklist

- Technical design owns realization detail and does not duplicate SRS, ADR, roadmap, or contract authority.
- Current-state claims match source code or verified specs.
- Planned-state claims are clearly labeled.
- Terminology matches SRS, architecture, ADRs, and current code where appropriate.
- Links to SRS IDs, ADRs, specs, contracts, and source files resolve or are reported.
- Diagrams are Mermaid where helpful and stay at one abstraction level.
- `src/` and `specs/` follow-ups are reported when outside the edit scope.
- `git diff --check` passes for changed docs.
- Changed-file scope matches the user request.

## Validation Commands

Use scoped validation whenever possible:

```powershell
git diff --check -- <changed-docs>
git diff --name-only
```

For technical-design sync work, also consider targeted searches:

```powershell
rg --line-number "<module-or-term>" docs src specs
```

Avoid broad recursive reads when a focused section or file search is enough.

## Final Report Format

Use this structure for final responses:

```markdown
Updated the technical design.

Updated:
- path/to/TECHNICAL_DESIGN.md: summary of realization changes

Impact summary:
- promoted from implementation: ...
- promoted from verified specs: ...
- labeled planned/target state: ...
- follow-ups outside scope: ...

Validation:
- git diff --check ...
- consistency review result ...
```