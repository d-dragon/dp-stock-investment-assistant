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

- Agent maintainers
- Backend and API maintainers
- Architecture owners
- Product and domain reviewers
- Security and compliance reviewers
- Operations and support

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

## 9. Traceability

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

