# Architecture Decision Record (ADR)
## Investment Assistant – Memory, RAG, Prompting & Fine-Tuning

**Status:** Accepted  
**Date:** 2026-01-22  
**Last Reviewed:** 2026-03-31  
**Context:** DP-StockAI-Assistant

---

## ADR-001 — Adopt a Layered LLM Architecture for Investment Analysis

### 1. Decision Summary
We adopt a **layered architecture** combining:
- Long-Term Memory (LTM)
- Short-Term Memory (STM)
- Intent-based Routing
- Retrieval-Augmented Generation (RAG)
- Deterministic Prompt Compilation
- Selective Fine-Tuning

This design explicitly separates **personalization**, **facts**, **reasoning style**, and **computation**, producing a scalable and auditable investment assistant.

---

## 2. Problem Statement
A naïve LLM-based investment assistant suffers from:
- Hallucinated financial facts
- Inconsistent analytical structure
- Poor personalization
- Tight coupling between memory and truth
- High maintenance cost as scope expands

We require a system that:
- Produces repeatable, structured investment analysis
- Grounds all facts in verifiable sources
- Personalizes output without contaminating reasoning
- Scales across multiple investment intents

---

## 3. Constraints & Non-Goals

### Constraints
- MongoDB is the primary data store
- LLM must remain stateless between calls
- Market data must be externalized via tools

### Non-Goals
- Stock price prediction
- Automated trade execution
- Storing financial facts in memory

---
## 4. Architectural Principles (Hard Rules)

1. **Memory never stores facts**  
   - LTM/STM retain user preferences, reusable session context, and conversation-scoped routing hints only.  
   - All financial facts originate from external sources or verified data stores (see ADR §6 LTM exclusions; §3 Constraints).  
2. **RAG never stores opinions**  
   - RAG indices contain sourced documents (filings, news, macro data) and retrieved snippets only.  
   - Interpretations remain in the LLM output and are tied to cited evidence (see ADR §9).  
3. **Fine-tuning never stores knowledge**  
   - Fine-tuning enforces structure and tone, not factual content.  
   - Training data is human-verified and excludes invented numbers or forecasts (see ADR §10).  
4. **Prompting controls behavior, not data**  
   - Prompts encode rules, safety constraints, and output schema.  
   - Data used for answers is injected at runtime from LTM/STM/RAG/tools (see ADR §8).  
5. **Tools compute numbers, LLM reasons about them**  
   - Deterministic tools fetch and calculate metrics; the LLM explains implications.  
   - This separation keeps computations auditable and prevents fabricated figures (see ADR §3, §4).    
6. **Investment data sources are external**  
   - Stock-related data is fetched from pre-listed external websites, approved data sources, and the in-system database.  
   - The agent may request the LLM or tools to collect, normalize, and organize data into a structured format for analysis.  
7. **Market manipulation safeguards are enforced**  
   - No intent to influence markets, prices, or trading behavior.  
   - Outputs are informational and grounded in verifiable sources only.  

These principles prevent hallucination, leakage, and compounding error.

---

## 5. High-Level Architecture

```
┌────────────────────────────┐
│ System Prompt (Static)     │
│ Investment rules & policy │
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│ Long-Term Memory (LTM)     │
│ User risk & preferences   │
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│ Short-Term Memory (STM)    │
│ Conversation STM +        │
│ session context           │
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│ Intent Router              │
│ Route + model + tools     │
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│ RAG Layer                  │
│ Filings, news, macro      │
└──────────────┬─────────────┘
               ↓
┌────────────────────────────┐
│ Fine-Tuned LLM             │
│ Structured reasoning      │
└────────────────────────────┘
```

---

## 6. Memory Design

### 6.1 Long-Term Memory (LTM)

**Decision:** Long-Term Memory (LTM) persists **stable, slow-changing preferences and context** used for personalization and intent routing. LTM is **not** a source of financial truth and must never contain market facts or analytical conclusions.

**Rationale:** LTM stores durable user identity signals and symbol-level context so the assistant can tailor explanations and prioritization **without contaminating factual analysis**. This keeps “who the user is” separate from “what is true about the market,” which remains grounded in tools and RAG.

**Stored User Characteristics (preference + personalization only):**
- Risk profile (conservative, moderate, aggressive)
- Investment style (value, growth, dividend, momentum)
- Investment goals (income, capital appreciation, wealth preservation)
- Default time horizon (short-term: <6 months, medium-term: 6–18 months, long-term: >18 months)
- Experience level (beginner, intermediate, advanced, professional)
- Sector preferences and exclusions
- Output verbosity and technical depth preference
- Language and cultural context (e.g., Vietnamese market nuances)

**Stored Symbol Characteristics (context + tracking intelligence only):**
- Symbol metadata (ticker, full name, sector, exchange)
- Historical timeline of structural events (splits, mergers, restructuring, leadership changes, major announcements)
- User-specific tracking context (watch date, reasons for tracking, custom tags/categories)
- Cross-reference links (peer group, supply chain relationships, sector dependencies)
- Known catalyst dates (earnings calendars, dividend dates, regulatory milestones)

**Explicitly Excluded (must live in RAG/Tools layer):**
- Real-time or historical prices
- Financial ratios and calculated metrics
- Valuation assessments or price targets
- Forecasts or forward-looking statements
- News content or filing text
- Analytical conclusions or recommendations

**Persistence & Governance:**
- User characteristics update only via explicit user actions (or confirmed preference changes)
- Symbol characteristics refresh schedulely, upon structural events or manual evaluation/valuation works.
- Maintain an immutable audit trail for preference changes (compliance + explainability)
- LTM reads are summarized into ≤2 lines during prompt compilation (avoid prompt bloat)

---

### 6.2 Short-Term Memory (STM)
**Decision:** Store STM as conversation-scoped threads inside a `workspace -> session -> conversation` hierarchy. Sessions remain reusable business-context containers, while conversations own the LangGraph thread state and are archived instead of hard-deleted.

**Rationale:** Separating reusable session context from conversation-owned STM prevents sibling threads from leaking into each other while preserving the user's analytical workflow. By archiving conversations rather than purging them, we enable:
- Continuity tracking across related conversations inside a session
- Pattern analysis for improved personalization without conflating thread state
- Audit trail for investment reasoning
- Learning from past assumptions without contaminating active context

**Characteristics:**
- Conversation-scoped: Each conversation owns its own `conversation_id -> thread_id` mapping and metadata.
- Session-bound reusable context: Sessions group related conversations and can hold shared analytical context without sharing checkpoints.
- Support archive option: Conversations are archived, while sessions can be closed or archived through lifecycle management.
- Workspace-bound: Conversations isolated per workspace to prevent context leakage
- Selective recall: Only recent session summaries loaded into active context
- Query-specific retrieval: Past conversations retrievable via explicit user request or RAG when semantically relevant
- Stores conversational state only: User assumptions, focused symbols, pinned intents, summarized turn snippets
- Never stores: Market data, computed ratios, or analytical conclusions (these remain in RAG/tools layer)

**Implementation Note (2026-03-31):** The current runtime implements conversation-scoped checkpoints, management APIs for workspace/session/conversation lifecycle, and operator tooling for reconciliation and legacy-thread migration. Session-context retrieval helpers exist in the service layer; prompt-level injection of that context into the agent prompt path remains follow-up work.


---

## 7. Intent Routing

### 7.1 Supported Intents

| Intent | Description |
|------|------------|
| PRICE_CHECK | Latest market data |
| NEWS_ANALYSIS | Event & headline impact |
| FINANCIAL_ANALYSIS | Fundamental review |
| EARNINGS_SUMMARY | Quarterly results |
| TECHNICAL_ANALYSIS | Indicator interpretation |
| PORTFOLIO_QUERY | Holdings & exposure |
| EXPLAIN_CONCEPT | Educational |

---

### 7.2 Routing Flow

```
User Query
   ↓
Rule-Based Match
   ↓ (if uncertain)
Intent Classifier
   ↓
Route Configuration
(model + RAG + tools)
```

Each route defines:
- Model selection
- RAG index
- Freshness bias
- Tool access
- Output schema

---

## 8. Prompt Compiler

### Decision
Use a deterministic prompt compiler rather than ad-hoc prompt concatenation.

### Prompt Assembly Order

1. System rules
2. LTM summary (≤2 lines)
3. STM assumptions
4. RAG evidence snippets
5. Task instruction
6. Output schema

### Flow Diagram

```
[LTM]   [STM]   [RAG]
   \      |      /
    \     |     /
     → Prompt Compiler → LLM
```

---

## 9. Retrieval-Augmented Generation (RAG)

### Decision
Maintain **separate vector indices per intent**.

### Rationale
- Financials ≠ News ≠ Macro ≠ Technicals
- Each has different freshness and semantic structure

### Example

| Intent | Index | Freshness |
|------|------|-----------|
| Earnings | Filings | 12 months |
| News | Press | Days |
| Macro | Commodities | Weeks |

---

## 10. Fine-Tuning Strategy

### Decision
Apply fine-tuning **only to enforce reasoning structure and tone**.

### Included
- Earnings summaries
- Risk framing
- Scenario tables

### Excluded
- Valuation logic
- Price prediction
- Macro outlook

### Dataset Characteristics
- Human-verified outputs
- No invented numbers
- Consistent structure
- Confidence scores per claim

---

## 11. End-to-End Flow Example (Financial Analysis)

```
User: "Đánh giá HSG trung hạn"
   ↓
Load LTM (risk: moderate, horizon: 6–18m)
   ↓
Load session context + conversation STM (steel price bottoming assumption)
   ↓
Route → FINANCIAL_ANALYSIS
   ↓
RAG → financials + HRC price
   ↓
Prompt Compiler
   ↓
Fine-Tuned LLM Output
```

---

## 12. Consequences

### Positive
- Strong hallucination control
- High analytical consistency
- Clean separation of concerns
- Scales to new intents easily

### Trade-offs
- Higher upfront design cost
- More infrastructure components

---

## 13. Implementation Checklist

- [ ] MongoDB memory collections + TTL
- [ ] Intent router (rules + classifier)
- [ ] Prompt compiler service
- [ ] RAG indices per intent
- [ ] Fine-tune earnings model
- [ ] Evaluation & monitoring

---

## 14. Further Reading (Official Documentation)

- OpenAI: Function Calling & Tool Use
- OpenAI: Fine-Tuning Best Practices
- LangChain: Agents & RAG Architecture
- MongoDB Atlas: Vector Search
- Architectural Decision Records (ADR) by Michael Nygard

---

## 15. Strategic Conclusion

> **Memory personalizes. RAG informs. Prompting governs. Fine-tuning disciplines.**

This architecture defines the boundary between an experimental chatbot and a production-grade investment intelligence system.

