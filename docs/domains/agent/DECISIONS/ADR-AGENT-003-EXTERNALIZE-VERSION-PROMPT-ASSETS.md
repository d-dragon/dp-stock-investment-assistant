# Architecture Decision Record

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-003 |
| **Domain** | Agent |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-04-13 |
| **Last Updated** | 2026-05-15 |
| **Context** | DP-StockAI-Assistant |
| **Decision Owners** | Engineering · Architecture · Agent maintainers |

## ADR-003 — Externalize and Version Prompt Assets as File-Based Configuration

## 1. Decision Summary

Externalize prompt assets as versioned, repo-owned prompt assets so prompt changes, version identity, rollback, and controlled experimentation are managed through governed assets and runtime loading rather than code edits.

The asset model is composed of:

- Versioned system prompt assets
- Baseline fallback assets per prompt lineage
- Skill fragments and experiment variants
- Runtime prompt loading and validation through `PromptAssetLoader`
- Configuration-driven activation, reload, and rollback behavior

## 2. Stakeholders Affected

- Product
- AI Engineers / Agent Maintainers
- Backend Engineers
- DevOps / SRE
- Security & Compliance
- Architecture Owners

## 3. Architecture Concerns Addressed

- Prompt version traceability
- Decoupling prompt change velocity from code deployment
- Controlled experimentation and rollback safety
- Governance of runtime-loaded prompt assets

## 4. Problem Statement

The current agent loads its system prompt from a hardcoded string in `src/core/stock_assistant_agent.py`. This creates several operational problems:

- **Code-deployment coupling**: Any prompt change requires a code commit, CI build, and deployment.
- **No version traceability**: There is no way to identify which prompt version was used for a given agent invocation.
- **No rollback path**: A bad prompt edit propagates immediately; reverting requires another code deployment.
- **No experimentation support**: A/B testing different prompts requires conditional code branches.

## 5. Decision

Externalize all prompt content into **versioned prompt assets** under a dedicated directory (e.g., `src/prompts/`), tagged with embedded metadata and loaded at runtime by a `PromptAssetLoader` component inside the planned prompt compiler path.

Key design choices:
1. **Governed text-asset format** with front-matter metadata (name, version, description, author, activation criteria) and content body.
2. **Version identity**: Each prompt asset embeds a version string (e.g., `v1.0.0`); the loader injects this into agent response metadata and trace spans (FR-1.4.6, NFR-5.2.5).
3. **Baseline fallback**: Each governed prompt lineage has a known-good baseline asset or designated baseline alias that is loaded when the selected asset fails to parse or is missing (FR-1.4.8).
4. **Activation and reload behavior**: The loader supports configuration-driven activation and reload without requiring a new code release or a mandatory full service restart, aligning with the external-prompt-management contract (FR-1.4.5, NFR-6.2.3).
5. **Directory convention**:
   ```
   src/prompts/
     system/
       shared/                    # Shared policy assets
       react_analyst/             # Current primary role lineage
         _baseline.md             # Example baseline asset
         v1.md                    # Example versioned asset
     skills/
       always_on/                 # Cross-cutting skills (see ADR-002)
       routes/                    # Route-matched skills
     experiments/
       react_analyst/             # Candidate prompt variants
   ```

## 6. Rationale

| Concern | Hardcoded Prompt | Externalized Assets |
|---------|-----------------|---------------------|
| Change velocity | Code commit + deploy per edit | Asset edit + governed activation path |
| Version traceability | None (git blame only) | Embedded version in metadata and traces |
| Rollback | Revert commit + redeploy | Switch selection to the baseline or prior version |
| Experimentation | Conditional code branches | Variant files + experiment config |
| Audit / compliance | Implicit in code history | Explicit version tag per invocation |

## 7. Consequences

**Positive:**
- Prompt changes decouple from code deployment (aligns with NFR-6.2.3).
- Every agent invocation is traceable to a specific prompt version (FR-1.4.6).
- Rollback is a configuration change, not a code revert (FR-1.4.8).
- Enables prompt experimentation without code branches (FR-1.4.9).
- Keeps the near-term target on the compiler path for the current ReAct baseline while still allowing later specialist prompt families.

**Trade-offs:**
- Requires a file-based loader with validation and caching.
- Prompt directory must be included in container images or mounted as a volume.
- Schema validation needed to prevent malformed assets from reaching production.

## 8. Related Documents

- Supersedes: None
- ADR-001 defines the prompt-compilation and layered runtime boundary that this ADR operationalizes.
- ADR-002 defines the skills-pattern composition model that relies on these externalized assets.
- `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` provides the research basis for externalized and versioned prompt assets.

## 9. Affected Views / Impacted Architectural Elements

### 9.1 Views Impacted by This Decision

| View | Impact Scope | Updated / Governed Content |
|------|--------------|----------------------------|
| Prompt and Behavior View | Primary | Governs versioned prompt assets, baseline fallback behavior, and prompt-version metadata as part of the prompt architecture |
| Development View | Primary | Governs the architectural expectation of a dedicated `src/prompts/` asset structure for prompt sources |
| Deployment View | Secondary | Governs inclusion and lifecycle of prompt assets in containers or deployment packages |
| Operations and Maintenance View | Secondary | Governs prompt-version observability, rollback posture, and baseline fallback during asset failure |

### 9.2 Architectural Elements Newly Defined or Reframed

- **Versioned Prompt Assets:** File-based prompt artifacts that carry explicit version identity and support controlled change.
- **Baseline Fallback Asset:** Last-known-good prompt asset used when a selected version is missing or invalid.
- **PromptAssetLoader:** Asset-loading mechanism that discovers, validates, and resolves prompt assets before assembly.
- **Prompt Lineage:** A governed family of related prompt assets for one role or runtime path with a defined baseline and candidate versions.
- **Runtime Reload Behavior:** Architecture-level ability to adopt prompt changes through configuration refresh or watcher-driven reload rather than code redeployment.
- **Prompt-Version Traceability:** Runtime metadata expectation that prompt versions and experiment identifiers remain observable to operators.

### 9.3 Applicability Note

This ADR is **Proposed**. The architecture-description package may describe externalized prompt assets as the intended asset layer inside the planned prompt compiler path, but companion documents must continue to distinguish the proposed asset model from the current hardcoded runtime prompt until implementation and deployment artifacts actually converge on this design.

### 9.4 Consistency Checkpoints

- [ ] Prompt and Behavior, Development, Deployment, and Operations and Maintenance views use the same asset-model terminology defined by this ADR.
- [ ] Companion documents do not describe versioned prompt assets, baseline fallback, or reload behavior as current runtime fact unless realization artifacts confirm implementation.
- [ ] `PromptAssetLoader` remains distinct from `PromptAssembler` and from the broader `Prompt Compiler` concept in concept-evolution discussions.
- [ ] Companion documents use the same near-term prompt asset taxonomy (`src/prompts/system|skills|experiments`) when describing planned file layout.
- [ ] Prompt observability and rollback language remains consistent with this ADR's proposed status and with the architecture description's planned-state labeling.

## 10. Implementation Checklist

- [ ] Define prompt asset schema with front-matter validation
- [ ] Implement PromptAssetLoader with caching, validation, and fallback logic
- [ ] Create the baseline asset for the current ReAct lineage under `src/prompts/system/react_analyst/`
- [ ] Add prompt version injection into agent response metadata
- [ ] Add prompt version to trace span attributes (NFR-5.2.5)
- [ ] Update Dockerfile to include `src/prompts/` in container image
- [ ] Add prompt asset integration tests (load, fallback, version extraction)

## 11. Traceability

Supports:

Functional requirements:

- `FR-1.4.5` External Prompt Management
- `FR-1.4.6` Prompt Version Identity
- `FR-1.4.8` Prompt Rollback Safety
- `FR-1.4.9` Prompt Experiment Assignment

Non-functional requirements:

- `NFR-5.2.5` Prompt version identifier in traces
- `NFR-5.2.7` Experiment identifier and variant assignment in traces
- `NFR-6.2.3` Versioned prompt assets configurable without code deployment

