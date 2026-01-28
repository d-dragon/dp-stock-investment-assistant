# Research: FR-3.1 Short-Term Memory Implementation

**Date**: 2025-01-27 | **Plan**: [plan.md](./plan.md)

---

## 1. LangGraph MongoDBSaver Checkpointer

### Decision: Use Native LangGraph MongoDBSaver

**Rationale**:
- Built-in support in LangGraph >=0.2.0 via `langgraph.checkpoint.mongodb`
- Handles serialization of `MessagesState` automatically
- Provides thread-based state isolation via `thread_id` in config
- Auto-manages checkpoint versioning and state history
- Eliminates need for custom serialization logic

**Alternatives Considered**:

| Alternative | Rejected Because |
|-------------|------------------|
| Custom MongoDB persistence | Duplicates LangGraph functionality; higher maintenance burden |
| Redis-based checkpointer | No built-in LangGraph support; messages don't need sub-ms latency |
| SQLite checkpointer | Not suitable for multi-instance deployment (file-based) |
| In-memory checkpointer | Loses state on restart; not production-viable |

**Implementation Reference**:
```python
from langgraph.checkpoint.mongodb import MongoDBSaver

checkpointer = MongoDBSaver(
    connection_string="mongodb://...",
    db_name="stock_assistant",
    collection_name="agent_checkpoints"
)

# Usage with thread_id = session_id (1:1 direct mapping)
result = agent_executor.invoke(
    {"messages": [HumanMessage(content=query)]},
    config={"configurable": {"thread_id": session_id}}
)
```

---

## 2. Thread ID Mapping Strategy

### Decision: Direct 1:1 Mapping (session_id → thread_id)

**Rationale**:
- Simplicity: No translation layer needed
- Sessions already have unique UUIDs (P(collision) < 1e-18)
- Workspace isolation enforced at session level (session.workspace_id)
- Existing session lifecycle maps cleanly to conversation lifecycle

**Alternatives Considered**:

| Alternative | Rejected Because |
|-------------|------------------|
| Separate thread_id generation | Adds complexity; session_id already unique |
| Composite key (user_id + session_id) | Unnecessary; session_id already scoped to user |
| Hash-based thread_id | Obscures traceability; debugging harder |

**Validation**:
- Session UUID format: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- Entropy: 122 bits (sufficient for P(collision) < 1e-18 requirement)
- Existing `sessions` collection guarantees uniqueness

---

## 3. Dual Collection Architecture

### Decision: Separate `conversations` + `agent_checkpoints` Collections

**Rationale**:
- `agent_checkpoints`: Owned by LangGraph MongoDBSaver; DO NOT modify schema
- `conversations`: App-managed metadata (status, message_count, summary, focused_symbols)
- Separation allows independent scaling and maintenance
- LangGraph schema can evolve without breaking app logic

**Collection Responsibilities**:

| Collection | Owner | Purpose | Schema Control |
|------------|-------|---------|----------------|
| `agent_checkpoints` | LangGraph | Full message history, tool calls, graph state | LangGraph (DO NOT MODIFY) |
| `conversations` | Application | Metadata, status, summary, focused_symbols | Application-defined |

**Relationship**:
```
sessions (existing)
    │
    └──→ conversations (NEW, 1:1)
              │
              └──→ agent_checkpoints (LangGraph, by thread_id)
```

---

## 4. Conversation Summarization Strategy

### Decision: LLM-Based Summarization with Token Threshold

**Rationale**:
- Token-based trigger (4000 tokens) aligns with model context limits
- LLM summarization preserves semantic meaning better than truncation
- Keep last K messages (10) provides recent context + summary for older

**Summarization Flow**:
```
1. After each response, check: total_tokens > threshold (4000)?
2. If yes, invoke summarization LLM call:
   - Input: All messages except last K (10)
   - Output: Summary (max 500 chars)
3. Replace old messages with SystemMessage containing summary
4. Update conversations.summary and conversations.status = "summarized"
```

**Prompt Pattern** (from technical design):
```
Summarize the following conversation between a user and an AI stock assistant.
Focus on:
- Main topics discussed (stocks, analysis types)
- Key questions asked
- Important conclusions or recommendations made
- User's apparent investment focus

Keep the summary under 500 characters.
```

**Alternatives Considered**:

| Alternative | Rejected Because |
|-------------|------------------|
| Simple truncation (drop oldest) | Loses important early context |
| Sliding window only | Forgets setup context (user intent) |
| No summarization (unlimited tokens) | Context window limits; cost concerns |
| Message count threshold | Token count more accurate for context management |

---

## 5. Memory Scope Boundaries

### Decision: Strict Content Filtering per ADR-001

**Allowed Content** (stored in checkpoints):
- User query text (verbatim)
- Assistant response text (verbatim)
- Tool call names and arguments (metadata only)
- Session assumptions, pinned intent
- Focused symbol names (e.g., "AAPL", "MSFT") — **NO prices**

**Prohibited Content** (NEVER stored):
- Stock prices, market data, quotes
- Financial ratios (P/E, P/B, ROE, etc.)
- Tool output data (only tool names allowed)
- Computed values, calculations
- External API response payloads

**Implementation Enforcement**:
- LangGraph stores `MessagesState` which includes full message text
- Tool outputs are NOT included in messages by default (only tool call metadata)
- Pre-storage filtering not required due to LangGraph's message-centric design
- Post-hoc audit script to verify no price patterns in checkpoints

---

## 6. Backward Compatibility Strategy

### Decision: Optional session_id with Stateless Fallback

**Rationale**:
- Existing clients without session_id continue to work (FR-3.1.4)
- Stateless mode uses ephemeral UUID (not persisted)
- No conversations record created for stateless queries
- Zero breaking changes to existing API contract

**Behavior Matrix**:

| session_id Provided | Behavior |
|---------------------|----------|
| Yes (valid) | Load conversation, restore context, persist state |
| Yes (invalid format) | Return 400 Bad Request |
| Yes (not found) | Return 404 Not Found |
| Yes (unauthorized) | Return 403 Forbidden |
| No / null | Stateless single-turn, ephemeral thread_id, no persistence |

**API Contract** (backward compatible):
```json
// Existing (still works)
POST /api/chat
{"message": "What is AAPL trading at?"}

// New (opt-in memory)
POST /api/chat
{"message": "What about its P/E ratio?", "session_id": "uuid-here"}
```

---

## 7. Archive Strategy per ADR-001

### Decision: Three-State Lifecycle (active → summarized → archived)

**Rationale**:
- ADR-001 prohibits hard deletion of conversations
- Active: Currently in use
- Summarized: Token threshold exceeded, summary generated
- Archived: Session closed or inactive 30+ days, read-only

**State Transitions**:
```
┌─────────┐    summarize()    ┌────────────┐    archive()     ┌──────────┐
│ active  │ ─────────────────→│ summarized │ ─────────────────→│ archived │
└─────────┘                   └────────────┘                   └──────────┘
     │                                                               │
     │                  archive() (direct)                           │
     └───────────────────────────────────────────────────────────────┘
```

**Archive Triggers**:
1. Manual: User closes session
2. Automatic: `last_activity_at` > 30 days (background job)

**Archived Behavior**:
- Read-only (reject updates with `ConversationArchivedError`)
- Checkpoint TTL: 30 days (MongoDB TTL index auto-purges)
- Conversation metadata retained indefinitely

---

## 8. Performance Considerations

### Context Load Performance

**Target**: <500ms (SC-7)

**Optimization Strategies**:
1. MongoDBSaver uses indexed `thread_id` lookup
2. Single document fetch (checkpoints stored as single doc per thread)
3. MongoDB connection pooling via existing PyMongo setup
4. No expensive joins (thread_id is direct key)

**Expected Latency Breakdown**:
| Operation | Expected Time |
|-----------|---------------|
| MongoDB query by thread_id | 5-20ms |
| Checkpoint deserialization | 10-30ms |
| Message injection to state | 5-10ms |
| **Total** | **20-60ms** (well under 500ms) |

### State Save Performance

**Target**: <50ms

**Optimization Strategies**:
1. MongoDBSaver upserts by thread_id (atomic)
2. Async save option for non-blocking response delivery
3. Batch token counting using tiktoken

---

## 9. Testing Strategy

### Unit Tests (per Constitution Article VI)

| Component | Test Cases |
|-----------|------------|
| ConversationRepository | CRUD, find_by_session, update_activity, archive |
| ConversationService | create_conversation, update_metrics, trigger_summarization |
| Agent memory | process_query with/without session_id |

### Integration Tests

| Scenario | Verification |
|----------|--------------|
| Multi-turn conversation | Context from turn N visible in turn N+1 |
| Process restart | Kill process, restart, verify context restored |
| Summarization trigger | Exceed 4000 tokens, verify summary generated |
| Backward compatibility | No session_id → stateless, no state persisted |

### Performance Benchmarks

| Metric | Target | Test Method |
|--------|--------|-------------|
| Context load | <500ms | Profile `graph.get_state()` with 50 message history |
| State save | <50ms | Profile `checkpointer.put()` |
| Summarization | <2s | Profile LLM summarization call |

---

## 10. Configuration Schema

```yaml
# config/config.yaml additions
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
      archive_after_days: 30
```

---

## References

- [AGENT_MEMORY_TECHNICAL_DESIGN.md](../../docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md) — Full technical design
- [ADR-001: Layered LLM Architecture](../../docs/langchain-agent/AGENT_ARCHITECTURE_DECISION_RECORDS.md) — Architectural decisions
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) — Official docs
- [MongoDBSaver API](https://langchain-ai.github.io/langgraph/reference/checkpoints/mongodb/) — Checkpointer reference
