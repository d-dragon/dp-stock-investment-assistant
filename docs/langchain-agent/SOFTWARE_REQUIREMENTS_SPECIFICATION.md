# Stock Investment Assistant Agent — Software Requirements Specification

> **Document Version**: 2.3  
> **Created**: January 22, 2026  
> **Last Updated**: April 13, 2026  
> **Status**: Active  
> **Scope**: LangChain-based AI Agent for Stock Investment Assistant  
## Related Documents

This specification builds upon and references several architectural and design documents:

| Document | Purpose | Reference |
|----------|---------|-----------|
| [AGENT_ARCHITECTURE_DECISION_RECORDS.md](../domains/agent/decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md) | Architectural decisions for LTM/STM, RAG, fine-tuning strategy, and memory separation | Design foundations for FR-3 (Memory System) |
| [ARCHITECTURE_DESIGN.md](../domains/agent/ARCHITECTURE_DESIGN.md) | Comprehensive agent architecture overview, component deep dive, data flow, and Phase 2 improvements | Implementation guidance for FR-1, FR-2, FR-4 |
| [LANGCHAIN_AGENT_HOWTO.md](./LANGCHAIN_AGENT_HOWTO.md) | Complete guide to ReAct pattern, semantic routing, tool system, and operations | Operational reference for agent deployment and usage |
| [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) | Future enhancement roadmap including multi-agent, advanced memory, and observability | Planning for P2 requirements beyond current release |
| [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) | Detailed technical design for conversation memory, checkpointing, and summarization | Implementation guidance supporting FR-3 (Memory System) |
| [AGENTIC_APP_WITH_STM_INTEGRATION_ROADMAP.md](../High-level%20Design/AGENTIC_APP_WITH_STM_INTEGRATION_ROADMAP.md) | Technical roadmap for workspace-session-conversation hierarchy and STM integration | Roadmap for FR-5.3–5.5, FR-7 (management, consistency, migration) |
| [SRS_SPEC_TRACEABILITY.md](./SRS_SPEC_TRACEABILITY.md) | Bidirectional trace between SRS items and spec-kit feature artifacts | Companion delivery trace for implementation coverage and sync status |
| [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](../domains/agent/PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) | Prompt system research, design patterns, and implementation roadmap | Research foundation for FR-1.4.6–1.4.9, FR-1.5, NFR-5.2.5–5.2.7 |



---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Functional Requirements](#2-functional-requirements)
   - [FR-1: Agent Core](#fr-1-agent-core)
   - [FR-2: Tool System](#fr-2-tool-system)
   - [FR-3: Conversation Memory](#fr-3-conversation-memory)
   - [FR-4: Semantic Routing](#fr-4-semantic-routing)
   - [FR-5: API Integration](#fr-5-api-integration)
   - [FR-6: Streaming](#fr-6-streaming)
   - [FR-7: Data Integrity and Operational Tooling](#fr-7-data-integrity-and-operational-tooling)
3. [Non-Functional Requirements](#3-non-functional-requirements)
   - [NFR-1: Performance](#nfr-1-performance)
   - [NFR-2: Reliability](#nfr-2-reliability)
   - [NFR-3: Scalability](#nfr-3-scalability)
   - [NFR-4: Security](#nfr-4-security)
   - [NFR-5: Observability](#nfr-5-observability)
   - [NFR-6: Maintainability](#nfr-6-maintainability)
4. [Constraints](#4-constraints)
5. [Acceptance Criteria](#5-acceptance-criteria)
6. [Traceability Matrix](#6-traceability-matrix)
7. [Interface Requirements](#7-interface-requirements)
8. [Error Semantics](#8-error-semantics)
9. [Data Handling & Privacy](#9-data-handling--privacy)
10. [Assumptions & Open Issues](#10-assumptions--open-issues)
11. [Revision History](#11-revision-history)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and non-functional requirements for the Stock Investment Assistant Agent. It serves as the authoritative source for agent behavior, capabilities, performance expectations, and quality attributes.

This specification follows **spec-driven development** principles, enabling AI-assisted development (vibe coding) where requirements are precise enough to guide implementation while remaining focused on **WHAT** the system does, not **HOW** it achieves it.

### 1.2 Scope

#### 1.2.1 In Scope

| Area | Description |
|------|-------------|
| **Agent Behavior** | Natural language query processing, response generation, and conversation management |
| **Tool Capabilities** | What tools can accomplish (stock prices, news, analysis, reports) |
| **Memory Behavior** | Conversation persistence, context recall, summarization |
| **Query Understanding** | How the agent categorizes and routes user intents |
| **API Contracts** | Request/response formats for REST and WebSocket interfaces |
| **Response Delivery** | Streaming behavior and incremental content delivery |
| **Quality Attributes** | Performance, reliability, security, and observability requirements |

#### 1.2.2 Out of Scope

| Area | Reason |
|------|--------|
| Implementation architecture | Belongs in [ARCHITECTURE_DESIGN.md](../domains/agent/ARCHITECTURE_DESIGN.md) |
| Database schemas and indexes | Belongs in [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) |
| Library/package dependencies | Belongs in technical design documentation |
| Infrastructure and deployment | Belongs in IaC documentation |
| Frontend implementation | Belongs in frontend documentation |
| Configuration schemas | Belongs in technical design documentation |

### 1.3 Definitions and Acronyms

| Term | Definition |
|------|------------|
| **Agent** | The AI-powered component that processes user queries and generates responses |
| **Workspace** | The top-level business container that owns sessions and enforces user and isolation boundaries |
| **Session** | A business workflow container within a workspace that groups related conversations under a shared analytical context |
| **Conversation** | A discrete agent interaction thread within a session that owns its own STM state and metadata |
| **Thread** | The stateful memory identifier bound 1:1 to a conversation for checkpoint tracking |
| **Tool** | A capability the agent can invoke to retrieve data or perform actions |
| **Streaming** | Incremental delivery of response content as it's generated |
| **Summarization** | Condensing a conversation thread's prior exchanges to manage context size while preserving recent continuity |
| **TTL** | Time To Live (duration before data expires) |
| **Management API** | REST endpoints for creating, listing, retrieving, updating, and archiving workspace, session, and conversation resources |
| **Cascade Archive** | When a parent resource is archived, its child resources are also transitioned to archived status |
| **Reconciliation** | The process of detecting and optionally repairing inconsistencies between related data stores (e.g., conversation metadata vs. checkpointer state) |
| **Migration** | The controlled transformation of historical data from the legacy identity model (session_id as thread_id) to the canonical hierarchy (conversation_id as thread_id) |
| **Orphan Record** | A child record whose required parent record is missing or invalid (e.g., a conversation without a valid parent session) |

### 1.4 Document Conventions

| Prefix | Category |
|--------|----------|
| FR-X.Y | Functional Requirement |
| NFR-X.Y | Non-Functional Requirement |
| CON-X | Constraint |
| AC-X.Y | Acceptance Criteria |

Priority levels:
- **P0**: Must have (blocking for release)
- **P1**: Should have (important for usability)
- **P2**: Nice to have (can defer)
- **P3**: Future (planned for later phases)

---

## 2. Functional Requirements

### FR-1: Agent Core

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have

#### FR-1.1 ReAct Agent Pattern

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-1.1.1 | **Reasoning Before Action** | Agent explains its reasoning before taking any action | User submits query | Response includes visible reasoning step before tool invocation | P0 |
| FR-1.1.2 | **Tool-Augmented Responses** | Agent uses tools to gather information when needed | Query requires external data | Agent invokes appropriate tool(s) and incorporates results in response | P0 |
| FR-1.1.3 | **Iterative Problem Solving** | Agent can invoke multiple tools in sequence to answer complex queries | Query requires multiple data points | Agent completes all necessary tool calls before final answer | P0 |
| FR-1.1.4 | **Self-Correction** | Agent can recognize and recover from failed tool calls | Tool returns error | Agent attempts alternative approach or explains limitation | P0 |
| FR-1.1.5 | **Answer Completeness** | Agent continues reasoning until a complete answer is formed | Query submitted | Response directly addresses user's question with supporting data | P0 |

#### FR-1.2 Query Processing

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-1.2.1 | **Natural Language Input** | Agent accepts free-form text queries in natural language | — | Any grammatically reasonable query is processed without format errors | P0 |
| FR-1.2.2 | **Structured Response** | Agent returns responses with consistent structure | Query processed | Response contains: content, model used, status, tools invoked, token count | P0 |
| FR-1.2.3 | **Synchronous Processing** | Agent can process queries and return complete response | Non-streaming request | Complete response returned within timeout (see NFR-1.1) | P0 |
| FR-1.2.4 | **Streaming Processing** | Agent can deliver response incrementally as it's generated | Streaming request | First token delivered within 2 seconds; continuous delivery until complete | P0 |
| FR-1.2.5 | **Structured Output Mode** | Agent can return responses in a predefined schema | Schema specified in request | Response validates against provided schema (100% compliance) | P1 |

#### FR-1.3 Model Selection

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-1.3.1 | **Primary Model Usage** | Agent uses the configured primary AI model by default | Configuration specifies primary model | Response metadata shows primary model name | P0 |
| FR-1.3.2 | **Automatic Failover** | Agent switches to backup model when primary is unavailable | Primary model returns error | Response generated using backup model; no user intervention required | P0 |
| FR-1.3.3 | **Failover Transparency** | Agent indicates when backup model was used | Failover occurred | Response status clearly indicates fallback was used | P0 |
| FR-1.3.4 | **Model Override** | User can request a specific model for a query | User specifies model preference | Requested model used if available; error if unavailable | P1 |
| FR-1.3.5 | **Multi-Provider Support** | Agent supports multiple AI model providers | Provider configured | Agent can use any configured provider interchangeably | P0 |

#### FR-1.4 System Prompt

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-1.4.1 | **Behavioral Instructions** | Agent behavior is guided by configurable instructions | Configuration provided | Agent responses align with defined persona and guidelines | P0 |
| FR-1.4.2 | **Tool Awareness** | Agent knows what tools are available and their purposes | Tools registered | Agent can describe available capabilities when asked | P1 |
| FR-1.4.3 | **Disclaimer Inclusion** | Agent includes investment disclaimers in relevant responses | Response contains financial advice | Disclaimer present in response (verified by keyword match) | P0 |
| FR-1.4.4 | **Memory Context Injection** | Agent receives prior conversation context as part of its instructions | Session has history | Agent demonstrates awareness of prior conversation | P1 |
| FR-1.4.5 | **External Prompt Management** | System prompt can be modified without code deployment | — | Prompt changes take effect within 60 seconds without restart | P2 |
| FR-1.4.6 | **Prompt Version Identity** | Every agent invocation SHALL carry an identifiable prompt version tag derived from the loaded prompt asset | Prompt assets deployed | Prompt version appears in agent response metadata and trace spans | P1 |
| FR-1.4.7 | **Route-Specific Prompt Context** | Agent SHALL receive route-specific prompt context based on query classification (e.g., analysis, news, general) | Semantic router classifies query | Agent response reflects domain-appropriate persona and instructions for the classified route | P2 |
| FR-1.4.8 | **Prompt Rollback Safety** | If a configured prompt version fails to load or parse, the system SHALL fall back to the most recent known-good baseline prompt | Prompt asset missing or malformed | Agent operates with baseline prompt; incident logged at WARN level with prompt version identifier | P1 |
| FR-1.4.9 | **Prompt Experiment Assignment** | System SHALL support assigning prompt variants to conversations via a configurable selection mode (e.g., pinned version, random allocation, weighted distribution) | Experiment configuration provided | Conversation receives the designated prompt variant; variant identifier recorded in trace metadata | P2 |

---

#### FR-1.5 Finance-Domain Behavioral Guardrails

> **Rationale**: A financial-advisory agent must enforce epistemic discipline — grounding responses in evidence, disclosing uncertainty, and separating facts from inferences — to maintain user trust and regulatory defensibility.
> **Research Reference**: [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §7 Behavioral Guardrails](../domains/agent/PROMPT_SYSTEM_RESEARCH_PROPOSAL.md)

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-1.5.1 | **Evidence-First Responses** | Agent SHALL ground financial assertions in data retrieved by tools (price, fundamentals, news) rather than parametric training knowledge alone | Tool data available for queried symbol | Response references specific data points (price, ratio, date) obtained from tool results | P0 |
| FR-1.5.2 | **Uncertainty Disclosure** | Agent SHALL explicitly disclose when it lacks sufficient data or confidence to answer a financial question | Insufficient or stale data for queried topic | Response includes an explicit uncertainty qualifier (e.g., "I don't have enough data to…", "This may be outdated…") | P0 |
| FR-1.5.3 | **Anti-Hype and Anti-Manipulation** | Agent SHALL NOT generate language that could constitute market hype, price manipulation, or guaranteed-return claims | Any financial query | Response avoids superlatives, guarantees, and urgency language; verified by keyword/phrase blocklist | P0 |
| FR-1.5.4 | **Fact-Assumption-Inference Separation** | Agent SHALL clearly label which parts of a response are factual data, which are assumptions, and which are inferences or opinions | Response mixes data and analysis | Response uses explicit markers or structure to distinguish data vs. assumption vs. inference | P1 |
| FR-1.5.5 | **Source Attribution** | Agent SHALL attribute financial data to the originating tool or data source | Tools returned data used in response | Response includes attribution (e.g., "According to Yahoo Finance…", "Based on the latest SEC filing…") | P1 |

---
### FR-2: Tool System

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have

#### FR-2.1 Tool Result Caching

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-2.1.1 | **Automatic Result Caching** | Tool results are cached to avoid redundant external calls | Tool executed with cacheable input | Identical subsequent call returns cached result (cache hit rate ≥40%) | P0 |
| FR-2.1.2 | **Configurable Cache Duration** | Each tool type has its own cache expiration time | Tool configured with TTL | Cached result expires after configured duration (±5 seconds) | P0 |
| FR-2.1.3 | **Deterministic Cache Keys** | Same input always maps to same cached result | — | Two calls with identical input return same cached value | P0 |
| FR-2.1.4 | **Cache Bypass Option** | Individual requests can skip cache when fresh data required | Bypass flag set | Tool fetches fresh data; response time matches uncached call | P1 |
| FR-2.1.5 | **Tool Execution Logging** | Every tool invocation is recorded for analytics | Tool executed | Log contains: tool name, input, duration, cache hit/miss, timestamp | P1 |
| FR-2.1.6 | **Cache Failure Tolerance** | Tools function normally when cache is unavailable | Cache service down | Tool executes successfully; result not cached; no error shown to user | P0 |

#### FR-2.2 Tool Registry

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-2.2.1 | **Central Tool Management** | All tools are managed through a single registry | — | Tool list retrievable from one location | P0 |
| FR-2.2.2 | **Tool Enablement Control** | Individual tools can be enabled or disabled | Tool registered | Disabled tools not available to agent; enabled tools available | P0 |
| FR-2.2.3 | **Runtime Toggle** | Tools can be enabled/disabled without restart | System running | Tool availability changes within 5 seconds of toggle | P1 |
| FR-2.2.4 | **Tool Discovery** | Agent can retrieve list of available tools by name | — | Tool lookup by name returns correct tool or null if not found | P0 |
| FR-2.2.5 | **Unique Tool Names** | Each tool has a unique identifier | Tool registration attempted | Duplicate name registration rejected with error message | P0 |
| FR-2.2.6 | **Tool Health Status** | System can report which tools are operational | — | Health check returns status for each registered tool | P1 |

#### FR-2.3 Stock Investment Tools

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-2.3.1 | **Stock Price Lookup** | User can request current price for any stock symbol | Valid stock symbol | Current price returned with timestamp (data ≤15 minutes old) | P0 |
| FR-2.3.2 | **Symbol Search** | User can search for stock symbols by company name | Search query provided | Matching symbols returned with company names (≥1 result for valid queries) | P0 |
| FR-2.3.3 | **Company Information** | User can retrieve company details for a symbol | Valid stock symbol | Company profile returned: name, sector, market cap, description | P0 |
| FR-2.3.4 | **Technical Chart Generation** | User can request technical analysis charts | Valid symbol and timeframe | Chart URL or image returned showing price with indicators | P1 |
| FR-2.3.5 | **Investment Report Generation** | User can generate formatted investment reports | Analysis data available | PDF/HTML report generated with executive summary and data | P2 |

---

### FR-3: Conversation Memory

> **Design Reference**: For implementation details, see [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md)  
> **Architecture Context**: [ADR-001 — Layered LLM Architecture](../domains/agent/decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md)

#### Priority Levels
| Level | Meaning | Release Criteria |
|-------|---------|------------------|
| **P0** | MUST have | Blocking for MVP release |
| **P1** | SHOULD have | Required for production readiness |
| **P2** | NICE to have | Deferred to next release |
| **P3** | FUTURE | Planned for later phases |

---

#### FR-3.1 Short-Term Memory (Conversation Thread Buffer)

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-3.1.1 | **Conversation History Retention** | The agent remembers all messages exchanged within a single conversation thread | User has an active conversation | Given 5 prior exchanges in the same conversation, the agent references any of them accurately when asked "What did I ask earlier?" | P0 |
| FR-3.1.2 | **Conversation State Persistence** | Conversation thread state survives system restarts without data loss | Conversation was created and has ≥1 message | After restart, resuming the same conversation returns identical message history (100% match) | P0 |
| FR-3.1.3 | **Conversation Identification** | Each stateful conversation is uniquely identifiable by a conversation identifier that resolves to a single memory thread | API request includes `conversation_id` | Requests with the same `conversation_id` return consistent conversation context and resolve to the same `thread_id` | P0 |
| FR-3.1.4 | **Conversation Context Binding** | Agent responses incorporate prior context from the same conversation thread | Conversation has ≥2 prior messages | Response demonstrates awareness of earlier exchanges from the same conversation and does not mix context from sibling conversations in the same session | P0 |
| FR-3.1.5 | **Conversation Recall on Reconnect** | User can resume a conversation after disconnection by reconnecting to the same conversation resource | Valid `conversation_id` provided | First response after reconnect includes acknowledgment of prior context from that conversation | P1 |
| FR-3.1.6 | **Stateless Fallback Mode** | Agent functions without conversation tracking when no `conversation_id` is provided | `conversation_id` is null or omitted | Agent responds normally; no stateful conversation thread is loaded or persisted | P0 |
| FR-3.1.7 | **No Financial Data Persistence** | Memory stores conversation text only, never computed financial metrics | — | Inspection of stored data shows zero price values, ratios, or calculated figures | P0 |
| FR-3.1.8 | **Conversational Content Only** | Memory contains user messages and agent responses, not raw tool outputs | Tools were invoked during session | Stored content includes "I found the price" but not the actual price data | P0 |

---

#### FR-3.2 Hierarchical Conversation Management

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-3.2.1 | **Session-Scoped Conversation Creation** | The system creates conversation records as children of an existing session, not as implicit aliases of the session itself | A valid workspace and session exist; user starts a new conversation | Conversation record exists with `conversation_id`, parent `session_id`, parent `workspace_id`, and creation timestamp within 1 second of request | P0 |
| FR-3.2.2 | **Distinct Conversation Identity** | Each conversation is uniquely identifiable by a conversation identifier separate from the session identifier | A conversation is created | Requests referring to the same `conversation_id` resolve the same conversation resource; `conversation_id != session_id` for multi-conversation sessions | P0 |
| FR-3.2.3 | **Conversation-to-Thread Binding** | Each conversation maps 1:1 to a single agent memory thread | Conversation exists and STM is enabled | Requests for the same `conversation_id` load the same `thread_id`; different conversations under the same session do not share thread state | P0 |
| FR-3.2.4 | **Multiple Conversations Per Session** | A session can contain multiple independent conversations under the same business workflow | Session is active and already contains at least one conversation | Additional conversation can be created without mutating or overwriting existing conversation state | P0 |
| FR-3.2.5 | **Conversation Parent Integrity** | Every conversation belongs to exactly one valid session and exactly one valid workspace | Conversation create, load, or update is requested | Operation succeeds only when referenced parent session and workspace exist and are consistent | P0 |
| FR-3.2.6 | **Conversation Metadata Synchronization** | The system updates conversation metadata as part of the active chat processing flow — not as a background or deferred operation — so that message count, token count, status, and activity timestamp reflect the conversation's exchanges after each turn and remain retrievable via conversation APIs | Conversation has active exchanges | After each user and assistant turn, message_count and total_tokens are incremented and last_activity_at is updated within the same request cycle; metadata is query-consistent within 5 seconds | P0 |
| FR-3.2.7 | **Boundary Isolation** | Conversations cannot be accessed across workspace or session boundaries | User in Workspace A or Session A attempts to access Conversation B outside the boundary | Access denied; conversation not found or forbidden response returned | P0 |
| FR-3.2.8 | **Conversation Lifecycle Status** | Conversations transition through defined states independent of session identity: active → summarized → archived | Conversation exists | Status field is always one of three valid values; transitions follow defined order only | P1 |
| FR-3.2.9 | **Conversation Archival** | Ended conversations are archived, never permanently deleted, even when their parent session remains available for audit or review | User or system requests conversation closure | Conversation status = `archived`; record remains queryable for audit and historical navigation | P2 |
| FR-3.2.10 | **Archive Immutability** | Archived conversations cannot accept new stateful writes or message updates | Attempt to send or persist updates to archived conversation | Update rejected; error message indicates archive status | P2 |

---

#### FR-3.3 Memory Summarization

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-3.3.1 | **Automatic Summarization Trigger** | System generates summary when conversation exceeds size threshold | Conversation token count ≥ configured limit | Summary is generated; status transitions to "summarized" | P1 |
| FR-3.3.2 | **Recent Message Preservation** | After summarization, most recent messages are retained for continuity | Summarization triggered | Last K messages remain accessible; earlier messages replaced by summary | P1 |
| FR-3.3.3 | **AI-Generated Summary** | Summary is produced by language model, not rule-based extraction | Summarization triggered | Summary is coherent natural language, ≤3 sentences, captures conversation essence | P1 |
| FR-3.3.4 | **Summary Storage** | Generated summary is persisted with the conversation record bound to the same `conversation_id` and thread | Summary generated | Summary field is non-empty; retrievable on subsequent conversation access | P1 |
| FR-3.3.5 | **Summary Boundary Tracking** | System knows which messages are covered by the summary | Summary exists | Summary boundary marker indicates message index where summary was created | P2 |
| FR-3.3.6 | **Summary Context Injection** | Summary is included as context when the same conversation resumes | Conversation has existing summary | Agent's first response demonstrates awareness of summarized content from that conversation thread | P1 |
| FR-3.3.7 | **Intent Preservation in Summary** | Summary captures the conversation's goals, focus areas, and inherited session context without storing factual market data | Summary generated | Summary contains intent and context phrases (e.g., "User is evaluating dividend growth candidates") rather than computed or quoted facts (e.g., "AAPL price is $150") | P1 |
| FR-3.3.8 | **Summary Isolation Across Conversations** | A summary generated for one conversation does not become active context for sibling conversations unless separately propagated through session context rules | Session contains multiple conversations and one conversation has been summarized | Only the summarized conversation automatically loads its own summary; sibling conversations remain isolated unless they independently store or inherit approved session context | P1 |

---

#### FR-3.4 Session Context and Assumptions

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-3.4.1 | **Session Context Recording** | User-stated preferences, constraints, and analytical goals are captured at the session level as reusable business context | User declares a reusable context statement (e.g., "Use a dividend-growth lens for this review") | Session context is stored and retrievable for subsequent conversations within the same session | P1 |
| FR-3.4.2 | **Pinned Session Intent** | A session can maintain a primary intent that persists across multiple conversations in that session | User states a session goal (e.g., "Compare AAPL vs MSFT across several threads") | Session intent is stored once and remains available to new or resumed conversations in the same session | P1 |
| FR-3.4.3 | **Session Symbol Focus Set** | The session tracks symbols and analytical targets that remain relevant across multiple conversations | User mentions one or more symbols during session workflow | Focused symbol set is updated at session scope and can be inherited by conversations in the same session | P1 |
| FR-3.4.4 | **Context Propagation to Conversations** | New or resumed conversations under a session inherit the session's stored assumptions, intent, and focus context | Session has stored context and a conversation is created or resumed | Agent processing for that conversation receives the session context without the user restating it manually | P0 |
| FR-3.4.5 | **Conversation-Level Refinement** | A conversation may refine the active session context for its own thread without breaking the parent session contract | Session context exists and user adds conversation-specific nuance | The conversation uses the refined context for its thread while the base session context remains intact and reusable | P1 |
| FR-3.4.6 | **Context Isolation by Session Boundary** | Session context cannot leak to conversations belonging to other sessions or workspaces | User attempts to access or reuse context outside the owning session/workspace | Only conversations within the owning session can access the stored context; external access is rejected or omitted | P0 |
| FR-3.4.7 | **Assumption Application Across Threads** | Stored session assumptions influence agent behavior across all conversations belonging to the same session | Session has one or more recorded assumptions and at least two conversations | Agent responses in each conversation align with the stated assumptions without requiring repeated user input | P1 |

---

#### FR-3.5 Long-Term Memory (Future)

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-3.5.1 | **Semantic Memory Search** | System SHALL find relevant past conversations based on meaning, not keywords | User asks about topic discussed in prior session | Relevant past exchanges surface with ≥70% relevance score | P3 |
| FR-3.5.2 | **Cross-Session Recall** | Agent SHALL be able to reference information from previous sessions with same user | User has completed ≥2 sessions previously | Agent can retrieve context from any prior session when prompted | P3 |
| FR-3.5.3 | **Conversation Indexing** | Past conversations SHALL be indexed for efficient retrieval | Session completed and archived | Conversation searchable within 60 seconds of archival | P3 |
| FR-3.5.4 | **User Preference Learning** | System SHALL learn user's investment style and preferences over time | User has ≥5 completed sessions | Agent proactively applies learned preferences without explicit instruction | P3 |
| FR-3.5.5 | **Symbol Interest Tracking** | System SHALL remember which symbols user has researched across sessions | User has researched symbols in past sessions | Agent can list user's historically researched symbols on request | P3 |

---

### FR-4: Semantic Routing

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have

#### FR-4.1 Query Classification

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-4.1.1 | **Automatic Query Categorization** | System determines the intent category of each user query | Query submitted | Query assigned to one of predefined categories | P1 |
| FR-4.1.2 | **Investment Intent Categories** | System recognizes standard investment query types | — | Categories include: price inquiry, news, portfolio, technical analysis, fundamentals, ideas, market overview, general conversation | P1 |
| FR-4.1.3 | **Meaning-Based Classification** | Classification based on query meaning, not just keywords | Query uses synonyms or indirect phrasing | Correct category assigned regardless of exact wording (≥85% accuracy) | P1 |
| FR-4.1.4 | **Classification Confidence** | System indicates how confident it is in the classification | Query classified | Confidence score (0-100%) returned with category | P1 |
| FR-4.1.5 | **Confidence Threshold** | Low-confidence classifications are handled differently | Confidence below threshold | System uses default handling or asks for clarification | P2 |

#### FR-4.2 Route-Based Behavior

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-4.2.1 | **Optimized Tool Selection** | Agent prioritizes relevant tools based on query category | Query classified | Most relevant tool invoked first (reduces unnecessary tool calls by ≥20%) | P2 |
| FR-4.2.2 | **Context-Aware Instructions** | Agent receives category-specific guidance | Query classified | Response style matches category (e.g., technical analysis includes chart references) | P2 |
| FR-4.2.3 | **Category-Specific Formatting** | Response format optimized for query type | Query classified | Price queries show structured data; narrative queries show prose | P2 |

---

### FR-5: API Integration

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have

#### FR-5.1 REST API

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-5.1.1 | **Chat Endpoint** | Client can send messages to the agent via HTTP POST | — | POST request with message returns agent response | P0 |
| FR-5.1.2 | **Request Parameters** | Chat endpoint accepts message, model preference, streaming flag, and conversation identifier; it may also accept parent session context when needed for conversation creation or validation | — | All supported parameters are accepted; stateful requests resolve by `conversation_id`; unrecognized parameters ignored | P0 |
| FR-5.1.3 | **Response Structure** | API response contains all relevant metadata | Request processed | Response includes: content, model used, status, tools invoked | P0 |
| FR-5.1.4 | **Streaming Response Format** | Streaming responses delivered as server-sent events | Streaming requested | Response content-type is text/event-stream; chunks delivered incrementally | P0 |
| FR-5.1.5 | **Backward Compatibility** | API works without conversation identifier for stateless queries | `conversation_id` omitted | Request processes normally; no stateful conversation thread is persisted | P0 |
| FR-5.1.6 | **Input Validation** | Invalid requests return appropriate error codes | Malformed request | 400 returned for invalid format; 503 for service unavailable | P0 |
| FR-5.1.7 | **Hierarchical Management Endpoints** | REST API provides CRUD and lifecycle management interfaces for workspace, session, and conversation resources as specified in FR-5.3, FR-5.4, and FR-5.5 | Management feature enabled | Endpoints exist for creating, listing, retrieving, updating, and archiving hierarchical resources; responses include parent references for navigation | P0 |
| FR-5.1.8 | **Boundary-Aware Resource Resolution** | Stateful and management endpoints validate workspace-session-conversation parent relationships before processing | Request includes hierarchical resource identifiers | Request succeeds only when identifiers describe a valid resource hierarchy; otherwise 404 or 403 returned | P0 |

#### FR-5.2 WebSocket Interface

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-5.2.1 | **Real-Time Messaging** | Client can send messages via WebSocket connection | WebSocket connected | Message delivered to agent; response emitted back | P0 |
| FR-5.2.2 | **Conversation Support** | WebSocket messages can include conversation identifier for stateful message routing | — | Conversation context loaded when `conversation_id` is provided | P0 |
| FR-5.2.3 | **Complete Response Event** | Server emits event when full response is ready | Non-streaming request | Single response event contains complete answer | P0 |
| FR-5.2.4 | **Streaming Chunk Events** | Server emits incremental events during streaming | Streaming requested | Multiple chunk events delivered; final event signals completion | P0 |
| FR-5.2.5 | **Error Notification** | Server emits error event when processing fails | Error occurs | Error event contains error type and user-friendly message | P0 |
| FR-5.2.6 | **Hierarchy Context Support** | WebSocket workflows can supply or resolve parent session context separately from conversation identity when needed for conversation creation or validation | Stateful workflow requires parent session awareness | Conversation routing uses `conversation_id` for STM while preserving the correct parent session boundary | P1 |

---

#### FR-5.3 Management API — Workspace

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have  
> **Roadmap Reference**: Phase C — Management API Delivery

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-5.3.1 | **List User Workspaces** | Client can retrieve all workspaces owned by the authenticated user | User is authenticated | List of workspaces returned with id, name, description, status, and session count; empty list if none exist | P1 |
| FR-5.3.2 | **Create Workspace** | Client can create a new workspace with a name and optional description | User is authenticated | Workspace record created; response includes workspace_id and creation timestamp | P1 |
| FR-5.3.3 | **Get Workspace Details** | Client can retrieve a single workspace by its identifier including aggregate statistics | Valid workspace_id provided; user owns workspace | Response includes workspace metadata plus session count and active conversation count | P1 |
| FR-5.3.4 | **Update Workspace Metadata** | Client can update workspace name and description | Valid workspace_id; workspace is not archived | Updated workspace returned; only provided fields are changed | P2 |
| FR-5.3.5 | **Archive Workspace** | Client can archive a workspace, cascading archive status to all child sessions and conversations | Valid workspace_id; workspace is active | Workspace status transitions to archived; all child sessions and conversations also transition to archived; no new sessions or conversations can be created under it | P2 |
| FR-5.3.6 | **Workspace Ownership Enforcement** | All workspace operations validate that the requesting user owns the workspace | Any workspace request | Requests for workspaces not owned by the user return 403 or 404 | P0 |

---

#### FR-5.4 Management API — Session

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have  
> **Roadmap Reference**: Phase C — Management API Delivery

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-5.4.1 | **Create Session Under Workspace** | Client can create a new session with a title and optional seed context (assumptions, pinned_intent, focused_symbols) | Valid workspace_id; workspace is active; user owns workspace | Session record created with session_id, parent workspace_id, and creation timestamp; status is active | P0 |
| FR-5.4.2 | **Get Session** | Client can retrieve a session by its identifier including context fields | Valid session_id; user has access | Response includes session metadata, status, assumptions, pinned_intent, focused_symbols, and conversation count | P0 |
| FR-5.4.3 | **List Sessions in Workspace** | Client can list sessions belonging to a workspace with optional status filter | Valid workspace_id; user owns workspace | Paginated list of sessions with id, title, status, and conversation count; supports filtering by status (active, closed, archived) | P0 |
| FR-5.4.4 | **Update Session Context** | Client can update session assumptions, pinned_intent, and focused_symbols | Valid session_id; session is active; user has access | Updated session returned; changes are available to subsequent conversation context loading | P1 |
| FR-5.4.5 | **Close Session** | Client can transition a session from active to closed | Valid session_id; session is currently active | Session status transitions to closed; existing conversations remain in their current state; new conversation creation under this session is constrained by policy | P1 |
| FR-5.4.6 | **Archive Session** | Client can archive a session, cascading archive status to all child conversations | Valid session_id; session is closed or active | Session status transitions to archived; all child conversations also transition to archived; no new messages accepted in any child conversation | P1 |
| FR-5.4.7 | **Session Lifecycle Enforcement** | Session state transitions follow the defined order: active → closed → archived | Any session status change requested | Invalid transitions (e.g., archived → active) are rejected with a clear error message | P0 |
| FR-5.4.8 | **Session Parent Validation** | All session operations validate that the session belongs to a workspace owned by the requesting user | Any session request | Requests for sessions outside the user's workspace boundary return 403 or 404 | P0 |

---

#### FR-5.5 Management API — Conversation

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have  
> **Roadmap Reference**: Phase C — Management API Delivery

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-5.5.1 | **Create Conversation Under Session** | Client can create a new conversation within a session, optionally providing a title and seed context | Valid session_id; session is active; user has access | Conversation record created with conversation_id, thread_id, parent session_id and workspace_id, status active; response includes the conversation_id that can be used for subsequent chat requests | P0 |
| FR-5.5.2 | **Get Conversation** | Client can retrieve a conversation by its identifier including metadata and statistics | Valid conversation_id; user has access through hierarchy | Response includes conversation metadata, status, message_count, total_tokens, summary (if summarized), focused_symbols, and parent identifiers | P0 |
| FR-5.5.3 | **List Conversations in Session** | Client can list conversations belonging to a session with optional status filter | Valid session_id; user has access | Paginated list of conversations with id, status, message_count, last_activity_at; supports filtering by status | P0 |
| FR-5.5.4 | **Archive Conversation** | Client can archive an active or summarized conversation | Valid conversation_id; conversation is not already archived; user has access | Conversation status transitions to archived; archive_reason recorded; no further messages accepted | P1 |
| FR-5.5.5 | **Get Conversation History Summary** | Client can retrieve a high-level summary of a conversation's exchanges | Valid conversation_id with ≥1 message | Response includes AI-generated summary (if available), message_count, total_tokens, focused_symbols, and time range | P2 |
| FR-5.5.6 | **Conversation Parent Validation** | All conversation management operations validate the full ownership chain (user → workspace → session → conversation) | Any conversation management request | Requests for conversations outside the user's hierarchy return 403 or 404 | P0 |

---

#### FR-5.6 Management API — Cross-Cutting Behaviors

> **Roadmap Reference**: Phase C — Management API Delivery

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-5.6.1 | **Pagination Support** | List endpoints support paginated results to handle large collections | List request issued | Response includes items array, total count, and pagination cursor or offset metadata | P1 |
| FR-5.6.2 | **Archive Over Delete** | No management endpoint performs hard deletion of any hierarchical resource; all removal operations transition to archived status | Delete or removal action requested | Resource marked as archived; record remains queryable for audit; 410 Gone or equivalent not used | P0 |
| FR-5.6.3 | **Cascade Archive** | Archiving a parent resource cascades the archive transition to all descendant resources | Parent archive requested | All descendants transitioned to archived; cascade is atomic per parent operation | P1 |
| FR-5.6.4 | **Consistent Error Shape** | Management API errors follow the same JSON error shape as chat API errors (ERR-1.1) | Error occurs on management endpoint | Error response includes error.code, error.message, and error.correlation_id | P0 |
| FR-5.6.5 | **Idempotent Resource Lookup** | GET operations are idempotent and safe; repeated identical requests return the same result | Any GET request | Response is identical across retries for unchanged resources | P0 |

---

### FR-6: Streaming

> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have

#### FR-6.1 Response Streaming

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-6.1.1 | **Incremental Delivery** | Response is delivered progressively as it's generated | Streaming requested | User sees response appearing word-by-word or phrase-by-phrase | P0 |
| FR-6.1.2 | **Low Latency Start** | First content appears quickly after request | Streaming requested | First visible content within 2 seconds of request (P95) | P0 |
| FR-6.1.3 | **HTTP Streaming Format** | REST streaming uses standard server-sent events | HTTP streaming request | Response conforms to SSE specification; parseable by EventSource | P0 |
| FR-6.1.4 | **WebSocket Streaming Format** | WebSocket streaming uses sequential events | WebSocket streaming request | Chunks delivered as separate events; client can render incrementally | P0 |
| FR-6.1.5 | **Metadata on Completion** | Final message includes summary metadata | Streaming completes | Last event contains: total tokens, tools invoked, processing time | P0 |
| FR-6.1.6 | **Client Cancellation** | User can stop a streaming response mid-delivery | User initiates cancel | Streaming stops within 1 second; partial response preserved | P1 |

---

### FR-7: Data Integrity and Operational Tooling

> **Roadmap Reference**: Phase D — Runtime Consistency and Reconciliation  
> **Priority Levels**: P0 = Must have (MVP), P1 = Should have (production readiness), P2 = Nice to have

#### FR-7.1 Runtime Metadata Consistency

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-7.1.1 | **Conversation Record Assurance** | The system ensures a conversation metadata record exists before the agent processes a chat message for a given conversation_id | Chat request with conversation_id submitted | Conversation record exists in the conversations collection before agent invocation; auto-created if missing with correct parent references | P0 |
| FR-7.1.2 | **User Turn Tracking** | Each user message processed by the chat flow increments the conversation's message_count and updates last_activity_at | User sends a chat message within a conversation | message_count incremented by 1; last_activity_at updated to current timestamp; visible via conversation GET endpoint within 5 seconds | P0 |
| FR-7.1.3 | **Assistant Turn Tracking** | Each assistant response updates the conversation's message_count and total_tokens estimate | Agent produces a response | message_count incremented by 1; total_tokens updated with estimated token count; visible via conversation GET endpoint within 5 seconds | P0 |
| FR-7.1.4 | **Focused Symbol Refresh** | When the agent detects new stock symbols during processing, the conversation-level focused_symbols field is updated | Agent processes a query mentioning a new symbol | focused_symbols array includes newly detected symbols without removing previously tracked ones | P1 |
| FR-7.1.5 | **Dual Persistence Coordination** | Checkpoint state (managed by LangGraph) and conversation metadata (managed by application) are treated as two coordinated but distinct persistence layers; neither is authoritative over the other's domain | Chat flow executes with STM enabled | Checkpoint stores agent graph state; conversation record stores searchable application metadata; both updated in the same request cycle | P0 |

---

#### FR-7.2 Data Reconciliation

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-7.2.1 | **Orphan Conversation Detection** | The system can detect conversations whose parent session does not exist or is invalid | Reconciliation scan triggered | Report lists all conversation_ids referencing non-existent or invalid session_ids | P1 |
| FR-7.2.2 | **Orphan Session Detection** | The system can detect sessions whose parent workspace does not exist or is invalid | Reconciliation scan triggered | Report lists all session_ids referencing non-existent or invalid workspace_ids | P1 |
| FR-7.2.3 | **Checkpoint-Metadata Misalignment Detection** | The system can detect checkpoints without corresponding conversation records and conversation records without corresponding checkpoints (when STM should exist) | Reconciliation scan triggered | Report lists unmatched thread_ids in both directions | P1 |
| FR-7.2.4 | **Reconciliation Report** | Reconciliation produces a machine-readable report of all detected anomalies | Reconciliation scan completes | JSON report includes anomaly type, affected resource identifiers, and suggested remediation | P1 |
| FR-7.2.5 | **Non-Blocking Reconciliation** | Reconciliation scans execute without blocking production traffic or degrading chat performance | Reconciliation running alongside active chat sessions | Chat response latency is not materially affected (< 5% increase) during reconciliation | P1 |

---

#### FR-7.3 Data Migration

| ID | Title | Description | Precondition | Expected Output | Priority |
|----|-------|-------------|--------------|-----------------|----------|
| FR-7.3.1 | **Legacy Thread Promotion** | The system can convert historical session_id-based checkpoint threads into conversation records with correctly assigned conversation_id and thread_id | Legacy data exists from pre-hierarchy implementation | Each legacy thread_id is promoted to a conversation record with preserved checkpoint accessibility | P1 |
| FR-7.3.2 | **Migration Dry-Run** | The migration tool supports a preview mode that reports planned changes without writing to the database | Migration initiated in dry-run mode | Report shows number of records to create, update, or skip; no database writes occur | P1 |
| FR-7.3.3 | **Migration Audit Trail** | All migration actions are recorded in an audit log for traceability | Migration executed | Audit log entries include timestamp, action type, source identifier, target identifier, and outcome | P1 |
| FR-7.3.4 | **Incremental Migration** | Migration supports resumable execution; if interrupted, it can continue from the last successful point without re-processing completed records | Migration interrupted and restarted | Previously processed records are skipped; remaining records are processed; final state is identical to uninterrupted execution | P1 |
| FR-7.3.5 | **Zero Data Loss** | Migration does not discard, overwrite, or orphan any existing checkpoint data | Migration completes | All pre-migration checkpoint threads remain accessible via their new conversation_id mapping | P0 |
| FR-7.3.6 | **Backward-Compatible Operation During Migration** | The system continues to serve both legacy stateless requests and new hierarchy-aware requests during the migration window | Migration in progress | Stateless requests (no conversation_id) process normally; conversation-scoped requests resolve correctly for both migrated and not-yet-migrated records | P0 |

---

## 3. Non-Functional Requirements

### NFR-1: Performance

#### NFR-1.1 Latency
**Priority**: P0

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1.1 | Time to first token for streaming responses SHALL be < 2 seconds | P95 |
| NFR-1.1.2 | Simple query (no tool calls) response time SHALL be < 3 seconds | P95 |
| NFR-1.1.3 | Query with single tool call response time SHALL be < 5 seconds | P95 |
| NFR-1.1.4 | Query with multiple tool calls response time SHALL be < 10 seconds | P95 |
| NFR-1.1.5 | Memory retrieval SHALL NOT add > 100ms latency | P95 |
| NFR-1.1.6 | Cache hit response time SHALL be < 500ms | P95 |

#### NFR-1.2 Throughput
**Priority**: P1

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.2.1 | System SHALL support ≥ 50 concurrent conversations | Minimum |
| NFR-1.2.2 | System SHALL handle ≥ 100 queries per minute | Sustained |
| NFR-1.2.3 | System SHALL handle burst of 500 queries per minute | Peak (5 min) |

#### NFR-1.3 Resource Utilization
**Priority**: P1

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.3.1 | Agent memory footprint per conversation SHALL be < 50MB | Maximum |
| NFR-1.3.2 | Cache hit rate SHALL be ≥ 40% for repeated queries | Minimum |
| NFR-1.3.3 | Database connection pool utilization SHALL stay < 80% | Normal ops |

#### NFR-1.4 Management API Latency
**Priority**: P1

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.4.1 | Single-resource GET response time SHALL be < 200ms | P95 |
| NFR-1.4.2 | List operations (with pagination) response time SHALL be < 500ms | P95 |
| NFR-1.4.3 | Create/update/archive operations response time SHALL be < 500ms | P95 |
| NFR-1.4.4 | Cascade archive operations response time SHALL be < 2 seconds | P95 |

---

### NFR-2: Reliability

#### NFR-2.1 Availability
**Priority**: P0

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-2.1.1 | Agent service availability SHALL be ≥ 99.5% | Monthly |
| NFR-2.1.2 | Planned maintenance windows SHALL be < 4 hours per month | Maximum |
| NFR-2.1.3 | System SHALL recover from transient failures within 30 seconds | P95 |

#### NFR-2.2 Fault Tolerance
**Priority**: P0

| ID | Requirement |
|----|-------------|
| NFR-2.2.1 | The agent SHALL fallback to secondary model on primary model failure |
| NFR-2.2.2 | The agent SHALL gracefully degrade when tools fail (return partial response) |
| NFR-2.2.3 | The agent SHALL continue operating when cache is unavailable |
| NFR-2.2.4 | The agent SHALL continue operating when checkpointer is unavailable (stateless mode) |
| NFR-2.2.5 | Failed tool calls SHALL NOT crash the agent execution |

#### NFR-2.3 Data Integrity
**Priority**: P0

| ID | Requirement |
|----|-------------|
| NFR-2.3.1 | Conversation checkpoints SHALL be atomically persisted |
| NFR-2.3.2 | Conversation metadata SHALL be eventually consistent within 5 seconds |
| NFR-2.3.3 | Token counts SHALL be accurate within 5% of actual usage |

#### NFR-2.4 Data Migration Reliability
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-2.4.1 | Migration SHALL NOT cause data loss; all pre-existing checkpoints SHALL remain accessible after migration |
| NFR-2.4.2 | Migration SHALL be resumable after interruption without re-processing completed records |
| NFR-2.4.3 | Migration SHALL support dry-run mode that reports planned changes without database writes |
| NFR-2.4.4 | Migration and reconciliation actions SHALL be logged with correlation ID and timestamps |
| NFR-2.4.5 | Migration SHALL be executable during normal system operation without service downtime |

#### NFR-2.5 Reconciliation Safety
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-2.5.1 | Reconciliation scans SHALL be non-blocking and SHALL NOT degrade production query latency by more than 5% |
| NFR-2.5.2 | Reconciliation operations SHALL be idempotent; repeated runs produce the same report for unchanged data |
| NFR-2.5.3 | Reconciliation SHALL NOT auto-repair data without explicit operator confirmation unless configured for auto-heal mode |
| NFR-2.5.4 | Reconciliation and migration tools SHALL require elevated permissions; they SHALL NOT be accessible via public API endpoints |

---

### NFR-3: Scalability

#### NFR-3.1 Horizontal Scaling
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-3.1.1 | Agent service SHALL be stateless; durable state SHALL be externalized to shared backend services |
| NFR-3.1.2 | Multiple agent instances SHALL share the same durable conversation state store |
| NFR-3.1.3 | Tool registry SHALL be per-instance (no cross-instance state) |
| NFR-3.1.4 | Cache SHALL be shared across instances via a shared cache backend |

#### NFR-3.2 Data Scaling
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-3.2.1 | Conversation history SHALL scale to 10,000+ messages per conversation thread |
| NFR-3.2.2 | System SHALL support 1M+ total conversations |
| NFR-3.2.3 | Conversation state store SHALL support automatic TTL-based cleanup |

---

### NFR-4: Security

#### NFR-4.1 Authentication & Authorization
**Priority**: P0

| ID | Requirement |
|----|-------------|
| NFR-4.1.1 | API keys for LLM providers SHALL NOT be logged or exposed |
| NFR-4.1.2 | API keys SHALL be loaded from environment variables or secure vault |
| NFR-4.1.3 | Workspace, session, and conversation access SHALL be validated against user ownership and parent-boundary integrity |
| NFR-4.1.4 | Cross-user conversation access SHALL be prevented |

#### NFR-4.2 Data Protection
**Priority**: P0

| ID | Requirement |
|----|-------------|
| NFR-4.2.1 | Conversation content SHALL be stored encrypted at rest |
| NFR-4.2.2 | API communication SHALL use HTTPS/WSS in production |
| NFR-4.2.3 | Sensitive user data (including financial information and PII) SHALL NOT be logged or emitted into traces |
| NFR-4.2.4 | PII in conversations SHALL be handled per privacy policy |

#### NFR-4.3 Input Validation
**Priority**: P0

| ID | Requirement |
|----|-------------|
| NFR-4.3.1 | Query input SHALL be sanitized before processing |
| NFR-4.3.2 | Maximum query length SHALL be enforced (configurable, default 10,000 chars) |
| NFR-4.3.3 | Tool inputs SHALL be validated against expected schemas |
| NFR-4.3.4 | Injection attempts SHALL be detected and rejected |

---

### NFR-5: Observability

#### NFR-5.1 Logging
**Priority**: P0

| ID | Requirement |
|----|-------------|
| NFR-5.1.1 | All agent queries SHALL be logged with correlation ID |
| NFR-5.1.2 | Tool invocations SHALL be logged with execution time |
| NFR-5.1.3 | Errors SHALL be logged with full context (sanitized) |
| NFR-5.1.4 | Model selection decisions SHALL be logged |
| NFR-5.1.5 | Memory operations SHALL be logged at DEBUG level |

#### NFR-5.2 Tracing
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-5.2.1 | Distributed tracing SHALL be supported for agent execution |
| NFR-5.2.2 | Traces SHALL include message history, tool calls, and token usage |
| NFR-5.2.3 | Trace data SHALL be exportable for analysis |
| NFR-5.2.4 | Tracing SHALL be configurable (enable/disable per environment) |
| NFR-5.2.5 | Traces SHALL include the prompt version identifier used for each agent invocation |
| NFR-5.2.6 | Traces SHALL include the agent role or route classification applied to the request |
| NFR-5.2.7 | When prompt experiments are active, traces SHALL include the experiment identifier and variant assignment |

#### NFR-5.3 Metrics
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-5.3.1 | System SHALL track query count by route category |
| NFR-5.3.2 | System SHALL track average response latency |
| NFR-5.3.3 | System SHALL track token usage by provider/model |
| NFR-5.3.4 | System SHALL track cache hit/miss ratio |
| NFR-5.3.5 | System SHALL track tool invocation frequency |
| NFR-5.3.6 | System SHALL track error rate by type |

---

### NFR-6: Maintainability

#### NFR-6.1 Code Quality
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-6.1.1 | Code SHALL follow project Python conventions (PEP 8, type hints) |
| NFR-6.1.2 | All public methods SHALL have docstrings |
| NFR-6.1.3 | Test coverage for agent core SHALL be ≥ 80% |
| NFR-6.1.4 | Test coverage for tools SHALL be ≥ 70% |
| NFR-6.1.5 | All tools SHALL have unit tests |

#### NFR-6.2 Extensibility
**Priority**: P1

| ID | Requirement |
|----|-------------|
| NFR-6.2.1 | New tools SHALL be addable without modifying agent core |
| NFR-6.2.2 | New routes SHALL be addable without modifying router core |
| NFR-6.2.3 | System prompts SHALL be loaded from versioned file assets and SHALL be configurable without code deployment; prompt changes SHALL take effect via configuration reload or service restart without a new code release |
| NFR-6.2.4 | Model providers SHALL be pluggable via factory pattern |

#### NFR-6.3 Configuration
**Priority**: P0

| ID | Requirement |
|----|-------------|
| NFR-6.3.1 | All agent settings SHALL be configurable via environment-aware configuration |
| NFR-6.3.2 | Sensitive values SHALL support environment variable override |
| NFR-6.3.3 | Configuration changes SHALL NOT require code deployment |
| NFR-6.3.4 | Configuration SHALL support environment-specific overlays |

---

## 4. Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| CON-1 | Supported runtime and framework versions SHALL be used | Ensures compatibility and supportability (see design docs) |
| CON-2 | A primary LLM provider account SHALL be available | Required to generate responses |
| CON-3 | A persistent conversation state store SHALL be available for stateful conversations and conversation-thread recovery | Required for FR-3 persistence behavior |
| CON-4 | A caching backend SHALL be available for tool result caching | Required to meet FR-2.1 performance/cost goals |
| CON-5 | A tracing/observability backend SHOULD be available | Enables NFR-5 observability targets |

---

## 5. Acceptance Criteria

### AC-1: Core Agent Functionality

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-1.1 | Agent processes natural language queries and returns structured responses | Integration test |
| AC-1.2 | Agent uses tools when appropriate for data retrieval | Integration test |
| AC-1.3 | Agent falls back to secondary model on primary failure | Chaos test |
| AC-1.4 | Streaming responses deliver tokens incrementally | E2E test |

### AC-2: Memory Functionality

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-2.1 | Agent recalls previous exchanges within the same conversation thread | Integration test |
| AC-2.2 | Conversation thread state persists across API restarts for the same `conversation_id` | System test |
| AC-2.3 | Memory retrieval adds < 100ms latency | Performance test |
| AC-2.4 | Summarization triggers at configured threshold | Unit test |
| AC-2.5 | API remains backward compatible without `conversation_id` | Regression test |
| AC-2.6 | Two conversations under the same session do not share STM context | Integration test |
| AC-2.7 | Session context is propagated into new or resumed conversations within the same session | Integration test |

### AC-3: Performance

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-3.1 | P95 response latency < 5s for single-tool queries | Load test |
| AC-3.2 | System handles 50 concurrent conversations | Stress test |
| AC-3.3 | Cache hit rate ≥ 40% under normal load | Metrics |

### AC-4: Security

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-4.1 | API keys never appear in logs | Log audit |
| AC-4.2 | Cross-user and cross-boundary conversation access is prevented | Security test |
| AC-4.3 | Input validation rejects injection attempts | Penetration test |

### AC-5: Management API Functionality

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-5.1 | Workspace CRUD: create, list, get, and archive workspaces via REST API | Integration test |
| AC-5.2 | Session CRUD: create session under workspace, list sessions, get session details, update context, close, and archive | Integration test |
| AC-5.3 | Conversation CRUD: create conversation under session, list conversations, get conversation details, and archive | Integration test |
| AC-5.4 | Cascade archive: archiving a session archives all child conversations; archiving a workspace archives all child sessions and conversations | Integration test |
| AC-5.5 | Management API response times within NFR-1.4 targets | Load test |
| AC-5.6 | Management endpoints enforce user ownership at every hierarchy level | Security test |
| AC-5.7 | List endpoints support pagination for collections with > 50 items | Integration test |

### AC-6: Data Consistency and Reconciliation

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-6.1 | After each chat turn, conversation metadata (message_count, total_tokens, last_activity_at) reflects the exchange within 5 seconds | Integration test |
| AC-6.2 | Reconciliation scan detects orphan conversations (missing parent session) and orphan sessions (missing parent workspace) | System test |
| AC-6.3 | Reconciliation scan detects checkpoint-metadata misalignment (checkpoints without conversation records and vice versa) | System test |
| AC-6.4 | Migration promotes legacy session_id-based threads into conversation records without data loss | Migration test |
| AC-6.5 | Migration dry-run reports planned changes without writing to the database | Unit test |
| AC-6.6 | System operates normally during migration window (both legacy and new-model requests succeed) | System test |

### AC-7: Lifecycle Enforcement

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-7.1 | Archived conversation rejects new chat messages with appropriate error | Integration test |
| AC-7.2 | Closed or archived session constrains new conversation creation according to policy | Integration test |
| AC-7.3 | Session state transitions follow defined order (active → closed → archived); invalid transitions are rejected | Unit test |
| AC-7.4 | Cross-workspace session access is rejected | Security test |
| AC-7.5 | Cross-session conversation access (from outside the owning session's workspace) is rejected | Security test |
### AC-8: Prompt System

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-8.1 | Prompt version identifier appears in agent response metadata and trace spans for every invocation | Integration test |
| AC-8.2 | When the configured prompt asset is missing or malformed, the agent falls back to baseline prompt and logs a WARN-level event | Fault-injection test |
| AC-8.3 | Agent responses to financial queries reference specific tool-sourced data points and include source attribution | Integration test |
| AC-8.4 | Agent responses do not contain hype, guaranteed-return claims, or urgency language (verified by blocklist scan) | Unit test + regression test |

---

## 6. Traceability Matrix

This section maps acceptance criteria (AC-*) to the functional and non-functional requirements they verify. Mappings are many-to-many.

| Acceptance Criteria | Verified Requirements |
|--------------------|----------------------|
| AC-1.1 | FR-1.2.1, FR-1.2.2, FR-5.1.3 |
| AC-1.2 | FR-1.1.2, FR-2.2.1, FR-2.2.4 |
| AC-1.3 | FR-1.3.2, FR-1.3.3, NFR-2.2.1 |
| AC-1.4 | FR-1.2.4, FR-6.1.1, FR-6.1.2, NFR-1.1.1 |
| AC-2.1 | FR-3.1.1, FR-3.1.4 |
| AC-2.2 | FR-3.1.2, FR-3.1.5, NFR-2.3.1 |
| AC-2.3 | NFR-1.1.5 |
| AC-2.4 | FR-3.3.1, FR-3.3.4 |
| AC-2.5 | FR-3.1.6, FR-5.1.5 |
| AC-2.6 | FR-3.2.3, FR-3.2.4, FR-3.2.7 |
| AC-2.7 | FR-3.4.1, FR-3.4.2, FR-3.4.4, FR-3.4.7 |
| AC-3.1 | NFR-1.1.3 |
| AC-3.2 | NFR-1.2.1 |
| AC-3.3 | FR-2.1.1, NFR-1.3.2, NFR-5.3.4 |
| AC-4.1 | NFR-4.1.1, NFR-4.2.3 |
| AC-4.2 | NFR-4.1.3, NFR-4.1.4, FR-3.2.7, FR-3.4.6 |
| AC-4.3 | NFR-4.3.1, NFR-4.3.4 |
| AC-5.1 | FR-5.3.1, FR-5.3.2, FR-5.3.3, FR-5.3.5, FR-5.3.6 |
| AC-5.2 | FR-5.4.1, FR-5.4.2, FR-5.4.3, FR-5.4.4, FR-5.4.5, FR-5.4.6, FR-5.4.7 |
| AC-5.3 | FR-5.5.1, FR-5.5.2, FR-5.5.3, FR-5.5.4 |
| AC-5.4 | FR-5.6.3, FR-5.4.6, FR-5.3.5 |
| AC-5.5 | NFR-1.4.1, NFR-1.4.2, NFR-1.4.3, NFR-1.4.4 |
| AC-5.6 | FR-5.3.6, FR-5.4.8, FR-5.5.6 |
| AC-5.7 | FR-5.6.1 |
| AC-6.1 | FR-7.1.2, FR-7.1.3, FR-3.2.6, NFR-2.3.2 |
| AC-6.2 | FR-7.2.1, FR-7.2.2, FR-7.2.4 |
| AC-6.3 | FR-7.2.3, FR-7.2.4 |
| AC-6.4 | FR-7.3.1, FR-7.3.5 |
| AC-6.5 | FR-7.3.2, NFR-2.4.3 |
| AC-6.6 | FR-7.3.6, NFR-2.4.5 |
| AC-7.1 | FR-3.2.10, FR-7.1.1 |
| AC-7.2 | FR-5.4.5, FR-5.4.7 |
| AC-7.3 | FR-5.4.7, FR-3.2.8 |
| AC-7.4 | FR-5.4.8, FR-3.2.7 |
| AC-7.5 | FR-5.5.6, FR-3.2.7, FR-3.4.6 |
| AC-8.1 | FR-1.4.6, NFR-5.2.5 |
| AC-8.2 | FR-1.4.8, NFR-2.2.2 |
| AC-8.3 | FR-1.5.1, FR-1.5.5 |
| AC-8.4 | FR-1.5.3 |

---

## 7. Interface Requirements

### IR-1 REST API Contract

| ID | Requirement |
|----|-------------|
| IR-1.1 | The REST API SHALL conform to the OpenAPI specification in [docs/openapi.yaml](../openapi.yaml) |
| IR-1.2 | Request and response payloads SHALL validate against the schemas defined in [docs/openapi.yaml](../openapi.yaml) |
| IR-1.3 | The API SHALL return `application/json` for non-streaming responses |
| IR-1.4 | Streaming endpoints SHALL use SSE and SHALL return `text/event-stream` |
| IR-1.5 | Stateful chat requests SHOULD support a `conversation_id` field to identify the conversation thread to load or resume |
| IR-1.6 | Management APIs SHOULD expose hierarchical resource relationships for workspaces, sessions, and conversations |
| IR-1.7 | Conversation management APIs SHOULD preserve parent references (`workspace_id`, `session_id`) in request or response payloads where required for navigation and validation |
| IR-1.8 | Workspace management endpoints SHALL be rooted at `/api/workspaces` with nested session navigation at `/api/workspaces/{workspace_id}/sessions` |
| IR-1.9 | Session management endpoints SHALL support both nested access (`/api/workspaces/{workspace_id}/sessions`) and direct access (`/api/sessions/{session_id}`) with parent validation |
| IR-1.10 | Conversation management endpoints SHALL support both nested access (`/api/sessions/{session_id}/conversations`) and direct access (`/api/conversations/{conversation_id}`) with hierarchy validation |
| IR-1.11 | List responses SHALL include pagination metadata (total count, page/cursor info) and SHALL support query parameters for filtering by status |
| IR-1.12 | Archive action endpoints SHALL use POST method (e.g., `POST /api/conversations/{id}/archive`) rather than DELETE, to distinguish archive-over-delete semantics |
| IR-1.13 | Management API responses SHALL include `workspace_id`, `session_id`, and `conversation_id` in resource payloads to support client-side hierarchy navigation |

### IR-2 WebSocket Contract

| ID | Requirement |
|----|-------------|
| IR-2.1 | WebSocket event names used by the backend and frontend SHALL be consistent and centrally defined by the frontend configuration (see [frontend/src/config.ts](../../frontend/src/config.ts)) |
| IR-2.2 | WebSocket message payloads SHALL be JSON objects |
| IR-2.3 | WebSocket requests SHOULD support a `conversation_id` field for stateful conversation behavior |
| IR-2.4 | WebSocket responses SHALL include a response payload and sufficient metadata to correlate to the initiating request |
| IR-2.5 | When session-scoped context is required for conversation creation or restoration, interfaces SHOULD support supplying or resolving the parent `session_id` separately from `conversation_id` |

---

## 8. Error Semantics

### ERR-1 Standard Error Shape

| ID | Requirement |
|----|-------------|
| ERR-1.1 | All non-streaming API error responses SHALL be JSON and SHALL include: `error.code`, `error.message`, and `error.correlation_id` |
| ERR-1.2 | Error messages returned to clients SHALL be user-friendly and SHALL NOT expose internal stack traces or secrets |
| ERR-1.3 | Errors SHALL use appropriate HTTP status codes (e.g., 400 validation error, 401/403 auth error, 404 not found, 429 rate limit, 500 internal error, 503 dependency unavailable) |

### ERR-2 Streaming Errors and Cancellation

| ID | Requirement |
|----|-------------|
| ERR-2.1 | If an error occurs during streaming, the system SHALL emit a terminal error event/message that is machine-detectable by the client |
| ERR-2.2 | Client-initiated streaming cancellation SHALL stop the stream within 1 second and SHALL release any associated resources |
| ERR-2.3 | Streaming partial output SHOULD be preserved and returned to the client if available |

### ERR-3 Retry and Rate Limits

| ID | Requirement |
|----|-------------|
| ERR-3.1 | The system SHALL implement safe retry behavior for transient upstream failures (e.g., model provider or tool provider) without duplicating side effects |
| ERR-3.2 | When rate-limited, the system SHALL return a clear rate-limit error and SHOULD provide retry guidance (e.g., recommended wait time) |

---

## 9. Data Handling & Privacy

### PRIV-1 Data Minimization and Classification

| ID | Requirement |
|----|-------------|
| PRIV-1.1 | The system SHALL minimize stored conversation content to what is required to satisfy FR-3 behavior |
| PRIV-1.2 | The system SHALL NOT persist raw tool outputs in conversation storage (see FR-3.1.8) |
| PRIV-1.3 | The system SHALL NOT persist computed financial metrics in conversation storage (see FR-3.1.7) |

### PRIV-2 Retention, Archival, and Deletion

| ID | Requirement |
|----|-------------|
| PRIV-2.1 | The system SHALL support configurable retention windows for stored conversation records |
| PRIV-2.2 | The system SHALL support archival of conversations as a distinct lifecycle state (see FR-3.2.7) |
| PRIV-2.3 | The system SHALL support user-initiated deletion requests for conversation content, subject to audit and compliance requirements |

### PRIV-3 PII Handling and Redaction

| ID | Requirement |
|----|-------------|
| PRIV-3.1 | The system SHALL treat conversation content as potentially sensitive and SHALL apply redaction policies to logs and traces |
| PRIV-3.2 | The system SHALL ensure that secrets (API keys, tokens, passwords) are never logged or traced |
| PRIV-3.3 | The system SHALL provide an auditable record of access to conversation data (who/what accessed it and when) |

---

## 10. Assumptions & Open Issues

### Assumptions

- A user-workspace-session-conversation identity model exists to support ownership validation and hierarchical boundary checks (see NFR-4.1.3).
- A privacy policy exists to define what constitutes PII and how it must be handled (see NFR-4.2.4).
- Clients consuming SSE and WebSocket streaming are capable of handling incremental updates and terminal error signaling.
- Stateful clients can persist and resend `conversation_id` when resuming a conversation thread.

### Open Issues

| ID | Issue | Impact |
|----|-------|--------|
| OI-1 | Define default retention windows per environment for PRIV-2.1 | Needed to make retention testable out-of-the-box |
| OI-2 | Define the canonical error code taxonomy for ERR-1.1 | Required for consistent client handling and analytics |
| OI-3 | Specify the exact WebSocket event payload schemas (beyond high-level contract) | Needed for strict schema validation and frontend/back alignment |
| OI-4 | Define the canonical REST and WebSocket payload contract for `conversation_id` and optional parent `session_id` usage | Required to avoid ambiguity between conversation-scoped STM and session-scoped business workflow |
| ~~OI-5~~ | ~~Define the formal CRUD policy per resource, especially archive versus delete semantics for workspace and session resources~~ | **Resolved in v2.2** — FR-5.3–5.6 define full CRUD policy; FR-5.6.2 mandates archive-over-delete semantics |
| OI-6 | Define the migration execution window and rollback strategy for legacy thread promotion (FR-7.3) | Required before production migration; determines maintenance-window needs and data-safety guarantees |
| OI-7 | Define reconciliation schedule and alerting thresholds for orphan/misalignment detection (FR-7.2) | Required to operationalize reconciliation — determines frequency, severity tiers, and notification targets |
| OI-8 | Define pagination defaults (page size, max page size, sort order) for management API list endpoints (FR-5.6.1) | Required for consistent client behavior and to prevent unbound result sets |
| OI-9 | Define prompt asset directory structure, naming convention, and version-tagging scheme for externalized prompt files (FR-1.4.6, NFR-6.2.3) | Required before prompt versioning and experiment assignment can be implemented |

---

## 11. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-22 | System | Initial requirements specification |
| 1.1 | 2026-01-23 | System | Rewrote FR-3 Memory System with business-driven format: Added Title/Precondition/Expected Output columns, measurable acceptance criteria, declarative language. Removed technical implementation details. |
| 1.2 | 2026-01-23 | System | Rewrote FR-1 (Agent Core), FR-2 (Tool System), FR-4 (Semantic Routing), FR-5 (API Integration), FR-6 (Streaming) with same business-driven format. All FRs now use consistent table structure with ID, Title, Description, Precondition, Expected Output, Priority columns. |
| 2.0 | 2026-01-23 | System | Major restructure to standard SRS format. (1) Removed MEM-* section containing implementation details—memory behaviors already specified in FR-3. (2) Moved Dependencies to technical design document. (3) Enhanced Introduction with explicit In Scope/Out of Scope boundaries. (4) Cleaned Definitions section—removed implementation terms. (5) Restructured ToC from 8 to 6 sections. (6) Adopted spec-driven development approach for AI-assisted implementation. |
| 2.1 | 2026-03-17 | System | Realigned terminology and API/memory semantics to the conversation-scoped STM model: updated FR-3 and FR-5 language for `conversation_id -> thread_id`, clarified session-as-parent context behavior, and corrected NFR/constraint wording that previously implied session-scoped STM persistence. |
| 2.2 | 2026-03-19 | System | Phase C–E requirement integration. Added FR-5.3–5.6 (Management API for workspace, session, conversation, cross-cutting behaviors), FR-7 (Data Integrity and Operational Tooling — runtime metadata consistency, reconciliation, migration). Added NFR-1.4 (Management API Latency), NFR-2.4 (Data Migration Reliability), NFR-2.5 (Reconciliation Safety). Added AC-5 (Management API Functionality), AC-6 (Data Consistency and Reconciliation), AC-7 (Lifecycle Enforcement). Added IR-1.8–IR-1.13 (management API interface contracts). Strengthened FR-3.2.6 to P0 runtime-wiring requirement and FR-5.1.7 to P0 with explicit cross-references. Resolved OI-5; added OI-6–OI-8. Governing analysis: PHASE_CDE_REQUIREMENT_ANALYSIS.md. |
| 2.3 | 2026-04-13 | System | Prompt system and behavioral guardrails integration. Added FR-1.4.6–1.4.9 (prompt version identity, route-specific context, rollback safety, experiment assignment). Added FR-1.5 (Finance-Domain Behavioral Guardrails — evidence-first responses, uncertainty disclosure, anti-hype, fact-assumption separation, source attribution). Added NFR-5.2.5–5.2.7 (prompt version, agent role, and experiment ID in traces). Strengthened NFR-6.2.3 to require versioned file assets and no-code-deployment configurability. Added AC-8 (Prompt System acceptance criteria). Added related document reference to PROMPT_SYSTEM_RESEARCH_PROPOSAL.md. Added OI-9 (prompt asset directory structure). Research foundation: PROMPT_SYSTEM_RESEARCH_PROPOSAL.md v1.2. |
---

*End of Requirements Document*
