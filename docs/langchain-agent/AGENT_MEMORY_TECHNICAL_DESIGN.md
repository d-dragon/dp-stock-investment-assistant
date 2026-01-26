# Agent Memory Technical Design

> **Document Version**: 1.1  
> **Last Updated**: January 22, 2026  
> **Phase**: 2A.1 - Long-Term Conversation Memory  
> **Status**: Technical Design Complete  
> **Governing ADR**: [ADR-001 — Layered LLM Architecture](./AGENT_ARCHITECTURE_DECISION_RECORDS.md)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Alignment with ADR-001](#alignment-with-adr-001)
3. [Architectural Decisions](#architectural-decisions)
4. [Data Model Design](#data-model-design)
5. [Sequence Diagrams](#sequence-diagrams)
6. [API Contract Changes](#api-contract-changes)
7. [Configuration Requirements](#configuration-requirements)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Testing Strategy](#testing-strategy)

---

## Executive Summary

### Objective

Implement persistent conversation memory for the Stock Assistant LangChain agent, enabling multi-turn conversations where the agent recalls previous exchanges within a session.

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Dual Memory Strategy** | Short-term (checkpointer) + Long-term (vector store for personalization) |
| **Memory Never Stores Facts** | Financial data stays in RAG/Tools layer per ADR-001 |
| **Backward Compatibility** | Existing APIs continue to work without `session_id` |
| **Separation of Concerns** | LangGraph handles agent state; ChatRepository handles UI queries |
| **Native Integration** | Use LangGraph's built-in MongoDBSaver for checkpoints |
| **Archive Over Delete** | Sessions archived for historical reference, not purged |

### Scope

**In Scope:**
- Short-term conversation memory via LangGraph checkpointer
- New MongoDB collections for agent memory
- API changes to support `session_id` parameter
- Memory summarization for long conversations
- Conversation archival strategy

**Out of Scope (Phase 2A.2+):**
- Long-term vector store memory (semantic search over past conversations)
- Cross-session memory retrieval
- User preference learning (LTM personalization layer)

---

## Alignment with ADR-001

This technical design implements the **Short-Term Memory (STM)** component defined in ADR-001. The following table maps ADR principles to implementation decisions:

| ADR Principle | Implementation |
|---|---|
| **Memory never stores facts** | Conversation checkpoints and summaries store messages, preferences, and routing hints only; no prices, ratios, filings, or conclusions. |
| **RAG never stores opinions** | RAG indices are sourced evidence only; interpretations remain in LLM output with citations. |
| **Fine-tuning never stores knowledge** | Fine-tuning enforces structure and tone; training excludes invented data and forecasts. |
| **Prompting controls behavior, not data** | Prompt compiler injects rules and schema; data is injected at runtime from STM/LTM/RAG/tools. |
| **Tools compute numbers, LLM reasons about them** | Calculations are performed by tools; summaries reference tool calls without persisting outputs. |
| **Investment data sources are external** | Market data and filings come from approved sources or internal databases via tools; memory only stores references. |
| **Market manipulation safeguards are enforced** | Responses are informational and grounded in verifiable sources; no price influence or trade instructions. |

| ADR Principle | Implementation |
|---------------|----------------|
| **Memory never stores facts** | Conversation checkpoints store messages only; no financial data, prices, or computed metrics |
| **RAG never stores opinions** | Memory layer distinct from RAG indices (future `memory_vectors` for semantic recall only) |
| **Prompting controls behavior** | Prompt compiler summarizes LTM/STM to ≤2 lines (future integration) |
| **Tools compute numbers** | Memory does not persist tool outputs—only references to tools called |

### Memory Layer Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MEMORY BOUNDARIES (per ADR-001)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ✅ STORED IN MEMORY                    ❌ NEVER IN MEMORY                  │
│   ─────────────────────                  ──────────────────                  │
│   • User query text                      • Stock prices (real-time/historical)│
│   • Assistant response text              • Financial ratios/metrics          │
│   • Tool call references (name, args)    • Valuation assessments             │
│   • Session assumptions                  • Price targets/forecasts           │
│   • Conversation summaries               • News content or filing text       │
│   • Pinned intents                       • Analytical conclusions            │
│   • Focused symbols (by name only)       • RAG-retrieved document content    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### STM Design per ADR-001 Section 6.2

| ADR Specification | Technical Implementation |
|-------------------|-------------------------|
| Session-scoped conversations | `conversations` collection with `session_id` FK |
| Archive option (not delete) | `status: archived` with read-only enforcement |
| Workspace-bound isolation | `session.workspace_id` ensures context isolation |
| Selective recall | `summarize_threshold` triggers condensation |
| Query-specific retrieval | Future: RAG over `memory_vectors` collection |
| Stores conversational state only | Checkpoint stores messages, not financial data |

---

## Architectural Decisions

### Decision 1: Dual Memory Architecture

**Decision**: Implement two types of memory with distinct purposes aligned with ADR-001.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MEMORY ARCHITECTURE (ADR-001 Aligned)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │   SHORT-TERM MEMORY (STM)   │    │   LONG-TERM MEMORY (LTM)            │ │
│  │   (Conversation Buffer)     │    │   (Personalization - FUTURE)        │ │
│  ├─────────────────────────────┤    ├─────────────────────────────────────┤ │
│  │ • Thread-scoped             │    │ • User preferences & risk profile  │ │
│  │ • LangGraph Checkpointer    │    │ • Symbol tracking context          │ │
│  │ • Auto-summarization        │    │ • Investment style preferences     │ │
│  │ • Full message history      │    │ • NO financial facts (ADR rule)    │ │
│  │ • Archive over delete       │    │ • Audit trail for changes          │ │
│  └─────────────────────────────┘    └─────────────────────────────────────┘ │
│              │                                   │                          │
│              ▼                                   ▼                          │
│  ┌─────────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │  agent_checkpoints          │    │  user_preferences (FUTURE)          │ │
│  │  conversations              │    │  symbol_tracking (FUTURE)           │ │
│  │  (MongoDB Collections)      │    │  (MongoDB Collections)              │ │
│  └─────────────────────────────┘    └─────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │   SEMANTIC MEMORY (Future - memory_vectors)                          │   │
│  │   • Cross-session retrieval via embeddings                           │   │
│  │   • Query-specific recall (RAG over past conversations)              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Rationale:**
- Short-term memory enables coherent multi-turn conversations within a session
- Long-term memory (future) enables personalization without contaminating factual analysis
- Semantic memory (future) enables cross-session retrieval via explicit user request
- Clear separation prevents hallucination and maintains analytical integrity per ADR-001

---

### Decision 2: LangGraph MongoDBSaver Checkpointer

**Decision**: Use LangGraph's built-in `MongoDBSaver` instead of custom implementation.

**Pros:**
- Native integration with LangGraph's agent execution
- Auto-serialization of agent state (messages, tool calls, metadata)
- Built-in support for checkpoint versioning
- Maintained by LangGraph team

**Cons:**
- Creates separate collection from existing `chats` collection
- Less control over schema structure

**Trade-off Resolution:**
- Use `MongoDBSaver` for agent state persistence
- Continue using `ChatRepository` for UI chat history display
- Sync between collections is NOT required (different concerns)

---

### Decision 3: Thread ID Mapping Strategy

**Decision**: Map `session_id` directly to LangGraph's `thread_id`.

```
┌──────────────────────────────────────────────────────────────┐
│                    THREAD ID MAPPING                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   Application Layer           LangGraph Layer                 │
│   ─────────────────           ───────────────                 │
│                                                               │
│   session_id ─────────────────► thread_id                     │
│   (ObjectId string)             (configurable)                │
│                                                               │
│   Example:                                                    │
│   "507f1f77bcf86cd799439011" ──► thread_id                   │
│                                                               │
│   config = {                                                  │
│       "configurable": {                                       │
│           "thread_id": session_id                             │
│       }                                                       │
│   }                                                           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Rationale:**
- 1:1 mapping simplifies debugging and tracing
- Session already represents a conversation unit in the domain model
- No translation layer required

---

### Decision 4: Conversation Collection with Archive Strategy

**Decision**: Introduce new `conversations` collection with 1:1 mapping to `sessions`.

**Purpose:**
- Track conversation metadata (message count, token usage, summary)
- Enable memory-specific operations without polluting session entity
- Support conversation archival per ADR-001 (archive over delete)
- Maintain workspace isolation per ADR-001 Section 6.2

**Archive Strategy (per ADR-001 Section 6.2):**

| Status | Description | Behavior |
|--------|-------------|----------|
| `active` | Current working conversation | Full context available |
| `summarized` | Long conversation compressed | Summary in active context |
| `archived` | Session closed by user | Not in active context, query-retrievable |
| ~~`deleted`~~ | **Never used** | ADR: Archive over delete |

**Archive Lifecycle:**
```
┌──────────┐    auto-summarize    ┌─────────────┐    user closes    ┌──────────┐
│  active  │ ──────────────────►  │ summarized  │ ────────────────► │ archived │
└──────────┘    (token limit)     └─────────────┘     session       └──────────┘
                                                                         │
                                                                         │ explicit
                                                                         │ request
                                                                         ▼
                                                               ┌──────────────────┐
                                                               │ Query-retrievable │
                                                               │ via RAG (future)  │
                                                               └──────────────────┘
```

**Relationship:**

```
┌────────────┐     1:1      ┌────────────────┐
│  sessions  │◄────────────►│ conversations  │
└────────────┘              └────────────────┘
      │                            │
      │ 1:N                        │ 1:N (via thread_id)
      ▼                            ▼
┌────────────┐              ┌───────────────────┐
│   chats    │              │ agent_checkpoints │
│ (UI view)  │              │ (agent state)     │
└────────────┘              └───────────────────┘
```

---

### Decision 5: Memory Scope and Limits

**Decision**: Support full history with configurable summarization.

| Mode | Description | Configuration |
|------|-------------|---------------|
| **Full History** | Keep all messages in context | Default mode |
| **Window Buffer** | Keep last N messages | `memory.max_messages: 50` |
| **Summary Mode** | Summarize when context exceeds limit | `memory.summarize_threshold: 4000` |

**Summarization Strategy:**
```
When total_tokens > summarize_threshold:
  1. Keep last K messages (configurable, default 10)
  2. Summarize older messages using LLM
  3. Prepend summary to conversation context
  4. Store summary in conversations.summary field
```

---

## Data Model Design

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA MODEL OVERVIEW                              │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐                                                           
    │  users   │                                                           
    └────┬─────┘                                                           
         │ 1:N                                                             
         ▼                                                                 
    ┌──────────────┐                                                       
    │  workspaces  │                                                       
    └──────┬───────┘                                                       
           │ 1:N                                                           
           ▼                                                               
    ┌──────────────┐        1:1        ┌───────────────────┐               
    │   sessions   │◄─────────────────►│  conversations    │               
    └──────┬───────┘                   └─────────┬─────────┘               
           │                                     │                         
           │ 1:N                                 │ uses thread_id          
           ▼                                     ▼                         
    ┌──────────────┐               ┌─────────────────────────┐             
    │    chats     │               │   agent_checkpoints     │             
    │  (UI view)   │               │   (LangGraph state)     │             
    └──────────────┘               └─────────────────────────┘             
                                                                           
                                   ┌─────────────────────────┐             
                                   │   memory_vectors        │             
                                   │   (future: semantic)    │             
                                   └─────────────────────────┘             
```

---

### Collection Schemas

#### 1. `conversations` Collection (NEW)

**Purpose**: Track conversation metadata and memory state (per ADR-001 STM).

**ADR-001 Compliance Notes:**
- Stores conversation state only (assumptions, focused symbols, pinned intents)
- **Never stores**: market data, computed ratios, analytical conclusions
- Archive over delete: status transitions to "archived", never hard deleted
- Workspace isolation enforced via session_id → workspace relationship

```javascript
// conversations_schema.py equivalent
CONVERSATIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "created_at"],
    "properties": {
        "_id": {
            "bsonType": "objectId"
        },
        "session_id": {
            "bsonType": "objectId",
            "description": "Reference to sessions collection (1:1 mapping)"
        },
        "thread_id": {
            "bsonType": "string",
            "description": "LangGraph thread identifier (equals string of session_id)"
        },
        "status": {
            "bsonType": "string",
            "enum": ["active", "summarized", "archived"],  // NO "deleted" per ADR
            "description": "Conversation memory status"
        },
        "message_count": {
            "bsonType": "int",
            "description": "Total messages in conversation"
        },
        "total_tokens": {
            "bsonType": "int",
            "description": "Estimated token count for memory management"
        },
        "summary": {
            "bsonType": "string",
            "description": "LLM-generated summary when conversation is long"
        },
        "summary_up_to_message": {
            "bsonType": "int",
            "description": "Message index where summary ends"
        },
        "last_activity_at": {
            "bsonType": "date",
            "description": "Timestamp of last message"
        },
        "archived_at": {
            "bsonType": "date",
            "description": "Timestamp when archived (null if active/summarized)"
        },
        "archive_reason": {
            "bsonType": "string",
            "enum": ["user_closed", "inactivity", "workspace_archived"],
            "description": "Why conversation was archived"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Creation timestamp"
        },
        "updated_at": {
            "bsonType": "date",
            "description": "Last update timestamp"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional metadata (model used, tool calls count, etc.)"
        },
        // Conversational state per ADR-001 (NOT facts)
        "focused_symbols": {
            "bsonType": "array",
            "description": "Symbols currently in focus for this session"
        },
        "pinned_intents": {
            "bsonType": "array",
            "description": "User-pinned intents for context retention"
        },
        "session_assumptions": {
            "bsonType": "object",
            "description": "Assumptions made during this session"
        }
    }
}

CONVERSATIONS_INDEXES = [
    {
        "keys": [("session_id", 1)],
        "options": {"name": "idx_conversations_session", "unique": true}
    },
    {
        "keys": [("thread_id", 1)],
        "options": {"name": "idx_conversations_thread", "unique": true}
    },
    {
        "keys": [("status", 1), ("last_activity_at", -1)],
        "options": {"name": "idx_conversations_status_activity"}
    }
]
```

---

#### 2. `agent_checkpoints` Collection (NEW - LangGraph Managed)

**Purpose**: Store LangGraph checkpointer state (managed by MongoDBSaver).

**Note**: This schema is defined by LangGraph's MongoDBSaver. We document it for reference.

```javascript
// Schema managed by langgraph-checkpoint-mongodb
// Documented here for understanding

AGENT_CHECKPOINTS_SCHEMA = {
    "bsonType": "object",
    "properties": {
        "_id": {
            "bsonType": "objectId"
        },
        "thread_id": {
            "bsonType": "string",
            "description": "Conversation thread identifier"
        },
        "checkpoint_id": {
            "bsonType": "string",
            "description": "Unique checkpoint identifier"
        },
        "parent_checkpoint_id": {
            "bsonType": ["string", "null"],
            "description": "Parent checkpoint for versioning"
        },
        "checkpoint": {
            "bsonType": "object",
            "description": "Serialized agent state (messages, tool calls)"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Checkpoint metadata"
        },
        "created_at": {
            "bsonType": "date"
        }
    }
}

// Indexes created by MongoDBSaver
AGENT_CHECKPOINTS_INDEXES = [
    {"keys": [("thread_id", 1), ("checkpoint_id", 1)]},
    {"keys": [("thread_id", 1), ("created_at", -1)]}
]
```

---

#### 3. `memory_vectors` Collection (FUTURE - Phase 2A.2+)

**Purpose**: Store conversation embeddings for semantic search.

```javascript
// memory_vectors_schema.py equivalent (Future implementation)
MEMORY_VECTORS_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "content", "embedding", "created_at"],
    "properties": {
        "_id": {
            "bsonType": "objectId"
        },
        "session_id": {
            "bsonType": "objectId",
            "description": "Reference to source session"
        },
        "user_id": {
            "bsonType": "objectId",
            "description": "User who owns this memory"
        },
        "content": {
            "bsonType": "string",
            "description": "Text content that was embedded"
        },
        "content_type": {
            "bsonType": "string",
            "enum": ["user_query", "assistant_response", "summary", "insight"],
            "description": "Type of content"
        },
        "embedding": {
            "bsonType": "array",
            "items": {"bsonType": "double"},
            "description": "Vector embedding (1536 dimensions for OpenAI)"
        },
        "metadata": {
            "bsonType": "object",
            "description": "Additional context (symbols mentioned, topics, etc.)"
        },
        "created_at": {
            "bsonType": "date"
        }
    }
}

MEMORY_VECTORS_INDEXES = [
    {
        "keys": [("user_id", 1), ("created_at", -1)],
        "options": {"name": "idx_memory_vectors_user"}
    },
    {
        "keys": [("session_id", 1)],
        "options": {"name": "idx_memory_vectors_session"}
    }
    // Vector search index created separately via MongoDB Atlas
]
```

---

### Schema Summary Table

| Collection | Purpose | Managed By | New/Existing |
|------------|---------|------------|--------------|
| `sessions` | Workspace session metadata | Application | Existing |
| `chats` | UI chat message display | Application | Existing |
| `conversations` | Memory metadata and state | Application | **NEW** |
| `agent_checkpoints` | LangGraph agent state | MongoDBSaver | **NEW** |
| `memory_vectors` | Semantic search embeddings | Application | **FUTURE** |

---

## Sequence Diagrams

### Sequence 1: Query Processing with Memory

```
┌─────────┐  ┌─────────┐  ┌──────────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│  User   │  │   API   │  │  StockAssistantAgent │  │   MongoDBSaver    │  │  agent_checkpoints│
└────┬────┘  └────┬────┘  └──────────┬───────────┘  └─────────┬─────────┘  └────────┬─────────┘
     │            │                  │                        │                     │
     │ POST /api/chat               │                        │                     │
     │ {message, session_id}        │                        │                     │
     │ ──────────────────────────►  │                        │                     │
     │            │                  │                        │                     │
     │            │  process_query(  │                        │                     │
     │            │    query,        │                        │                     │
     │            │    session_id)   │                        │                     │
     │            │ ────────────────►│                        │                     │
     │            │                  │                        │                     │
     │            │                  │  Load checkpoint       │                     │
     │            │                  │  (thread_id=session_id)│                     │
     │            │                  │ ──────────────────────►│                     │
     │            │                  │                        │  find_one           │
     │            │                  │                        │ (thread_id)         │
     │            │                  │                        │ ──────────────────► │
     │            │                  │                        │                     │
     │            │                  │                        │◄─── checkpoint data │
     │            │                  │◄─────────────────────  │     (prev messages) │
     │            │                  │   Previous messages    │                     │
     │            │                  │                        │                     │
     │            │                  │  ┌─────────────────────┴─────────────────┐   │
     │            │                  │  │ Agent Executor invoked with:          │   │
     │            │                  │  │  - Previous messages from checkpoint  │   │
     │            │                  │  │  - New HumanMessage(query)            │   │
     │            │                  │  │  - config: {thread_id: session_id}    │   │
     │            │                  │  └─────────────────────┬─────────────────┘   │
     │            │                  │                        │                     │
     │            │                  │  [ReAct reasoning + tool execution]          │
     │            │                  │                        │                     │
     │            │                  │  Save checkpoint       │                     │
     │            │                  │  (new state)           │                     │
     │            │                  │ ──────────────────────►│                     │
     │            │                  │                        │  insert_one         │
     │            │                  │                        │ (new checkpoint)    │
     │            │                  │                        │ ──────────────────► │
     │            │                  │                        │                     │
     │            │◄─────────────────│                        │                     │
     │            │  AgentResponse   │                        │                     │
     │            │                  │                        │                     │
     │◄───────────│                  │                        │                     │
     │ JSON response                 │                        │                     │
     │                               │                        │                     │
```

---

### Sequence 2: Session Creation with Conversation Init

```
┌─────────┐  ┌─────────┐  ┌───────────────┐  ┌──────────────────┐  ┌───────────────┐
│  User   │  │   API   │  │ SessionService│  │ConversationService│  │    MongoDB    │
└────┬────┘  └────┬────┘  └───────┬───────┘  └────────┬─────────┘  └───────┬───────┘
     │            │               │                   │                    │
     │ POST /api/sessions        │                   │                    │
     │ {workspace_id, title}     │                   │                    │
     │ ─────────────────────────►│                   │                    │
     │            │               │                   │                    │
     │            │ create_session│                   │                    │
     │            │ ─────────────►│                   │                    │
     │            │               │                   │                    │
     │            │               │  Insert session   │                    │
     │            │               │ ─────────────────────────────────────► │
     │            │               │                   │                    │
     │            │               │◄────────────────  │   session_id       │
     │            │               │                   │                    │
     │            │               │ init_conversation │                    │
     │            │               │ (session_id)      │                    │
     │            │               │ ─────────────────►│                    │
     │            │               │                   │                    │
     │            │               │                   │  Insert conversation│
     │            │               │                   │  {session_id,       │
     │            │               │                   │   thread_id,        │
     │            │               │                   │   status: "active"} │
     │            │               │                   │ ──────────────────► │
     │            │               │                   │                    │
     │            │               │                   │◄─────conversation_id│
     │            │               │◄──────────────────│                    │
     │            │               │                   │                    │
     │            │◄──────────────│                   │                    │
     │            │  session_id   │                   │                    │
     │            │               │                   │                    │
     │◄───────────│               │                   │                    │
     │ {session_id, ...}          │                   │                    │
     │                            │                   │                    │
```

---

### Sequence 3: Memory Summarization Flow

```
┌─────────────────────┐  ┌───────────────────┐  ┌─────────────────┐  ┌─────────┐
│ StockAssistantAgent │  │ ConversationService│  │  SummaryLLM     │  │ MongoDB │
└──────────┬──────────┘  └─────────┬─────────┘  └────────┬────────┘  └────┬────┘
           │                       │                     │                │
           │ Check token count     │                     │                │
           │ before invoke         │                     │                │
           │ ─────────────────────►│                     │                │
           │                       │                     │                │
           │                       │ get_conversation    │                │
           │                       │ (session_id)        │                │
           │                       │ ────────────────────────────────────►│
           │                       │                     │                │
           │                       │◄───────────────────────── {total_tokens, │
           │                       │                     │     summary, ...} │
           │                       │                     │                │
           │◄──────────────────────│                     │                │
           │ total_tokens > threshold?                   │                │
           │                       │                     │                │
           │ ──── IF EXCEEDS ─────►│                     │                │
           │     summarize_conversation                  │                │
           │                       │                     │                │
           │                       │ Get old messages    │                │
           │                       │ (before cutoff)     │                │
           │                       │ ────────────────────────────────────►│
           │                       │                     │                │
           │                       │◄───────────────────────── messages[] │
           │                       │                     │                │
           │                       │ Generate summary    │                │
           │                       │ ───────────────────►│                │
           │                       │                     │                │
           │                       │                     │ [LLM summarizes
           │                       │                     │  conversation]
           │                       │                     │                │
           │                       │◄──────────────────  │                │
           │                       │   summary_text      │                │
           │                       │                     │                │
           │                       │ Update conversation │                │
           │                       │ {summary, status:   │                │
           │                       │  "summarized"}      │                │
           │                       │ ────────────────────────────────────►│
           │                       │                     │                │
           │◄──────────────────────│                     │                │
           │ Use summary in context│                     │                │
           │                       │                     │                │
```

---

### Sequence 4: Streaming Response with Memory

```
┌─────────┐  ┌──────────────┐  ┌──────────────────────┐  ┌───────────────┐
│  Client │  │ Socket.IO    │  │  StockAssistantAgent │  │ MongoDBSaver  │
└────┬────┘  └──────┬───────┘  └──────────┬───────────┘  └───────┬───────┘
     │              │                     │                      │
     │ emit('chat_message',              │                      │
     │  {message, session_id})           │                      │
     │ ────────────────────────►         │                      │
     │              │                     │                      │
     │              │ process_query_streaming                    │
     │              │ (query, session_id) │                      │
     │              │ ───────────────────►│                      │
     │              │                     │                      │
     │              │                     │ Load checkpoint      │
     │              │                     │ ────────────────────►│
     │              │                     │                      │
     │              │                     │◄──── prev messages   │
     │              │                     │                      │
     │              │                     │ ┌─────────────────┐  │
     │              │                     │ │ astream_events  │  │
     │              │                     │ │ with config:    │  │
     │              │                     │ │ {thread_id}     │  │
     │              │                     │ └─────────────────┘  │
     │              │                     │                      │
     │              │◄────────────────────│                      │
     │              │   yield chunk_1     │                      │
     │◄─────────────│                     │                      │
     │ emit('chat_chunk', chunk_1)        │                      │
     │              │                     │                      │
     │              │◄────────────────────│                      │
     │              │   yield chunk_2     │                      │
     │◄─────────────│                     │                      │
     │ emit('chat_chunk', chunk_2)        │                      │
     │              │                     │                      │
     │              │  ... more chunks    │                      │
     │              │                     │                      │
     │              │                     │ Save checkpoint      │
     │              │                     │ (final state)        │
     │              │                     │ ────────────────────►│
     │              │                     │                      │
     │◄─────────────│                     │                      │
     │ emit('chat_stream_end')            │                      │
     │              │                     │                      │
```

---

## API Contract Changes

### REST API Changes

#### POST /api/chat

**Current Contract:**
```json
{
    "message": "string (required)",
    "provider": "string (optional, default: 'openai')",
    "stream": "boolean (optional, default: false)"
}
```

**Updated Contract:**
```json
{
    "message": "string (required)",
    "provider": "string (optional, default: 'openai')",
    "stream": "boolean (optional, default: false)",
    "session_id": "string (optional, ObjectId string)"
}
```

**Behavior:**
- If `session_id` is provided: Load conversation history, maintain context
- If `session_id` is omitted: Stateless single-turn (backward compatible)

---

### Socket.IO Changes

#### Event: `chat_message`

**Current Payload:**
```json
{
    "message": "string"
}
```

**Updated Payload:**
```json
{
    "message": "string",
    "session_id": "string (optional)"
}
```

---

### Internal Method Signatures

#### StockAssistantAgent

```python
# Before
def process_query(self, query: str, *, provider: Optional[str] = None) -> str:

# After
def process_query(
    self, 
    query: str, 
    *, 
    provider: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:

# Streaming - Before
def process_query_streaming(self, query: str, *, provider: Optional[str] = None) -> Generator[str, None, None]:

# Streaming - After
def process_query_streaming(
    self, 
    query: str, 
    *, 
    provider: Optional[str] = None,
    session_id: Optional[str] = None
) -> Generator[str, None, None]:

# Structured - Before
def process_query_structured(self, query: str, *, provider: Optional[str] = None) -> AgentResponse:

# Structured - After
def process_query_structured(
    self, 
    query: str, 
    *, 
    provider: Optional[str] = None,
    session_id: Optional[str] = None
) -> AgentResponse:
```

---

## Configuration Requirements

### config.yaml Additions

```yaml
# Add to existing langchain section
langchain:
  # ... existing tracing config ...
  
  memory:
    # Checkpointer configuration
    checkpointer:
      type: mongodb  # Options: mongodb, memory (for testing)
      collection_name: agent_checkpoints
    
    # Memory scope settings
    max_messages: null  # null = unlimited, or integer for window buffer
    summarize_threshold: 4000  # Token count to trigger summarization
    summarize_keep_recent: 10  # Messages to keep after summarization
    
    # TTL settings
    checkpoint_ttl_days: 30  # Auto-expire old checkpoints
    
    # Feature flags
    enabled: true
    auto_summarize: true
```

---

### Environment Variables

```bash
# Optional overrides
LANGCHAIN_MEMORY_ENABLED=true
LANGCHAIN_MEMORY_CHECKPOINTER_TYPE=mongodb
LANGCHAIN_MEMORY_SUMMARIZE_THRESHOLD=4000
```

---

## Implementation Roadmap

### Phase 2A.1 Implementation Tasks

| # | Task | Effort | Dependencies |
|---|------|--------|--------------|
| 1 | Add `langgraph-checkpoint-mongodb` to requirements.txt | XS | None |
| 2 | Create `conversations_schema.py` | S | None |
| 3 | Register conversations collection in SchemaManager | S | Task 2 |
| 4 | Create `ConversationRepository` | M | Task 2, 3 |
| 5 | Create `ConversationService` | M | Task 4 |
| 6 | Add memory config section to config.yaml | S | None |
| 7 | Modify `StockAssistantAgent.__init__()` to init checkpointer | M | Task 1, 6 |
| 8 | Modify `_build_agent_executor()` to pass checkpointer | M | Task 7 |
| 9 | Update `process_query()` with session_id parameter | M | Task 8 |
| 10 | Update `process_query_streaming()` with session_id | M | Task 8 |
| 11 | Update `process_query_structured()` with session_id | S | Task 8 |
| 12 | Update REST API routes for session_id | M | Task 9-11 |
| 13 | Update Socket.IO handlers for session_id | M | Task 9-11 |
| 14 | Implement memory summarization logic | L | Task 5, 8 |
| 15 | Run database migration | S | Task 3 |
| 16 | Unit tests for memory components | L | Tasks 4-11 |
| 17 | Integration tests for multi-turn conversation | L | Task 16 |

**Total Estimated Effort**: ~15-20 story points

---

## Testing Strategy

### Unit Tests

| Component | Test Cases |
|-----------|------------|
| `ConversationRepository` | CRUD operations, thread_id lookup, status updates |
| `ConversationService` | Init conversation, get/update, summarization trigger |
| `StockAssistantAgent` | Checkpointer initialization, session_id flow |

### Integration Tests

| Scenario | Description |
|----------|-------------|
| Multi-turn conversation | User asks follow-up, agent recalls previous |
| Session restart | API restart, conversation resumes correctly |
| Summarization trigger | Long conversation triggers summarization |
| Backward compatibility | Request without session_id works |

### Performance Tests

| Metric | Target | Test Method |
|--------|--------|-------------|
| Memory load latency | <100ms | Load checkpoint benchmark |
| Memory save latency | <50ms | Save checkpoint benchmark |
| Summarization latency | <2s | Trigger summarization test |

---

## Appendix

### A. LangGraph Checkpointer Reference

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

# Initialization
checkpointer = MongoDBSaver(
    connection_string="mongodb://...",
    db_name="stock_assistant",
    collection_name="agent_checkpoints"
)

# Usage with agent
agent_executor = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=checkpointer
)

# Invoke with thread_id
result = agent_executor.invoke(
    {"messages": [HumanMessage(content="query")]},
    config={"configurable": {"thread_id": session_id}}
)
```

### B. Related Documents

- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) - Full enhancement roadmap
- [LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md](./LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md) - Current architecture
- [LANGCHAIN_AGENT_HOWTO.md](./LANGCHAIN_AGENT_HOWTO.md) - Implementation patterns
- [backend-python.instructions.md](../../.github/instructions/backend-python.instructions.md) - Coding conventions

### C. Diagrams Source

- Data Model: `Langchain_agent_data_model.xml` (draw.io)
- Architecture: `Langchain_agent_high_level_design.xml` (draw.io)

---

> **Document Status**: Technical Design Complete  
> **Next Step**: Implementation Phase  
> **Review Required**: Architecture Team

### D. Memory technical requirements (backup)

> **Architectural Context**: This section details requirements for the conversation memory system as designed in [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md)  
> **Governing ADR**: [ADR-001 — Layered LLM Architecture](./AGENT_ARCHITECTURE_DECISION_RECORDS.md)

#### MEM-1: Data Model Requirements

##### MEM-1.1 Conversations Collection

| ID | Priority | Requirement | Data Type | Description |
|----|----------|-------------|-----------|-------------|
| MEM-1.1.1 | **P0** | Each conversation SHALL have unique `_id` | ObjectId | Primary key. Auto-generated by MongoDB. |
| MEM-1.1.2 | **P0** | Each conversation SHALL reference `session_id` | ObjectId | FK to `sessions` collection. 1:1 relationship. |
| MEM-1.1.3 | **P0** | Each conversation SHALL have `thread_id` | String | LangGraph thread identifier. Used by checkpointer for state lookup. |
| MEM-1.1.4 | **P0** | `session_id` and `thread_id` SHALL be unique indexes | - | Create compound unique index `{session_id: 1, thread_id: 1}` to prevent duplicates. |
| MEM-1.1.5 | **P0** | Each conversation SHALL track `status` | Enum | Values: `active`, `summarized`, `archived`. Use string enum in Pydantic model. |
| MEM-1.1.6 | **P0** | Each conversation SHALL track `message_count` | Integer | Auto-incremented via `$inc`. Start at 0, increment on each user+assistant exchange. |
| MEM-1.1.7 | **P0** | Each conversation SHALL track `total_tokens` | Integer | Cumulative prompt+completion tokens. Use LangChain callback handler to track. |
| MEM-1.1.8 | **P1** | Each conversation SHALL track `summary` | String | Optional. Populated when summarization triggers. Max 500 chars. |
| MEM-1.1.9 | **P1** | Each conversation SHALL track `summary_up_to_message` | Integer | Message index at which summary was generated. Used for incremental summarization. |
| MEM-1.1.10 | **P0** | Each conversation SHALL track `last_activity_at` | DateTime | UTC timestamp. Updated on each message via `$set` with `datetime.utcnow()`. |
| MEM-1.1.11 | **P0** | Each conversation SHALL track `created_at` and `updated_at` | DateTime | Audit fields. `created_at` set once; `updated_at` on every write. |
| MEM-1.1.12 | **P0** | Each conversation SHALL reference `workspace_id` | ObjectId | **ADR Compliance**: Sessions are workspace-bound. Required field, not nullable. |
| MEM-1.1.13 | **P0** | Each conversation SHALL reference `user_id` | ObjectId | FK to `users` collection. Required for authorization checks. |
| MEM-1.1.14 | **P1** | Each conversation MAY store `assumptions[]` | Array[String] | Session-scoped assumptions. Example: `["Risk tolerance: moderate"]`. |
| MEM-1.1.15 | **P1** | Each conversation MAY store `pinned_intent` | String | User's stated focus. Example: `"Compare AAPL vs MSFT"`. |
| MEM-1.1.16 | **P1** | Each conversation MAY store `focused_symbols[]` | Array[String] | Symbol names only (NO prices). Example: `["AAPL", "MSFT"]`. |
| MEM-1.1.17 | **P1** | Archived conversations SHALL track `archived_at` | DateTime | Timestamp when archived. Null for active/summarized conversations. |

##### MEM-1.2 Agent Checkpoints Collection

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-1.2.1 | **P0** | Collection SHALL be named `agent_checkpoints` | Configurable via `config.langchain.memory.checkpointer.collection`. |
| MEM-1.2.2 | **P0** | Schema SHALL be managed by LangGraph `MongoDBSaver` | Do NOT define custom schema—LangGraph owns this collection structure. |
| MEM-1.2.3 | **P0** | Checkpoints SHALL be indexed by `thread_id` | Primary lookup key. Index created automatically by MongoDBSaver. |
| MEM-1.2.4 | **P1** | Checkpoints SHALL support TTL-based expiration | Default 30 days. Configure via `ttl_days` in config. MongoDB TTL index on `created_at`. |
| MEM-1.2.5 | **P0** | Checkpoint data SHALL include full message history | LangGraph stores `MessagesState` with all `HumanMessage`/`AIMessage` instances. |
| MEM-1.2.6 | **P0** | Checkpoint data SHALL include agent state metadata | Includes tool call history, intermediate states, graph node positions. |

##### MEM-1.3 Memory Vectors Collection (Future)

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-1.3.1 | **P2** | Collection SHALL be named `memory_vectors` | Future Phase 2A.2+. Define schema but do not implement yet. |
| MEM-1.3.2 | **P2** | Each vector SHALL include 1536-dimension embedding | Use `text-embedding-3-small` model. Store as `embedding: Float[1536]`. |
| MEM-1.3.3 | **P2** | Vectors SHALL be indexed for cosine similarity search | Requires MongoDB Atlas Vector Search. Create `vectorSearchIndex` on deployment. |
| MEM-1.3.4 | **P2** | Vectors SHALL reference `user_id`, `session_id`, `conversation_id` | Enable cross-reference queries. All fields indexed. |
| MEM-1.3.5 | **P2** | Vectors SHALL include content type classification | Enum: `user_query`, `assistant_response`, `summary`, `insight`, `preference`. |

---

#### MEM-2: API Requirements

##### MEM-2.1 Session-Aware Endpoints

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-2.1.1 | **P0** | `POST /api/chat` SHALL accept optional `session_id` parameter | Add to request body: `{"message": "...", "session_id": "..."}`. Type: `Optional[str]`. |
| MEM-2.1.2 | **P0** | When `session_id` provided, agent SHALL load conversation history | Pass `session_id` to `StockAgentGraph.run()`. Checkpointer auto-loads state. |
| MEM-2.1.3 | **P0** | When `session_id` omitted, agent SHALL operate statelessly | Generate ephemeral UUID for single-turn. Do NOT create `conversations` record. |
| MEM-2.1.4 | **P0** | Invalid `session_id` format SHALL return 400 Bad Request | Validate UUID format before processing. Return `{"error": "Invalid session_id format"}`. |
| MEM-2.1.5 | **P0** | Unauthorized `session_id` access SHALL return 403 Forbidden | Check `conversation.user_id == request.user_id`. Return 403 if mismatch. |
| MEM-2.1.6 | **P0** | Non-existent `session_id` SHALL return 404 Not Found | Query `conversations` collection first. Return 404 if not found. |

##### MEM-2.2 WebSocket Memory Integration

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-2.2.1 | **P0** | `chat_message` event SHALL accept optional `session_id` | Add to event payload: `{message: "...", session_id: "..."}`. |
| MEM-2.2.2 | **P0** | Streaming responses SHALL maintain memory context | Pass `session_id` through entire streaming pipeline. Context must persist across chunks. |
| MEM-2.2.3 | **P0** | Memory state SHALL be persisted after each complete response | Call `checkpointer.put()` after stream completes, not during. Ensures atomic persistence. |

---

#### MEM-3: Behavioral Requirements

##### MEM-3.1 Context Loading

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.1.1 | **P0** | Agent SHALL load conversation history before processing query | Call `graph.get_state(config)` to retrieve existing checkpoint. Pass to first node. |
| MEM-3.1.2 | **P0** | Agent SHALL include history in LLM context via LangGraph checkpointer | History auto-injected by `MessagesState`. Verify `state["messages"]` contains history. |
| MEM-3.1.3 | **P1** | If summary exists, agent SHALL prepend summary to context | Inject `SystemMessage(content=f"Context: {summary}")` at messages[0]. Check `state.get("summary")`. |
| MEM-3.1.4 | **P0** | Agent SHALL handle missing/corrupted checkpoints gracefully | Catch `CheckpointNotFound` exception. Start fresh with empty state. Log warning. |

##### MEM-3.2 Context Persistence

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.2.1 | **P0** | Agent SHALL persist state after each query completion | Automatic via `MongoDBSaver`. Verify by checking `agent_checkpoints` collection. |
| MEM-3.2.2 | **P0** | Persistence SHALL include user message, agent response, tool calls | All stored in `MessagesState`. Tool calls stored as `AIMessage.tool_calls[]`. |
| MEM-3.2.3 | **P0** | Persistence SHALL be atomic (all-or-nothing) | MongoDBSaver handles atomicity. On failure, no partial state saved. |
| MEM-3.2.4 | **P0** | Failed persistence SHALL NOT affect response delivery | Catch persistence errors in finally block. Log error but return response to user. |
| MEM-3.2.5 | **P0** | `conversations` metadata SHALL be updated after each exchange | Call `ConversationRepository.update_activity()` with `message_count`, `total_tokens`, `updated_at`. |

##### MEM-3.3 Summarization Trigger

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.3.1 | **P1** | Summarization SHALL trigger when `total_tokens > summarize_threshold` | Check after each response. Default threshold: 4000 tokens. |
| MEM-3.3.2 | **P1** | Default `summarize_threshold` SHALL be 4000 tokens | Configurable via `config.langchain.memory.summarization.threshold_tokens`. |
| MEM-3.3.3 | **P1** | Summarization SHALL preserve last K messages (default K=10) | After summary, trim `state["messages"]` to last K. Configurable via `keep_recent_messages`. |
| MEM-3.3.4 | **P1** | Summary generation SHALL use dedicated LLM call | Call `llm.invoke(summarization_prompt)`. Use same model as agent or cheaper model. |
| MEM-3.3.5 | **P1** | Post-summarization, `conversations.status` SHALL be `summarized` | Update via `ConversationRepository.set_status("summarized")`. |

##### MEM-3.4 Memory Archival (per ADR-001)

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.4.1 | **P1** | Inactive conversations SHALL be archived after configurable period | Default: 30 days inactive. Cron job or background task to check `last_activity_at`. |
| MEM-3.4.2 | **P0** | Archived conversations SHALL be read-only | **ADR Compliance**: Reject updates with `ConversationArchivedError`. Only allow read queries. |
| MEM-3.4.3 | **P1** | Checkpoint TTL SHALL default to 30 days | Configure via `config.langchain.memory.checkpointer.ttl_days`. |
| MEM-3.4.4 | **P1** | Expired checkpoints SHALL be automatically purged by MongoDB TTL index | Create TTL index on `created_at` field. MongoDB handles expiration automatically. |
| MEM-3.4.5 | **P0** | The system SHALL NOT hard-delete conversations | **ADR Compliance**: Implement `archive()` method only. No `delete()` method in repository. |

---

#### MEM-4: Configuration Requirements

##### MEM-4.1 Memory Configuration Schema

```yaml
# config.yaml memory section
langchain:
  memory:
    enabled: true
    checkpointer:
      type: "mongodb"
      collection: "agent_checkpoints"
      ttl_days: 30
    summarization:
      enabled: true
      threshold_tokens: 4000
      keep_recent_messages: 10
    conversation:
      collection: "conversations"
      max_messages: null  # null = unlimited
      archive_after_days: 30  # auto-archive inactive conversations
```

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-4.1.1 | **P0** | Memory feature SHALL be toggleable via `memory.enabled` | When `false`, agent operates statelessly. No checkpointer initialized. |
| MEM-4.1.2 | **P0** | Checkpointer collection name SHALL be configurable | Default: `agent_checkpoints`. Override via `checkpointer.collection`. |
| MEM-4.1.3 | **P1** | Checkpoint TTL SHALL be configurable (days) | Default: 30 days. Set via `checkpointer.ttl_days`. |
| MEM-4.1.4 | **P1** | Summarization threshold SHALL be configurable (tokens) | Default: 4000. Set via `summarization.threshold_tokens`. |
| MEM-4.1.5 | **P1** | Recent message retention count SHALL be configurable | Default: 10. Set via `summarization.keep_recent_messages`. |
| MEM-4.1.6 | **P0** | All memory settings SHALL have sensible defaults | Defaults must allow system to run without explicit config. |
| MEM-4.1.7 | **P1** | Archive period SHALL be configurable | Default: 30 days. Set via `conversation.archive_after_days`. |

---