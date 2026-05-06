# Architecture Decision Record

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-002 |
| **Domain** | Agent |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-04-13 |
| **Last Updated** | 2026-05-06 |
| **Context** | DP-StockAI-Assistant |
| **Decision Owners** | Engineering · Architecture · Agent maintainers |

## ADR-002 — Adopt Skills Pattern for Agent Prompt Composition

## 1. Decision Summary

Adopt a skills pattern for agent prompt composition so route-specific behavior, cross-cutting guardrails, and reusable domain instructions can be authored, tested, versioned, and activated independently rather than being maintained as one monolithic system prompt.

The composition model is built from:

- Base system instructions
- Always-active skills
- Route-matched skills
- Conversation and memory context
- Retrieved evidence
- Output schema constraints

## 2. Stakeholders Affected

- AI engineers and agent maintainers
- Architecture owners
- Product and domain reviewers
- QA and test maintainers

## 3. Architecture Concerns Addressed

- Change isolation for prompt behavior updates
- Testability of route-specific and cross-cutting prompt logic
- Reuse of shared behavioral instructions across intents
- Maintainability of prompt composition as the agent surface expands
- Governance of composable prompt behavior without collapsing concerns into one file

## 4. Problem Statement

ADR-001 defines a deterministic prompt compiler that assembles system rules, LTM, STM, RAG evidence, task instructions, and output schema into a single prompt payload. As the agent scope grows (new intents, new financial domains, regulatory constraints), monolithic prompt definitions become increasingly fragile:

- **Change collision risk**: Editing one domain’s instructions can inadvertently affect unrelated behaviors.
- **Testing burden**: The entire prompt must be regression-tested on every edit.
- **Reuse friction**: Cross-cutting concerns (e.g., disclaimers, uncertainty disclosure) are copy-pasted across intents.

## 5. Decision

Adopt a **Skills pattern** that decomposes the agent’s behavioral repertoire into independently authorable, testable, and composable prompt fragments called *skills*.

Each skill:
- Is a self-contained YAML/Markdown file with metadata (name, version, description, tags).
- Targets a single domain concern (e.g., `earnings-analysis`, `risk-framing`, `disclaimer-injection`, `anti-hype-guardrail`).
- Declares its own activation criteria (e.g., route match, keyword trigger, always-active).
- Is loaded and composed by the PromptAssembler at invocation time according to the active route and configuration.

The composition flow implied by this decision is:

```
[Base System Instructions]
      +
[Always-Active Skills]     (e.g., disclaimer, anti-hype)
      +
[Route-Matched Skills]     (e.g., earnings-analysis for EARNINGS_SUMMARY route)
      +
[LTM + STM Context]
      +
[RAG Evidence]
      +
[Output Schema]
      ↓
   Prompt Compiler → LLM
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
- Enables prompt A/B experimentation at the skill level (see FR-1.4.9).

**Trade-offs:**
- Introduces a skill registry/loader component (PromptAssetLoader) with file-system I/O.
- Skill composition order and conflict resolution rules must be defined (priority, override semantics).
- Debugging assembled prompts requires tooling to dump the final composed payload.

## 8. Related Documents

- Supersedes: None
- ADR-001 defines the prompt-compiler and layered composition boundary that this ADR extends.
- ADR-003 defines how prompt assets and skills are externalized and versioned as file-based configuration.
- `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` provides the research basis for the skills-pattern decision.

## 9. Implementation Checklist

- [ ] Define skill YAML schema (name, version, description, activation_criteria, content)
- [ ] Implement PromptAssetLoader to discover and load skill files from `src/prompts/skills/`
- [ ] Implement PromptAssembler that composes skills based on active route and configuration
- [ ] Migrate existing hardcoded system prompt into base + skill files
- [ ] Add skill integration tests (composition order, conflict resolution, fallback)
- [ ] Document skill authoring guide for contributors

## 10. Traceability

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

