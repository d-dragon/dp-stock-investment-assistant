# Architecture Decision Record

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-002 |
| **Domain** | Agent |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-04-13 |
| **Last Updated** | 2026-05-15 |
| **Context** | DP-StockAI-Assistant |
| **Decision Owners** | Engineering · Architecture · Agent maintainers |

## ADR-002 — Adopt Skills Pattern for Agent Prompt Composition

## 1. Decision Summary

Adopt a skills pattern as the near-term prompt-composition model inside the governed prompt compiler path so route-specific behavior, cross-cutting guardrails, and reusable domain instructions can be authored, tested, versioned, and activated independently rather than being maintained as one monolithic system prompt.

The composition model is built from:

- Shared policy and base system instructions
- Always-active skills
- Route-matched skills
- Bounded runtime context
- Retrieved evidence
- Output schema constraints

## 2. Stakeholders Affected

- Product
- End Users
- AI Engineers / Agent Maintainers
- Backend Engineers
- QA / Test Maintainers
- Security & Compliance
- Architecture Owners

## 3. Architecture Concerns Addressed

- Change isolation for prompt behavior updates
- Testability of route-specific and cross-cutting prompt logic
- Reuse of shared behavioral instructions across intents
- Maintainability of prompt composition as the agent surface expands
- Governance of composable prompt behavior without collapsing concerns into one file

## 4. Problem Statement

ADR-001 defines a deterministic prompt compiler that assembles system rules, LTM, STM, RAG evidence, task instructions, and output schema into a single prompt payload. As the prompt package evolves from the current hardcoded ReAct baseline toward the planned `PromptAssetLoader -> PromptAssembler -> ResponseGuardrailMiddleware` path, monolithic prompt definitions become increasingly fragile:

- **Change collision risk**: Editing one domain’s instructions can inadvertently affect unrelated behaviors.
- **Testing burden**: The entire prompt must be regression-tested on every edit.
- **Reuse friction**: Cross-cutting concerns (e.g., disclaimers, uncertainty disclosure) are copy-pasted across intents.

## 5. Decision

Adopt a **Skills pattern** that decomposes the agent’s behavioral repertoire into independently authorable, testable, and composable prompt fragments called *skills* within the planned prompt compiler path.

Each skill:
- Is a self-contained governed prompt asset with front-matter metadata (name, version, description, tags, activation criteria).
- Targets a single domain concern (e.g., `earnings-analysis`, `risk-framing`, `disclaimer-injection`, `anti-hype-guardrail`).
- Declares its own activation criteria (e.g., route match, keyword trigger, always-active).
- Is resolved by `PromptAssetLoader` and ordered by `PromptAssembler` according to the active route and configuration.

The composition flow implied by this decision is:

```
[Governed Prompt Assets]
      ↓ PromptAssetLoader
[Shared Policy + Always-Active Skills]
      +
[Route-Matched Skills]
      ↓ PromptAssembler
[Bounded Runtime Context + Evidence + Output Contract]
      ↓ Model Invocation
   ResponseGuardrailMiddleware → Response Surface
```

## 6. Rationale

| Concern | Monolithic Prompt | Skills Pattern |
|---------|------------------|----------------|
| Change isolation | Any edit risks regression | Changes scoped to a single skill file |
| Testability | Must test full prompt | Each skill independently testable |
| Reuse | Copy-paste across intents | Shared skills with activation rules |
| Versioning | One version for entire prompt | Per-skill versioning; experiment assignment per variant |
| Onboarding | New contributor must understand full prompt | Contributors author isolated skills |

## 7. Consequences

**Positive:**
- Skills can be authored, reviewed, and versioned independently.
- Route-specific behaviors are encapsulated, reducing cross-domain regressions.
- Cross-cutting concerns (disclaimers, guardrails) are defined once and applied consistently.
- Keeps the near-term target on one agent plus route-aware composition instead of prematurely requiring a multi-agent runtime.
- Enables prompt A/B experimentation at the skill level (see FR-1.4.9).

**Trade-offs:**
- Depends on a governed asset-loading boundary (`PromptAssetLoader`) and externalized prompt assets defined by ADR-003.
- Skill composition order and conflict resolution rules must be defined (priority, override semantics).
- Debugging assembled prompts requires tooling to dump the final composed payload.

## 8. Related Documents

- Supersedes: None
- ADR-001 defines the prompt-compiler and layered composition boundary that this ADR extends.
- ADR-003 defines how prompt assets and skills are externalized and versioned as file-based configuration.
- `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` provides the research basis for the skills-pattern decision.

## 9. Affected Views / Impacted Architectural Elements

### 9.1 Views Impacted by This Decision

| View | Impact Scope | Updated / Governed Content |
|------|--------------|----------------------------|
| Prompt and Behavior View | Primary | Governs decomposition of monolithic prompt behavior into composable skills with explicit activation and reuse boundaries |
| Process View | Secondary | Governs where skill selection and prompt composition sit in the runtime flow before model invocation |
| Development View | Secondary | Governs the expectation that skills are independently authorable assets rather than hardcoded prompt fragments |

### 9.2 Architectural Elements Newly Defined or Reframed

- **Always-Active Skills:** Cross-cutting prompt fragments such as disclaimers or anti-hype guardrails that apply across routes.
- **Route-Matched Skills:** Route-specific prompt fragments activated according to classification and configuration.
- **Skill Activation Criteria:** Metadata-driven rules that determine when a skill is applied.
- **PromptAssembler:** Composition mechanism that orders and merges the active skill set with base instructions and context.
- **Compiler-Scoped Skills Model:** Near-term architectural rule that skills are one composition layer inside the broader prompt compiler path, not a separate runtime system.
- **Skills Composition Governance:** Architectural rule that prompt behavior is decomposed into independently governable fragments rather than one monolithic prompt asset.

### 9.3 Applicability Note

This ADR is **Proposed**. The architecture-description package may describe this pattern as the planned near-term composition layer inside the prompt compiler path, but companion documents must not imply that route-aware skills runtime behavior, loader behavior, or skill-governance tooling are already implemented unless realization documents explicitly say so.

### 9.4 Consistency Checkpoints

- [ ] Prompt and Behavior, Process, and Development views use the same skills terminology and view names defined in the architecture description.
- [ ] Skills are described as prompt-behavior components, not as data stores, business-state owners, or substitutes for tool execution.
- [ ] `PromptAssembler` remains distinct from the higher-level `Prompt Compiler` concept and from `PromptAssetLoader` in ADR-003.
- [ ] Skills are described as the near-term route-aware composition model before any later specialist prompt families or multi-agent runtime evolution.
- [ ] Proposed-status language remains visible anywhere this ADR is reflected in companion documents.

## 10. Implementation Checklist

- [ ] Define skill asset schema (name, version, activation_criteria, tags, content)
- [ ] Implement PromptAssetLoader to discover and load skill files from `src/prompts/skills/`
- [ ] Implement PromptAssembler that composes skills based on active route and configuration
- [ ] Migrate existing hardcoded system prompt into base + skill files
- [ ] Add skill integration tests (composition order, conflict resolution, fallback)
- [ ] Document skill authoring guide for contributors

## 11. Traceability

Supports:

Functional requirements:

- `FR-1.4.6` Prompt Version Identity
- `FR-1.4.7` Route-Specific Prompt Context
- `FR-1.4.9` Prompt Experiment Assignment
- `FR-1.5.1` Evidence-First Responses
- `FR-1.5.2` Uncertainty Disclosure
- `FR-1.5.3` Anti-Hype and Anti-Manipulation
- `FR-1.5.5` Source Attribution

Non-functional requirements:

- `NFR-5.2.5` Prompt version identifier in traces
- `NFR-5.2.6` Route classification in traces
- `NFR-5.2.7` Experiment identifier and variant assignment in traces

