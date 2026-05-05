# Agent Memory Technical Design

> **Document Version**: 1.4  
> **Last Updated**: March 31, 2026  
> **Phase**: 2A.1 - Short-Term Conversation Memory  
> **Status**: STM hierarchy implemented; summarization trigger and Socket.IO parity remain follow-up work  
> **Governing ADR**: [ADR-001 — Layered LLM Architecture](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md)

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

Implement persistent conversation memory for the Stock Assistant LangChain agent, enabling multi-turn conversations where the agent recalls previous exchanges within a conversation thread while allowing a single session to own multiple conversations.

### Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| `MemoryConfig` frozen dataclass | ✅ Done | `src/utils/memory_config.py` |
| `ContentValidator` compliance scanner | ✅ Done | `src/utils/memory_config.py` (utility available; pipeline enforcement is incremental) |
| `MongoDBSaver` checkpointer factory | ✅ Done | `src/core/langgraph_bootstrap.py::create_checkpointer()` |
| Canonical STM parameter wiring (`conversation_id`) | ✅ Done | `src/core/stock_assistant_agent.py` (`process_query`, `process_query_streaming`, `process_query_structured`) |
| Agent checkpointer wiring | ✅ Done | `src/web/api_server.py::APIServer.__init__()` |
| `ConversationRepository` | ✅ Done | `src/data/repositories/conversation_repository.py` |
| `ConversationService` | ✅ Done | `src/services/conversation_service.py` |
| REST API `conversation_id` support with deprecated `session_id` alias normalization | ✅ Done | `src/web/routes/ai_chat_routes.py` |
| Socket.IO `conversation_id` passthrough support | ✅ Done | `src/web/sockets/chat_events.py` |
| Conversation-scoped `conversation_id -> thread_id` contract | ✅ Done | Agent + chat service + conversation repository |
| Session-owned multi-conversation hierarchy | ✅ Done | Routes + services + repositories |
| Management APIs for workspace/session/conversation lifecycle | ✅ Done | `src/web/routes/*_routes.py`, `src/services/*_service.py` |
| Runtime reconciliation service + operator CLI | ✅ Done | `src/services/runtime_reconciliation_service.py`, `scripts/reconcile_stm_runtime.py` |
| Legacy checkpoint migration CLI | ✅ Done | `src/data/migration/legacy_checkpoint_migration.py`, `scripts/migrate_legacy_threads.py` |
| Automated summarization trigger pipeline | ⏳ Not yet wired | Config + schema exist; no runtime trigger currently invokes summarization |
| Socket.IO parity with REST archive guard and metadata sync | ⏳ Not yet wired | `chat_events.py` still calls agent directly |
| YAML config `langchain.memory` section | ✅ Done | `config/config.yaml` |
| `create_react_agent` → `create_agent` migration | ✅ Done | `src/core/stock_assistant_agent.py` |
| `memory_vectors` collection (LTM) | ⏳ Future | Phase 2A.2+ |
| Cross-session memory retrieval | ⏳ Future | Phase 2A.2+ |
| User preference learning | ⏳ Future | Phase 2A.2+ |

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Dual Memory Strategy** | Short-term (checkpointer) + Long-term (vector store for personalization) |
| **Memory Never Stores Facts** | Financial data stays in RAG/Tools layer per ADR-001 |
| **Session Is Business Context** | Session stores reusable assumptions, intent, and symbol focus across conversations |
| **Conversation Owns STM Thread** | Each conversation maps 1:1 to the LangGraph `thread_id` used for checkpoint recovery |
| **Backward Compatibility** | APIs continue to support stateless operation when `conversation_id` is omitted |
| **Separation of Concerns** | LangGraph handles agent state; ChatRepository handles UI queries |
| **Native Integration** | Use LangGraph's built-in MongoDBSaver for checkpoints |
| **Archive Over Delete** | Conversations are archived for historical reference, not purged |

### Scope

**In Scope:**
- Short-term conversation memory via LangGraph checkpointer
- New MongoDB collections for agent memory
- API changes to support `conversation_id`, with a deprecated REST-only `session_id` alias during the migration window
- Explicit session -> conversation -> thread hierarchy
- Summarization schema/config groundwork for long conversations
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
| Session-owned conversations | `conversations` collection with `session_id` FK plus distinct `conversation_id` and `thread_id` |
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
│  │ • Summary metadata support  │    │ • Investment style preferences     │ │
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
- Short-term memory enables coherent multi-turn conversations within a single conversation thread
- Session-level context can be propagated across multiple sibling conversations without merging their STM buffers
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

**Implementation Notes (post-implementation):**
- Config path for connection string: `config["database"]["mongodb"]["connection_string"]`
- Collection name configurable via `MemoryConfig.checkpoint_collection` (default: `agent_checkpoints`)
- Checkpointer factory: `langgraph_bootstrap.py::create_checkpointer(config)`
- Wired into agent via `APIServer.__init__()` → `StockAssistantAgent(checkpointer=checkpointer)`
- Uses `MongoClient` instance (not raw connection string) as required by `MongoDBSaver` API

---

### Decision 3: Thread ID Mapping Strategy

**Decision**: Map `conversation_id` to LangGraph's `thread_id`, with session identity retained separately for hierarchy validation and reusable context.

```
┌──────────────────────────────────────────────────────────────┐
│                    THREAD ID MAPPING                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   Application Layer           LangGraph Layer                 │
│   ─────────────────           ───────────────                 │
│                                                               │
│ conversation_id ──────────────► thread_id                     │
│   (conversation key)           (configurable)                 │
│                                                               │
│   Example:                                                    │
│   "123e4567-e89b-42d3-a456-426614174000" ──► thread_id │
│                                                               │
│   config = {                                                  │
│       "configurable": {                                       │
│           "thread_id": conversation_id                        │
│       }                                                       │
│   }                                                           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Rationale:**
- 1:1 mapping simplifies debugging and tracing
- Session no longer doubles as the STM unit in the domain model
- Conversation identity becomes the canonical checkpoint lookup key
- Session context remains reusable across conversations without sharing thread state

---

### Decision 4: Conversation Collection with Archive Strategy

**Decision**: Introduce a `conversations` collection with a 1:N relationship from `sessions`, while preserving a 1:1 relationship between `conversation_id` and `thread_id`.

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
| `archived` | Conversation closed by user or policy | Not in active context, query-retrievable |
| ~~`deleted`~~ | **Never used** | ADR: Archive over delete |

**Archive Lifecycle:**
```
┌──────────┐    auto-summarize    ┌─────────────┐    user closes    ┌──────────┐
│  active  │ ──────────────────►  │ summarized  │ ────────────────► │ archived │
└──────────┘    (token limit)     └─────────────┘   conversation    └──────────┘
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
┌────────────┐     1:N      ┌────────────────┐     1:1      ┌───────────────────┐
│  sessions  │─────────────►│ conversations  │─────────────►│ agent_checkpoints │
└────────────┘              └────────────────┘              │ (agent state)     │
    │                            │                        └───────────────────┘
    │ 1:N                        │
    ▼                            ▼
┌────────────┐              ┌───────────────────┐
│   chats    │              │ conversation meta │
│ (UI view)  │              │ + summaries       │
└────────────┘              └───────────────────┘
```

---

### Decision 5: Memory Scope and Limits

**Decision**: Support full history with configurable summarization thresholds and schema support. The automatic summarization trigger remains a planned follow-up, not an active runtime behavior.

| Mode | Description | Configuration |
|------|-------------|---------------|
| **Full History** | Keep all messages in context | Default mode |
| **Window Buffer** | Keep last N messages | `memory.max_messages: 50` |
| **Summary Mode** | Planned runtime behavior once summarization is wired | `memory.summarize_threshold: 4000` |

**Summarization Strategy:**
```
When total_tokens > summarize_threshold:
  1. Keep last K messages (configurable, default 10)
  2. Summarize older messages using LLM
  3. Prepend summary to conversation context
  4. Store summary in conversations.summary field
```

**Current Runtime Note:** The configuration, schema fields, and repository helpers for summaries exist today, but the chat execution path does not yet invoke this workflow automatically.

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
        ┌──────────────┐        1:N        ┌───────────────────┐               
        │   sessions   │──────────────────►│  conversations    │               
        └──────┬───────┘                   └─────────┬─────────┘               
            │                                     │ 1:1                     
            │ 1:N                                 ▼                         
            ▼                           ┌─────────────────────────┐         
        ┌──────────────┐                   │   agent_checkpoints     │         
        │    chats     │                   │   (LangGraph state)     │         
        │  (UI view)   │                   └─────────────────────────┘         
        └──────────────┘                                                        
                                                                           
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
- Stores conversation state only (summary, message counters, conversation-level refinements)
- **Never stores**: market data, computed ratios, analytical conclusions
- Archive over delete: status transitions to "archived", never hard deleted
- Workspace isolation enforced via explicit `workspace_id` and validated session relationship

```javascript
// conversations_schema.py equivalent
CONVERSATIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["conversation_id", "session_id", "workspace_id", "created_at"],
    "properties": {
        "_id": {
            "bsonType": "objectId"
        },
        "conversation_id": {
            "bsonType": "string",
            "pattern": "^[A-Za-z0-9_-]{8,128}$",
            "description": "Canonical conversation identifier exposed to clients and services"
        },
        "session_id": {
            "bsonType": "string",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            "description": "Parent session identifier that groups related conversations under shared business context"
        },
        "workspace_id": {
            "bsonType": "string",
            "description": "Parent workspace identifier for hierarchy validation and isolation"
        },
        "thread_id": {
            "bsonType": "string",
            "description": "LangGraph thread identifier (1:1 with conversation_id; may equal conversation_id)"
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
        // Conversation-specific refinements per ADR-001 (NOT facts)
        "focused_symbols": {
            "bsonType": "array",
            "description": "Symbols currently in focus for this conversation thread"
        },
        "conversation_intent": {
            "bsonType": "string",
            "description": "Conversation-specific refinement of the parent session intent"
        },
        "context_overrides": {
            "bsonType": "object",
            "description": "Conversation-level overrides applied on top of inherited session context"
        }
    }
}

CONVERSATIONS_INDEXES = [
    {
        "keys": [("conversation_id", 1)],
        "options": {"name": "idx_conversations_conversation_id", "unique": true}
    },
    {
        "keys": [("session_id", 1)],
        "options": {"name": "idx_conversations_session"}
    },
    {
        "keys": [("workspace_id", 1), ("session_id", 1), ("status", 1)],
        "options": {"name": "idx_conversations_hierarchy_status"}
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
            "bsonType": "string",
            "description": "Reference to source session (UUID v4)"
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
┌─────────┐  ┌────────────┐  ┌─────────────────┐  ┌──────────────────────┐  ┌───────────────┐
│  User   │  │ Chat Route  │  │   ChatService    │  │  StockAssistantAgent │  │ MongoDBSaver  │
└────┬────┘  └─────┬──────┘  └────────┬────────┘  └──────────┬───────────┘  └───────┬───────┘
    │             │                  │                        │                      │
    │ POST /api/chat                  │                        │                      │
    │ {message, conversation_id?}     │                        │                      │
    │ ───────────────────────────────► │                        │                      │
    │             │ process_chat_query │                        │                      │
    │             │ ─────────────────► │                        │                      │
    │             │                  │ ensure_conversation_exists()                    │
    │             │                  │ (non-blocking, only when conversation_id set)   │
    │             │                  │                        │                      │
    │             │                  │ process_query(query, conversation_id)          │
    │             │                  │ ──────────────────────► │                      │
    │             │                  │                        │ invoke(...,          │
    │             │                  │                        │ config={"configurable":
    │             │                  │                        │        {"thread_id": conversation_id}})
    │             │                  │                        │ ────────────────────►│
    │             │                  │                        │                      │
    │             │                  │                        │◄──── checkpoint/state│
    │             │                  │◄────────────────────── │                      │
    │             │                  │ record_message_metadata()                      │
    │             │                  │ (non-blocking; REST path only)                │
    │             │◄───────────────── │                        │                      │
    │◄────────────│ JSON response     │                        │                      │
```

---

### Sequence 2: Session Creation and Explicit Conversation Creation

```
┌─────────┐  ┌─────────┐  ┌───────────────┐  ┌──────────────────┐  ┌───────────────┐
│  User   │  │   API   │  │ SessionService│  │ConversationService│  │    MongoDB    │
└────┬────┘  └────┬────┘  └───────┬───────┘  └────────┬─────────┘  └───────┬───────┘
     │            │               │                   │                    │
    │ POST /api/workspaces/{workspace_id}/sessions  │                    │
    │ {title} + X-User-ID                           │                    │
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
    │ POST /api/sessions/{id}/conversations          │                    │
    │ {} + X-User-ID                                 │                    │
    │ ─────────────────────────►│                   │                    │
    │            │               │ validate_session  │                    │
    │            │               │ + workspace       │                    │
     │            │               │ ─────────────────►│                    │
     │            │               │                   │                    │
     │            │               │                   │  Insert conversation│
    │            │               │                   │  {conversation_id,  │
    │            │               │                   │   session_id,       │
    │            │               │                   │   workspace_id,     │
    │            │               │                   │   thread_id,        │
     │            │               │                   │   status: "active"} │
     │            │               │                   │ ──────────────────► │
     │            │               │                   │                    │
     │            │               │                   │◄─────conversation_id│
     │            │               │◄──────────────────│                    │
     │            │               │                   │                    │
    │            │◄──────────────│                   │                    │
    │            │  conversation_id                  │                    │
     │            │               │                   │                    │
     │◄───────────│               │                   │                    │
    │ {session_id, conversation_id, ...}            │                    │
     │                            │                   │                    │
```

---

### Sequence 3: Memory Summarization Flow

> **Status**: Planned follow-up. The current runtime exposes summary fields and thresholds but does not yet trigger automated summarization from the chat execution path.

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
           │                       │ (conversation_id)   │                │
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
    │  {message, provider?,             │                      │
    │   conversation_id?})              │                      │
     │ ────────────────────────►         │                      │
     │              │                     │                      │
    │              │ process_query(message, conversation_id)   │
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

> **Current Limitation**: The Socket.IO path validates UUID format and preserves `conversation_id`, but it still bypasses `ChatService`, so it does not yet enforce archived-conversation rejection or REST-style metadata recording.

---

## API Contract Changes

### REST API Changes

#### POST /api/chat

**Current Contract:**
```json
{
    "message": "string (required)",
    "provider": "string (optional, default: 'openai')",
    "stream": "boolean (optional, default: false)",
    "conversation_id": "string (optional, UUID v4)"
}
```

**Compatibility Note:** The REST route still accepts a deprecated `session_id` alias and normalizes it into `conversation_id` before UUID v4 validation. This alias is not the canonical contract and is not supported by the Socket.IO handler.

**Behavior:**
- If `conversation_id` is provided: `ChatService` validates that the conversation is not archived, ensures a metadata record exists, and the agent binds `conversation_id` directly as LangGraph `thread_id`.
- If `conversation_id` is omitted: Process as stateless single-turn.
- If conversation metadata is missing: the REST path may auto-create an `unlinked` conversation record non-blocking; canonical hierarchy creation still happens through the management APIs.
- If the conversation is archived: the REST path returns HTTP `409` with `code=CONVERSATION_ARCHIVED`.

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
    "provider": "string (optional)",
    "conversation_id": "string (optional, UUID v4)"
}
```

**Current Behavior:**
- Validates `conversation_id` format and passes it directly into `agent.process_query(...)`.
- Echoes `conversation_id` back in the response when supplied.
- Does not currently use `ChatService`, so archive guards, metadata sync, and conversation auto-create semantics are REST-only today.

---

### Internal Method Signatures

#### StockAssistantAgent

```python
def process_query(
    self, 
    query: str, 
    *, 
    provider: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> str:

def process_query_streaming(
    self, 
    query: str, 
    *, 
    provider: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> Generator[str, None, None]:

def process_query_structured(
    self,
    query: str,
    *,
    provider: Optional[str] = None,
    conversation_id: Optional[str] = None,
) -> AgentResponse:
```

> **Current Runtime Note**: The canonical agent API is now `conversation_id`-only. The REST chat route retains a deprecated `session_id` alias as a compatibility shim before passing the normalized identifier to the service layer. Session-context lookup helpers exist in `ChatService` and `ConversationService`, but that merged context is not yet injected into the agent prompt path.

---

## Configuration Requirements

### config.yaml — Implemented Structure

The memory configuration lives under `langchain.memory` in `config/config.yaml`.
All parameters are loaded by the `MemoryConfig` frozen dataclass (`src/utils/memory_config.py`)
with fail-fast validation on construction (FR-3.1.10).

```yaml
langchain:
  # Memory Configuration (FR-3.1: Short-Term Memory)
  memory:
    enabled: true                           # Master switch (FR-3.1.1)

    # Summarization Settings (FR-3.1.6)
    summarize_threshold: 4000               # Token count to trigger summarization (valid: 1000-10000)
    max_messages: 50                        # Max messages per conversation thread before pruning (valid: 10-200)
    messages_to_keep: 10                    # Messages to preserve when pruning (valid: 5-50, < max_messages)
    max_content_size: 32768                 # Max bytes for single message content (valid: 1024-65536)
    summary_max_length: 500                 # Max tokens for summary (valid: 100-2000)

    # Performance Settings (FR-3.1.9)
    context_load_timeout_ms: 500            # Max time to load context (valid: 100-5000)
    state_save_timeout_ms: 50               # Max time to persist state (valid: 10-500)

    # MongoDB Collections (FR-3.1.2)
    checkpoint_collection: "agent_checkpoints"    # LangGraph-managed checkpoints
    conversations_collection: "conversations"     # Application-managed metadata
```

### MemoryConfig Validation Rules

| Parameter | Type | Valid Range | Constraint |
|-----------|------|-------------|------------|
| `enabled` | bool | `true`/`false` | Master switch |
| `summarize_threshold` | int | 1000–10000 | Token count trigger |
| `max_messages` | int | 10–200 | Session limit |
| `messages_to_keep` | int | 5–50 | Must be < `max_messages` |
| `max_content_size` | int | 1024–65536 | Per-message bytes |
| `summary_max_length` | int | 100–2000 | Summary token cap |
| `context_load_timeout_ms` | int | 100–5000 | Performance SLA |
| `state_save_timeout_ms` | int | 10–500 | Performance SLA |
| `checkpoint_collection` | str | Non-empty | MongoDB collection name |
| `conversations_collection` | str | Non-empty | MongoDB collection name |

### MongoDB Connection

The checkpointer reads the connection string from `config["database"]["mongodb"]["connection_string"]`
and database name from `config["database"]["mongodb"]["database_name"]` (default: `stock_assistant`).

---

## Implementation Roadmap

### Phase 2A.1 Implementation Tasks

| # | Task | Effort | Status |
|---|------|--------|--------|
| 1 | Add `langgraph-checkpoint-mongodb` to requirements.txt | XS | ✅ Done |
| 2 | Create `conversations_schema.py` | S | ✅ Done |
| 3 | Register conversations collection in SchemaManager | S | ✅ Done |
| 4 | Create `ConversationRepository` | M | ✅ Done |
| 5 | Create `ConversationService` | M | ✅ Done |
| 6 | Add memory config section to config.yaml | S | ✅ Done |
| 7 | Create `MemoryConfig` dataclass with fail-fast validation | M | ✅ Done |
| 8 | Create `create_checkpointer()` factory in langgraph_bootstrap | M | ✅ Done |
| 9 | Update `StockAssistantAgent.__init__()` to accept checkpointer | M | ✅ Done |
| 10 | Update `_build_agent_executor()` to pass checkpointer via `create_agent()` | M | ✅ Done |
| 11 | Route stateful query plumbing through `conversation_id` in `process_query()` and `process_query_streaming()` | M | ✅ Done |
| 12 | Expose `conversation_id` as canonical STM identifier in agent methods | M | ✅ Done |
| 13 | Update REST API routes for `conversation_id` with REST-only deprecated `session_id` alias normalization | M | ✅ Done |
| 14 | Update Socket.IO handlers for `conversation_id` UUID validation and passthrough | M | ✅ Done |
| 15 | Wire checkpointer in `APIServer.__init__()` | S | ✅ Done |
| 16 | Migrate `create_react_agent` → `create_agent` (LangGraph v1.0 deprecation) | M | ✅ Done |
| 17 | Fix MongoDB config key (`database.mongodb.connection_string`) | S | ✅ Done |
| 18 | Create `ContentValidator` for FR-3.1.7/FR-3.1.8 compliance | M | ✅ Done |
| 19 | Unit tests for memory components | L | ✅ Done |
| 20 | Integration tests for multi-turn conversation | L | ✅ Done |
| 21 | Enforce 1:N session-to-conversation relationships in repositories and schema indexes | M | ✅ Done |
| 22 | Resolve `conversation_id -> thread_id` before checkpointer access | M | ✅ Done |
| 23 | Resolve session context plus conversation overrides in service helpers without sharing checkpoints | M | ⚠ Partial |
| 24 | Implement runtime reconciliation service and operator CLI | M | ✅ Done |
| 25 | Implement additive legacy-checkpoint migration CLI with resume cursor | M | ✅ Done |

### Key Implementation Gaps Resolved

During implementation, five critical wiring gaps were discovered and fixed:

1. **`create_react_agent` deprecated**: The `langgraph.prebuilt.create_react_agent` API was deprecated in LangGraph v1.0. Migrated to `langchain.agents.create_agent` with `system_prompt=` and `name=` parameters.

2. **Checkpointer not wired to agent**: The checkpointer was created in `create_checkpointer()` but never passed to `StockAssistantAgent` in `APIServer.__init__()`. Fixed by adding `checkpointer=checkpointer` to the constructor call.

3. **MongoDB config key mismatch**: The original design assumed `config["mongodb"]["uri"]` but the actual config uses `config["database"]["mongodb"]["connection_string"]`. Fixed in `create_checkpointer()` factory.

4. **Canonical chat contract changed**: Stateful runtime routing now uses `conversation_id` end-to-end. The REST chat route retains `session_id` only as a deprecated compatibility alias that is normalized before validation.

5. **Hierarchy and tooling landed in production code**: The workspace/session/conversation management APIs, reconciliation scan service, and additive legacy migration CLI are all implemented on this branch.

### Remaining Runtime Gaps

1. **Automated summarization trigger**: Summary fields, status values, and thresholds exist, but the chat execution path does not yet invoke summarization when thresholds are exceeded.
2. **Socket.IO parity**: The Socket.IO handler preserves `conversation_id`, but it still bypasses `ChatService`, so archive guards and metadata sync remain REST-only.

---

## Testing Strategy

### Unit Tests

| Component | Test File | Test Cases |
|-----------|-----------|------------|
| `MemoryConfig` | `tests/test_memory_config.py` | Validation ranges, fail-fast, cross-field constraints, factory methods |
| `ConversationRepository` | `tests/test_conversation_repository.py` | CRUD operations, find_by_conversation_id, list_by_session_id, archive, find_stale |
| `ConversationService` | `tests/test_conversation_service.py` | track_message, get_conversation_stats, archive_conversation |
| `StockAssistantAgent` | `tests/test_agent_memory.py` | Checkpointer initialization, conversation_id flow, stateless fallback |
| `ContentValidator` | `tests/test_memory_config.py` | Prohibited pattern detection, compliance scanning |

### Integration Tests

| Test File | Scenario |
|-----------|----------|
| `tests/integration/test_memory_persistence.py` | Full persistence flow, conversation restart, parent session validation |
| `tests/integration/test_stm_runtime_wiring.py` | Runtime wiring verification (checkpointer → agent → API) |
| `tests/api/test_chat_routes_memory.py` | REST API conversation_id handling, optional session_id validation |

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
from pymongo import MongoClient

# Initialization (in langgraph_bootstrap.py::create_checkpointer)
client = MongoClient(connection_string)
checkpointer = MongoDBSaver(
    client=client,
    db_name="stock_assistant",
    checkpoint_collection_name="agent_checkpoints"  # via MemoryConfig
)

# Usage with agent (in stock_assistant_agent.py::_build_agent_executor)
from langchain.agents import create_agent

agent_executor = create_agent(
    model=model,
    tools=tools,
    checkpointer=checkpointer,
    system_prompt=system_prompt,
    name="stock_assistant",
)

# Invoke with thread_id (in _process_with_react)
result = agent_executor.invoke(
    {"messages": [HumanMessage(content="query")]},
    config={"configurable": {"thread_id": conversation_id}}
)
```

### B. Related Documents

- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) - Full enhancement roadmap
- [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md) - Current architecture
- [LANGCHAIN_AGENT_HOWTO.md](./LANGCHAIN_AGENT_HOWTO.md) - Implementation patterns
- [backend-python.instructions.md](../../../.github/instructions/backend-python.instructions.md) - Coding conventions

### C. Diagrams Source

- Data Model: `Langchain_agent_data_model.xml` (draw.io)
- Architecture: `Langchain_agent_high_level_design.xml` (draw.io)

---

> **Document Status**: STM hierarchy implemented and verified; summarization trigger and Socket.IO parity remain follow-up work  
> **Next Step**: Phase 2A.2 — Long-Term Memory (vector store, cross-session recall)  
> **Review Required**: Architecture Team

### D. Memory technical requirements (backup)

> **Architectural Context**: This section details requirements for the conversation memory system as designed in [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md)  
> **Governing ADR**: [ADR-001 — Layered LLM Architecture](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md)

#### MEM-1: Data Model Requirements

##### MEM-1.1 Conversations Collection

| ID | Priority | Requirement | Data Type | Description |
|----|----------|-------------|-----------|-------------|
| MEM-1.1.1 | **P0** | Each conversation SHALL have unique `_id` | ObjectId | Primary key. Auto-generated by MongoDB. |
| MEM-1.1.2 | **P0** | Each conversation SHALL expose a unique `conversation_id` | String | Canonical external identifier for lookup, routing, and authorization. |
| MEM-1.1.3 | **P0** | Each conversation SHALL reference `session_id` | String (UUID v4) | FK to `sessions.id`; parent business context for grouping related conversations. |
| MEM-1.1.4 | **P0** | `thread_id` SHALL map 1:1 to `conversation_id` | Derived String | `thread_id` is resolved from the conversation record and passed to LangGraph invoke config as `thread_id=conversation_id` or an equivalent derived value. |
| MEM-1.1.5 | **P0** | `conversation_id` and `thread_id` SHALL be uniquely indexed | - | Unique indexes prevent duplicate STM resources and checkpoint aliasing. |
| MEM-1.1.6 | **P0** | Each conversation SHALL track `status` | Enum | Values: `active`, `summarized`, `archived`. Use string enum in Pydantic model. |
| MEM-1.1.7 | **P0** | Each conversation SHALL track `message_count` | Integer | Auto-incremented via `$inc`. Start at 0 and increment once per completed chat turn in the current REST runtime metadata path. |
| MEM-1.1.8 | **P0** | Each conversation SHALL track `total_tokens` | Integer | Cumulative estimated tokens. The current runtime uses a rough character-based estimator during metadata recording. |
| MEM-1.1.9 | **P1** | Each conversation SHALL track `summary` | String | Optional. Populated when summarization triggers. Max 500 chars. |
| MEM-1.1.10 | **P1** | Each conversation MAY track summary progress metadata | Integer/Optional | Future enhancement for incremental summarization; not required in current schema. |
| MEM-1.1.11 | **P0** | Each conversation SHALL track `last_activity_at` | DateTime | UTC timestamp. Updated on each message via `$set` with `datetime.now(timezone.utc)`. |
| MEM-1.1.12 | **P0** | Each conversation SHALL track `created_at` and `updated_at` | DateTime | Audit fields. `created_at` set once; `updated_at` on every write. |
| MEM-1.1.13 | **P0** | Each conversation SHALL reference `workspace_id` | String | Required for hierarchy validation and workspace isolation. |
| MEM-1.1.14 | **P0** | Each conversation SHALL reference `user_id` | String | FK-style reference for authorization checks. Runtime auto-create and legacy migration flows may temporarily use sentinel values such as `unlinked` or `legacy`. |
| MEM-1.1.15 | **P1** | Each conversation MAY store `context_overrides` | Object | Conversation-scoped refinements layered over the parent session context. |
| MEM-1.1.16 | **P1** | Each conversation MAY store `conversation_intent` | String | Conversation-specific focus. Example: `"Stress test the dividend thesis"`. |
| MEM-1.1.17 | **P1** | Each conversation MAY store `focused_symbols[]` | Array[String] | Symbol names only (NO prices). Example: `["AAPL", "MSFT"]`. |
| MEM-1.1.18 | **P1** | Archived conversations SHALL track `archived_at` | DateTime | Timestamp when archived. Null for active/summarized conversations. |

##### MEM-1.2 Agent Checkpoints Collection

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-1.2.1 | **P0** | Collection SHALL be named `agent_checkpoints` | Configurable via `config.langchain.memory.checkpoint_collection`. |
| MEM-1.2.2 | **P0** | Schema SHALL be managed by LangGraph `MongoDBSaver` | Do NOT define custom schema—LangGraph owns this collection structure. |
| MEM-1.2.3 | **P0** | Checkpoints SHALL be indexed by `thread_id` | Primary lookup key. Index created automatically by MongoDBSaver. |
| MEM-1.2.4 | **P2** | Checkpoints MAY support TTL-based expiration in a future phase | Not implemented in the current runtime. MongoDBSaver checkpoints currently persist until explicit operational cleanup. |
| MEM-1.2.5 | **P0** | Checkpoint data SHALL include full message history | LangGraph stores `MessagesState` with all `HumanMessage`/`AIMessage` instances. |
| MEM-1.2.6 | **P0** | Checkpoint data SHALL include agent state metadata | Includes tool call history, intermediate states, graph node positions. |

##### MEM-1.3 Memory Vectors Collection (Future)

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-1.3.1 | **P2** | Collection SHALL be named `memory_vectors` | Future Phase 2A.2+. Define schema but do not implement yet. |
| MEM-1.3.2 | **P2** | Each vector SHALL include 1536-dimension embedding | Use `text-embedding-3-small` model. Store as `embedding: Float[1536]`. |
| MEM-1.3.3 | **P2** | Vectors SHALL be indexed for cosine similarity search | Requires MongoDB Atlas Vector Search. Create `vectorSearchIndex` on deployment. |
| MEM-1.3.4 | **P2** | Vectors SHALL reference `user_id`, `workspace_id`, `session_id`, `conversation_id` | Enable cross-reference queries and hierarchical recall controls. Indexed according to retrieval patterns. |
| MEM-1.3.5 | **P2** | Vectors SHALL include content type classification | Enum: `user_query`, `assistant_response`, `summary`, `insight`, `preference`. |

---

#### MEM-2: API Requirements

##### MEM-2.1 Conversation-Aware Endpoints

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-2.1.1 | **P0** | `POST /api/chat` SHALL accept optional `conversation_id` parameter | Add to request body: `{"message": "...", "conversation_id": "..."}`. Type: `Optional[str]`. |
| MEM-2.1.2 | **P0** | `POST /api/chat` MAY accept deprecated REST-only `session_id` alias | The route normalizes `session_id` into `conversation_id` before UUID validation during the migration window. |
| MEM-2.1.3 | **P0** | When `conversation_id` is provided, the agent SHALL bind it as the LangGraph thread identifier | The REST path may auto-create missing conversation metadata non-blocking, then invokes LangGraph with `configurable.thread_id=conversation_id`. |
| MEM-2.1.4 | **P0** | When `conversation_id` is omitted, the agent SHALL operate statelessly unless a create-conversation workflow is invoked | Process request without `thread_id` config. Do NOT create `conversations` record on ordinary stateless chat requests. |
| MEM-2.1.5 | **P0** | Invalid identifier formats SHALL return 400 Bad Request | Validate the canonical conversation identifier after any REST alias normalization. |
| MEM-2.1.6 | **P0** | Management APIs SHALL return 403 Forbidden on unauthorized workspace/session/conversation access | Ownership and parent integrity are enforced on the management API surface via `X-User-ID`; the chat route currently has no user-bound authorization layer. |
| MEM-2.1.7 | **P0** | Management APIs SHALL return 404 Not Found for missing hierarchy resources | `POST /api/chat` does not 404 on a missing conversation metadata record; the REST path may auto-create a placeholder record instead. |

##### MEM-2.2 WebSocket Memory Integration

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-2.2.1 | **P0** | `chat_message` event SHALL accept optional `conversation_id` | Add to event payload: `{message: "...", conversation_id: "..."}`. |
| MEM-2.2.2 | **P0** | Streaming responses SHALL maintain memory context | Pass `conversation_id` through the streaming pipeline and bind it as `thread_id` before execution. REST streaming also enforces archive guards; Socket.IO parity is still pending. |
| MEM-2.2.3 | **P0** | Memory state SHALL be persisted after each complete response | Persistence is handled by LangGraph checkpointer during `invoke()` / `astream_events()` execution with `thread_id`. |

---

#### MEM-3: Behavioral Requirements

> **Status Note:** MEM-3.1.1, MEM-3.1.2, MEM-3.2.x, and MEM-3.4.2 / MEM-3.4.5 describe behavior that is implemented or substantially represented in the current runtime. MEM-3.1.3 and MEM-3.3.x remain follow-up requirements for the summarization pipeline and are not fully wired yet.

##### MEM-3.1 Context Loading

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.1.1 | **P0** | Agent SHALL load conversation history before processing query | Call `graph.get_state(config)` to retrieve existing checkpoint. Pass to first node. |
| MEM-3.1.2 | **P0** | Agent SHALL include history in LLM context via LangGraph checkpointer | History auto-injected by `MessagesState`. Verify `state["messages"]` contains history. |
| MEM-3.1.3 | **P1** | If summary exists, a future prompt-compilation path SHALL be able to prepend summary to context | Not wired in the current runtime. Planned follow-up once automated summarization is active. |
| MEM-3.1.4 | **P0** | Agent SHALL handle missing/corrupted checkpoints gracefully | Catch `CheckpointNotFound` exception. Start fresh with empty state. Log warning. |

##### MEM-3.2 Context Persistence

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.2.1 | **P0** | Agent SHALL persist state after each query completion | Automatic via `MongoDBSaver`. Verify by checking `agent_checkpoints` collection. |
| MEM-3.2.2 | **P0** | Persistence SHALL include user message, agent response, tool calls | All stored in `MessagesState`. Tool calls stored as `AIMessage.tool_calls[]`. |
| MEM-3.2.3 | **P0** | Persistence SHALL be atomic (all-or-nothing) | MongoDBSaver handles atomicity. On failure, no partial state saved. |
| MEM-3.2.4 | **P0** | Failed persistence SHALL NOT affect response delivery | Catch persistence errors in finally block. Log error but return response to user. |
| MEM-3.2.5 | **P0** | `conversations` metadata SHALL be updated after each exchange | The REST chat path uses `ChatService.record_message_metadata()` and `ConversationRepository.update_metadata()` to update counters and timestamps non-blocking. |

##### MEM-3.3 Summarization Trigger

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.3.1 | **P1** | Summarization SHALL trigger when `total_tokens > summarize_threshold` | Check after each response. Default threshold: 4000 tokens. |
| MEM-3.3.2 | **P1** | Default `summarize_threshold` SHALL be 4000 tokens | Configurable via `config.langchain.memory.summarize_threshold`. |
| MEM-3.3.3 | **P1** | Summarization SHALL preserve last K messages (default K=10) | After summary, trim `state["messages"]` to last K. Configurable via `messages_to_keep`. |
| MEM-3.3.4 | **P1** | Summary generation SHALL use dedicated LLM call | Call `llm.invoke(summarization_prompt)`. Use same model as agent or cheaper model. |
| MEM-3.3.5 | **P1** | Post-summarization, `conversations.status` SHALL be `summarized` | Update via `ConversationRepository.set_status("summarized")`. |

##### MEM-3.4 Memory Archival (per ADR-001)

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-3.4.1 | **P1** | Inactive conversations SHALL be archived after configurable period | Default: 30 days inactive. Cron job or background task to check `last_activity_at`. |
| MEM-3.4.2 | **P0** | Archived conversations SHALL be read-only | **ADR Compliance**: Reject updates with `ConversationArchivedError`. Only allow read queries. |
| MEM-3.4.3 | **P1** | Checkpoint TTL SHALL default to 30 days | Future enhancement; not currently implemented in `MemoryConfig`. |
| MEM-3.4.4 | **P1** | Expired checkpoints SHALL be automatically purged by MongoDB TTL index | Create TTL index on `created_at` field. MongoDB handles expiration automatically. |
| MEM-3.4.5 | **P0** | The system SHALL NOT hard-delete conversations | **ADR Compliance**: Implement `archive()` method only. No `delete()` method in repository. |

---

#### MEM-4: Configuration Requirements

##### MEM-4.1 Memory Configuration Schema

> **Implementation Note**: The originally proposed nested structure (`checkpointer.type`, `summarization.threshold_tokens`)
> was simplified during implementation to a flat structure managed by the `MemoryConfig` frozen dataclass
> (`src/utils/memory_config.py`). All parameters are validated at startup with fail-fast semantics (FR-3.1.10).

**Implemented config structure** (see [Configuration Requirements](#configuration-requirements) above):
```yaml
langchain:
  memory:
    enabled: true
    summarize_threshold: 4000
    max_messages: 50
    messages_to_keep: 10
    max_content_size: 32768
    summary_max_length: 500
    context_load_timeout_ms: 500
    state_save_timeout_ms: 50
    checkpoint_collection: "agent_checkpoints"
    conversations_collection: "conversations"
```

| ID | Priority | Requirement | Description |
|----|----------|-------------|-------------|
| MEM-4.1.1 | **P0** | Memory feature SHALL be toggleable via `memory.enabled` | When `false`, agent operates statelessly. No checkpointer initialized. |
| MEM-4.1.2 | **P0** | Checkpointer collection name SHALL be configurable | Default: `agent_checkpoints`. Set via `checkpoint_collection`. |
| MEM-4.1.3 | **P1** | Checkpoint TTL SHALL be configurable (days) | Future enhancement; not currently in `MemoryConfig` schema. |
| MEM-4.1.4 | **P1** | Summarization threshold SHALL be configurable (tokens) | Default: 4000. Set via `summarize_threshold`. |
| MEM-4.1.5 | **P1** | Recent message retention count SHALL be configurable | Default: 10. Set via `messages_to_keep`. |
| MEM-4.1.6 | **P0** | All memory settings SHALL have sensible defaults | Defaults must allow system to run without explicit config. |
| MEM-4.1.7 | **P1** | Archive period SHALL be configurable | Future enhancement; not currently in `MemoryConfig` schema. |

---