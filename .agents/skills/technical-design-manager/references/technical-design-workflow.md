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

## Compact Cross-Reference Pattern

Use links to make claims traceable without flooding the design text. Prefer one compact reference block per subsection, table row, or diagram caption.

Recommended pattern:

```markdown
Refs: SRS FR-x/AC-y; ADR-###; `specs/<feature>/plan.md`; `src/<module>.py`; `tests/<module>`.
```

Rules:

- Use repository-relative links or inline code paths for project artifacts.
- Link a source once where it supports a design claim; do not repeat the same link in nearby sentences.
- Prefer stable requirement IDs, ADR IDs, spec paths, contract paths, and source/test files over broad document links.
- Use a `Refs:` line under a diagram or table when several claims share the same evidence.
- Report unresolved or unstable links instead of inventing anchors.

## Diagram and Table Selection Guide

Prefer visual structure when it reduces prose:

| Design Need | Preferred Form | Use When |
|-------------|----------------|----------|
| Component boundary or ownership | Mermaid `flowchart` or responsibility table | Showing modules, dependencies, stores, and external providers |
| Runtime interaction | Mermaid `sequenceDiagram` | Showing calls, async steps, gateway behavior, retries, or fallback |
| Data shape or persistence ownership | Mermaid `classDiagram`, ER-style sketch, or compact table | Showing records, state, cache, lineage, and lifecycle |
| Interface or contract relationship | Contract summary table | Linking executable schema truth without duplicating payload details |
| Current vs target drift | Comparison matrix | Separating implemented, transition, target, and future behavior |

Keep diagrams small enough to scan. Use prose only to explain non-obvious constraints, tradeoffs, or failure behavior.

## Link Budget Checklist

Before finalizing technical design content, check:

- Every important design claim has either nearby evidence or an intentional no-link rationale.
- Each subsection avoids repeated links to the same artifact.
- Links point to the narrowest useful artifact: requirement ID, ADR, spec file, contract, source file, or test file.
- Reference blocks support groups of claims instead of adding links to every sentence.
- External proposal/research links are marked as evidence input, not authority.

## Compactness Checklist

Prefer:

- one diagram plus a short caption over multi-paragraph flow explanation,
- a responsibility table over repeated component prose,
- a current/target matrix over mixed-state narrative,
- a `Refs:` line over repeated parenthetical citations,
- explicit follow-up bullets over speculative design paragraphs.

Avoid exhaustive method lists, copied schemas, full proposal rationale, duplicated requirements, and implementation task lists unless the requested technical-design slice depends on them.

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
- Link relevant SRS IDs, ADRs, specs, source files, tests, and contracts only where useful.
- Prefer diagrams, matrices, and responsibility tables when they keep the update shorter and clearer than prose.
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
- Cross-references follow the link budget and do not flood prose.
- Tables and diagrams replace verbose prose where they preserve meaning.
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
