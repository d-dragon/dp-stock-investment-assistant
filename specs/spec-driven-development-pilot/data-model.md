# Data Model: FR-3.1 Short-Term Memory

**Date**: 2025-01-27 | **Plan**: [plan.md](./plan.md)

---

## 1. Entity Relationship Diagram

```
┌────────────────────────┐
│        users           │
│  (existing collection) │
└───────────┬────────────┘
            │ 1:N
            ▼
┌────────────────────────┐
│      workspaces        │
│  (existing collection) │
└───────────┬────────────┘
            │ 1:N
            ▼
┌────────────────────────┐
│       sessions         │
│  (existing collection) │
└───────────┬────────────┘
            │ 1:1
            ▼
┌────────────────────────┐       ┌─────────────────────────────┐
│     conversations      │◄─────►│     agent_checkpoints       │
│   (NEW - app-managed)  │ 1:1   │ (LangGraph - DO NOT MODIFY) │
└────────────────────────┘       └─────────────────────────────┘
```

---

## 2. Conversations Collection (NEW)

### Purpose
Application-managed metadata for conversation state, separate from LangGraph's internal checkpoint storage.

### Schema Definition

```python
# src/data/schema/conversations_schema.py

CONVERSATIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "status", "created_at", "updated_at"],
    "properties": {
        "_id": {
            "bsonType": "objectId",
            "description": "MongoDB auto-generated ID"
        },
        "session_id": {
            "bsonType": "string",
            "description": "FK to sessions.id, also used as thread_id",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        },
        "workspace_id": {
            "bsonType": "string",
            "description": "FK to workspaces.id for isolation verification"
        },
        "user_id": {
            "bsonType": "string",
            "description": "FK to users.id for authorization"
        },
        "status": {
            "enum": ["active", "summarized", "archived"],
            "description": "Conversation lifecycle state"
        },
        "message_count": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Number of human messages exchanged"
        },
        "total_tokens": {
            "bsonType": "int",
            "minimum": 0,
            "description": "Estimated token count for summarization trigger"
        },
        "summary": {
            "bsonType": ["string", "null"],
            "maxLength": 500,
            "description": "LLM-generated summary when status=summarized"
        },
        "focused_symbols": {
            "bsonType": "array",
            "items": {
                "bsonType": "string",
                "pattern": "^[A-Z]{1,5}$"
            },
            "description": "Stock symbols mentioned (e.g., ['AAPL', 'MSFT'])"
        },
        "session_assumptions": {
            "bsonType": ["string", "null"],
            "description": "User's stated preferences/assumptions for session"
        },
        "pinned_intent": {
            "bsonType": ["string", "null"],
            "description": "Pinned analysis intent (e.g., 'long-term value investing')"
        },
        "last_activity_at": {
            "bsonType": "date",
            "description": "Last user interaction timestamp"
        },
        "created_at": {
            "bsonType": "date",
            "description": "Conversation creation timestamp"
        },
        "updated_at": {
            "bsonType": "date",
            "description": "Last update timestamp"
        },
        "archived_at": {
            "bsonType": ["date", "null"],
            "description": "Archive timestamp if status=archived"
        }
    },
    "additionalProperties": False
}
```

### Indexes

```python
CONVERSATIONS_INDEXES = [
    # Primary lookup: session → conversation (1:1)
    {
        "keys": [("session_id", 1)],
        "unique": True,
        "name": "idx_conversations_session_id_unique"
    },
    # Authorization queries
    {
        "keys": [("user_id", 1), ("status", 1)],
        "name": "idx_conversations_user_status"
    },
    # Workspace isolation
    {
        "keys": [("workspace_id", 1), ("status", 1)],
        "name": "idx_conversations_workspace_status"
    },
    # Archive job queries
    {
        "keys": [("status", 1), ("last_activity_at", 1)],
        "name": "idx_conversations_status_activity"
    },
    # Text search on symbols (optional)
    {
        "keys": [("focused_symbols", 1)],
        "name": "idx_conversations_symbols"
    }
]
```

### Example Document

```json
{
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "session_id": "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789",
    "workspace_id": "ws-123",
    "user_id": "user-456",
    "status": "active",
    "message_count": 5,
    "total_tokens": 1250,
    "summary": null,
    "focused_symbols": ["AAPL", "MSFT"],
    "session_assumptions": "I prefer value stocks with dividends",
    "pinned_intent": "Dividend growth investing",
    "last_activity_at": ISODate("2025-01-27T10:30:00Z"),
    "created_at": ISODate("2025-01-27T10:00:00Z"),
    "updated_at": ISODate("2025-01-27T10:30:00Z"),
    "archived_at": null
}
```

---

## 3. Agent Checkpoints Collection (LangGraph-Managed)

### ⚠️ DO NOT MODIFY THIS SCHEMA

This collection is owned and managed by LangGraph's `MongoDBSaver`. The schema is defined by the LangGraph library.

### Collection Name
`agent_checkpoints` (configurable via `MongoDBSaver` constructor)

### Expected Structure (for reference only)

```python
# DO NOT create schema validation - let LangGraph manage this
{
    "thread_id": str,           # Our session_id
    "checkpoint": bytes,        # Serialized graph state
    "metadata": dict,           # LangGraph internal metadata
    "created_at": datetime,
    # Additional LangGraph-managed fields...
}
```

### Recommended Index (if not created by LangGraph)

```python
CHECKPOINTS_INDEX = {
    "keys": [("thread_id", 1)],
    "name": "idx_checkpoints_thread_id"
}
```

### TTL Index for Cleanup

```python
CHECKPOINTS_TTL_INDEX = {
    "keys": [("created_at", 1)],
    "expireAfterSeconds": 30 * 24 * 60 * 60,  # 30 days
    "name": "idx_checkpoints_ttl"
}
```

---

## 4. Sessions Collection (EXISTING - Reference)

### Current Schema (unchanged)

```python
# Existing schema - DO NOT MODIFY
{
    "_id": ObjectId,
    "id": str,  # UUID - used as session_id/thread_id
    "workspace_id": str,
    "user_id": str,
    "title": str,
    "status": str,  # "open", "closed"
    "created_at": datetime,
    "updated_at": datetime
}
```

### New Relationship

```
sessions.id (1) ──────────► conversations.session_id (1)
                    ▲
                    │ 1:1 mapping
                    │
                    ▼
              agent_checkpoints.thread_id
```

---

## 5. State Transitions

### Conversation Lifecycle

```
                  ┌───────────────────────┐
                  │       CREATED         │
                  │  (on first message)   │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
           ┌──────│       ACTIVE          │◄─────┐
           │      │  (ongoing dialogue)   │      │
           │      └───────────┬───────────┘      │
           │                  │                   │
           │  token > 4000    │                   │ new message
           │                  ▼                   │
           │      ┌───────────────────────┐      │
           │      │     SUMMARIZED        │──────┘
           │      │  (summary generated)  │
           │      └───────────┬───────────┘
           │                  │
           │  session close   │ inactivity >30d
           │  OR inactivity   │ OR session close
           │                  │
           │                  ▼
           │      ┌───────────────────────┐
           └─────►│      ARCHIVED         │
                  │  (read-only, no TTL)  │
                  └───────────────────────┘
```

### Status Transition Rules

| From | To | Trigger | Action |
|------|-----|---------|--------|
| - | active | First message in session | Create conversation doc |
| active | summarized | `total_tokens > 4000` | Generate summary, update status |
| active | archived | Session closed OR inactive 30d | Set `archived_at`, freeze writes |
| summarized | archived | Session closed OR inactive 30d | Set `archived_at`, freeze writes |

---

## 6. Validation Rules

### Business Rules (enforced in service layer)

```python
class ConversationValidation:
    """Validation rules for Conversation entity."""
    
    # Status values
    VALID_STATUSES = frozenset(["active", "summarized", "archived"])
    
    # Summarization
    SUMMARY_MAX_LENGTH = 500
    TOKEN_THRESHOLD = 4000
    KEEP_RECENT_MESSAGES = 10
    
    # Archive policy
    INACTIVITY_DAYS = 30
    
    # Symbol validation
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{1,5}$')
    MAX_FOCUSED_SYMBOLS = 20
    
    @classmethod
    def validate_status_transition(cls, current: str, target: str) -> bool:
        """Validate status state machine transitions."""
        allowed_transitions = {
            None: {"active"},
            "active": {"summarized", "archived"},
            "summarized": {"archived"},
            "archived": set()  # Terminal state
        }
        return target in allowed_transitions.get(current, set())
    
    @classmethod
    def validate_focused_symbols(cls, symbols: List[str]) -> List[str]:
        """Validate and normalize symbol list."""
        if not symbols:
            return []
        
        valid = []
        for sym in symbols[:cls.MAX_FOCUSED_SYMBOLS]:
            normalized = sym.upper().strip()
            if cls.SYMBOL_PATTERN.match(normalized):
                valid.append(normalized)
        
        return list(set(valid))  # Deduplicate
```

### Invariants

1. **1:1 Relationship**: `conversations.session_id` MUST be unique (enforced by index)
2. **No Orphans**: Conversation MUST have valid `session_id` referencing `sessions.id`
3. **Immutable Archive**: `status=archived` → all update operations MUST fail
4. **Summary on Summarize**: `status=summarized` → `summary` MUST be non-null
5. **No Delete**: Conversations are NEVER deleted (per ADR-001)

---

## 7. Migration Strategy

### Step 1: Create Collections (idempotent)

```python
# src/data/migration/conversations_setup.py

def setup_conversations_collection(db):
    """Create conversations collection with validation and indexes."""
    
    # Create collection with schema validation
    if "conversations" not in db.list_collection_names():
        db.create_collection(
            "conversations",
            validator={"$jsonSchema": CONVERSATIONS_SCHEMA},
            validationLevel="moderate",
            validationAction="error"
        )
    
    # Create indexes
    for index_spec in CONVERSATIONS_INDEXES:
        db.conversations.create_index(
            index_spec["keys"],
            name=index_spec["name"],
            unique=index_spec.get("unique", False),
            background=True
        )

def setup_checkpoints_indexes(db):
    """Create indexes for agent_checkpoints (LangGraph collection)."""
    
    # TTL index for cleanup
    db.agent_checkpoints.create_index(
        [("created_at", 1)],
        name="idx_checkpoints_ttl",
        expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days
        background=True
    )
```

### Step 2: Verify Existing Sessions

```python
def verify_sessions_compatibility(db):
    """Verify existing sessions have required fields."""
    
    # Check sessions have 'id' field (used as session_id)
    sample = db.sessions.find_one()
    if sample and 'id' not in sample:
        raise MigrationError("sessions collection missing 'id' field")
    
    return True
```

---

## 8. Repository Interface

```python
# src/data/repositories/conversation_repository.py

class ConversationRepository(MongoGenericRepository):
    """Repository for Conversation entities."""
    
    def __init__(self, db):
        super().__init__(db, "conversations")
    
    # ─────────────────────────────────────────────────────────────────
    # Core CRUD (inherited from MongoGenericRepository)
    # ─────────────────────────────────────────────────────────────────
    # - find_one(filter_dict) -> Optional[Dict]
    # - find_many(filter_dict, limit, skip, sort) -> List[Dict]
    # - insert_one(document) -> str
    # - update_one(id, updates) -> Optional[Dict]
    # - delete_one(id) -> bool  # NOTE: Disabled for conversations
    # - count(filter_dict) -> int
    # - health_check() -> Tuple[bool, Dict]
    
    # ─────────────────────────────────────────────────────────────────
    # Domain-Specific Methods
    # ─────────────────────────────────────────────────────────────────
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict]:
        """Find conversation by session_id (primary lookup)."""
        pass
    
    def find_active_by_user(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Find active conversations for a user."""
        pass
    
    def update_activity(self, session_id: str, message_count_delta: int = 1, 
                        token_delta: int = 0) -> Optional[Dict]:
        """Update activity metrics after message exchange."""
        pass
    
    def update_summary(self, session_id: str, summary: str) -> Optional[Dict]:
        """Update summary and set status to 'summarized'."""
        pass
    
    def archive(self, session_id: str) -> Optional[Dict]:
        """Archive conversation (terminal state)."""
        pass
    
    def find_stale(self, days: int = 30, limit: int = 100) -> List[Dict]:
        """Find conversations inactive for N days (for archive job)."""
        pass
```

---

## References

- [AGENT_MEMORY_TECHNICAL_DESIGN.md](../../docs/domains/agent/AGENT_MEMORY_TECHNICAL_DESIGN.md) — MEM-1 data model requirements
- [ADR-001](../../docs/domains/agent/decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md) — No-delete policy
- [MongoDB Schema Patterns](../../.github/instructions/backend-python.instructions.md) — Repository patterns
