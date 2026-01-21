# Agent Memory Technical Design

> **Document Version**: 1.0  
> **Last Updated**: January 21, 2026  
> **Phase**: 2A.1 - Long-Term Conversation Memory  
> **Status**: Technical Design Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architectural Decisions](#architectural-decisions)
3. [Data Model Design](#data-model-design)
4. [Sequence Diagrams](#sequence-diagrams)
5. [API Contract Changes](#api-contract-changes)
6. [Configuration Requirements](#configuration-requirements)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Testing Strategy](#testing-strategy)

---

## Executive Summary

### Objective

Implement persistent conversation memory for the Stock Assistant LangChain agent, enabling multi-turn conversations where the agent recalls previous exchanges within a session.

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Dual Memory Strategy** | Short-term (checkpointer) + Long-term (vector store) |
| **Backward Compatibility** | Existing APIs continue to work without `session_id` |
| **Separation of Concerns** | LangGraph handles agent state; ChatRepository handles UI queries |
| **Native Integration** | Use LangGraph's built-in MongoDBSaver for checkpoints |

### Scope

**In Scope:**
- Short-term conversation memory via LangGraph checkpointer
- New MongoDB collections for agent memory
- API changes to support `session_id` parameter
- Memory summarization for long conversations

**Out of Scope (Phase 2A.2+):**
- Long-term vector store memory (semantic search over past conversations)
- Cross-session memory retrieval
- User preference learning

---

## Architectural Decisions

### Decision 1: Dual Memory Architecture

**Decision**: Implement two types of memory with distinct purposes.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MEMORY ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐ │
│  │   SHORT-TERM MEMORY         │    │   LONG-TERM MEMORY          │ │
│  │   (Conversation Buffer)     │    │   (Vector Store)            │ │
│  ├─────────────────────────────┤    ├─────────────────────────────┤ │
│  │ • Thread-scoped             │    │ • Cross-session             │ │
│  │ • LangGraph Checkpointer    │    │ • Semantic search           │ │
│  │ • Auto-summarization        │    │ • MongoDB Atlas Vector      │ │
│  │ • Full message history      │    │ • Embedding-based retrieval │ │
│  └─────────────────────────────┘    └─────────────────────────────┘ │
│              │                                   │                   │
│              ▼                                   ▼                   │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐ │
│  │  agent_checkpoints          │    │  memory_vectors             │ │
│  │  (MongoDB Collection)       │    │  (MongoDB Collection)       │ │
│  └─────────────────────────────┘    └─────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Rationale:**
- Short-term memory enables coherent multi-turn conversations
- Long-term memory (future) enables learning from past interactions
- Separation allows independent scaling and optimization

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

### Decision 4: Conversation Collection Introduction

**Decision**: Introduce new `conversations` collection with 1:1 mapping to `sessions`.

**Purpose:**
- Track conversation metadata (message count, token usage, summary)
- Enable memory-specific operations without polluting session entity
- Support future features like conversation archival

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

**Purpose**: Track conversation metadata and memory state.

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
            "enum": ["active", "summarized", "archived"],
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
