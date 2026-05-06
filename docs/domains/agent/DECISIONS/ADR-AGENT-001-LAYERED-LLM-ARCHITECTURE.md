# Architecture Decision Record

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-001 |
| **Domain** | Agent |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Accepted |
| **Date** | 2026-01-22 |
| **Last Updated** | 2026-05-06 |
| **Context** | DP-StockAI-Assistant |
| **Decision Owners** | Engineering · Architecture · Agent maintainers |

## ADR-001 — Adopt a Layered LLM Architecture for Investment Analysis

## 1. Decision Summary

Adopt a layered LLM architecture for the agent domain so personalization, conversation state, evidence retrieval, prompt policy, deterministic computation, and behavior shaping remain separate concerns.

The architecture is composed of:

- Long-Term Memory (LTM)
- Short-Term Memory (STM)
- Intent-based routing
- Retrieval-Augmented Generation (RAG)
- Deterministic prompt compilation
- Selective fine-tuning

## 2. Stakeholders Affected

- Product
- Business
- End Users
- AI Engineers / Agent Maintainers
- Backend Engineers
- DevOps / SRE
- Security & Compliance
- Architecture Owners

## 3. Architecture Concerns Addressed

- Fact grounding and evidence separation
- Memory-scope boundaries between personalization and financial truth
- Separation of concerns across routing, retrieval, prompting, and deterministic computation
- Extensibility for new intents, providers, and retrieval layers
- Auditability and explainability of investment reasoning
- Safety controls for non-manipulative, evidence-first behavior

## 4. Problem Statement

A naive LLM-based investment assistant tends to mix user context, market facts, reasoning style, and computation into one prompt-centric path. That creates hallucinated facts, unstable analytical structure, poor personalization boundaries, and higher maintenance cost as the domain grows.

The agent domain therefore needs an architecture that preserves factual grounding, supports personalization without contaminating truth, and scales across multiple investment intents with explicit control boundaries.

## 5. Constraints and Non-Goals

Constraints:

- MongoDB is the primary data store.
- The LLM must remain effectively stateless between calls unless state is reintroduced through explicit memory wiring.
- Market data must be externalized through tools and approved evidence paths.

Non-goals:

- Stock price prediction
- Automated trade execution
- Storing financial facts in memory

## 6. Decision

The system SHALL enforce the following hard rules:

1. Memory never stores facts.
2. RAG never stores opinions.
3. Fine-tuning never stores knowledge.
4. Prompting controls behavior, not data.
5. Tools compute numbers, the LLM reasons about them.
6. Investment data sources are external.
7. Market-manipulation safeguards are enforced.

The layered boundary implied by those rules is:

- LTM stores stable personalization and symbol-tracking context only.
- STM stores conversation-local state only.
- Intent routing selects the appropriate behavior path.
- RAG provides sourced evidence for reasoning.
- Prompting and guardrails control behavior and disclosure.
- Tools fetch data and compute auditable metrics.
- Fine-tuning shapes structure and tone only.

Detailed structure and realization are intentionally delegated to companion documents so this ADR remains the decision authority rather than a mixed design specification.

## 7. Consequences

Positive:

- Stronger hallucination control
- Higher analytical consistency
- Clearer separation of concerns across memory, evidence, prompting, and computation
- Better extensibility for new routes, providers, and retrieval paths

Trade-offs:

- Higher upfront design complexity
- More moving parts across architecture, prompt assets, and runtime integration
- Greater need for cross-document discipline to avoid authority drift

## 8. Related Documents

- `ARCHITECTURE_DESIGN.md` is the canonical home for architecture-level layer boundaries, state/evidence allocation, and viewpoint-governed structure.
- `TECHNICAL_DESIGN.md` is the canonical home for runtime realization, prompt assembly order, fine-tuning realization, and example flows.
- `AGENT_MEMORY_TECHNICAL_DESIGN.md` is the canonical home for STM-specific data model, archive lifecycle, and migration/tooling detail.
- ADR-002 extends the prompt-composition decision with composable skills.
- ADR-003 extends the prompt-compilation decision with externalized versioned prompt assets.

## 9. Affected Views / Impacted Architectural Elements

### 9.1 Views Impacted by This Decision

| View | Impact Scope | Updated / Governed Content |
|------|--------------|----------------------------|
| Logical View | Primary | Governs the layer decomposition between memory, routing, retrieval, prompting, tools, and fine-tuning responsibilities |
| Process View | Primary | Governs how routing, evidence use, tool execution, and behavior controls are kept as distinct runtime concerns |
| Information and State View | Primary | Governs the separation between personalization state, conversation state, sourced evidence, and deterministic financial data |
| Prompt and Behavior View | Secondary | Constrains prompts and guardrails to behavior control rather than factual storage |

### 9.2 Architectural Elements Newly Defined or Reframed

- **Long-Term Memory (LTM):** Stable personalization and symbol-tracking context that remains separate from financial truth.
- **Short-Term Memory (STM):** Conversation-scoped state that remains local to the active conversation boundary.
- **Intent Routing:** Classification layer that selects behavior paths without becoming a persistence or evidence boundary.
- **Retrieval-Augmented Generation (RAG):** Evidence layer for sourced retrieval rather than memory-backed factual storage.
- **Prompting and Guardrails:** Behavioral policy layer that governs disclosure, tone, and safety rather than domain data.
- **Tools and Deterministic Computation:** Auditable computation layer that fetches data and calculates metrics outside the LLM.
- **Fine-Tuning:** Behavior-shaping layer that affects structure and tone without functioning as a knowledge store.

### 9.3 Applicability Note

This ADR is **Accepted** and therefore governs the architecture-description package wherever layer boundaries, state allocation, evidence handling, or behavior-control responsibilities are described. Some layers defined here remain architectural boundaries ahead of full runtime realization; companion documents must preserve that distinction rather than implying completed implementation.

### 9.4 Consistency Checkpoints

- [ ] Logical, Process, Information and State, and Prompt and Behavior views preserve the same layer boundaries defined by this ADR.
- [ ] Memory, prompts, and tools are not described elsewhere as alternate stores of financial truth.
- [ ] Future-state layers such as LTM, RAG, or fine-tuning remain marked as architectural scope where implementation is incomplete.
- [ ] If a companion document disagrees with this ADR on a boundary decision, this accepted ADR wins and the companion document must be reconciled.

## 10. Traceability

Supports:

Functional requirements:

- `FR-1.5.1` Evidence-First Responses
- `FR-1.5.3` Anti-Hype and Anti-Manipulation
- `FR-1.5.4` Fact-Assumption-Inference Separation
- `FR-1.5.5` Source Attribution
- `FR-3.1.7` No Financial Data Persistence
- `FR-3.1.8` Conversational Content Only
- `FR-3.2.3` Conversation-to-Thread Binding
- `FR-3.2.7` Boundary Isolation
- `FR-3.4.4` Context Propagation to Conversations
- `FR-4.1.1` Automatic Query Categorization
- `FR-4.1.2` Investment Intent Categories
- `FR-4.2.2` Context-Aware Instructions

Non-functional requirements:

- `NFR-2.2.1` Secondary-model fallback on primary-model failure
- `NFR-2.2.4` Operation when checkpointer is unavailable
- `NFR-3.1.1` Stateless agent service with externalized durable state
- `NFR-6.2.2` New routes addable without modifying router core
- `NFR-6.2.4` Model providers pluggable via factory pattern

> Memory personalizes. RAG informs. Prompting governs. Fine-tuning disciplines.

