# ADR-Frontend-006: Generated UI Renders Only Allow-Listed Registry Components (Future)

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-006 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed — Future |
| **Date** | 2026-11-10 |
| **Last Updated** | 2026-11-10 |
| **Decision Owners** | Engineering · Architecture · Frontend maintainers |

## Context

ADR-Frontend-002 defers the generated-UI artifact protocol to **Future**. **SR-1.3.3** (Future) requires that where the AI generates UI, the Agent only proposes it, the Frontend renders it only in Z4 or as a draft in Z3, and generated UI never writes Core objects. Agent output is untrusted ([OWASP LLM05](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)). Reserving the seam now keeps later work from rendering arbitrary model output as UI.

## Decision

- Generated UI may render **only components from an allow-listed registry** owned by the Frontend design system.
- Each proposal is **validated against the registry schema** before rendering; anything invalid renders as plain sanitized text.
- Registry components are presentation-only; any action they offer goes through normal Backend commands and the user's confirmation, never a direct Core write.
- Rendered content carries `ai.*` provenance styling.
- Protocol, registry contents and schema format are decided when the Milestone is scheduled.

## Considered Options

| Option | Outcome |
|--------|---------|
| Allow-listed registry + schema validation (chosen) | Safe, consistent with the design system |
| Render model-produced markup or code | Rejected: untrusted output, XSS and agency risk |
| No generated UI ever | Not chosen: keeps the Future option open |

## Consequences

- Positive: generated UI stays inside design and trust rules.
- Negative: every new generated card needs a registry entry.

## Requirement Alignment

| Requirement | Relevance |
|-------------|-----------|
| **SR-1.3.3** Generated UI stays in its place and never writes Core *(Future)* | Direct realization boundary |

## Related Documents

- [Frontend Domain Architecture](../ARCHITECTURE.md) §4.3, §6.5
- [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) (GenUI carve-out)

## References

- [OWASP GenAI — LLM05 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-11-10 | Software Architect Assistant | Proposed; horizon M-000 to M-009 agreed with the Product Owner |
