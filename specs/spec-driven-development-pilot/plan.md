# Implementation Plan: FR-3.1 Short-Term Memory (STM)

**Branch**: `spec-driven-development-pilot` | **Date**: 2025-01-28 | **Spec**: [spec.md v1.1.0](../../.specify/specs/1-short-term-memory/spec.md)
**Input**: Feature specification from `/.specify/specs/1-short-term-memory/spec.md`

**Governing Documents**:
- [Constitution v1.1.0](../../.specify/memory/constitution.md) — Project-wide governance
- [AGENT_MEMORY_TECHNICAL_DESIGN.md](../../docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md) — Full technical design
- [AGENT_ARCHITECTURE_DECISION_RECORDS.md](../../docs/langchain-agent/AGENT_ARCHITECTURE_DECISION_RECORDS.md) — ADR-001: Layered LLM Architecture
- [LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md](../../docs/langchain-agent/LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md) — Current agent architecture

---

## Summary

Implement **Short-Term Memory (STM)** for the StockAssistantAgent to enable multi-turn conversational context within sessions. The solution uses **LangGraph's `MongoDBSaver` checkpointer** to persist agent state (`MessagesState`) across requests, allowing users to conduct natural multi-turn conversations where the agent remembers context from earlier exchanges.

**Key Technical Approach**:
- Use `langgraph.checkpoint.mongodb.MongoDBSaver` for automatic state persistence
- Direct 1:1 mapping: `session_id` → `thread_id` (no translation layer)
- Dual collection strategy: `conversations` (app-managed metadata) + `agent_checkpoints` (LangGraph-managed)
- Archive-over-delete policy per ADR-001 (active → summarized → archived lifecycle)
- Backward-compatible: omitting `session_id` preserves stateless single-turn behavior (FR-3.1.4)
- **Configurable parameters**: All operational thresholds loaded from YAML config with validation (FR-3.1.9, FR-3.1.10)

**Focus**: STM implementation with extensibility for future LTM (Phase 2A.2+) using same architectural foundation.

---

## Technical Context

**Language/Version**: Python 3.8+ (per Constitution Article VIII)  
**Primary Dependencies**: LangGraph >=0.2.0, LangChain >=1.0.0, Flask 2.x, PyMongo 4.x  
**Storage**: MongoDB 5.0+ (collections: `sessions`, `conversations` [NEW], `agent_checkpoints` [NEW])  
**Testing**: pytest with 80%+ coverage target (per Constitution Article VI)  
**Target Platform**: Linux server (Docker/Kubernetes), local development on Windows  
**Project Type**: Web application (Flask backend + React frontend)  
**Performance Goals**:
- Context load time: <500ms (SC-7)
- State save time: <50ms (from technical design)
- Context accuracy: ≥95% (SC-1)
- Persistence reliability: 100% (SC-2)

**Constraints**:
- Memory scope: Store conversation text ONLY; NEVER store financial data, prices, ratios (FR-3.1.7, FR-3.1.8)
- Summarization: Configurable via `memory.summarize_threshold` (default 4000 tokens), `memory.messages_to_keep` (default 10) (FR-3.1.9)
- Session isolation: P(collision) < 1e-18 for session IDs (SC-5)
- Archive policy: NO hard-delete ever (ADR-001)
- Configuration: All operational parameters must be configurable via YAML; fail-fast on invalid config (FR-3.1.9, FR-3.1.10)

**Scale/Scope**: Multi-user, workspace-scoped sessions

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Check ✅

| Article | Requirement | Status | Notes |
|---------|-------------|--------|-------|
| **III.1** Repository Pattern | ✅ PASS | Create `ConversationRepository` extending `MongoGenericRepository` |
| **III.2** Factory Pattern | ✅ PASS | Add to `RepositoryFactory` and `ServiceFactory` |
| **III.3** Protocol DI | ✅ PASS | Agent receives `checkpointer` via constructor injection |
| **III.4** ≤3 Logical Projects | ✅ PASS | No new projects; extends existing `src/` and `tests/` |
| **IV.1-5** SOLID Principles | ✅ PASS | Single responsibility for new service/repository |
| **V.1** Memory Boundaries | ✅ PASS | Store conversation text only; no financial data |
| **VI.1** Test Pyramid | ✅ PASS | Unit > Integration > E2E proportions planned |
| **VI.2** 80% Coverage | ⏳ TARGET | Must maintain or exceed after implementation |
| **VII.1** No Secrets in Code | ✅ PASS | MongoDB connection via config loader |
| **VIII.2** Type Hints | ✅ PASS | All public methods will have type annotations |

### Memory Boundaries (Article V) — Critical Compliance

| Content Type | Storage Allowed | Constitution Reference |
|--------------|-----------------|------------------------|
| User query text | ✅ YES | V.2.a |
| Agent response text | ✅ YES | V.2.a |
| Tool call names | ✅ YES | V.2.a |
| Session assumptions | ✅ YES | V.2.b |
| Focused symbols (names only) | ✅ YES | V.2.c — NO prices/ratios |
| Stock prices | ❌ NEVER | V.3.a |
| Financial ratios | ❌ NEVER | V.3.a |
| Tool output data | ❌ NEVER | V.3.b |

### Post-Phase 1 Design Check ✅

*Re-evaluated after Phase 0 research and Phase 1 design completion.*

| Article | Requirement | Status | Evidence |
|---------|-------------|--------|----------|
| **IV.1** Repository Pattern | ✅ PASS | `ConversationRepository` defined in [data-model.md](./data-model.md) |
| **IV.2** Factory Pattern | ✅ PASS | `RepositoryFactory.get_conversation_repository()` specified |
| **IV.3** Protocol DI | ✅ PASS | Checkpointer injected via config; mockable interface |
| **IV.4** Blueprint Architecture | ✅ PASS | Routes modify existing `ai_chat_routes.py` blueprint |
| **V.1** Single Responsibility | ✅ PASS | Schema, Repository, Service, Routes each in dedicated files |
| **V.2** Open/Closed | ✅ PASS | New files extend system; minimal modification to existing |
| **V.3** Liskov Substitution | ✅ PASS | ConversationRepository extends MongoGenericRepository |
| **V.4** Interface Segregation | ✅ PASS | Minimal interface: get_or_create, update, archive |
| **V.5** Dependency Inversion | ✅ PASS | Agent depends on checkpointer protocol, not concrete |
| **VI.1** Test Pyramid | ✅ PASS | Plan includes unit (6), integration (3), e2e (1) tests |
| **VI.2** 80% Coverage | ⏳ TARGET | Test files planned for all new code |
| **VI.3** Mocking | ✅ PASS | Mock checkpointer pattern documented in [research.md](./research.md) |
| **VII.1** Pre-commit checks | ✅ PASS | No secrets in planned code |
| **VIII.1** Python standards | ✅ PASS | Type hints specified in all interfaces |

**Gate Result**: ✅ All constitutional requirements verified. Proceed to implementation.

---

## Project Structure

### Documentation (this feature)

```text
specs/spec-driven-development-pilot/
├── plan.md              # This file
├── research.md          # Phase 0: MongoDBSaver research, summarization patterns
├── data-model.md        # Phase 1: conversations collection schema, entity relationships
├── quickstart.md        # Phase 1: Developer setup guide for memory feature
└── contracts/           # Phase 1: API contracts for session-aware endpoints
    ├── chat-api.yaml    # OpenAPI for POST /api/chat with session_id
    └── socket-events.md # Socket.IO event specifications
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── stock_assistant_agent.py  # MODIFY: Add checkpointer, session_id params
│   ├── langgraph_bootstrap.py    # MODIFY: Initialize MongoDBSaver checkpointer
│   └── types.py                  # MODIFY: Add ConversationState dataclass (if needed)
│
├── data/
│   ├── schema/
│   │   └── conversations_schema.py     # NEW: Pydantic models, JSON schema
│   ├── repositories/
│   │   └── conversation_repository.py  # NEW: ConversationRepository
│   ├── migration/
│   │   └── db_setup.py                 # MODIFY: Add conversations, agent_checkpoints
│   └── repositories/factory.py         # MODIFY: Add get_conversation_repository()
│
├── services/
│   ├── conversation_service.py   # NEW: ConversationService (summarization, lifecycle)
│   └── factory.py                # MODIFY: Add get_conversation_service()
│
├── web/
│   ├── routes/
│   │   └── ai_chat_routes.py     # MODIFY: Add session_id parameter
│   └── sockets/
│       └── chat_events.py        # MODIFY: Add session_id to Socket.IO events
│
└── utils/
    ├── config_loader.py          # MODIFY: Add langchain.memory config section
    └── memory_config.py          # NEW: MemoryConfig dataclass with validation

config/
└── config.yaml                   # MODIFY: Add memory configuration section (9 parameters)

tests/
├── test_conversation_repository.py  # NEW: Unit tests for repository
├── test_conversation_service.py     # NEW: Unit tests for service
├── test_memory_config.py            # NEW: Unit tests for config validation (FR-3.1.10)
├── test_agent_memory.py             # NEW: Integration tests for multi-turn
├── api/
│   └── test_chat_routes_memory.py   # NEW: API tests with session_id
└── integration/
    └── test_memory_persistence.py   # NEW: Full persistence flow tests
```

**Structure Decision**: Extends existing `src/` structure following Constitution Article III patterns. New files created in domain-appropriate locations (schema → repositories → services → routes). Test files mirror source structure.

---

## Synchronization Matrix

> **Documents to keep aligned with this implementation**

| Document | Sync Points | Update Trigger |
|----------|-------------|----------------|
| [spec.md](../../.specify/specs/1-short-term-memory/spec.md) | Requirements FR-3.1.x, Success Criteria | If implementation changes scope |
| [constitution.md](../../.specify/memory/constitution.md) | Memory boundaries (Article V) | If new content types stored |
| [AGENT_MEMORY_TECHNICAL_DESIGN.md](../../docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md) | Data models, sequence diagrams, API contracts | If schema or flow changes |
| [LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md](../../docs/langchain-agent/LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md) | Architecture overview, component descriptions | After implementation complete |
| [docs/openapi.yaml](../../docs/openapi.yaml) | POST /api/chat request/response schema | When API contract finalized |
| [config/config_example.yaml](../../config/config_example.yaml) | Memory configuration section | When config schema finalized |

---

## Implementation Roadmap

> **Source**: Adapted from [AGENT_MEMORY_TECHNICAL_DESIGN.md](../../docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md) § Implementation Roadmap

### Phase 1: Foundation (6-7 story points)

| # | Task | Files | Est. |
|---|------|-------|------|
| 1.1 | Create `conversations` collection schema | `src/data/schema/conversations_schema.py` | 1 SP |
| 1.2 | Update `db_setup.py` with collection + indexes | `src/data/migration/db_setup.py` | 0.5 SP |
| 1.3 | Implement `ConversationRepository` | `src/data/repositories/conversation_repository.py` | 2 SP |
| 1.4 | Register in `RepositoryFactory` | `src/data/repositories/factory.py` | 0.5 SP |
| 1.5 | **Create `MemoryConfig` dataclass with validation (FR-3.1.9, FR-3.1.10)** | `src/utils/memory_config.py` | 1 SP |
| 1.6 | Add memory config to `config.yaml` (9 parameters) | `config/config.yaml`, `config_loader.py` | 1 SP |
| 1.7 | Unit tests for repository | `tests/test_conversation_repository.py` | 1 SP |
| 1.8 | **Unit tests for config validation** | `tests/test_memory_config.py` | 0.5 SP |

### Phase 2: Agent Integration (5-6 story points)

| # | Task | Files | Est. |
|---|------|-------|------|
| 2.1 | Initialize `MongoDBSaver` checkpointer | `src/core/langgraph_bootstrap.py` | 1.5 SP |
| 2.2 | Modify `StockAssistantAgent.__init__` for checkpointer | `src/core/stock_assistant_agent.py` | 1 SP |
| 2.3 | Add `session_id` param to `process_query()` | `src/core/stock_assistant_agent.py` | 1.5 SP |
| 2.4 | Add `session_id` param to `process_query_streaming()` | `src/core/stock_assistant_agent.py` | 1 SP |
| 2.5 | Unit tests for agent memory integration | `tests/test_agent_memory.py` | 1 SP |

### Phase 3: Service Layer (3-4 story points)

| # | Task | Files | Est. |
|---|------|-------|------|
| 3.1 | Implement `ConversationService` | `src/services/conversation_service.py` | 2 SP |
| 3.2 | Implement summarization trigger using `MemoryConfig` values | `src/services/conversation_service.py` | 1 SP |
| 3.3 | Register in `ServiceFactory` | `src/services/factory.py` | 0.5 SP |
| 3.4 | Unit tests for service (including config-driven behavior) | `tests/test_conversation_service.py` | 1 SP |

### Phase 4: API Integration (3-4 story points)

| # | Task | Files | Est. |
|---|------|-------|------|
| 4.1 | Modify `POST /api/chat` for `session_id` | `src/web/routes/ai_chat_routes.py` | 1 SP |
| 4.2 | Modify Socket.IO `chat_message` event | `src/web/sockets/chat_events.py` | 1 SP |
| 4.3 | Integration tests for API + memory | `tests/api/test_chat_routes_memory.py` | 1 SP |
| 4.4 | Update `docs/openapi.yaml` | `docs/openapi.yaml` | 0.5 SP |

### Phase 5: Testing & Polish (2-3 story points)

| # | Task | Files | Est. |
|---|------|-------|------|
| 5.1 | End-to-end multi-turn conversation test | `tests/integration/test_memory_persistence.py` | 1 SP |
| 5.2 | Performance benchmark (<500ms load) | `tests/integration/test_memory_persistence.py` | 0.5 SP |
| 5.3 | Backward compatibility test (no session_id) | `tests/test_agent_memory.py` | 0.5 SP |
| 5.4 | Documentation: quickstart.md | `specs/spec-driven-development-pilot/quickstart.md` | 0.5 SP |

**Total Estimated**: 20-25 story points

---

## Key Integration Points

### 1. MemoryConfig Dataclass Pattern (FR-3.1.9, FR-3.1.10)

```python
# src/utils/memory_config.py
from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class MemoryConfig:
    """Immutable memory configuration with validation (FR-3.1.9, FR-3.1.10)."""
    
    # Summarization thresholds
    summarize_threshold: int = 4000      # tokens; valid: 1000-10000
    max_messages: int = 50               # hard cap; valid: 10-200
    messages_to_keep: int = 10           # after summarization; valid: 5-50
    
    # Content limits
    max_content_size: int = 32768        # bytes; valid: 1024-65536
    summary_max_length: int = 500        # chars; valid: 100-2000
    
    # Performance tuning
    context_load_timeout_ms: int = 500   # valid: 100-5000
    state_save_timeout_ms: int = 50      # valid: 10-500
    
    # Collection names
    checkpoint_collection: str = "agent_checkpoints"
    conversations_collection: str = "conversations"
    
    def __post_init__(self):
        """Validate all parameters (fail-fast on invalid config)."""
        self._validate_range("summarize_threshold", 1000, 10000)
        self._validate_range("max_messages", 10, 200)
        self._validate_range("messages_to_keep", 5, 50)
        self._validate_range("max_content_size", 1024, 65536)
        self._validate_range("summary_max_length", 100, 2000)
        self._validate_range("context_load_timeout_ms", 100, 5000)
        self._validate_range("state_save_timeout_ms", 10, 500)
        
        if self.messages_to_keep >= self.max_messages:
            raise ValueError(f"messages_to_keep ({self.messages_to_keep}) must be < max_messages ({self.max_messages})")
    
    def _validate_range(self, field: str, min_val: int, max_val: int) -> None:
        value = getattr(self, field)
        if not (min_val <= value <= max_val):
            raise ValueError(f"{field}={value} out of range [{min_val}, {max_val}]")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "MemoryConfig":
        """Load from YAML config dict."""
        memory = config.get("langchain", {}).get("memory", {})
        return cls(**{k: v for k, v in memory.items() if k in cls.__dataclass_fields__})
```

### 2. MongoDBSaver Initialization Pattern

```python
# src/core/langgraph_bootstrap.py
from langgraph.checkpoint.mongodb import MongoDBSaver
from utils.memory_config import MemoryConfig

def create_checkpointer(config: Dict[str, Any]) -> Optional[MongoDBSaver]:
    """Create MongoDBSaver if memory is enabled (uses MemoryConfig)."""
    memory_config = config.get("langchain", {}).get("memory", {})
    
    if not memory_config.get("enabled", False):
        return None
    
    # Load and validate config (fail-fast on invalid)
    mem_cfg = MemoryConfig.from_config(config)
    
    return MongoDBSaver(
        connection_string=config["mongodb"]["uri"],
        db_name=config["mongodb"]["database"],
        collection_name=mem_cfg.checkpoint_collection
    )
```

### 2. Agent Session-Aware Invocation Pattern

```python
# src/core/stock_assistant_agent.py (modified)
def process_query(
    self, 
    query: str, 
    *, 
    provider: Optional[str] = None,
    session_id: Optional[str] = None  # NEW parameter
) -> str:
    """Process query with optional session memory."""
    config = {}
    if session_id and self._checkpointer:
        config["configurable"] = {"thread_id": session_id}
    
    result = self._agent_executor.invoke(
        {"messages": [HumanMessage(content=query)]},
        config=config
    )
    return result["messages"][-1].content
```

### 3. API Route Pattern

```python
# src/web/routes/ai_chat_routes.py (modified)
@blueprint.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    session_id = data.get('session_id')  # NEW: Optional
    
    # Validate session_id if provided
    if session_id:
        # Validate format, authorization, existence
        ...
    
    response = agent.process_query(message, session_id=session_id)
    return jsonify({"response": response})
```

---

## Success Criteria Mapping

| Spec Criteria | Implementation Verification |
|---------------|----------------------------|
| **SC-1** Context accuracy ≥95% | Test: Multi-turn conversation references earlier context correctly |
| **SC-2** Persistence reliability 100% | Test: Kill process mid-conversation, restart, verify context restored |
| **SC-3** Stateless mode 100% compliant | Test: No session_id → single-turn, no state created |
| **SC-4** No financial data in memory | Audit: Grep checkpoints for price patterns, verify none found |
| **SC-5** Uniqueness P(collision)<1e-18 | Use: UUID4 for session_id (122-bit entropy) |
| **SC-6** Reconnection rate ≥90% | Test: Simulate disconnect/reconnect, verify context restoration |
| **SC-7** Load time <`context_load_timeout_ms` | Benchmark: Profile `graph.get_state()` call latency against configurable threshold |
| **SC-8** Config compliance 100% | Test: `MemoryConfig` rejects invalid values, all components use config values |

---

## Complexity Tracking

> **No constitution violations detected** — structure complies with ≤3 logical projects, uses Repository/Factory patterns, follows SOLID principles.

| Decision | Rationale | Simpler Alternative Rejected Because |
|----------|-----------|-------------------------------------|
| Separate `conversations` + `agent_checkpoints` collections | App-managed metadata vs LangGraph-managed state | Single collection would require schema modifications LangGraph owns |
| ConversationService layer | Encapsulate summarization, lifecycle logic | Direct repository calls in routes would violate single responsibility |
| Protocol-based checkpointer injection | Enable testing with mock checkpointer | Hard-coded dependency would prevent unit testing agent in isolation |
| Frozen `MemoryConfig` dataclass (FR-3.1.9) | Immutable config, fail-fast validation, type safety | Dict-based config prone to typos, no validation at load time |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-27 | Initial plan created from spec v1.0.0 |
| 1.1.0 | 2025-01-28 | Added configuration tasks (FR-3.1.9, FR-3.1.10): Phase 1 tasks 1.5, 1.8; MemoryConfig pattern; SC-8 mapping |
