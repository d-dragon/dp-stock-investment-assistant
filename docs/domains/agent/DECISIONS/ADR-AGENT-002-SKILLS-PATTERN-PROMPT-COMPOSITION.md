# Architecture Decision Record

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-002 |
| **Domain** | Agent |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-04-13 |
| **Last Updated** | 2026-04-14 |
| **Decision Owners** | Engineering · Architecture · Agent maintainers |

## ADR-002 — Adopt Skills Pattern for Agent Prompt Composition

### Table of Contents

1. [Context](#context)
2. [Decision](#decision)
3. [Prompt Assembly with Skills](#prompt-assembly-with-skills)
4. [Rationale](#rationale)
5. [Consequences](#consequences)
6. [Implementation Checklist](#implementation-checklist)

**Supersedes:** None  
**Related:** ADR-001 §8 (Prompt Compiler), ADR-003 (Externalized Prompts)  
**Research:** [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §5](../PROMPT_SYSTEM_RESEARCH_PROPOSAL.md)  

---

### Context

ADR-001 defines a deterministic prompt compiler that assembles system rules, LTM, STM, RAG evidence, task instructions, and output schema into a single prompt payload. As the agent scope grows (new intents, new financial domains, regulatory constraints), monolithic prompt definitions become increasingly fragile:

- **Change collision risk**: Editing one domain’s instructions can inadvertently affect unrelated behaviors.
- **Testing burden**: The entire prompt must be regression-tested on every edit.
- **Reuse friction**: Cross-cutting concerns (e.g., disclaimers, uncertainty disclosure) are copy-pasted across intents.

### Decision

Adopt a **Skills pattern** that decomposes the agent’s behavioral repertoire into independently authorable, testable, and composable prompt fragments called *skills*.

Each skill:
- Is a self-contained YAML/Markdown file with metadata (name, version, description, tags).
- Targets a single domain concern (e.g., `earnings-analysis`, `risk-framing`, `disclaimer-injection`, `anti-hype-guardrail`).
- Declares its own activation criteria (e.g., route match, keyword trigger, always-active).
- Is loaded and composed by the PromptAssembler at invocation time according to the active route and configuration.

### Prompt Assembly with Skills

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

### Rationale

| Concern | Monolithic Prompt | Skills Pattern |
|---------|------------------|----------------|
| Change isolation | Any edit risks regression | Changes scoped to a single skill file |
| Testability | Must test full prompt | Each skill independently testable |
| Reuse | Copy-paste across intents | Shared skills with activation rules |
| Versioning | One version for entire prompt | Per-skill versioning; experiment assignment per variant |
| Onboarding | New contributor must understand full prompt | Contributors author isolated skills |

### Consequences

**Positive:**
- Skills can be authored, reviewed, and versioned independently.
- Route-specific behaviors are encapsulated, reducing cross-domain regressions.
- Cross-cutting concerns (disclaimers, guardrails) are defined once and applied consistently.
- Enables prompt A/B experimentation at the skill level (see FR-1.4.9).

**Trade-offs:**
- Introduces a skill registry/loader component (PromptAssetLoader) with file-system I/O.
- Skill composition order and conflict resolution rules must be defined (priority, override semantics).
- Debugging assembled prompts requires tooling to dump the final composed payload.

### Implementation Checklist

- [ ] Define skill YAML schema (name, version, description, activation_criteria, content)
- [ ] Implement PromptAssetLoader to discover and load skill files from `src/prompts/skills/`
- [ ] Implement PromptAssembler that composes skills based on active route and configuration
- [ ] Migrate existing hardcoded system prompt into base + skill files
- [ ] Add skill integration tests (composition order, conflict resolution, fallback)
- [ ] Document skill authoring guide for contributors
---

