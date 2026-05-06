# Architecture Decision Record

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-003 |
| **Domain** | Agent |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-04-13 |
| **Last Updated** | 2026-05-06 |
| **Context** | DP-StockAI-Assistant |
| **Decision Owners** | Engineering · Architecture · Agent maintainers |

## ADR-003 — Externalize and Version Prompt Assets as File-Based Configuration

## 1. Decision Summary

Externalize prompt assets as versioned file-based configuration so prompt changes, version identity, rollback, and controlled experimentation are managed through governed assets and runtime loading rather than code edits.

The asset model is composed of:

- Versioned system prompt files
- Baseline fallback assets
- Skill fragments and prompt variants
- Runtime prompt loading and validation
- Configuration-driven reload and rollback behavior

## 2. Stakeholders Affected

- DevOps
- AI engineers
- Product

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

Externalize all prompt content into **versioned file-based assets** under a dedicated directory (e.g., `src/prompts/`), version-tagged via embedded metadata, and loaded at runtime by a `PromptAssetLoader` component.

Key design choices:
1. **YAML format** with front-matter metadata (name, version, description, author, activation_criteria) and content body.
2. **Version identity**: Each prompt asset embeds a version string (e.g., `v1.0.0`); the loader injects this into agent response metadata and trace spans (FR-1.4.6, NFR-5.2.5).
3. **Baseline fallback**: A `_baseline.yaml` prompt is always present and is loaded when the configured prompt version fails to parse or is missing (FR-1.4.8).
4. **Hot-reload capability**: The loader supports configuration-driven reload (via config change or service restart) without requiring a new code release (NFR-6.2.3).
5. **Directory convention**:
   ```
   src/prompts/
     system/           # Base system prompts
       _baseline.yaml  # Fallback prompt (always present)
       v1.0.0.yaml     # Versioned system prompt
     skills/            # Composable skill fragments (see ADR-002)
       disclaimer.yaml
       anti-hype.yaml
       earnings-analysis.yaml
     experiments/       # Prompt variants for A/B testing
       exp-001-concise.yaml
   ```

## 6. Rationale

| Concern | Hardcoded Prompt | Externalized Assets |
|---------|-----------------|---------------------|
| Change velocity | Code commit + deploy per edit | File edit + reload |
| Version traceability | None (git blame only) | Embedded version in metadata and traces |
| Rollback | Revert commit + redeploy | Switch config to previous version |
| Experimentation | Conditional code branches | Variant files + experiment config |
| Audit / compliance | Implicit in code history | Explicit version tag per invocation |

## 7. Consequences

**Positive:**
- Prompt changes decouple from code deployment (aligns with NFR-6.2.3).
- Every agent invocation is traceable to a specific prompt version (FR-1.4.6).
- Rollback is a configuration change, not a code revert (FR-1.4.8).
- Enables prompt experimentation without code branches (FR-1.4.9).

**Trade-offs:**
- Requires a file-based loader with validation and caching.
- Prompt directory must be included in container images or mounted as a volume.
- Schema validation needed to prevent malformed assets from reaching production.

## 8. Related Documents

- Supersedes: None
- ADR-001 defines the prompt-compilation and layered runtime boundary that this ADR operationalizes.
- ADR-002 defines the skills-pattern composition model that relies on these externalized assets.
- `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` provides the research basis for externalized and versioned prompt assets.

## 9. Implementation Checklist

- [ ] Define YAML prompt asset schema with JSON Schema validation
- [ ] Implement PromptAssetLoader with caching, validation, and fallback logic
- [ ] Create `src/prompts/system/_baseline.yaml` with current system prompt content
- [ ] Add prompt version injection into agent response metadata
- [ ] Add prompt version to trace span attributes (NFR-5.2.5)
- [ ] Update Dockerfile to include `src/prompts/` in container image
- [ ] Add prompt asset integration tests (load, fallback, version extraction)

## 10. Traceability

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

